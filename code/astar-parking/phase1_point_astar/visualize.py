import matplotlib.pyplot as plt
import numpy as np

def draw_path(maze, path, start, end):
    """
    可视化地图与规划路径
    :param maze: 二维列表地图
    :param path: A* 返回的坐标序列
    :param start: 起点坐标 (r, c)
    :param end: 终点坐标 (r, c)
    """
    # 1. 转换地图数据为 numpy 数组以便绘图
    grid = np.array(maze)
    rows = len(grid)
    cols = len(grid[0])

    fig, ax = plt.subplots(figsize=(10, 6))

    # 2. 绘制地图背景 (cmap='Greys' 0为白，1为黑)
    ax.imshow(grid, cmap='Greys', origin='upper')

    # 3. 如果存在路径，提取坐标并绘制红线
    if path:
        path_y = [p[0] for p in path]
        path_x = [p[1] for p in path]
        ax.plot(path_x, path_y, color='red', linewidth=2, label='Planned Path')

    # 4. 绘制起点和终点
    ax.scatter(start[1], start[0], color='green', s=100, label='Start', zorder=5)
    ax.scatter(end[1], end[0], color='blue', s=100, label='Goal', zorder=5)

    # 5. 图表格式美化
    ax.set_xticks(np.arange(-0.5, cols, 1))
    ax.set_yticks(np.arange(-0.5, rows, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(color='gray', linestyle='-', linewidth=0.5)
    ax.set_title("A* Path Planning - Point Mass Model")
    ax.legend()

    plt.show()