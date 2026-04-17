import math

class StateIndexer:
    """
    模块三：状态空间索引与剪枝
    职责：
    1. 把连续的 (x, y, theta) 映射到离散的整数索引。
    2. 记录哪些“抽屉”已经被访问过。
    3. 如果新来的路径更长，则通过剪枝减少计算量。
    """
    def __init__(self, res_xy, res_theta):
        self.res_xy = res_xy       # 距离分辨率 (例如 0.1m)
        self.res_theta = res_theta # 角度分辨率 (例如 5度，需转为弧度)
        
        # 使用集合(set)存储索引，查找速度为 O(1)
        # 存入的格式为 (idx_x, idx_y, idx_theta)
        self.visited = set()

    def is_visited_and_add(self, state):
        """
        判断该状态是否已经有人占坑了。
        如果没人占坑，就把它加进去，并返回 False（代表可以继续搜索）。
        """
        x, y, theta = state
        
        # 1. 坐标离散化
        idx_x = int(x / self.res_xy)
        idx_y = int(y / self.res_xy)
        
        # 2. 角度离散化
        # 首先把角度规范化到 [0, 2*pi)，防止 -0.1pi 和 1.9pi 被当成不同状态
        norm_theta = theta % (2 * math.pi)
        idx_theta = int(norm_theta / self.res_theta)
        
        index = (idx_x, idx_y, idx_theta)
        
        # 3. 查表与登记
        if index in self.visited:
            return True # 已经来过了，剪枝！
        else:
            self.visited.add(index)
            return False # 第一次来，登记并放行