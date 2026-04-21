import heapq
import math
from reeds_shepp import rs_distance


class HybridAStar:
    def __init__(self, car, checker, indexer, goal_pos, turning_radius=5.0):
        self.car = car
        self.checker = checker
        self.indexer = indexer
        self.goal = goal_pos
        self.turning_radius = turning_radius
        self.actions = [
            (1.0, 0.4), (1.0, 0.0), (1.0, -0.4),
            (-1.0, 0.4), (-1.0, 0.0), (-1.0, -0.4)
        ]

    def solve(self, start_pos):
        open_list = []
        counter = 0
        start = (start_pos[0], start_pos[1], start_pos[2], 0)
        heapq.heappush(open_list, (0, counter, start_pos, [start], 0))
        self.indexer.is_visited_and_add(start_pos)

        while open_list:
            f, _, curr_state, path, g = heapq.heappop(open_list)

            if self.calc_dist(curr_state, self.goal) < 0.3 and \
               abs(self.calc_angle_diff(curr_state[2], self.goal[2])) < math.radians(5):
                print("找到路径了！")
                return path

            for v, phi in self.actions:
                next_state = self.car.update_state(curr_state, v, phi, dt=1.0)
                corners = self.car.get_corners(next_state)

                if not self.checker.is_collision(corners):
                    if not self.indexer.is_visited_and_add(next_state):
                        new_g = g + self.calc_cost(v, phi)
                        euclidean = self.calc_dist(next_state, self.goal)
                        h = rs_distance(next_state, self.goal, self.turning_radius) if euclidean < 5.0 else euclidean
                        counter += 1
                        next_with_v = (next_state[0], next_state[1], next_state[2], v)
                        heapq.heappush(open_list, (new_g + h, counter, next_state, path + [next_with_v], new_g))

        return None

    def calc_cost(self, v, phi):
        cost = 1.0
        if v < 0: cost += 2.0
        if abs(phi) > 0: cost += 0.5
        return cost

    def calc_dist(self, s1, s2):
        return math.sqrt((s1[0]-s2[0])**2 + (s1[1]-s2[1])**2)

    def calc_angle_diff(self, a1, a2):
        diff = a1 - a2
        return math.atan2(math.sin(diff), math.cos(diff))
