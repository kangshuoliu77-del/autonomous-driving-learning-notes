"""
MPC 路径跟踪控制器（含碰撞惩罚）

给定 Hybrid A* 规划的参考路径，每步对未来 N 步做滚动优化，
输出连续控制量 (v, phi) 使车辆平滑跟踪参考轨迹。

优化变量: u = [v_0, phi_0, v_1, phi_1, ..., v_{N-1}, phi_{N-1}]
代价函数: J = Σ (位置偏差² + 角度偏差² + 控制量变化² + 碰撞惩罚)
约束:     v ∈ [-1, 1],  phi ∈ [-0.4, 0.4]
求解器:   scipy.optimize.minimize (SLSQP)
"""

import math
import numpy as np
from scipy.optimize import minimize
from scipy.ndimage import distance_transform_edt


class MPCController:
    def __init__(self, car, grid_map, resolution, N=5, dt=0.5,
                 w_pos=5.0, w_theta=2.0, w_ctrl=0.1, w_obs=10.0, d_safe=0.5):
        self.car = car
        self.N = N
        self.dt = dt
        self.w_pos   = w_pos
        self.w_theta = w_theta
        self.w_ctrl  = w_ctrl
        self.w_obs   = w_obs    # 碰撞惩罚权重
        self.d_safe  = d_safe   # 安全距离 (m)

        self.v_max   =  1.0
        self.v_min   = -1.0
        self.phi_max =  0.4
        self.phi_min = -0.4

        # 构建距离场
        self.res  = resolution
        free_map  = np.array(grid_map == 0, dtype=np.float32)
        self.dist_field = distance_transform_edt(free_map) * resolution
        self.rows = self.dist_field.shape[0]
        self.cols = self.dist_field.shape[1]

    def _get_dist(self, x, y):
        ix = int(x / self.res)
        iy = int(y / self.res)
        if not (0 <= ix < self.rows and 0 <= iy < self.cols):
            return 0.0
        return float(self.dist_field[ix, iy])

    def _nearest_ref(self, state, ref_path, start_idx):
        min_dist = float('inf')
        best_idx = start_idx
        end = min(start_idx + 30, len(ref_path))
        for i in range(start_idx, end):
            dx = ref_path[i][0] - state[0]
            dy = ref_path[i][1] - state[1]
            d = math.sqrt(dx*dx + dy*dy)
            if d < min_dist:
                min_dist = d
                best_idx = i
        if min_dist < 0.5 and best_idx < len(ref_path) - 1:
            best_idx = min(best_idx + 1, len(ref_path) - 1)
        return best_idx

    def _predict(self, state, u_seq):
        states = [state]
        x, y, theta = state
        for k in range(self.N):
            v   = u_seq[2*k]
            phi = u_seq[2*k + 1]
            dx     = v * math.cos(theta) * self.dt
            dy     = v * math.sin(theta) * self.dt
            dtheta = (v * math.tan(phi) / self.car.L) * self.dt
            x     += dx
            y     += dy
            theta  = math.atan2(math.sin(theta + dtheta), math.cos(theta + dtheta))
            states.append((x, y, theta))
        return states

    def _cost(self, u_seq, state, ref_points):
        predicted = self._predict(state, u_seq)
        J = 0.0
        for k in range(self.N):
            px, py, ptheta = predicted[k+1]
            rx = ref_points[k][0]
            ry = ref_points[k][1]
            rtheta = ref_points[k][2]

            # 位置偏差
            J += self.w_pos * ((px - rx)**2 + (py - ry)**2)

            # 角度偏差
            angle_err = math.atan2(math.sin(ptheta - rtheta),
                                   math.cos(ptheta - rtheta))
            J += self.w_theta * angle_err**2

            # 碰撞惩罚：距离障碍物越近，惩罚越大
            dist = self._get_dist(px, py)
            if dist < self.d_safe:
                J += self.w_obs * (self.d_safe - dist) ** 2

            # 控制量平滑
            if k > 0:
                dv   = u_seq[2*k]   - u_seq[2*(k-1)]
                dphi = u_seq[2*k+1] - u_seq[2*(k-1)+1]
                J += self.w_ctrl * (dv**2 + dphi**2)

        return J

    def step(self, state, ref_path, ref_idx):
        idx = self._nearest_ref(state, ref_path, ref_idx)

        # 构造未来 N 步的参考状态
        ref_points = []
        for k in range(1, self.N + 1):
            ri = min(idx + k, len(ref_path) - 1)
            ref_points.append(ref_path[ri])

        # 到达路径末尾时，加大终点权重（将最后一个点重复填满预测窗口）
        if idx >= len(ref_path) - 10:
            goal = ref_path[-1]
            ref_points = [goal] * self.N

        ref0 = ref_points[0]
        v_sign = 1.0 if (len(ref0) < 4 or ref0[3] >= 0) else -1.0
        u0 = np.array([v_sign * 0.8, 0.0] * self.N, dtype=float)

        bounds = []
        for _ in range(self.N):
            bounds.append((self.v_min,   self.v_max))
            bounds.append((self.phi_min, self.phi_max))

        result = minimize(
            self._cost,
            u0,
            args=(state, ref_points),
            method='SLSQP',
            bounds=bounds,
            options={'maxiter': 100, 'ftol': 1e-4}
        )

        u_opt = result.x
        v   = float(np.clip(u_opt[0], self.v_min, self.v_max))
        phi = float(np.clip(u_opt[1], self.phi_min, self.phi_max))

        return (v, phi), idx
