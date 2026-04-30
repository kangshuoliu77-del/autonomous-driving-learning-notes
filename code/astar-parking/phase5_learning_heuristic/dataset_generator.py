import argparse
import math
import random
import sys
import time
from pathlib import Path

import numpy as np


# 复用 Phase 4 里的 Hybrid A* 模块，第一版只生成搜索启发式数据，不用 MPC。
PHASE4_DIR = Path(__file__).resolve().parents[1] / "phase4_hybrid_astar_v2"
sys.path.insert(0, str(PHASE4_DIR))

from car_model import KinematicCar  # noqa: E402
from collision_checker import CollisionChecker  # noqa: E402
from hybrid_astar import HybridAStar  # noqa: E402
from state_indexer import StateIndexer  # noqa: E402


def create_parking_scenario(res):
    """创建和 Phase 4 垂直泊车一致的地图和目标车位。"""
    width, height = 20, 15
    grid_map = np.zeros((int(width / res), int(height / res)))

    parking_slot_x = 10.0
    parking_slot_y = 2.5
    slot_width = 2.5
    slot_length = 5.0

    def to_idx(val):
        return int(val / res)

    # 左右两辆障碍车。
    left_car_start_x = parking_slot_x - slot_width - 0.2
    left_car_end_x = parking_slot_x - slot_width / 2.0 - 0.2
    grid_map[
        to_idx(left_car_start_x):to_idx(left_car_end_x),
        to_idx(1.0):to_idx(1.0 + slot_length),
    ] = 1

    right_car_start_x = parking_slot_x + slot_width / 2.0 + 0.2
    right_car_end_x = parking_slot_x + slot_width + 0.2
    grid_map[
        to_idx(right_car_start_x):to_idx(right_car_end_x),
        to_idx(1.0):to_idx(1.0 + slot_length),
    ] = 1

    # 底部边界/路沿。
    grid_map[:, to_idx(0.0):to_idx(1.0)] = 1

    goal_pos = (parking_slot_x, parking_slot_y, math.radians(90))
    return grid_map, goal_pos


def get_random_start_pos(car, checker):
    """随机采样一个不碰撞的起点。"""
    while True:
        rx = random.uniform(2.0, 18.0)
        ry = random.uniform(9.0, 13.0)
        rt = random.uniform(0, 2 * math.pi)
        start = (rx, ry, rt)

        if not checker.is_collision(car.get_corners(start)):
            return start


def angle_features(theta):
    """用 sin/cos 表示角度，避免 -pi 和 pi 附近数值跳变。"""
    return math.sin(theta), math.cos(theta)


def make_feature(state, goal):
    """把一个搜索状态和目标位姿变成 8 维 MLP 输入。"""
    sin_theta, cos_theta = angle_features(state[2])
    sin_goal, cos_goal = angle_features(goal[2])

    return [
        state[0],
        state[1],
        sin_theta,
        cos_theta,
        goal[0],
        goal[1],
        sin_goal,
        cos_goal,
    ]


def cumulative_remaining_lengths(path):
    """计算路径上每个点到终点还剩多少路径长度。"""
    remaining = np.zeros(len(path), dtype=np.float32)
    total = 0.0

    for i in range(len(path) - 2, -1, -1):
        x1, y1 = path[i][0], path[i][1]
        x2, y2 = path[i + 1][0], path[i + 1][1]
        total += math.hypot(x2 - x1, y2 - y1)
        remaining[i] = total

    return remaining


def path_to_samples(path, goal):
    """把一条成功路径拆成多条 (state, goal) -> cost_to_go 样本。"""
    features = []
    labels = []
    cost_to_go = cumulative_remaining_lengths(path)

    for state, cost in zip(path, cost_to_go):
        features.append(make_feature(state, goal))
        labels.append([cost])

    return features, labels


def run_one_trial(trial_id, res_xy, res_theta):
    """随机起点跑一次 Hybrid A*，成功则返回训练样本。"""
    grid_map, goal = create_parking_scenario(res_xy)

    car = KinematicCar()
    checker = CollisionChecker(grid_map, res_xy)
    start = get_random_start_pos(car, checker)

    indexer = StateIndexer(res_xy, res_theta)
    planner = HybridAStar(car, checker, indexer, goal)

    t0 = time.perf_counter()
    path = planner.solve(start)
    elapsed = time.perf_counter() - t0

    if path is None:
        return {
            "trial_id": trial_id,
            "success": False,
            "num_path_states": 0,
            "num_samples": 0,
            "elapsed": elapsed,
            "features": [],
            "labels": [],
        }

    features, labels = path_to_samples(path, goal)

    return {
        "trial_id": trial_id,
        "success": True,
        "num_path_states": len(path),
        "num_samples": len(features),
        "elapsed": elapsed,
        "features": features,
        "labels": labels,
    }


def generate_dataset(num_trials, seed, output_path):
    """多次随机实验，汇总并保存 npz 数据集。"""
    random.seed(seed)
    np.random.seed(seed)

    res_xy = 0.3
    res_theta = math.radians(5)

    all_features = []
    all_labels = []
    trial_stats = []

    for trial_id in range(num_trials):
        result = run_one_trial(trial_id, res_xy, res_theta)

        if result["success"]:
            all_features.extend(result["features"])
            all_labels.extend(result["labels"])

        trial_stats.append(
            [
                result["trial_id"],
                int(result["success"]),
                result["num_path_states"],
                result["num_samples"],
                result["elapsed"],
            ]
        )

        status = "ok" if result["success"] else "fail"
        print(
            f"trial {trial_id:03d}: {status}, "
            f"path={result['num_path_states']}, "
            f"samples={result['num_samples']}, "
            f"time={result['elapsed']:.3f}s"
        )

    X = np.asarray(all_features, dtype=np.float32)
    y = np.asarray(all_labels, dtype=np.float32)
    stats = np.asarray(trial_stats, dtype=np.float32)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        output_path,
        X=X,
        y=y,
        trial_stats=stats,
        feature_names=np.array(
            [
                "x",
                "y",
                "sin_theta",
                "cos_theta",
                "goal_x",
                "goal_y",
                "sin_goal_theta",
                "cos_goal_theta",
            ]
        ),
        label_name=np.array(["cost_to_go"]),
    )

    print()
    print(f"saved: {output_path}")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"success trials: {int(stats[:, 1].sum())}/{num_trials}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-trials", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("datasets/parking_cost_to_go_v1.npz"),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    generate_dataset(args.num_trials, args.seed, args.output)


if __name__ == "__main__":
    main()
