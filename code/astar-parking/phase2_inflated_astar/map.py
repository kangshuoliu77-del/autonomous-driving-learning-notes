import random
import math

def get_safe_random_map(rows=50, cols=80, obstacle_prob=0.05, start=(0,0), end=(49,79)):
    """随机生成地图，并确保起点和终点是空的。"""
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if random.random() < obstacle_prob:
                maze[r][c] = 1
    maze[start[0]][start[1]] = 0
    maze[end[0]][end[1]] = 0
    return maze

def get_inflated_map(maze, radius):
    """
    配置空间(C-Space)转换：通过膨胀障碍物给机器人留出安全余量。
    """
    if radius <= 0: return maze
    rows, cols = len(maze), len(maze[0])
    new_maze = [row[:] for row in maze]
    
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 1:
                # 整数半径膨胀：遍历周围的正方形区域
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            new_maze[nr][nc] = 1
    return new_maze