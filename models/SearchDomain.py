from models.DeadlockDetection import get_static_deadlock_positions
from models.Utils import create_move, get_keeper_pos, get_adjs_pos, can_push_box, create_push
from consts import Tiles
from mapa import Map

class SearchDomain():

    def __init__(self):
        self.deadlocks = set()

    def read_deadlocks(self, state: Map):
        self.deadlocks = get_static_deadlock_positions(state)

    def actions(self, state : Map):
        actions = []
        keeper_pos = get_keeper_pos(state)
        adjs_pos = get_adjs_pos(state, keeper_pos)
        for pos in adjs_pos:
            tile = state.get_tile(pos)
            if tile in [Tiles.FLOOR, Tiles.GOAL]:
                actions.append(("goto", pos))
            elif tile in [Tiles.BOX, Tiles.BOX_ON_GOAL]:
                if can_push_box(state, pos, keeper_pos):
                    actions.append(("push", pos))
        return actions

    def result(self, state: Map, action):
        (name, pos) = action
        if name == "goto":
            create_move(state, pos)
        elif name == "push":
            create_push(state, pos)
        return state

    def cost(self, state, action):
        pass

    def heuristic(self, state: Map):
        return self.manhatan_distance(state)
    
    def manhatan_distance(self, state: Map):
        taxi_distance = 0
        for box in state.boxes:
            for goal in state.filter_tiles([Tiles.BOX_ON_GOAL, Tiles.GOAL, Tiles.MAN_ON_GOAL]):
                taxi_distance += abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            taxi_distance += abs(box[0] - state.keeper[0]) + abs(box[1] - state.keeper[1])
        return taxi_distance

    def satisfies(self, state : Map):
        return state.empty_goals == []
