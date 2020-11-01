from copy import deepcopy
from models.Utils import can_push_box, get_adjs_pos, switch_tiles
from models.AStar import astar_get_path
from consts import Tiles
from mapa import Map

def get_static_deadlock_positions(state: Map):
    deadlocks = set()
    floor_inside = set()
    state = switch_tiles(state, [Tiles.MAN, Tiles.BOX], Tiles.FLOOR)
    state = switch_tiles(state, [Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL], Tiles.GOAL)
    goal_boxes = state.filter_tiles([Tiles.GOAL])

    box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL

    # receive floor for inside the actual game space
    for floor in state.filter_tiles([Tiles.FLOOR]):
        for goal in goal_boxes:
            path = astar_get_path(state, floor, goal)
            if path != None:
                floor_inside.add(floor)
                break

    # look for deadlocks
    for floor in floor_inside:
        is_deadlock = True
        for goal in goal_boxes:
            if astar_get_path(state, floor, goal, box_movement_rules) != None:
                is_deadlock = False
                break
        if is_deadlock:
            deadlocks.add(floor)
    return deadlocks

def has_deadlocks_dynamic(state: Map):
    if len(state.filter_tiles([Tiles.BOX])) < 2: return False
    box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL
    adjs_lambda = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]
    square_lambda = lambda box: [(box[0], box[1]), (box[0]+1,box[1]), (box[0], box[1]+1), (box[0]+1, box[1]+1)]

    # squares
    boxes = state.filter_tiles([Tiles.BOX, Tiles.BOX_ON_GOAL])
    while len(boxes) >= 4:
        box = boxes.pop(0)
        squared_boxes = square_lambda(box)
        square_counter = 1
        for i in range(1, len(squared_boxes)):
            if squared_boxes[i] in boxes:
                square_counter += 1
        if square_counter == 4:
            for b in squared_boxes:
                if state.get_tile(b) != Tiles.BOX_ON_GOAL:
                    return True
    
    # two blocks together along a wall
    boxes = state.filter_tiles([Tiles.BOX, Tiles.BOX_ON_GOAL])
    boxes_on_goal = state.filter_tiles([Tiles.BOX_ON_GOAL])
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
                        pass
                    #vertical
                    else:
                        if state.get_tile((box[0]-1, box[1])) == Tiles.WALL and state.get_tile((adjs[i][0]-1, adjs[i][1])) == Tiles.WALL: return True
                        if state.get_tile((box[0]+1, box[1])) == Tiles.WALL and state.get_tile((adjs[i][0]+1, adjs[i][1])) == Tiles.WALL: return True

    # check if game is winnable (should be the last check)
    '''
    goals = state.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])
    boxes_on_goal = state.filter_tiles([Tiles.BOX_ON_GOAL])
    boxes = state.filter_tiles([Tiles.BOX, Tiles.BOX_ON_GOAL])
    state2 = deepcopy(state)
    for goal in goals:
        if state2.get_tile(goal) == Tiles.BOX_ON_GOAL:
            continue
        found = False
        for box in boxes:
            if astar_get_path(state2, box, goal, box_movement_rules) != None:
                found = True
                break
        if not found:
            return True
    '''
    return False