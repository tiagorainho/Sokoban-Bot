from models.SearchNode import SearchNode
from consts import Tiles
from models.Utils import get_oposite_coord
from models.OptimizedMap import OptimizedMap
from models.Search import get_best_path
from models.Search import get_reachable_positions
import asyncio

GOTO = 1
PUSH = 2
MAN_TILES = [Tiles.MAN, Tiles.MAN_ON_GOAL]
BOX_TILES = [Tiles.BOX, Tiles.BOX_ON_GOAL]
GOAL_TILES = [Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL]
adjs = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]

class SearchTree:

    # construtor
    def __init__(self, problem, heuristic_grid, floor_inside, state: OptimizedMap, corral_area):
        self.problem = problem
        self.heuristic_grid = heuristic_grid
        root = SearchNode(state, None, 0, 0, self.heuristic_grid)
        self.open_nodes = [root]
        self.dict = {}
        self.num_nodes = 0
        self.floor_inside = floor_inside
        self.corral_area = corral_area
        
    # procurar a solucao
    async def search(self, limit=40):
        while self.open_nodes != []:
            await asyncio.sleep(0)
            node = self.open_nodes.pop(0)
            actions = node.next_move
            if self.problem.goal_test(node.state): return True # solution has been found
            for box in node.state.all_boxes:
                if box not in self.corral_area: return True # way out of the corral has been found
            if node.pushes >= limit: return None # couldnt be found in time
            lnewnodes = []
            if node.next_move == None:
                reachable_coords = get_reachable_positions(node.state, node.state.all_man[0])
                actions = self.problem.domain.actions(node.state, reachable_coords)

            for action in actions:
                next_action = None
                if len(action) == 3:
                    next_action = [action[2]]
                    action = (action[0], action[1])
                pushes = node.pushes
                if action[0] == PUSH:
                    pushes += 1
                newstate = self.problem.domain.result(node.state.deepcopy(), action)
                newnode = SearchNode(newstate, node, node.depth + 1, pushes, self.heuristic_grid, next_action)
                if action[0] == PUSH:
                    if self.new_state(node.state, action[1]):
                        if self.problem.deadlocks_free(newnode.state, get_oposite_coord(node.state.all_man[0], action[1])):
                            lnewnodes.append(newnode)
                else:
                    lnewnodes.append(newnode)
            self.num_nodes += len(lnewnodes)
            self.open_nodes.extend(lnewnodes)
        return False # is deadlock

    def new_state(self, state: OptimizedMap, destination):
        val = hash(state)
        val2 = (state.all_man[0], destination)
        if val in self.dict:
            if not val2 in self.dict[val]:
                self.dict[val].add(val2)
                return True
        else:
            self.dict[val] = set([val2])
            return True
        return False