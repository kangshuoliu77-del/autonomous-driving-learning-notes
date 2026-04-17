class Node:
    """
    A* 算法节点类，用于存储状态信息与路径拓扑
    """
    def __init__(self, position, parent=None):
        self.position = position  # 坐标元组 (x, y)
        self.parent = parent      # 父节点引用，用于路径回溯

        self.g = 0  # 起点到当前节点的实际代价值
        self.h = 0  # 当前节点到终点的预估代价值（启发式）
        self.f = 0  # 总代价值 f = g + h

    def __eq__(self, other):
        """定义节点等价性：基于位置坐标判断"""
        return self.position == other.position
