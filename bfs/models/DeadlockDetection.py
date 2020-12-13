from models.Utils import can_push_box
from models.AStar import astar_get_path
from consts import Tiles
from models.OptimizedMap import OptimizedMap

adjs_lambda = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]
square_lambda = lambda box: [(box[0], box[1]), (box[0]+1,box[1]), (box[0], box[1]+1), (box[0]+1, box[1]+1)]
box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL

def get_static_deadlock_positions(state: OptimizedMap):
    deadlocks = set()
    floor_inside = set()
    goal_boxes = state.all_goals
    keeper = state.all_man
    state = state.deepcopy()
    state._boxes = set()
    state._goals = set()
    state._keeper = set()
    
    # receive floor for inside the actual game space
    for floor in state.floor + keeper:
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
                        pass
                    #vertical
                    else:
                        if state.get_tile((box[0]-1, box[1])) == Tiles.WALL and state.get_tile((adjs[i][0]-1, adjs[i][1])) == Tiles.WALL: return True
                        if state.get_tile((box[0]+1, box[1])) == Tiles.WALL and state.get_tile((adjs[i][0]+1, adjs[i][1])) == Tiles.WALL: return True
                        
    # check if game stalled
    pushable_coords = [] # (box, adj)
    boxes = state.boxes
    for box in boxes:
        free_adjs = []
        adjs = adjs_lambda(box)
        if can_push_box(state, adjs[0], box): free_adjs += [(adjs[0]), (adjs[1])] # horizontal
        if can_push_box(state, adjs[2], box): free_adjs += [(adjs[2]), (adjs[3])] # vertical
        if free_adjs != []: pushable_coords.append((box, free_adjs))
    if pushable_coords == []: return True
    

    '''
    # check if man can move any box
    man = state.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]
    can_move = False
    for coords in pushable_coords:
        for coord in coords[1]:
            if astar_get_path(state, coord, man) != None:
                can_move = True
                break
        if can_move: break
    if not can_move:
        return True
    '''
    
    
    

        
    '''
    # check if game is winnable (should be the last check)
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