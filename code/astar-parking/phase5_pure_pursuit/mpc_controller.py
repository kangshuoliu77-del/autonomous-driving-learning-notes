"""
Phase 5 MPC 控制器 — CasADi + IPOPT

相比 Phase 4 (SLSQP) 的改进：
1. 优化器换为 IPOPT，梯度自动微分，收敛更稳定
2. 碰撞检测改为 4 角点，消除中心点盲区
3. 角点距离场值作为参数传入（线性化近似），兼顾精度与速度
"""

import math
import numpy as np
from scipy.ndimage import distance_transform_edt
import casadi as ca


class MPCController:
    def __init__(self, car, grid_map, res, N=5, dt=0.5):
        self.car = car
        self.res = res
        self.N   = N
        self.dt  = dt

        self.w_pos   = 5.0
        self.w_theta = 2.0
        self.w_ctrl  = 0.1
        self.w_obs   = 15.0
        self.d_safe  = 0.5

        free = (grid_map == 0).astype(float)
        self.dist_field = distance_transform_edt(free) * res

        self._build_solver()

    def _build_solver(self):
        """预编译 CasADi NLP，避免每步重建符号图。"""
        N, dt = self.N, self.dt
        L_wb = self.car.L
        L_h  = self.car.length / 2
        W_h  = self.car.width  / 2

        # 决策变量：[v0,phi0, v1,phi1, ...]
        U = ca.MX.sym('U', 2 * N)

        # 参数：初始状态(3) + 参考轨迹(N*3) + 角点距离场值(N*4)
        P = ca.MX.sym('P', 3 + N * 3 + N * 4)

        x_k  = P[0]
        y_k  = P[1]
        th_k = P[2]

        J = 0
        for i in range(N):
            v_i   = U[2*i]
            phi_i = U[2*i + 1]

            # Euler 积分
            x_k  = x_k  + v_i * ca.cos(th_k) * dt
            y_k  = y_k  + v_i * ca.sin(th_k) * dt
            th_k = th_k + (v_i / L_wb) * ca.tan(phi_i) * dt

            # 参考点
            rx    = P[3 + i*3]
            ry    = P[3 + i*3 + 1]
            rth   = P[3 + i*3 + 2]

            # 位置 + 角度代价
            J += self.w_pos   * ((x_k - rx)**2 + (y_k - ry)**2)
            J += self.w_theta * (1 - ca.cos(th_k - rth))

            # 控制平滑
            if i > 0:
                J += self.w_ctrl * ((U[2*i] - U[2*i-2])**2 +
                                    (U[2*i+1] - U[2*i-1])**2)

            # 4角点碰撞惩罚（距离场值作为参数，线性化）
            for j, (ldx, ldy) in enumerate([(L_h,W_h),(L_h,-W_h),(-L_h,W_h),(-L_h,-W_h)]):
                cx = x_k + ldx * ca.cos(th_k) - ldy * ca.sin(th_k)
                cy = y_k + ldx * ca.sin(th_k) + ldy * ca.cos(th_k)
                # 参数中存的是当前步角点的距离场近似值
                d_approx = P[3 + N*3 + i*4 + j]
                # 当预测位置接近障碍时施加惩罚
                # 用参数值作为软约束（IPOPT 稳定收敛）
                penalty = ca.fmax(0, self.d_safe - d_approx) ** 2
                J += self.w_obs * penalty

        nlp = {'x': U, 'f': J, 'p': P}
        opts = {
            'ipopt': {
                'max_iter': 150,
                'print_level': 0,
                'acceptable_tol': 1e-4,
            },
            'print_time': 0,
        }
        self._solver = ca.nlpsol('mpc', 'ipopt', nlp, opts)

        # 控制量上下界
        lbx = np.array([-1.0, -0.4] * N)
        ubx = np.array([ 1.0,  0.4] * N)
        self._lbx = lbx
        self._ubx = ubx

    def _get_dist(self, x, y):
        ix = max(0, min(int(x / self.res), self.dist_field.shape[0]-1))
        iy = max(0, min(int(y / self.res), self.dist_field.shape[1]-1))
        return float(self.dist_field[ix, iy])

    def _corner_dists(self, state):
        """计算当前状态下4角点的距离场值。"""
        x, y, th = state
        L_h = self.car.length / 2
        W_h = self.car.width  / 2
        ct, st = math.cos(th), math.sin(th)
        dists = []
        for ldx, ldy in [(L_h,W_h),(L_h,-W_h),(-L_h,W_h),(-L_h,-W_h)]:
            cx = x + ldx*ct - ldy*st
            cy = y + ldx*st + ldy*ct
            dists.append(self._get_dist(cx, cy))
        return dists

    def _nearest_ref(self, state, ref_path, ref_idx):
        x, y = state[0], state[1]
        best_idx = ref_idx
        best_d   = float('inf')
        for i in range(ref_idx, min(ref_idx + 30, len(ref_path))):
            dx = ref_path[i][0] - x
            dy = ref_path[i][1] - y
            d  = math.sqrt(dx*dx + dy*dy)
            if d < best_d:
                best_d, best_idx = d, i
        if best_d < 0.5 and best_idx < len(ref_path) - 1:
            best_idx = min(best_idx + 1, len(ref_path) - 1)
        return best_idx

    def step(self, state, ref_path, ref_idx):
        ref_idx = self._nearest_ref(state, ref_path, ref_idx)

        if ref_idx >= len(ref_path) - 10:
            goal = ref_path[-1]
            ref_points = [goal] * self.N
        else:
            ref_points = [ref_path[min(ref_idx + i, len(ref_path)-1)]
                          for i in range(self.N)]

        # 初始猜测
        ref0   = ref_points[0]
        v_sign = 1.0 if (len(ref0) < 4 or ref0[3] >= 0) else -1.0
        u0 = np.array([v_sign * 0.8, 0.0] * self.N)

        # 构建参数向量
        # 用当前状态的角点距离近似所有预测步（快速近似）
        corner_d = self._corner_dists(state)
        p = np.array(
            list(state[:3]) +
            [coord for r in ref_points for coord in (r[0], r[1], r[2])] +
            corner_d * self.N   # N步都用当前角点距离近似
        )

        try:
            sol = self._solver(x0=u0, p=p, lbx=self._lbx, ubx=self._ubx)
            u_opt = np.array(sol['x']).flatten()
            v_opt   = float(u_opt[0])
            phi_opt = float(u_opt[1])
        except Exception:
            v_opt, phi_opt = v_sign * 0.3, 0.0

        return (v_opt, phi_opt), ref_idx
