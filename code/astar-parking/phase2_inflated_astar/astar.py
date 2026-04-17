import heuristic
from node import Node

def is_valid(pos, maze):
    """边界检查与碰撞检测。"""
    rows, cols = len(maze), len(maze[0])
    r, c = pos
    return 0 <= r < rows and 0 <= c < cols and maze[r][c] == 0

def get_neighbors(current_node, maze):
    """扩展8连通邻居 (8-connected expansion)."""
    neighbors = []
    # (dr, dc, 代价) - 直行1.0, 斜行1.414
    directions = [
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
        (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)
    ]
    for dr, dc, cost in directions:
        new_pos = (current_node.position[0] + dr, current_node.position[1] + dc)
        if is_valid(new_pos, maze):
            new_node = Node(new_pos, current_node)
            new_node.step_cost = cost
            neighbors.append(new_node)
    return neighbors

def solve(maze, start_pos, end_pos):
    """执行 A* 路径搜索。"""
    open_list = [Node(start_pos)]
    closed_list = []
    
    while open_list:
        # 获取 F 值最小的节点
        current_node = min(open_list, key=lambda n: n.f)
        open_list.remove(current_node)
        closed_list.append(current_node)
        
        if current_node.position == end_pos:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
            
        for neighbor in get_neighbors(current_node, maze):
            if any(c_node == neighbor for c_node in closed_list): continue
            
            tentative_g = current_node.g + neighbor.step_cost
            existing_node = next((n for n in open_list if n == neighbor), None)
            
            if existing_node is None:
                neighbor.g = tentative_g
                neighbor.h = heuristic.calculate(neighbor.position, end_pos)
                neighbor.f = neighbor.g + neighbor.h
                open_list.append(neighbor)
            elif tentative_g < existing_node.g:
                existing_node.g = tentative_g
                existing_node.parent = current_node
                existing_node.f = existing_node.g + existing_node.h
    return None