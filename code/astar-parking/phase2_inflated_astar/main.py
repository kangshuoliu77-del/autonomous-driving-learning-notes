# main.py 最终版

import map
import astar
import visualize # 导入刚才写的文件
import time

def main():
    # 1. 地图参数 (100x100)
    ROWS, COLS = 100, 100
    START, END = (2, 2), (97, 97)
    
    # 2. 生成随机“原始”地图 (概率 0.05)
    print(f"正在生成 {ROWS}x{COLS} 的原始地图...")
    raw_maze = map.get_safe_random_map(rows=ROWS, cols=COLS, obstacle_prob=0.05, start=START, end=END)
    
    # 3. 膨胀地图 (radius=1 整数格子)
    # 这步把 Workspace 变成了 C-Space (MR 10.4 核心逻辑)
    print("正在根据车辆半径膨胀障碍物...")
    inflated_maze = map.get_inflated_map(raw_maze, radius=1)
    
    # 【重点】手动再次确保起点终点是干净的，防止被膨胀逻辑埋了
    inflated_maze[START[0]][START[1]] = 0
    inflated_maze[END[0]][END[1]] = 0

    # 4. A* 算法算路 (8连通)
    print("正在计算路径 (8-Connected A*)...")
    start_time = time.time()
    path = astar.solve(inflated_maze, START, END)
    end_time = time.time()
    
    # 5. 【可视化核心】
    if path:
        print(f"成功找到路径！用时: {end_time - start_time:.2f} 秒，路径点数: {len(path)}")
        
        # --- 方案A：只看膨胀后的路径图 ---
        # visualize.draw_grid(inflated_maze, path, START, END, title="Phase 2 Safe Path")
        
        # --- 方案B：【强烈建议】并排对比 Workspace 和 C-Space ---
        # 让你看清路径是如何自动绕开那些“并不存在的胖墙”的
        visualize.compare_inflation(raw_maze, inflated_maze, path, START, END)
        
    else:
        print("❌ 未能找到可行路径。")

if __name__ == "__main__":
    main()