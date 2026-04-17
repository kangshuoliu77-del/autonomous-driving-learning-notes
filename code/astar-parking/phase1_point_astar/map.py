# map.py
import random

def get_random_parking_map(rows=10, cols=15, obstacle_prob=0.2):
    """
    随机生成栅格地图
    :param rows: 地图行数
    :param cols: 地图列数
    :param obstacle_prob: 障碍物出现的概率 (0.0 ~ 1.0)
    """
    # 初始生成全 0 地图
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for r in range(rows):
        for c in range(cols):
            # 生成一个 0-1 之间的随机数，如果小于概率阈值，则设为障碍物
            if random.random() < obstacle_prob:
                maze[r][c] = 1
                
    return maze

def get_safe_random_map(rows=10, cols=15, obstacle_prob=0.2, start=(0,0), end=(9,14)):
    """
    生成随机地图并确保起点和终点是干净的
    """
    maze = get_random_parking_map(rows, cols, obstacle_prob)
    
    # 强制清空起点和终点，确保逻辑能跑通
    maze[start[0]][start[1]] = 0
    maze[end[0]][end[1]] = 0
    
    return maze