"""
项目名称: 基于 Hybrid A* 算法的自动泊车路径规划 (侧方位停车)
功能描述: 
    1. 模拟极其紧凑的侧方停车环境 (极限工况)；
    2. 实现高精度空间下的路径搜索与碰撞检测；
    3. 支持多轮换挡(揉库)逻辑的自动识别与轨迹可视化。
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import random

# 从核心算法库导入模块 (确保 car_model.py, collision_checker.py 等在同一目录下)
from car_model import KinematicCar
from collision_checker import CollisionChecker
from state_indexer import StateIndexer
from hybrid_astar import HybridAStar

def create_tight_parallel_scenario(res):
    """
    创建极其真实的侧方泊车场景
    配置: 车宽1.8m, 车位宽2.0m, 两侧仅留10cm余量 (极限紧贴)
    """
    width, height = 25, 10
    grid_map = np.zeros((int(width/res), int(height/res)))
    
    # 场景核心物理参数
    slot_length = 5.8   # 泊车位长度
    slot_width = 2.0    # 泊车位宽度
    parking_slot_x = 12.0
    parking_slot_y = 1.4  # 目标中心 Y 坐标 (确保车身紧靠路沿)
    
    def to_idx(val): return int(val / res)

    # A. 绘制路沿/路基边界 (黑色)
    grid_map[:, to_idx(0.0):to_idx(0.4)] = 1
    
    # B. 绘制前障碍车 (Positioned in front of slot)
    grid_map[to_idx(parking_slot_x + slot_length/2):to_idx(parking_slot_x + slot_length/2 + 4.0), 
             to_idx(0.4):to_idx(2.2)] = 1
             
    # C. 绘制后障碍车 (Positioned behind slot)
    grid_map[to_idx(parking_slot_x - slot_length/2 - 4.0):to_idx(parking_slot_x - slot_length/2), 
             to_idx(0.4):to_idx(2.2)] = 1

    # 设置泊车终点位姿
    goal_pos = (parking_slot_x, parking_slot_y, 0.0)
    return grid_map, goal_pos, (parking_slot_x, parking_slot_y, slot_length, slot_width)

def get_random_start_pos(car, checker):
    """
    在安全范围内采样生成随机起始位姿
    """
    while True:
        rx = random.uniform(5.0, 15.0)
        ry = random.uniform(5.0, 7.0)
        rt = random.uniform(-0.2, 0.2)
        start_node = (rx, ry, rt)
        
        # 验证初始采样位姿是否发生碰撞
        if not checker.is_collision(car.get_corners(start_node)):
            return start_node

def main():
    # --- 1. 算法与环境离散化配置 ---
    # 为支持窄位操作，使用更高分辨率的网格 (0.1m) 和角度步长 (2deg)
    res_xy = 0.1           
    res_theta = math.radians(2) 
    
    # 初始化场景数据
    grid_map, goal_pos, slot_info = create_tight_parallel_scenario(res_xy)
    car = KinematicCar()
    checker = CollisionChecker(grid_map, res_xy)
    
    # 随机生成起点位姿
    start_pos = get_random_start_pos(car, checker)

    # --- 2. 规划器实例化 ---
    indexer = StateIndexer(res_xy, res_theta)
    planner = HybridAStar(car, checker, indexer, goal_pos) 
    
    print(f"[*] 随机起点已就绪: X={start_pos[0]:.2f}, Y={start_pos[1]:.2f}")
    print("[*] 正在执行“侧方泊车”路径搜索...")
    
    # --- 3. 执行算法求解 ---
    path = planner.solve(start_pos) 

    # --- 4. 结果可视化分析 ---
    if path:
        print(f"[✔] 成功规划路径，包含 {len(path)} 个状态点。")
        plt.figure(figsize=(15, 7))
        
        # A. 绘制静态地图障碍物
        obs_x, obs_y = np.where(grid_map == 1)
        plt.scatter(obs_x * res_xy, obs_y * res_xy, color='black', marker='s', s=10, label="Obstacles")
        
        # B. 绘制目标泊车位边界参考 (蓝色虚线)
        sx, sy, sl, sw = slot_info
        rect_x = [sx-2, sx+2, sx+2, sx-2, sx-2] # 假设物理车长 4m
        rect_y = [sy-0.9, sy-0.9, sy+0.9, sy+0.9, sy-0.9] # 假设物理车宽 1.8m
        plt.plot(rect_x, rect_y, 'b--', linewidth=2, label="Target Alignment")

        # C. 绘制规划轨迹中心线
        px, py = [s[0] for s in path], [s[1] for s in path]
        plt.plot(px, py, 'r-', alpha=0.6, label="Path Centerline")

        # D. 绘制车辆包络帧及航向箭头
        for i, state in enumerate(path):
            if i % 3 == 0:  # 抽稀显示，提高渲染清晰度
                corners = car.get_corners(state)
                corners.append(corners[0]) 
                plt.plot(*zip(*corners), 'g-', alpha=0.15) 
                # 绘制车头方向指示箭头
                plt.arrow(state[0], state[1], math.cos(state[2])*0.5, math.sin(state[2])*0.5, 
                          head_width=0.2, color='blue', alpha=0.3)

        # E. 标注换挡修正点 (Gear Shift Points)
        gear_label_added = False
        for i in range(1, len(path)-1):
            # 通过位移向量积判断运动方向是否发生翻转
            if (path[i][0]-path[i-1][0]) * (path[i+1][0]-path[i][0]) < 0:
                plt.plot(path[i][0], path[i][1], 'yo', markersize=8, markeredgecolor='k', 
                         label="Gear Shift" if not gear_label_added else "")
                gear_label_added = True

        # F. 标注起始点、终点及最终泊车状态
        plt.plot(start_pos[0], start_pos[1], 'bo', markersize=12, label="Start Point")
        plt.plot(goal_pos[0], goal_pos[1], 'rx', markersize=15, markeredgewidth=3, label="Goal Point")

        final_corners = car.get_corners(path[-1])
        final_corners.append(final_corners[0])
        plt.plot(*zip(*final_corners), 'b-', linewidth=3, label="Final Parking Pose") 

        # 图像修饰与显示
        plt.title("Path Planning Results: Ultra-Tight Parallel Parking")
        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")
        plt.axis("equal")
        plt.ylim(0, 10)
        plt.grid(True, linestyle=':', alpha=0.4)
        plt.legend(loc="upper right", fontsize='small', framealpha=0.9)
        plt.show()
    else:
        print("[✘] 路径规划失败: 请检查搜索步长参数或碰撞检测边界。")

if __name__ == "__main__":
    main()