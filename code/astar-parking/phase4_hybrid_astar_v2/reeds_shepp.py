"""
Reeds-Shepp 曲线启发式距离计算

车辆可前进也可后退，路径由圆弧(C)和直线(S)组成。
这里只计算最短 RS 路径的长度，用作 Hybrid A* 的启发式 h(n)。

主要路径族（覆盖所有48种类型）：
  CSC: 圆弧-直线-圆弧
  CCC: 圆弧-圆弧-圆弧
每种都有前进/后退的符号组合变体。
"""

import math


def _mod2pi(x):
    """把角度规范化到 [0, 2π)"""
    return x - 2 * math.pi * math.floor(x / (2 * math.pi))


def _polar(x, y):
    """直角坐标转极坐标，返回 (r, theta)"""
    r = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)
    return r, theta


# ──────────────────────────────────────────────
# CSC 族：Left-Straight-Left / Right-Straight-Right 等
# ──────────────────────────────────────────────

def _LSL(x, y, phi):
    u, t = _polar(x - math.sin(phi), y - 1 + math.cos(phi))
    if u < 0:
        return None
    v = _mod2pi(phi - t)
    return t, u, v


def _RSR(x, y, phi):
    u, t = _polar(x + math.sin(phi), y + 1 - math.cos(phi))
    if u < 0:
        return None
    t = _mod2pi(-t)
    v = _mod2pi(-phi + t)
    return t, u, v


def _LSR(x, y, phi):
    u1, t1 = _polar(x + math.sin(phi), y - 1 - math.cos(phi))
    u1 = u1 * u1
    if u1 < 4:
        return None
    u = math.sqrt(u1 - 4)
    theta = math.atan2(2, u)
    t = _mod2pi(t1 + theta)
    v = _mod2pi(t - phi)
    return t, u, v


def _RSL(x, y, phi):
    u1, t1 = _polar(x - math.sin(phi), y + 1 + math.cos(phi))
    u1 = u1 * u1
    if u1 < 4:
        return None
    u = math.sqrt(u1 - 4)
    theta = math.atan2(2, u)
    t = _mod2pi(t1 - theta)
    v = _mod2pi(phi - t)
    return t, u, v


def _RLR(x, y, phi):
    u1, t1 = _polar(x - math.sin(phi), y + 1 - math.cos(phi))
    if abs(u1) > 4:
        return None
    u = _mod2pi(2 * math.pi - math.acos(u1 / 4 - 1))
    t = _mod2pi(t1 + math.atan2(4 - u1, 2 * math.sqrt(u1)) + math.pi)
    v = _mod2pi(phi - t + u)
    return t, u, v


def _LRL(x, y, phi):
    u1, t1 = _polar(x + math.sin(phi), y - 1 + math.cos(phi))
    if abs(u1) > 4:
        return None
    u = _mod2pi(2 * math.pi - math.acos(u1 / 4 - 1))
    t = _mod2pi(-t1 + math.atan2(4 - u1, 2 * math.sqrt(u1)) + math.pi)
    v = _mod2pi(-phi + t - u)
    return t, u, v


def _path_length(segs):
    """给定各段长度，返回总长（None 表示无效路径）"""
    if segs is None:
        return math.inf
    return sum(abs(s) for s in segs)


def _get_candidates(x, y, phi):
    """枚举所有路径族候选"""
    return [
        (_LSL(x, y, phi),   ['L', 'S', 'L'], False, False),
        (_RSR(x, y, phi),   ['R', 'S', 'R'], False, False),
        (_LSR(x, y, phi),   ['L', 'S', 'R'], False, False),
        (_RSL(x, y, phi),   ['R', 'S', 'L'], False, False),
        (_RLR(x, y, phi),   ['R', 'L', 'R'], False, False),
        (_LRL(x, y, phi),   ['L', 'R', 'L'], False, False),
        (_LSL(-x, y, -phi), ['L', 'S', 'L'], True,  False),
        (_RSR(-x, y, -phi), ['R', 'S', 'R'], True,  False),
        (_LSR(-x, y, -phi), ['L', 'S', 'R'], True,  False),
        (_RSL(-x, y, -phi), ['R', 'S', 'L'], True,  False),
        (_RLR(-x, y, -phi), ['R', 'L', 'R'], True,  False),
        (_LRL(-x, y, -phi), ['L', 'R', 'L'], True,  False),
        (_LSL(x, -y, -phi), ['L', 'S', 'L'], False, True),
        (_RSR(x, -y, -phi), ['R', 'S', 'R'], False, True),
        (_LSR(x, -y, -phi), ['L', 'S', 'R'], False, True),
        (_RSL(x, -y, -phi), ['R', 'S', 'L'], False, True),
        (_RLR(x, -y, -phi), ['R', 'L', 'R'], False, True),
        (_LRL(x, -y, -phi), ['L', 'R', 'L'], False, True),
        (_LSL(-x, -y, phi), ['L', 'S', 'L'], True,  True),
        (_RSR(-x, -y, phi), ['R', 'S', 'R'], True,  True),
        (_LSR(-x, -y, phi), ['L', 'S', 'R'], True,  True),
        (_RSL(-x, -y, phi), ['R', 'S', 'L'], True,  True),
        (_RLR(-x, -y, phi), ['R', 'L', 'R'], True,  True),
        (_LRL(-x, -y, phi), ['L', 'R', 'L'], True,  True),
    ]


def rs_distance(q0, q1, turning_radius):
    """
    计算从位姿 q0 到 q1 的最短 Reeds-Shepp 路径长度。
    用作 Hybrid A* 的启发式 h(n)。
    """
    dx = q1[0] - q0[0]
    dy = q1[1] - q0[1]
    cos_th = math.cos(q0[2])
    sin_th = math.sin(q0[2])
    x = (cos_th * dx + sin_th * dy) / turning_radius
    y = (-sin_th * dx + cos_th * dy) / turning_radius
    phi = q1[2] - q0[2]

    candidates = _get_candidates(x, y, phi)
    min_len = min(_path_length(c[0]) for c in candidates)
    return min_len * turning_radius


def _interpolate_segment(x, y, theta, seg_len, seg_type, step, turning_radius):
    """沿单段路径采样位姿点，seg_type: 'L'左转圆弧, 'R'右转圆弧, 'S'直线"""
    points = []
    dist = 0.0
    total = abs(seg_len) * turning_radius
    sign = 1.0 if seg_len >= 0 else -1.0  # 正=前进，负=倒退

    while dist < total:
        points.append((x, y, theta))
        if seg_type == 'S':
            x += sign * step * math.cos(theta)
            y += sign * step * math.sin(theta)
        elif seg_type == 'L':
            # 左转圆弧：先更新位置，再更新角度
            dtheta = sign * step / turning_radius
            x += turning_radius * (math.sin(theta + dtheta) - math.sin(theta))
            y += turning_radius * (-math.cos(theta + dtheta) + math.cos(theta))
            theta += dtheta
        elif seg_type == 'R':
            # 右转圆弧：先更新位置，再更新角度
            dtheta = sign * step / turning_radius
            x += turning_radius * (-math.sin(theta - dtheta) + math.sin(theta))
            y += turning_radius * (math.cos(theta - dtheta) - math.cos(theta))
            theta -= dtheta
        dist += step
    return points


def rs_path(q0, q1, turning_radius, step=0.3):
    """
    生成从 q0 到 q1 的最短 RS 路径的采样点序列。

    参数：
        q0, q1: (x, y, theta)
        turning_radius: 最小转弯半径 (m)
        step: 采样间隔 (m)

    返回：
        [(x, y, theta), ...] 路径点列表，失败返回 None
    """
    dx = q1[0] - q0[0]
    dy = q1[1] - q0[1]
    dth = q1[2] - q0[2]
    cos_th = math.cos(q0[2])
    sin_th = math.sin(q0[2])
    x = (cos_th * dx + sin_th * dy) / turning_radius
    y = (-sin_th * dx + cos_th * dy) / turning_radius
    phi = dth

    # 找最短路径对应的参数
    all_candidates = _get_candidates(x, y, phi)

    best_len = math.inf
    best = None
    for segs, types, time_flip, reflect in all_candidates:
        l = _path_length(segs)
        if l < best_len:
            best_len = l
            best = (segs, types, time_flip, reflect)

    if best is None:
        return None

    segs, types, time_flip, reflect = best
    points = [q0]
    cx, cy, cth = q0
    for seg_len, seg_type in zip(segs, types):
        if time_flip:
            seg_len = -seg_len
        if reflect:
            if seg_type == 'L':
                seg_type = 'R'
            elif seg_type == 'R':
                seg_type = 'L'
        pts = _interpolate_segment(cx, cy, cth, seg_len, seg_type, step, turning_radius)
        points.extend(pts)
        if pts:
            cx, cy, cth = pts[-1]

    points.append(q1)
    return points
