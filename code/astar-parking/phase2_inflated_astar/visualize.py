import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

def compare_inflation(raw_maze, inflated_maze, path, start, end):
    """Compare original workspace and inflated C-Space map."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    cmap = colors.ListedColormap(['white', 'black', 'red', 'green', 'blue'])
    norm = colors.BoundaryNorm([0, 1, 2, 3, 4, 5], cmap.N)

    def process_grid(m, p):
        g = np.array(m, dtype=float)
        if p:
            for node in p: g[node[0]][node[1]] = 2
        g[start[0]][start[1]], g[end[0]][end[1]] = 3, 4
        return g

    ax1.imshow(process_grid(raw_maze, None)[::-1], cmap=cmap, norm=norm)
    ax1.set_title("Original Workspace")

    ax2.imshow(process_grid(inflated_maze, path)[::-1], cmap=cmap, norm=norm)
    ax2.set_title("C-Space + Planned Path")
    plt.show()
