from models.DeadlockDetection import get_static_deadlock_positions
from models.Utils import boxes_inside, get_keeper_pos, get_adjs_pos, can_push_box
from consts import Tiles
from mapa import Map
from models.SearchTree import PUSH, GOTO
from models.OptimizedMap import OptimizedMap

class SearchDomain():

    def __init__(self):
        self.deadlocks = set()
        self.boxes_outside = set()

    def read_deadlocks(self, state: OptimizedMap):
        self.deadlocks = get_static_deadlock_positions(state)
    
    def process_map(self, state: OptimizedMap):
        self.read_deadlocks(state)

    def actions(self, state : OptimizedMap):
        actions = []
        keeper_pos = state.all_man[0]
        adjs_pos = get_adjs_pos(state, keeper_pos)
        for pos in adjs_pos:
            tile = state.get_tile(pos)
            if tile in [Tiles.FLOOR, Tiles.GOAL]:
                actions.append((GOTO, pos))
            else:
                if can_push_box(state, keeper_pos, pos):
                    actions.append((PUSH, pos))
        return actions

    def result(self, state: OptimizedMap, action):
        (name, pos) = action
        if name == GOTO:
            state.create_move(pos)
        elif name == PUSH:
            state.create_push(pos)
        return state

    def heuristic(self, state: Map):
        return self.manhatan_distance(state)
    
    def manhatan_distance(self, state: Map):
        distance = 0
        for box in state.boxes:
            minor = 1000000000000
            for goal in state.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL]):
                heuristic = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
                if heuristic == 0: heuristic = 1
                if heuristic < minor:
                    minor = heuristic
            distance += minor
        return distance