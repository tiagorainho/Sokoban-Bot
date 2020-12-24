from models.Utils import BLOCKIVE_TILES, get_adjs_pos, manhatan_distance
from models.OptimizedMap import OptimizedMap
from queue import PriorityQueue

class Node:
    def __init__(self, position, parent, depth):
        self.position = position
        self.parent = parent
        self.depth = depth
        self.distance_to_goal = 0
        self.cost = 0

    def apply_heuristics(self, goal):
        self.distance_to_goal = manhatan_distance(self.position, goal)
        self.cost = self.depth + self.distance_to_goal

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return ("({0},{1})".format(self.position, self.cost))
    
    def __hash__(self):
        return hash(self.position)

def astar_get_path(state: OptimizedMap, start, goal, custom = lambda x,y,z: True):
    closed = set()
    start_node = Node(start, None, 0)
    open_nodes = PriorityQueue()
    open_nodes.put((0, start_node))
    while not open_nodes.empty():
        current_node = open_nodes.get()[1]
        if current_node.position == goal:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        neighbors = get_adjs_pos(state, current_node.position)
        for new_node in neighbors:
            if not custom(state, current_node.position, new_node): continue
            new_tile = state.get_tile(new_node)
            if new_tile in BLOCKIVE_TILES: continue
            neighbor = Node(new_node, current_node, current_node.depth + 1)
            if neighbor in closed: continue
            neighbor.apply_heuristics(goal)
            if neighbor not in closed: open_nodes.put((neighbor.cost, neighbor))
        closed.add(current_node)
    return None


def get_best_path(state: OptimizedMap, start, goal, custom = lambda x,y,z: True):
    closed = set()
    start_node = Node(start, None, 0)
    open_node = [start_node]
    while open_node != []:
        open_node.sort()
        current_node = open_node.pop(0)
        closed.add(current_node)
        if current_node.position == goal:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        neighbors = get_adjs_pos(state, current_node.position)
        for new_node in neighbors:
            if not custom(state, current_node.position, new_node): continue
            new_tile = state.get_tile(new_node)
            if new_tile in BLOCKIVE_TILES: continue
            neighbor = Node(new_node, current_node, current_node.depth + 1)
            if neighbor in closed: continue
            if add_to_open(open_node, neighbor): open_node.append(neighbor)
    return None

def get_reachable_positions(state: OptimizedMap, start):
    closed = set()
    start_node = Node(start, None, 0)
    open_node = [start_node]
    while open_node != []:
        current_node = open_node.pop(0)
        closed.add(current_node.position)
        neighbors = get_adjs_pos(state, current_node.position)
        for new_node in neighbors:
            new_tile = state.get_tile(new_node)
            if new_tile in BLOCKIVE_TILES: continue
            neighbor = Node(new_node, current_node, current_node.depth + 1)
            if neighbor.position in closed: continue
            if add_to_open(open_node, neighbor): open_node.append(neighbor)
    return closed

def add_to_open(open_list, new_node):
    for node in open_list:
        if new_node == node and new_node.cost >= node.cost:
            return False
    return True