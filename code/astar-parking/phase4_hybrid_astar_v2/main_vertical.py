"""
项目名称: 基于 Hybrid A* 算法的自动泊车路径规划 (垂直入库)
功能描述:
    1. 模拟真实的停车场垂直车位环境；
    2. 实现随机起点采样，确保算法在多种起始角度下的鲁棒性；
    3. Hybrid A* 规划参考路径，MPC 控制器跟踪执行。
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import random

from car_model import KinematicCar
from collision_checker import CollisionChecker
from state_indexer import StateIndexer
from hybrid_astar import HybridAStar
from mpc_controller import MPCController

def create_parking_scenario(res):
    width, height = 20, 15
    grid_map = np.zeros((int(width/res), int(height/res)))

    parking_slot_x = 10.0
    parking_slot_y = 2.5
    slot_width = 2.5
    slot_length = 5.0

    def to_idx(val): return int(val / res)

    left_car_start_x = parking_slot_x - slot_width - 0.2
    left_car_end_x   = parking_slot_x - slot_width/2.0 - 0.2
    grid_map[to_idx(left_car_start_x):to_idx(left_car_end_x), to_idx(1.0):to_idx(1.0+slot_length)] = 1

    right_car_start_x = parking_slot_x + slot_width/2.0 + 0.2
    right_car_end_x   = parking_slot_x + slot_width + 0.2
    grid_map[to_idx(right_car_start_x):to_idx(right_car_end_x), to_idx(1.0):to_idx(1.0+slot_length)] = 1

    grid_map[:, to_idx(0.0):to_idx(1.0)] = 1

    goal_pos = (parking_slot_x, parking_slot_y, math.radians(90))
    return grid_map, goal_pos, (parking_slot_x, parking_slot_y, slot_width, slot_length)

def get_random_start_pos(car, checker):
    while True:
        rx = random.uniform(2.0, 18.0)
        ry = random.uniform(9.0, 13.0)
        rt = random.uniform(0, 2 * math.pi)
        start_node = (rx, ry, rt)
        if not checker.is_collision(car.get_corners(start_node)):
            return start_node

def interpolate_path(path, step=0.1):
    """把稀疏路径插值为每隔 step 米一个点的密集路径"""
    dense = [path[0]]
    for i in range(1, len(path)):
        p1, p2 = path[i-1], path[i]
        dx, dy = p2[0]-p1[0], p2[1]-p1[1]
        dist = math.sqrt(dx*dx + dy*dy)
        n = max(1, int(dist / step))
        for k in range(1, n):
            t = k / n
            dense.append((p1[0]+t*dx, p1[1]+t*dy, p1[2], p1[3]))
        dense.append(p2)
    return dense

def main():
    res_xy    = 0.3
    res_theta = math.radians(5)

    grid_map, goal_pos, slot_info = create_parking_scenario(res_xy)

    car     = KinematicCar()
    checker = CollisionChecker(grid_map, res_xy)
    start_pos = get_random_start_pos(car, checker)

    indexer = StateIndexer(res_xy, res_theta)
    planner = HybridAStar(car, checker, indexer, goal_pos)
    mpc     = MPCController(car, grid_map, res_xy, N=5, dt=0.5)

    print(f"[*] 采样随机起点: X={start_pos[0]:.2f}, Y={start_pos[1]:.2f}, θ={math.degrees(start_pos[2]):.1f}°")
    print(f"[*] 目标停车位: {goal_pos}")
    print("[*] Hybrid A* 算法正在计算泊车路径...")

    path = planner.solve(start_pos)

    if not path:
        print("[✘] 规划失败: 未找到有效路径。")
        return

    # 插值加密参考路径
    path = interpolate_path(path, step=0.1)
    print(f"[✔] 规划成功: 插值后 {len(path)} 个状态点，开始 MPC 跟踪...")

    # MPC 仿真循环
    sim_state = start_pos
    mpc_traj  = [sim_state]
    ref_idx   = 0

    for step in range(500):
        dx = sim_state[0] - goal_pos[0]
        dy = sim_state[1] - goal_pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        angle_err = abs(math.atan2(math.sin(sim_state[2] - goal_pos[2]),
                                   math.cos(sim_state[2] - goal_pos[2])))
        if dist < 0.3 and angle_err < math.radians(5):
            print(f"[✔] MPC 跟踪完成，共 {step} 步。")
            break

        (v, phi), ref_idx = mpc.step(sim_state, path, ref_idx)
        sim_state = car.update_state(sim_state, v, phi, dt=mpc.dt)
        mpc_traj.append(sim_state)
    else:
        print("[!] MPC 达到最大步数限制。")

    # 可视化
    plt.figure(figsize=(12, 10))

    obs_x, obs_y = np.where(grid_map == 1)
    plt.scatter(obs_x * res_xy, obs_y * res_xy, color='black', marker='s', s=80, label="Static Obstacles")

    sx, sy, sw, sl = slot_info
    plt.plot([sx-sw/2, sx+sw/2, sx+sw/2, sx-sw/2, sx-sw/2],
             [sy-sl/2+1, sy-sl/2+1, sy+sl/2+1, sy+sl/2+1, sy-sl/2+1],
             'b--', linewidth=2, label="Assigned Slot")

    plt.plot(start_pos[0], start_pos[1], 'bo', markersize=12, label="Start Point")
    plt.plot(goal_pos[0],  goal_pos[1],  'rx', markersize=12, label="Goal Point")

    # Hybrid A* 参考路径（灰色虚线）
    px, py = [s[0] for s in path], [s[1] for s in path]
    plt.plot(px, py, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label="Hybrid A* Ref")
    # MPC 实际轨迹（红色实线）
    mx, my = [s[0] for s in mpc_traj], [s[1] for s in mpc_traj]
    plt.plot(mx, my, 'r-', linewidth=2, label="MPC Trajectory")

    # 车身包络（沿 MPC 轨迹，每5步画一次）
    for i, state in enumerate(mpc_traj):
        if i % 5 == 0:
            corners = car.get_corners(state)
            if all(0 <= c[0] <= 20 and 0 <= c[1] <= 15 for c in corners):
                corners.append(corners[0])
                cx, cy = zip(*corners)
                plt.plot(cx, cy, 'g-', alpha=0.3)
                plt.arrow(state[0], state[1],
                          math.cos(state[2])*0.6, math.sin(state[2])*0.6,
                          head_width=0.3, color='blue', alpha=0.5)

    # 最终停放位姿
    final_corners = car.get_corners(mpc_traj[-1])
    final_corners.append(final_corners[0])
    fcx, fcy = zip(*final_corners)
    plt.plot(fcx, fcy, 'b-', linewidth=3, label="Final Pose")

    plt.title("Hybrid A* + MPC (CasADi/IPOPT): Vertical Parking")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.axis("equal")
    plt.xlim(0, 20)
    plt.ylim(0, 15)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper right")
    plt.show()

if __name__ == "__main__":
    main()
