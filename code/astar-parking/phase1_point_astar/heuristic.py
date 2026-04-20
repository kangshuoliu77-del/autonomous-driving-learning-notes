import math

def get_dist(p1, p2):
    """
    计算启发式代价 (Heuristic Cost)
    使用曼哈顿距离 (Manhattan Distance) — 4-connected 网格的最优 admissible heuristic
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])