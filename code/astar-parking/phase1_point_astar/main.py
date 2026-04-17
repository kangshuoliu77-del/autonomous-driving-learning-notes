# main.py
from map import get_safe_random_map
from astar import solve
from visualize import draw_path

def run_random_test():
    rows, cols = 15, 20
    start = (0, 0)
    end = (rows-1, cols-1)
    
    # 生成障碍物占比 25% 的地图
    maze = get_safe_random_map(rows, cols, 0.25, start, end)
    
    print("[INFO] 随机地图生成完毕，开始规划...")
    path = solve(maze, start, end)
    
    if path:
        print(f"[SUCCESS] 找到路径，步数: {len(path)-1}")
    else:
        print("[FAIL] 随机障碍物封死了道路。")
        
    draw_path(maze, path, start, end)

if __name__ == "__main__":
    run_random_test()