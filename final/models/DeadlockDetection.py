from consts import Tiles
from models.OptimizedMap import OptimizedMap
from models.SubSearchTree import SearchTree

adjs_lambda = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]
square_lambda = lambda box: [(box[0]+1,box[1]), (box[0]+1, box[1]+1), (box[0], box[1]+1)]
box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL

async def has_corral_deadlock(state: OptimizedMap, corral_area, border_boxes, floor_inside, problem, heuristic_grid, limit=50):
    boxes = set(state.all_boxes)
    aux_state = state.deepcopy()
    area = corral_area.union(border_boxes)
    for box in boxes:
        if box not in border_boxes:
            aux_state._boxes.remove(box)
    solver = SearchTree(problem, heuristic_grid, floor_inside, aux_state, area)
    answer = await solver.search(limit)
    if answer == False: return True
    return False

def get_static_deadlock_positions(state: OptimizedMap, heuristic_grid):
    return set([coord for coord in heuristic_grid if heuristic_grid[coord] == []])

def has_static_search_deadlock(state: OptimizedMap):
    boxes = state.all_boxes
    if len(boxes) < 2: return False
    set_boxes_on_goal = set(state.boxes_on_goal)
    set_boxes = set(boxes)
    set_goals = set(state.all_goals)
    # two blocks together along a wall
    for box in boxes:
        adjs = adjs_lambda(box)
        i = 0
        for adj in adjs:
            if adj in set_boxes:
                if box not in set_boxes_on_goal or adj not in set_boxes_on_goal:
                    #horizontal
                    if i < 2:
                        if state.get_tile((box[0], box[1]-1)) == Tiles.WALL and state.get_tile((adj[0], adj[1]-1)) == Tiles.WALL: return True
                        if state.get_tile((box[0], box[1]+1)) == Tiles.WALL and state.get_tile((adj[0], adj[1]+1)) == Tiles.WALL: return True
                    #vertical
                    else:
                        if state.get_tile((box[0]-1, box[1])) == Tiles.WALL and state.get_tile((adj[0]-1, adj[1])) == Tiles.WALL: return True
                        if state.get_tile((box[0]+1, box[1])) == Tiles.WALL and state.get_tile((adj[0]+1, adj[1])) == Tiles.WALL: return True
            i += 1

    # squares
    for box in boxes:
        square_counter = 1 if box in set_goals else 0
        squared_boxes = square_lambda(box)
        for box_in_square in squared_boxes:
            if box_in_square not in set_boxes: break
            if box_in_square not in set_goals: square_counter += 1
            if square_counter == 4: return True

    return False

def has_area_deadlock(state: OptimizedMap, areas):
    boxes = set(state.all_boxes)
    for area_value in areas:
        area, max_value = area_value
        counter = 0
        for box in boxes:
            if box in area: counter += 1
            if counter > max_value:
                return True
    return False

# informação para a funcao encontrada em http://sokobano.de/wiki/index.php?title=How_to_detect_deadlocks
def has_freeze_deadlock(state: OptimizedMap, box, static_deadlocks):
    deadlock_finder = DeadlockFinder(state, static_deadlocks)
    is_blocked = deadlock_finder.is_blocked(box)
    if is_blocked:
        goals = set(state.all_goals)
        for box in deadlock_finder.boxes_tested:
            if box not in goals:
                return True
    return False

class DeadlockFinder:
    def __init__(self, state: OptimizedMap, static_deadlocks):
        self.state = state
        self.static_deadlocks = static_deadlocks
        self.blocked_walls = []
        self.boxes_tested = []
        self.boxes = set(state.all_boxes)
        self.walls = set(state.walls)

    def is_blocked(self, box):
        self.boxes_tested.append(box)
        self.walls.add(box)
        is_blocked = self.blocked_vertically(box) and self.blocked_horizontally(box)
        self.walls.remove(box)
        return is_blocked

    def blocked_vertically(self, box):
        up, down = ((box[0], box[1]-1), (box[0], box[1]+1))
        if up in self.walls or down in self.walls: return True
        if up in self.static_deadlocks and down in self.static_deadlocks: return True
        if up in self.boxes:
            if self.is_blocked(up): return True
        if down in self.boxes:
            if self.is_blocked(down): return True
        return False

    def blocked_horizontally(self, box):
        left, right = ((box[0]-1, box[1]), (box[0]+1, box[1]))
        if left in self.walls or right in self.walls: return True
        if left in self.static_deadlocks and right in self.static_deadlocks: return True
        if left in self.boxes:
            if self.is_blocked(left): return True
        if right in self.boxes:
            if self.is_blocked(right): return True
        return False