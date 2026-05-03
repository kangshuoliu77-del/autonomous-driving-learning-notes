import argparse
import heapq
import math
import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
import numpy as np


matplotlib.use("Agg")

import matplotlib.pyplot as plt


FREE = 0
OBSTACLE = 1
INF = 1e9


def add_random_rectangles(grid, num_rectangles, rng):
    """添加大小不一的随机矩形障碍物。"""
    size = grid.shape[0]

    for _ in range(num_rectangles):
        rect_h = int(rng.integers(2, 8))
        rect_w = int(rng.integers(2, 8))
        top = int(rng.integers(0, size - rect_h + 1))
        left = int(rng.integers(0, size - rect_w + 1))
        grid[top : top + rect_h, left : left + rect_w] = OBSTACLE


def add_random_dots(grid, num_dots, rng):
    """添加散点或小块障碍物，让地图不只是大矩形。"""
    size = grid.shape[0]

    for _ in range(num_dots):
        row = int(rng.integers(0, size))
        col = int(rng.integers(0, size))
        block_size = int(rng.choice([1, 1, 1, 2, 2, 3]))

        row_end = min(size, row + block_size)
        col_end = min(size, col + block_size)
        grid[row:row_end, col:col_end] = OBSTACLE


def add_random_walls(grid, num_walls, rng):
    """添加短墙障碍物，制造更明显的绕行结构。"""
    size = grid.shape[0]

    for _ in range(num_walls):
        row = int(rng.integers(0, size))
        col = int(rng.integers(0, size))
        length = int(rng.integers(4, 14))
        horizontal = bool(rng.integers(0, 2))

        if horizontal:
            col_end = min(size, col + length)
            grid[row, col:col_end] = OBSTACLE
        else:
            row_end = min(size, row + length)
            grid[row:row_end, col] = OBSTACLE


def make_random_map(size, num_rectangles, num_dots, num_walls, rng):
    """生成一张混合随机障碍物地图。"""
    grid = np.zeros((size, size), dtype=np.uint8)

    add_random_rectangles(grid, num_rectangles, rng)
    add_random_dots(grid, num_dots, rng)
    add_random_walls(grid, num_walls, rng)

    return grid


def sample_free_cell(grid, rng):
    """从空地里随机选一个格子。"""
    free_cells = np.argwhere(grid == FREE)
    if len(free_cells) == 0:
        return None

    index = int(rng.integers(0, len(free_cells)))
    row, col = free_cells[index]
    return int(row), int(col)


def neighbors_4(row, col, size):
    """4邻域移动：上、下、左、右。"""
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr = row + dr
        nc = col + dc
        if 0 <= nr < size and 0 <= nc < size:
            yield nr, nc


def dijkstra_from_goal(grid, goal):
    """从 goal 反向跑 Dijkstra，得到每个格子到 goal 的最短距离。"""
    size = grid.shape[0]
    dist = np.full((size, size), INF, dtype=np.float32)

    goal_row, goal_col = goal
    dist[goal_row, goal_col] = 0.0
    open_heap = [(0.0, goal_row, goal_col)]

    while open_heap:
        current_dist, row, col = heapq.heappop(open_heap)

        if current_dist > dist[row, col]:
            continue

        for nr, nc in neighbors_4(row, col, size):
            if grid[nr, nc] == OBSTACLE:
                continue

            new_dist = current_dist + 1.0
            if new_dist < dist[nr, nc]:
                dist[nr, nc] = new_dist
                heapq.heappush(open_heap, (new_dist, nr, nc))

    return dist


def build_input_tensor(grid, start, goal):
    """把一张地图整理成 CNN 输入通道。"""
    size = grid.shape[0]

    obstacle_map = grid.astype(np.float32)
    start_map = np.zeros((size, size), dtype=np.float32)
    goal_map = np.zeros((size, size), dtype=np.float32)

    start_map[start] = 1.0
    goal_map[goal] = 1.0

    return np.stack([obstacle_map, start_map, goal_map], axis=0)


def make_one_sample(
    size,
    num_rectangles,
    num_dots,
    num_walls,
    min_start_goal_dist,
    min_free_ratio,
    rng,
):
    """生成一条有效样本：地图、起点、终点、Dijkstra 距离场。"""
    for _ in range(100):
        grid = make_random_map(size, num_rectangles, num_dots, num_walls, rng)
        free_ratio = float(np.mean(grid == FREE))
        if free_ratio < min_free_ratio:
            continue

        start = sample_free_cell(grid, rng)
        goal = sample_free_cell(grid, rng)

        if start is None or goal is None or start == goal:
            continue

        straight_dist = math.hypot(start[0] - goal[0], start[1] - goal[1])
        if straight_dist < min_start_goal_dist:
            continue

        dist = dijkstra_from_goal(grid, goal)
        if dist[start] >= INF:
            continue

        reachable_mask = ((grid == FREE) & (dist < INF)).astype(np.float32)
        target = dist.copy()
        target[reachable_mask == 0] = 0.0

        input_tensor = build_input_tensor(grid, start, goal)

        return {
            "input": input_tensor,
            "target": target[np.newaxis, :, :],
            "mask": reachable_mask[np.newaxis, :, :],
            "map": grid,
            "start": np.array(start, dtype=np.int64),
            "goal": np.array(goal, dtype=np.int64),
        }

    return None


def save_sample_figure(sample, output_path):
    """保存一张示例图，方便检查数据是否合理。"""
    grid = sample["map"]
    start_row, start_col = sample["start"]
    goal_row, goal_col = sample["goal"]
    target = sample["target"][0]
    mask = sample["mask"][0]

    visible_target = target.copy()
    visible_target[mask == 0] = np.nan

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].imshow(grid, cmap="gray_r", origin="upper")
    axes[0].scatter(start_col, start_row, c="lime", s=70, marker="o", label="start")
    axes[0].scatter(goal_col, goal_row, c="red", s=80, marker="*", label="goal")
    axes[0].set_title("random map")
    axes[0].legend(loc="upper right")

    image = axes[1].imshow(visible_target, cmap="viridis", origin="upper")
    axes[1].scatter(start_col, start_row, c="lime", s=70, marker="o")
    axes[1].scatter(goal_col, goal_row, c="red", s=80, marker="*")
    axes[1].set_title("Dijkstra cost-to-go")
    fig.colorbar(image, ax=axes[1], fraction=0.046, pad=0.04)

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_dataset(args):
    rng = np.random.default_rng(args.seed)

    inputs = []
    targets = []
    masks = []
    maps = []
    starts = []
    goals = []

    attempts = 0
    while len(inputs) < args.num_samples and attempts < args.num_samples * 200:
        attempts += 1
        sample = make_one_sample(
            size=args.size,
            num_rectangles=args.num_rectangles,
            num_dots=args.num_dots,
            num_walls=args.num_walls,
            min_start_goal_dist=args.min_start_goal_dist,
            min_free_ratio=args.min_free_ratio,
            rng=rng,
        )

        if sample is None:
            continue

        inputs.append(sample["input"])
        targets.append(sample["target"])
        masks.append(sample["mask"])
        maps.append(sample["map"])
        starts.append(sample["start"])
        goals.append(sample["goal"])

        if len(inputs) <= args.num_preview_figures:
            args.results_dir.mkdir(parents=True, exist_ok=True)
            figure_name = f"sample_{len(inputs) - 1:03d}.png"
            save_sample_figure(sample, args.results_dir / figure_name)

        if len(inputs) % 100 == 0 or len(inputs) == args.num_samples:
            print(f"generated {len(inputs)}/{args.num_samples} samples")

    if len(inputs) < args.num_samples:
        raise RuntimeError(
            f"only generated {len(inputs)} samples after {attempts} attempts"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        args.output,
        inputs=np.stack(inputs).astype(np.float32),
        targets=np.stack(targets).astype(np.float32),
        masks=np.stack(masks).astype(np.float32),
        maps=np.stack(maps).astype(np.uint8),
        starts=np.stack(starts).astype(np.int64),
        goals=np.stack(goals).astype(np.int64),
    )

    print(f"saved: {args.output}")
    print(f"inputs shape: {np.stack(inputs).shape}")
    print(f"targets shape: {np.stack(targets).shape}")
    print(f"masks shape: {np.stack(masks).shape}")
    print(f"mean obstacle ratio: {np.mean(np.stack(maps) == OBSTACLE):.3f}")
    print(f"sample figures: {args.results_dir / 'sample_*.png'}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-samples", type=int, default=200)
    parser.add_argument("--size", type=int, default=32)
    parser.add_argument("--num-rectangles", type=int, default=10)
    parser.add_argument("--num-dots", type=int, default=80)
    parser.add_argument("--num-walls", type=int, default=8)
    parser.add_argument("--min-free-ratio", type=float, default=0.45)
    parser.add_argument("--min-start-goal-dist", type=float, default=12.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--num-preview-figures", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("datasets/grid2d_heuristic_v1.npz"),
    )
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    return parser.parse_args()


def main():
    args = parse_args()
    generate_dataset(args)


if __name__ == "__main__":
    main()
