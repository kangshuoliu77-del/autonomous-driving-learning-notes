import argparse
import math
import random
import sys
import time
from pathlib import Path
import heapq

import numpy as np
import torch


PHASE4_DIR = Path(__file__).resolve().parents[1] / "phase4_hybrid_astar_v2"
sys.path.insert(0, str(PHASE4_DIR))

from car_model import KinematicCar  # noqa: E402
from collision_checker import CollisionChecker  # noqa: E402
from reeds_shepp import rs_distance  # noqa: E402
from state_indexer import StateIndexer  # noqa: E402

from dataset_generator import create_parking_scenario, get_random_start_pos, make_feature
from evaluate_heuristic import build_model


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "heuristic_mlp_v1.pth"


class InstrumentedHybridAStar:
    def __init__(
        self,
        car,
        checker,
        indexer,
        goal_pos,
        mode="baseline",
        model=None,
        turning_radius=5.0,
        tie_precision=1,
    ):
        self.car = car
        self.checker = checker
        self.indexer = indexer
        self.goal = goal_pos
        self.mode = mode
        self.model = model
        self.turning_radius = turning_radius
        self.tie_precision = tie_precision
        self.expanded_nodes = 0
        self.generated_nodes = 0
        self.actions = [
            (1.0, 0.4),
            (1.0, 0.0),
            (1.0, -0.4),
            (-1.0, 0.4),
            (-1.0, 0.0),
            (-1.0, -0.4),
        ]

    def solve(self, start_pos):
        open_list = []
        counter = 0
        start = (start_pos[0], start_pos[1], start_pos[2], 0)
        heapq.heappush(open_list, (0.0, 0.0, counter, start_pos, [start], 0.0))
        self.indexer.is_visited_and_add(start_pos)

        while open_list:
            _, _, _, curr_state, path, g = heapq.heappop(open_list)
            self.expanded_nodes += 1

            if self.is_goal(curr_state):
                return path

            candidates = []

            for v, phi in self.actions:
                next_state = self.car.update_state(curr_state, v, phi, dt=1.0)
                corners = self.car.get_corners(next_state)

                if self.checker.is_collision(corners):
                    continue

                if self.indexer.is_visited_and_add(next_state):
                    continue

                new_g = g + self.calc_cost(v, phi)
                original_h = self.original_heuristic(next_state)

                candidates.append((next_state, v, new_g, original_h))

            learned_values = self.learned_heuristics([candidate[0] for candidate in candidates])

            for candidate, learned_h in zip(candidates, learned_values):
                next_state, v, new_g, original_h = candidate
                priority, secondary = self.make_priority(new_g, original_h, learned_h)

                counter += 1
                self.generated_nodes += 1
                next_with_v = (next_state[0], next_state[1], next_state[2], v)
                heapq.heappush(
                    open_list,
                    (priority, secondary, counter, next_state, path + [next_with_v], new_g),
                )

        return None

    def is_goal(self, state):
        return self.calc_dist(state, self.goal) < 0.3 and abs(
            self.calc_angle_diff(state[2], self.goal[2])
        ) < math.radians(5)

    def make_priority(self, g, original_h, learned_h):
        base_f = g + original_h

        if self.mode == "baseline":
            return base_f, 0.0

        if self.mode == "mlp_tiebreak":
            return round(base_f, self.tie_precision), learned_h

        raise ValueError(f"unknown planner mode: {self.mode}")

    def learned_heuristics(self, states):
        if self.model is None or not states:
            return [0.0] * len(states)

        features = torch.tensor(
            [make_feature(state, self.goal) for state in states],
            dtype=torch.float32,
        )
        with torch.no_grad():
            return self.model(features).reshape(-1).tolist()

    def original_heuristic(self, state):
        euclidean = self.calc_dist(state, self.goal)
        if euclidean < 5.0:
            return rs_distance(state, self.goal, self.turning_radius)
        return euclidean

    def calc_cost(self, v, phi):
        cost = 1.0
        if v < 0:
            cost += 2.0
        if abs(phi) > 0:
            cost += 0.5
        return cost

    def calc_dist(self, s1, s2):
        return math.sqrt((s1[0] - s2[0]) ** 2 + (s1[1] - s2[1]) ** 2)

    def calc_angle_diff(self, a1, a2):
        diff = a1 - a2
        return math.atan2(math.sin(diff), math.cos(diff))


def load_model():
    model = build_model()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model


def path_length(path):
    if path is None or len(path) < 2:
        return float("nan")

    total = 0.0
    for i in range(len(path) - 1):
        total += math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
    return total


def run_planner(mode, start, grid_map, goal, res_xy, res_theta, model, tie_precision):
    car = KinematicCar()
    checker = CollisionChecker(grid_map, res_xy)
    indexer = StateIndexer(res_xy, res_theta)
    planner = InstrumentedHybridAStar(
        car=car,
        checker=checker,
        indexer=indexer,
        goal_pos=goal,
        mode=mode,
        model=model if mode == "mlp_tiebreak" else None,
        tie_precision=tie_precision,
    )

    t0 = time.perf_counter()
    path = planner.solve(start)
    elapsed = time.perf_counter() - t0

    return {
        "success": path is not None,
        "elapsed": elapsed,
        "expanded_nodes": planner.expanded_nodes,
        "generated_nodes": planner.generated_nodes,
        "path_states": len(path) if path is not None else 0,
        "path_length": path_length(path),
    }


def print_summary(name, results):
    successes = [r for r in results if r["success"]]

    success_count = len(successes)
    total_count = len(results)
    mean_time = np.mean([r["elapsed"] for r in successes]) if successes else float("nan")
    mean_expanded = (
        np.mean([r["expanded_nodes"] for r in successes]) if successes else float("nan")
    )
    mean_generated = (
        np.mean([r["generated_nodes"] for r in successes]) if successes else float("nan")
    )
    mean_path_length = (
        np.mean([r["path_length"] for r in successes]) if successes else float("nan")
    )

    print(f"\n{name} summary:")
    print(f"success: {success_count}/{total_count}")
    print(f"mean planning time: {mean_time:.4f}s")
    print(f"mean expanded nodes: {mean_expanded:.1f}")
    print(f"mean generated nodes: {mean_generated:.1f}")
    print(f"mean path length: {mean_path_length:.2f}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-trials", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--tie-precision",
        type=int,
        default=1,
        help="round original f to this decimal precision before using MLP tie-breaker",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    res_xy = 0.3
    res_theta = math.radians(5)

    grid_map, goal = create_parking_scenario(res_xy)
    model = load_model()

    start_car = KinematicCar()
    start_checker = CollisionChecker(grid_map, res_xy)

    baseline_results = []
    learned_results = []

    for trial_id in range(args.num_trials):
        start = get_random_start_pos(start_car, start_checker)

        baseline = run_planner(
            "baseline", start, grid_map, goal, res_xy, res_theta, model, args.tie_precision
        )
        learned = run_planner(
            "mlp_tiebreak",
            start,
            grid_map,
            goal,
            res_xy,
            res_theta,
            model,
            args.tie_precision,
        )

        baseline_results.append(baseline)
        learned_results.append(learned)

        print(
            f"trial {trial_id:03d}: "
            f"baseline success={baseline['success']}, "
            f"time={baseline['elapsed']:.3f}s, "
            f"expanded={baseline['expanded_nodes']} | "
            f"mlp_tiebreak success={learned['success']}, "
            f"time={learned['elapsed']:.3f}s, "
            f"expanded={learned['expanded_nodes']}"
        )

    print_summary("Baseline Hybrid A*", baseline_results)
    print_summary(f"MLP tie-breaker Hybrid A* (tie_precision={args.tie_precision})", learned_results)


if __name__ == "__main__":
    main()
