import math

def calculate(pos, goal_pos):
    """
    计算欧几里得距离 (Euclidean Distance).
    根据 MR 10.4，允许斜向移动时必须使用欧式距离。
    """
    return math.sqrt((pos[0] - goal_pos[0])**2 + (pos[1] - goal_pos[1])**2)