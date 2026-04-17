"""
项目名称: 基于 Hybrid A* 算法的自动泊车路径规划 (垂直入库)
功能描述: 
    1. 模拟真实的停车场垂直车位环境；
    2. 实现随机起点采样，确保算法在多种起始角度下的鲁棒性；
    3. 结合运动学模型与碰撞检测，输出符合车辆物理特性的平滑泊车轨迹。
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import random

# 导入底层核心模块 (car_model, collision_checker, state_indexer, hybrid_astar)
from car_model import KinematicCar
from collision_checker import CollisionChecker
from state_indexer import StateIndexer
from hybrid_astar import HybridAStar

def create_parking_scenario(res):
    """
    构建垂直泊车静态地图场景
    参数: res (float) - 栅格地图分辨率 (单位: 米)
    返回: grid_map, goal_pos, slot_info (车位几何参数)
    """
    # 1. 初始化仿真地图空间 (20m x 15m)
    width, height = 20, 15
    grid_map = np.zeros((int(width/res), int(height/res)))
    
    # 2. 定义目标车位与邻近障碍物
    # 标准垂直车位设计: 宽度 2.5m, 长度 5.0m
    parking_slot_x = 10.0  # 车位几何中心 X 坐标
    parking_slot_y = 2.5   # 车位几何中心 Y 坐标 (纵深位置)
    slot_width = 2.5
    slot_length = 5.0
    
    # 定义物理坐标至地图索引的映射函数
    def to_idx(val): return int(val / res)

    # A. 绘制左侧邻车障碍 (保持 0.2m 安全间隙)
    left_car_start_x = parking_slot_x - slot_width - 0.2
    left_car_end_x = parking_slot_x - slot_width/2.0 - 0.2
    grid_map[to_idx(left_car_start_x):to_idx(left_car_end_x), to_idx(1.0):to_idx(1.0+slot_length)] = 1
    
    # B. 绘制右侧邻车障碍 (保持 0.2m 安全间隙)
    right_car_start_x = parking_slot_x + slot_width/2.0 + 0.2
    right_car_end_x = parking_slot_x + slot_width + 0.2
    grid_map[to_idx(right_car_start_x):to_idx(right_car_end_x), to_idx(1.0):to_idx(1.0+slot_length)] = 1
    
    # C. 绘制底部墙壁/路沿边界
    grid_map[:, to_idx(0.0):to_idx(1.0)] = 1

    # 设定目标位姿 (Goal Pose): 车位中心，车头朝向垂直向上 (90度)
    goal_pos = (parking_slot_x, parking_slot_y, math.radians(90))
    
    return grid_map, goal_pos, (parking_slot_x, parking_slot_y, slot_width, slot_length)

def get_random_start_pos(car, checker):
    """
    在指定航道区域内随机生成合法的起始位姿 (无碰撞随机起点)
    采样范围: X[2.0, 18.0], Y[9.0, 13.0], Theta[0, 2π]
    """
    while True:
        rx = random.uniform(2.0, 18.0)
        ry = random.uniform(9.0, 13.0) 
        rt = random.uniform(0, 2 * math.pi)
        start_node = (rx, ry, rt)
        
        # 碰撞检测: 确保采样点不与车位障碍物重叠
        if not checker.is_collision(car.get_corners(start_node)):
            return start_node

def main():
    # --- 1. 环境配置与离散化参数 ---
    res_xy = 0.3                # 位置离散粒度 (m)
    res_theta = math.radians(5) # 航向角离散粒度 (deg)
    
    # 初始化地图与目标
    grid_map, goal_pos, slot_info = create_parking_scenario(res_xy)

    # --- 2. 核心模块实例化 ---
    car = KinematicCar()
    checker = CollisionChecker(grid_map, res_xy)

    # --- 3. 采样生成泊车起始点 ---
    start_pos = get_random_start_pos(car, checker)

    # --- 4. 路径规划器初始化 ---
    indexer = StateIndexer(res_xy, res_theta)
    planner = HybridAStar(car, checker, indexer, goal_pos) 
    
    print(f"[*] 采样随机起点: X={start_pos[0]:.2f}, Y={start_pos[1]:.2f}, θ={math.degrees(start_pos[2]):.1f}°")
    print(f"[*] 目标停车位: {goal_pos}")
    print("[*] Hybrid A* 算法正在计算泊车路径...")

    # --- 5. 执行路径搜索 ---
    path = planner.solve(start_pos) 

    # --- 6. 结果可视化与评估 ---
    if path:
        print(f"[✔] 规划成功: 生成轨迹包含 {len(path)} 个状态点。")
        plt.figure(figsize=(12, 10))
        
        # A. 绘制环境障碍物 (静态地图)
        obs_x, obs_y = np.where(grid_map == 1)
        plt.scatter(obs_x * res_xy, obs_y * res_xy, color='black', marker='s', s=80, label="Static Obstacles")
        
        # B. 绘制目标车位线 (蓝色虚线框)
        sx, sy, sw, sl = slot_info
        plt.plot([sx-sw/2, sx+sw/2, sx+sw/2, sx-sw/2, sx-sw/2], 
                 [sy-sl/2+1, sy-sl/2+1, sy+sl/2+1, sy+sl/2+1, sy-sl/2+1], 
                 'b--', linewidth=2, label="Assigned Slot")

        # C. 标注起点与目标点
        plt.plot(start_pos[0], start_pos[1], 'bo', markersize=12, label="Start Point")
        plt.plot(goal_pos[0], goal_pos[1], 'rx', markersize=12, label="Goal Point")
        
        # D. 绘制规划轨迹与车身几何包络
        px, py = [s[0] for s in path], [s[1] for s in path]
        plt.plot(px, py, 'r-', linewidth=2, label="Optimized Path")
        
        for i, state in enumerate(path):
            if i % 2 == 0:  # 隔帧绘制，保证图形清晰
                corners = car.get_corners(state)
                corners.append(corners[0]) 
                cx, cy = zip(*corners)
                plt.plot(cx, cy, 'g-', alpha=0.3) 
                # 绘制车头指向箭头 (Heading Indicator)
                plt.arrow(state[0], state[1], math.cos(state[2])*0.6, math.sin(state[2])*0.6, 
                          head_width=0.3, color='blue', alpha=0.5)

        # 突出显示最终停放位姿 (蓝色实线)
        final_state = path[-1]
        final_corners = car.get_corners(final_state)
        final_corners.append(final_corners[0])
        fcx, fcy = zip(*final_corners)
        plt.plot(fcx, fcy, 'b-', linewidth=3, label="Final Pose") 

        # 图表修饰
        plt.title("Path Planning Results: Vertical Parking Scenario")
        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")
        plt.axis("equal")
        plt.xlim(0, 20)
        plt.ylim(0, 15)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(loc="upper right")
        plt.show()
    else:
        print("[✘] 规划失败: 未找到有效路径。")

if __name__ == "__main__":
    main()