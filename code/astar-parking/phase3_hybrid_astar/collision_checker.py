import math

class CollisionChecker:
    """
    模块二：基于边缘采样的碰撞检测
    职责：
    1. 接收车身四个角点坐标。
    2. 在每条边上进行线性插值采样。
    3. 判定采样点是否落在地图障碍物或地图外。
    """
    def __init__(self, grid_map, resolution):
        self.grid_map = grid_map       # 二维数组，0为路，1为墙
        self.res = resolution          # 地图分辨率 (例如 0.1m/格)
        self.rows = len(grid_map)      # 栅格地图的行数 (X方向)
        self.cols = len(grid_map[0])   # 栅格地图的列数 (Y方向)

    def is_collision(self, corners):
        """
        判断当前的四个角点构成的矩形是否发生碰撞
        corners: [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
        """
        # 1. 遍历矩形的 4 条边
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]  # 技巧：当 i=3 时，i+1=4，取模后回到 0，闭合矩形
            
            # 2. 确定采样密度
            # 计算这条边的物理长度 (欧几里得距离)
            dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            # 保证采样点间隔小于地图分辨率，这样就不会“穿模”过细小的障碍物
            num_samples = int(dist / self.res) + 1
            
            # 3. 在边上“撒点” (线性插值)
            for n in range(num_samples):
                # t 从 0 变到 1
                t = n / num_samples
                # 线性插值公式：P = P1 + t * (P2 - P1)
                test_x = p1[0] + t * (p2[0] - p1[0])
                test_y = p1[1] + t * (p2[1] - p1[1])
                
                # 4. 坐标转索引并检查
                # 物理坐标 / 分辨率 = 数组下标
                idx_x = int(test_x / self.res)
                idx_y = int(test_y / self.res)
                
                # 5. 组合判断：越界 or 撞墙 (简洁写法)
                if not (0 <= idx_x < self.rows and 0 <= idx_y < self.cols and self.grid_map[idx_x][idx_y] == 0):
                    return True # 只要有一点不满足，就是撞了
        
        return False # 所有的边、所有的采样点都通过了，安全