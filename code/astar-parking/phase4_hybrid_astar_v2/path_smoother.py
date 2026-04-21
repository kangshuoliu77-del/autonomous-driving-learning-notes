"""
路径平滑模块：梯度下降法（分段）

按换挡点（前进↔倒车）把路径切成若干段，每段单独平滑：
  - 平滑力：牵引相邻三点趋向共线，消除曲率跳变
  - 障碍物排斥力：保证路径远离障碍物边界
  - 每段首尾固定不动，保持换挡点位置精确
  - theta 由位移方向重新计算，与 v 符号保持自洽
"""

import math
import numpy as np
from scipy.ndimage import distance_transform_edt


class PathSmoother:
    def __init__(self, grid_map, resolution,
                 alpha=0.2, beta=0.8, d_safe=1.0, max_iter=500):
        self.res = resolution
        self.alpha = alpha
        self.beta = beta
        self.d_safe = d_safe
        self.max_iter = max_iter

        free_map = np.array(grid_map == 0, dtype=np.float32)
        self.dist_field = distance_transform_edt(free_map) * resolution
        self.rows = self.dist_field.shape[0]
        self.cols = self.dist_field.shape[1]

    def _get_dist(self, x, y):
        ix = int(x / self.res)
        iy = int(y / self.res)
        if not (0 <= ix < self.rows and 0 <= iy < self.cols):
            return 0.0
        return float(self.dist_field[ix, iy])

    def _obs_gradient(self, x, y):
        eps = self.res
        gx = (self._get_dist(x + eps, y) - self._get_dist(x - eps, y)) / (2 * eps)
        gy = (self._get_dist(x, y + eps) - self._get_dist(x, y - eps)) / (2 * eps)
        return gx, gy

    def _interpolate_seg(self, seg, step=0.3):
        """插值加密单段路径，v 继承前一个点"""
        dense = [seg[0]]
        for i in range(1, len(seg)):
            p1, p2 = seg[i-1], seg[i]
            dx, dy = p2[0]-p1[0], p2[1]-p1[1]
            dist = math.sqrt(dx*dx + dy*dy)
            n_ins = max(1, int(dist / step))
            for k in range(1, n_ins):
                t = k / n_ins
                dense.append((p1[0]+t*dx, p1[1]+t*dy, p1[2], p1[3]))
            dense.append(p2)
        return dense

    def _smooth_seg(self, seg):
        """对单段路径做梯度下降，首尾固定，返回平滑后的段"""
        n = len(seg)
        if n < 3:
            return seg

        xs = [p[0] for p in seg]
        ys = [p[1] for p in seg]
        alpha, beta, d_safe = self.alpha, self.beta, self.d_safe

        for _ in range(self.max_iter):
            max_move = 0.0
            for i in range(1, n - 1):  # 首尾固定
                x, y = xs[i], ys[i]
                fx_s = alpha * (xs[i-1] + xs[i+1] - 2*x)
                fy_s = alpha * (ys[i-1] + ys[i+1] - 2*y)
                dist = self._get_dist(x, y)
                if dist < d_safe:
                    gx, gy = self._obs_gradient(x, y)
                    force = beta * (d_safe - dist)
                    fx_o, fy_o = force*gx, force*gy
                else:
                    fx_o, fy_o = 0.0, 0.0
                dx = fx_s + fx_o
                dy = fy_s + fy_o
                xs[i] += dx
                ys[i] += dy
                max_move = max(max_move, math.sqrt(dx*dx + dy*dy))
            if max_move < 1e-3:
                break

        # 重新计算 theta：位移方向与原始 theta 比较，判断前进/倒车
        thetas = [seg[i][2] for i in range(n)]
        for i in range(1, n - 1):
            ddx = xs[i+1] - xs[i-1]
            ddy = ys[i+1] - ys[i-1]
            if abs(ddx) > 1e-9 or abs(ddy) > 1e-9:
                base = math.atan2(ddy, ddx)
                orig = seg[i][2]
                diff = math.atan2(math.sin(base - orig), math.cos(base - orig))
                thetas[i] = base if abs(diff) < math.pi/2 else math.atan2(-ddy, -ddx)

        return [(xs[i], ys[i], thetas[i], seg[i][3]) for i in range(n)]

    def smooth(self, path):
        """
        按换挡点切段，每段单独插值+平滑，再拼回完整路径。
        path 每个点格式: (x, y, theta, v)
        返回: [(x, y, theta, v), ...]
        """
        if len(path) < 3:
            return path

        # 1. 按 v 符号找换挡点，切段
        segments = []
        seg_start = 0
        for i in range(1, len(path)):
            prev_fwd = path[i-1][3] >= 0
            curr_fwd = path[i][3] >= 0
            if curr_fwd != prev_fwd:
                segments.append(path[seg_start:i])
                seg_start = i
        segments.append(path[seg_start:])

        # 2. 每段插值加密 + 平滑
        result = []
        for k, seg in enumerate(segments):
            dense = self._interpolate_seg(seg, step=0.3)
            smoothed = self._smooth_seg(dense)
            # 避免段间重复拼接换挡点
            if k > 0:
                smoothed = smoothed[1:]
            result.extend(smoothed)

        return result
