import math


class CollisionChecker:
    """
    模块二：基于边缘采样的碰撞检测

    沿车身四条边均匀采样，逐点查栅格地图。
    精度高，适用于垂直/平行泊车窄间隙场景。
    """
    def __init__(self, grid_map, resolution):
        self.grid_map = grid_map
        self.res = resolution
        self.rows = len(grid_map)
        self.cols = len(grid_map[0])

    def is_collision(self, corners):
        res = self.res
        rows = self.rows
        cols = self.cols
        grid = self.grid_map

        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dist = math.sqrt(dx * dx + dy * dy)
            num_samples = int(dist / res) + 1

            for n in range(num_samples + 1):
                t = n / num_samples
                x = p1[0] + t * dx
                y = p1[1] + t * dy
                ix = int(x / res)
                iy = int(y / res)
                if not (0 <= ix < rows and 0 <= iy < cols and grid[ix][iy] == 0):
                    return True

        return False
