import math

class KinematicCar:
    """
    模块一：车辆运动学与几何模型
    职责：
    1. 存储车辆物理尺寸 (L, W, H)
    2. 执行运动学积分 (下一时刻在哪？)
    3. 执行坐标变换 (四个角点在大地系的哪里？)
    """
    def __init__(self):
        # --- 1. 车辆身份证参数 ---
        self.L = 2.5           # 轴距 (Wheelbase): 前后轮中心距离
        self.length = 4.0      # 车身总长
        self.width = 1.8       # 车身总宽
        self.rear_to_axle = 1.0 # 后轴中心到车尾的距离 (后悬)

        f_x = self.length - self.rear_to_axle
        b_x = -self.rear_to_axle
        l_y = self.width / 2.0
        r_y = -self.width / 2.0
        self.corners_b = [(f_x, l_y), (f_x, r_y), (b_x, r_y), (b_x, l_y)]

    def update_state(self, current_state, v, phi, dt=0.1):
        """
        基于一阶自行车模型更新位姿 (MR 第 13.3 节)
        state: (x, y, theta) -> theta 是弧度
        v: 线速度, phi: 前轮转角弧度
        """
        x, y, theta = current_state

        # --- 2. 运动学公式推导 (单车模型) ---
        # 这里的 dx, dy, d_theta 构成了车辆在 SE(2) 空间里的速度向量
        dx = v * math.cos(theta) * dt
        dy = v * math.sin(theta) * dt
        
        # d_theta = (v/L) * tan(phi)
        # 这是决定车辆非完整约束的核心：不跑(v=0)就不转
        d_theta = (v * math.tan(phi) / self.L) * dt

        new_x = x + dx
        new_y = y + dy
        new_theta = theta + d_theta
        
        # 角度规范化：保证在 [-pi, pi] 之间，防止搜索时角度累加过大
        new_theta = math.atan2(math.sin(new_theta), math.cos(new_theta))

        return (new_x, new_y, new_theta)

    def get_corners(self, state):
        """
        将车辆从身体系 {b} 变换到大地系 {s} (MR 第 3.3 节)
        """
        x, y, theta = state
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        corners_s = []
        for (bx, by) in self.corners_b:
            tx = x + bx * cos_t - by * sin_t
            ty = y + bx * sin_t + by * cos_t
            corners_s.append((tx, ty))

        return corners_s