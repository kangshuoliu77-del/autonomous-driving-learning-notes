import argparse
import heapq
import math
import os
import time
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
import numpy as np


matplotlib.use("Agg")

import matplotlib.pyplot as plt


FREE = 0
OBSTACLE = 1


def neighbors_4(row, col, size):
    """4邻域移动：上、下、左、右。"""
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr = row + dr
        nc = col + dc
        if 0 <= nr < size and 0 <= nc < size:
            yield nr, nc


def manhattan_heuristic(row, col, goal):
    goal_row, goal_col = goal
    return abs(row - goal_row) + abs(col - goal_col)


def euclidean_heuristic(row, col, goal):
    goal_row, goal_col = goal
    return math.hypot(row - goal_row, col - goal_col)


def make_heuristic_fn(name, goal, dijkstra_map=None):
    if name == "manhattan":
        return lambda row, col: manhattan_heuristic(row, col, goal)

    if name == "euclidean":
        return lambda row, col: euclidean_heuristic(row, col, goal)

    if name == "dijkstra":
        if dijkstra_map is None:
            raise ValueError("dijkstra_map is required for dijkstra heuristic")
        return lambda row, col: float(dijkstra_map[row, col])

    raise ValueError(f"unknown heuristic: {name}")


def reconstruct_path(came_from, start, goal):
    path = [goal]
    current = goal

    while current != start:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def astar_search(grid, start, goal, heuristic_name, dijkstra_map=None):
    """普通 2D A*，返回路径和搜索统计。"""
    size = grid.shape[0]
    heuristic = make_heuristic_fn(heuristic_name, goal, dijkstra_map)

    open_heap = []
    counter = 0

    start_h = heuristic(start[0], start[1])
    heapq.heappush(open_heap, (start_h, counter, start))

    came_from = {}
    g_score = {start: 0.0}
    closed = set()
    expanded_order = []
    expanded_nodes = 0
    generated_nodes = 1

    start_time = time.perf_counter()

    while open_heap:
        _, _, current = heapq.heappop(open_heap)

        if current in closed:
            continue

        closed.add(current)
        expanded_order.append(current)
        expanded_nodes += 1

        if current == goal:
            planning_time = time.perf_counter() - start_time
            path = reconstruct_path(came_from, start, goal)
            return {
                "success": True,
                "path": path,
                "path_length": len(path) - 1,
                "expanded_nodes": expanded_nodes,
                "generated_nodes": generated_nodes,
                "planning_time": planning_time,
                "expanded_order": expanded_order,
            }

        row, col = current
        for nr, nc in neighbors_4(row, col, size):
            if grid[nr, nc] == OBSTACLE:
                continue

            neighbor = (nr, nc)
            if neighbor in closed:
                continue

            new_g = g_score[current] + 1.0
            if new_g >= g_score.get(neighbor, float("inf")):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = new_g

            counter += 1
            f_score = new_g + heuristic(nr, nc)
            heapq.heappush(open_heap, (f_score, counter, neighbor))
            generated_nodes += 1

    planning_time = time.perf_counter() - start_time
    return {
        "success": False,
        "path": [],
        "path_length": None,
        "expanded_nodes": expanded_nodes,
        "generated_nodes": generated_nodes,
        "planning_time": planning_time,
        "expanded_order": expanded_order,
    }


def draw_one_result(ax, grid, start, goal, result, title):
    """画出一张 A* 搜索结果：障碍物、expanded nodes、路径。"""
    size = grid.shape[0]
    image = np.ones((size, size, 3), dtype=np.float32)

    image[grid == OBSTACLE] = np.array([0.0, 0.0, 0.0])

    for row, col in result["expanded_order"]:
        if (row, col) != start and (row, col) != goal and grid[row, col] == FREE:
            image[row, col] = np.array([0.78, 0.78, 0.78])

    ax.imshow(image, origin="upper")

    if result["path"]:
        path = np.array(result["path"])
        ax.plot(path[:, 1], path[:, 0], color="dodgerblue", linewidth=2.0)

    ax.scatter(start[1], start[0], c="lime", s=60, marker="o")
    ax.scatter(goal[1], goal[0], c="red", s=80, marker="*")

    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])


def save_baseline_figure(grid, start, goal, sample_results, output_path):
    """保存 Manhattan / Euclidean / Dijkstra 三种 heuristic 的可视化对比。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    for ax, heuristic_name in zip(axes, ["manhattan", "euclidean", "dijkstra"]):
        result = sample_results[heuristic_name]
        title = (
            f"{heuristic_name}\n"
            f"expanded={result['expanded_nodes']}, "
            f"path={result['path_length']}"
        )
        draw_one_result(ax, grid, start, goal, result, title)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def evaluate_dataset(dataset_path, max_samples, visualize_index, figure_path):
    data = np.load(dataset_path)
    maps = data["maps"]
    starts = data["starts"]
    goals = data["goals"]
    targets = data["targets"]

    num_samples = len(maps) if max_samples is None else min(max_samples, len(maps))
    heuristic_names = ["manhattan", "euclidean", "dijkstra"]
    results = {name: [] for name in heuristic_names}

    for i in range(num_samples):
        grid = maps[i]
        start = tuple(int(v) for v in starts[i])
        goal = tuple(int(v) for v in goals[i])
        dijkstra_map = targets[i, 0]

        for heuristic_name in heuristic_names:
            result = astar_search(
                grid=grid,
                start=start,
                goal=goal,
                heuristic_name=heuristic_name,
                dijkstra_map=dijkstra_map,
            )
            results[heuristic_name].append(result)

        if visualize_index is not None and i == visualize_index:
            sample_results = {
                heuristic_name: results[heuristic_name][-1]
                for heuristic_name in heuristic_names
            }
            save_baseline_figure(grid, start, goal, sample_results, figure_path)
            print(f"saved baseline figure: {figure_path}")

    return results


def summarize_results(results):
    for heuristic_name, records in results.items():
        success_records = [record for record in records if record["success"]]
        success_count = len(success_records)
        total_count = len(records)

        mean_time = np.mean([record["planning_time"] for record in records])
        mean_expanded = np.mean([record["expanded_nodes"] for record in records])
        mean_generated = np.mean([record["generated_nodes"] for record in records])

        if success_records:
            mean_path_length = np.mean(
                [record["path_length"] for record in success_records]
            )
        else:
            mean_path_length = float("nan")

        print(f"\n{heuristic_name} heuristic:")
        print(f"success: {success_count}/{total_count}")
        print(f"mean planning time: {mean_time:.6f}s")
        print(f"mean expanded nodes: {mean_expanded:.2f}")
        print(f"mean generated nodes: {mean_generated:.2f}")
        print(f"mean path length: {mean_path_length:.2f}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("datasets/grid2d_heuristic_v1.npz"),
    )
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--visualize-index", type=int, default=0)
    parser.add_argument(
        "--figure-path",
        type=Path,
        default=Path("results/baseline_expanded_nodes.png"),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    results = evaluate_dataset(
        dataset_path=args.dataset,
        max_samples=args.max_samples,
        visualize_index=args.visualize_index,
        figure_path=args.figure_path,
    )
    summarize_results(results)


if __name__ == "__main__":
    main()
