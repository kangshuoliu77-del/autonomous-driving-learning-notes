import math

def get_dist(p1, p2):
    """
    计算启发式代价 (Heuristic Cost)
    使用欧几里得距离 (Euclidean Distance)
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx**2 + dy**2)