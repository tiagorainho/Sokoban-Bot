from consts import Tiles
from models.OptimizedMap import OptimizedMap

adjs_lambda = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]
square_lambda = lambda box: [(box[0], box[1]), (box[0]+1,box[1]), (box[0], box[1]+1), (box[0]+1, box[1]+1)]
box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL

def get_static_deadlock_positions(state: OptimizedMap, heuristic_grid):
    reachable = set(list(heuristic_grid.keys()))
    positions = state.floor + state.man + state.boxes
    return set([coord for coord in positions if coord not in reachable])

def has_deadlocks_dynamic(state: OptimizedMap):
    if len(state.boxes) < 2: return False 
    
    # squares
    boxes = state.all_boxes
    while len(boxes) >= 4:
        box = boxes.pop(0)
        squared_boxes = square_lambda(box)
        square_counter = 1
        for i in range(1, len(squared_boxes)):
            if squared_boxes[i] in boxes:
                square_counter += 1
        if square_counter == 4:
            for b in squared_boxes:
                if state.get_tile(b) != Tiles.BOX_ON_GOAL: return True
    
    # two blocks together along a wall
    boxes = state.all_boxes
    boxes_on_goal = state.boxes_on_goal
    while len(boxes) >= 2:
        box = boxes.pop(0)
        adjs = adjs_lambda(box)
        for i in range(len(adjs)):
            if adjs[i] in boxes:
                if box not in boxes_on_goal or adjs[i] not in boxes_on_goal:
                    #horizontal
                    if i < 2:
                        if state.get_tile((box[0], box[1]-1)) == Tiles.WALL and state.get_tile((adjs[i][0], adjs[i][1]-1)) == Tiles.WALL: return True
                        if state.get_tile((box[0], box[1]+1)) == Tiles.WALL and state.get_tile((adjs[i][0], adjs[i][1]+1)) == Tiles.WALL: return True
                    #vertical
                    else:
                        if state.get_tile((box[0]-1, box[1])) == Tiles.WALL and state.get_tile((adjs[i][0]-1, adjs[i][1])) == Tiles.WALL: return True
                        if state.get_tile((box[0]+1, box[1])) == Tiles.WALL and state.get_tile((adjs[i][0]+1, adjs[i][1])) == Tiles.WALL: return True
    return False