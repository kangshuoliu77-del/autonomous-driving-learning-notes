# node.py
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0
        
        # Phase 2 新增：记录这一步是花了 1.0 还是 1.414
        self.step_cost = 0 

    def __eq__(self, other):
        return self.position == other.position