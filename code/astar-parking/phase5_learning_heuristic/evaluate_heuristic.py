from pathlib import Path
import heapq

import numpy as np
import torch
from torch import nn

from dataset_generator import create_parking_scenario


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "datasets" / "parking_cost_to_go_v1.npz"
MODEL_PATH = BASE_DIR / "models" / "heuristic_mlp_v1.pth"

RANDOM_SEED = 0
NUM_RANKING_PAIRS = 10000
RES_XY = 0.3


def build_model():
    # 必须和 train_heuristic_mlp.py 里保存参数时的模型结构一致。
    return nn.Sequential(
        nn.Linear(8, 64),
        nn.ReLU(),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Linear(64, 1),
    )


def compute_ranking_accuracy(score, target, idx_a, idx_b):
    # 比较 score 是否能排对 target 中的真实 cost_to_go 大小关系。
    target_a = target[idx_a]
    target_b = target[idx_b]
    score_a = score[idx_a]
    score_b = score[idx_b]

    target_order = target_a < target_b
    score_order = score_a < score_b
    valid = target_a != target_b

    return (target_order[valid] == score_order[valid]).float().mean().item()


def compute_dijkstra_distance_field(grid_map, goal_xy, resolution):
    # 在 2D 栅格地图上从 goal 反向跑 Dijkstra，得到每个格子的最短无碰撞距离。
    rows, cols = grid_map.shape
    dist = np.full((rows, cols), np.inf, dtype=np.float32)

    goal_ix = int(goal_xy[0] / resolution)
    goal_iy = int(goal_xy[1] / resolution)

    if not (0 <= goal_ix < rows and 0 <= goal_iy < cols):
        raise ValueError("goal is outside the grid map")

    if grid_map[goal_ix, goal_iy] != 0:
        raise ValueError("goal grid cell is occupied")

    moves = [
        (-1, 0, resolution),
        (1, 0, resolution),
        (0, -1, resolution),
        (0, 1, resolution),
        (-1, -1, resolution * np.sqrt(2.0)),
        (-1, 1, resolution * np.sqrt(2.0)),
        (1, -1, resolution * np.sqrt(2.0)),
        (1, 1, resolution * np.sqrt(2.0)),
    ]

    dist[goal_ix, goal_iy] = 0.0
    heap = [(0.0, goal_ix, goal_iy)]

    while heap:
        curr_dist, ix, iy = heapq.heappop(heap)

        if curr_dist > dist[ix, iy]:
            continue

        for dx, dy, step_cost in moves:
            nx = ix + dx
            ny = iy + dy

            if not (0 <= nx < rows and 0 <= ny < cols):
                continue

            if grid_map[nx, ny] != 0:
                continue

            next_dist = curr_dist + step_cost

            if next_dist < dist[nx, ny]:
                dist[nx, ny] = next_dist
                heapq.heappush(heap, (next_dist, nx, ny))

    return dist


def sample_distance_field(distance_field, states_xy, resolution):
    # 把连续坐标 (x,y) 映射到距离场中的栅格距离。
    rows, cols = distance_field.shape
    values = []

    finite_values = distance_field[np.isfinite(distance_field)]
    fallback = float(finite_values.max()) if len(finite_values) > 0 else 1e6

    for x, y in states_xy:
        ix = int(x / resolution)
        iy = int(y / resolution)

        if not (0 <= ix < rows and 0 <= iy < cols):
            values.append(fallback)
            continue

        value = float(distance_field[ix, iy])
        values.append(value if np.isfinite(value) else fallback)

    return torch.tensor(values, dtype=torch.float32).reshape(-1, 1)


def main():
    torch.manual_seed(RANDOM_SEED)

    data = np.load(DATA_PATH)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.float32)

    print("Dataset:")
    print("X shape:", X.shape)
    print("y shape:", y.shape)

    X_tensor = torch.tensor(X)
    y_tensor = torch.tensor(y)

    model = build_model()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    with torch.no_grad():
        pred = model(X_tensor)

    # 欧氏距离 baseline：只看当前位置到目标位置的直线距离。
    # X: [x, y, sin(theta), cos(theta), goal_x, goal_y, sin(goal_theta), cos(goal_theta)]
    position = X_tensor[:, 0:2]
    goal_position = X_tensor[:, 4:6]
    euclidean_h = torch.norm(position - goal_position, dim=1, keepdim=True)

    grid_map, goal = create_parking_scenario(RES_XY)
    distance_field = compute_dijkstra_distance_field(grid_map, goal[:2], RES_XY)
    dijkstra_h = sample_distance_field(distance_field, X[:, 0:2], RES_XY)

    print("\nSample predictions:")
    for i in range(10):
        true_value = y_tensor[i].item()
        pred_value = pred[i].item()
        print(f"true={true_value:.2f}, pred={pred_value:.2f}")

    error = pred - y_tensor
    abs_error = torch.abs(error)

    mae = abs_error.mean().item()
    rmse = torch.sqrt((error ** 2).mean()).item()
    max_error = abs_error.max().item()

    print("\nOverall error:")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"Max error: {max_error:.4f}")

    print("\nError by cost range:")

    ranges = [
        ("0-5", 0, 5),
        ("5-10", 5, 10),
        ("10-15", 10, 15),
        ("15-20", 15, 20),
        ("20+", 20, 100),
    ]

    for name, low, high in ranges:
        mask = (y_tensor >= low) & (y_tensor < high)

        if mask.sum().item() == 0:
            continue

        range_abs_error = abs_error[mask]
        range_mae = range_abs_error.mean().item()
        range_max_error = range_abs_error.max().item()
        count = mask.sum().item()

        print(
            f"{name:<6} "
            f"count={count:>4}, "
            f"MAE={range_mae:.4f}, "
            f"Max={range_max_error:.4f}"
        )

    idx_a = torch.randint(0, len(y_tensor), (NUM_RANKING_PAIRS,))
    idx_b = torch.randint(0, len(y_tensor), (NUM_RANKING_PAIRS,))

    mlp_ranking_acc = compute_ranking_accuracy(pred, y_tensor, idx_a, idx_b)
    euclidean_ranking_acc = compute_ranking_accuracy(euclidean_h, y_tensor, idx_a, idx_b)
    dijkstra_ranking_acc = compute_ranking_accuracy(dijkstra_h, y_tensor, idx_a, idx_b)

    print("\nRanking accuracy against Hybrid A* cost_to_go labels:")
    print(f"Euclidean h ranking acc: {euclidean_ranking_acc:.4f}")
    print(f"2D Dijkstra h ranking acc: {dijkstra_ranking_acc:.4f}")
    print(f"MLP learned h ranking acc: {mlp_ranking_acc:.4f}")


if __name__ == "__main__":
    main()
