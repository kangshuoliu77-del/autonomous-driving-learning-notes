from node import Node
from heuristic import get_dist

def is_valid(pos, maze):
    """边界检查与碰撞检测"""
    rows, cols = len(maze), len(maze[0])
    r, c = pos
    return 0 <= r < rows and 0 <= c < cols and maze[r][c] == 0

def get_neighbors(current_node, maze):
    """
    扩展当前节点的相邻节点
    默认采用 4 连通域（上下左右）
    """
    neighbors = []
    # 方向向量：(dx, dy)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for offset in directions:
        new_pos = (current_node.position[0] + offset[0], 
                   current_node.position[1] + offset[1])
        
        if is_valid(new_pos, maze):
            # 初始化邻居节点，预设当前节点为其父节点
            neighbors.append(Node(new_pos, current_node))
    return neighbors

def solve(maze, start_pos, end_pos):
    """
    执行 A* 路径规划
    """
    start_node = Node(start_pos)
    end_node = Node(end_pos)

    open_list = [start_node]
    closed_list = []

    while open_list:
        # 1. 选取 OpenList 中 f 值最小的节点作为当前处理节点
        current_node = min(open_list, key=lambda n: n.f)
        current_idx = open_list.index(current_node)
        
        open_list.pop(current_idx)
        closed_list.append(current_node)

        # 2. 目标达成判定
        if current_node == end_node:
            path = []
            curr = current_node
            while curr:
                path.append(curr.position)
                curr = curr.parent
            return path[::-1] # 返回正向路径

        # 3. 邻居节点遍历与代价更新
        for neighbor in get_neighbors(current_node, maze):
            if neighbor in closed_list:
                continue

            # 计算代价值
            new_g = current_node.g + 1 # 步速代价固定为 1
            new_h = get_dist(neighbor.position, end_node.position)
            new_f = new_g + new_h

            # 4. 节点更新逻辑：确保 OpenList 中同一坐标节点最优
            found_node = next((n for n in open_list if n == neighbor), None)

            if found_node:
                if new_g < found_node.g:
                    # 发现更优路径，更新其代价与父节点指向
                    found_node.g = new_g
                    found_node.f = new_f
                    found_node.parent = current_node
            else:
                # 新发现节点，赋值并加入 OpenList
                neighbor.g = new_g
                neighbor.h = new_h
                neighbor.f = new_f
                open_list.append(neighbor)

    return None