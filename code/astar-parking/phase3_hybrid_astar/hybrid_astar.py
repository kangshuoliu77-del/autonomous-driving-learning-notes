import heapq
import math

class HybridAStar:
    """
    模块四：混合 A* 搜索主程序
    职责：
    1. 管理 OpenList（待探索的树枝）。
    2. 执行扩展循环。
    3. 调用模块一二三进行物理推算、碰撞检查和剪枝。
    """
    def __init__(self, car, checker, indexer, goal_pos):
        self.car = car          # 模块一：车辆物理模型
        self.checker = checker  # 模块二：碰撞检测
        self.indexer = indexer  # 模块三：状态记忆体
        self.goal = goal_pos    # 目标位姿 (gx, gy, gtheta)
        
        # 定义动作集：(v, phi) -> (速度, 转向角)
        # 这就是我们在空间中“长树枝”的方向
        self.actions = [
            (1.0, 0.4), (1.0, 0.0), (1.0, -0.4),  # 前进：左转、直行、右转
            (-1.0, 0.4), (-1.0, 0.0), (-1.0, -0.4) # 后退：左转、直行、右转
        ]

    def solve(self, start_pos):
        # 1. 初始化 OpenList (优先级队列)
        # 存储格式: (priority, current_state, path_list, current_g)
        # priority = g(n) + h(n)
        open_list = []
        
        # 初始状态
        start_node = (0, start_pos, [start_pos], 0)
        heapq.heappush(open_list, start_node)
        
        # 记录起点已被访问
        self.indexer.is_visited_and_add(start_pos)

        while open_list:
            # 2. 弹出当前代价最小的“树枝” (Dijkstra/A* 核心)
            f, curr_state, path, g = heapq.heappop(open_list)

            # 3. 检查是否到达终点（距离小于阈值且角度偏差小）
            if self.calc_dist(curr_state, self.goal) < 0.5 and \
               abs(self.calc_angle_diff(curr_state[2], self.goal[2])) < math.radians(10):
                print("找到路径了！")
                return path

            # 4. 尝试 6 种动作，向外长出新树枝
            for v, phi in self.actions:
                # --- 调用模块一：算新位姿 ---
                next_state = self.car.update_state(curr_state, v, phi, dt=1.0) # 步长略大一点
                corners = self.car.get_corners(next_state)

                # --- 调用模块二：查碰撞 ---
                if not self.checker.is_collision(corners):
                    
                    # --- 调用模块三：查记忆体（剪枝） ---
                    if not self.indexer.is_visited_and_add(next_state):
                        
                        # --- 计算代价 ---
                        new_g = g + self.calc_cost(v, phi, curr_state) # 走一步的代价
                        h = self.calc_dist(next_state, self.goal)     # 离终点的距离(启发式)
                        f = new_g + h
                        
                        # 将新节点加入 OpenList
                        new_path = path + [next_state]
                        heapq.heappush(open_list, (f, next_state, new_path, new_g))

        return None # 没找到路径

    def calc_cost(self, v, phi, last_state):
        # 这里的代价函数决定了路径的“美观度”
        cost = 1.0 # 基础行驶代价
        if v < 0: cost += 2.0  # 惩罚倒车（尽量往前开）
        if abs(phi) > 0: cost += 0.5 # 惩罚转弯（尽量走直线）
        return cost

    def calc_dist(self, s1, s2):
        return math.sqrt((s1[0]-s2[0])**2 + (s1[1]-s2[1])**2)

    def calc_angle_diff(self, a1, a2):
        # 角度差值规范化
        diff = a1 - a2
        return math.atan2(math.sin(diff), math.cos(diff))