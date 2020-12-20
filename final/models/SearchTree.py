from models.SearchNode import SearchNode
from consts import Tiles
from models.Utils import get_clean_map, get_heuristic_grid, get_deadlock_areas, get_oposite_coord, GOTO, PUSH, get_boxes_border, get_unreachable_areas, aglomerate_areas
from models.OptimizedMap import OptimizedMap
from queue import PriorityQueue
from models.Search import get_best_path
from models.DeadlockDetection import get_static_deadlock_positions, has_corral_deadlock
from models.Search import get_reachable_positions
import asyncio

MAN_TILES = [Tiles.MAN, Tiles.MAN_ON_GOAL]
BOX_TILES = [Tiles.BOX, Tiles.BOX_ON_GOAL]
GOAL_TILES = [Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL]
adjs = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]

MAX_BORDER_BOXES = 8
CORRAL_DEPTH_LIMIT_PER_BOX = 4
depth_limit = lambda limit_per_box, boxes_number: 6 #limit_per_box*boxes_number

class SearchTree:

    # construtor
    def __init__(self, problem):
        self.problem = problem
        mapa = problem.initial
        clean_map = get_clean_map(mapa)
        new_map = OptimizedMap((clean_map.hor_tiles, clean_map.ver_tiles), set(mapa.filter_tiles(MAN_TILES)), set(mapa.filter_tiles(BOX_TILES)), set(mapa.filter_tiles(GOAL_TILES)), set(mapa.filter_tiles([Tiles.WALL])))
        self.heuristic_grid = get_heuristic_grid(new_map)
        self.problem.domain.deadlocks = get_static_deadlock_positions(new_map, self.heuristic_grid)
        self.problem.domain.read_priority_actions(new_map)
        root = SearchNode(new_map, None, 0, 0, self.heuristic_grid)
        self.problem.domain.areas = get_deadlock_areas(self.heuristic_grid, new_map)
        self.open_nodes = PriorityQueue()
        self.open_nodes.put((0, root))
        self.dict = {}
        self.num_nodes = 0
        keeper = new_map.all_man[0]
        aux_map = new_map.deepcopy()
        aux_map._boxes = aux_map._keeper = set()
        self.floor_inside = get_reachable_positions(aux_map, keeper)
        self.corrals = {}
        self.goal_room_borders = set()
        
    # procurar a solucao
    async def search(self, limit=800):
        while not self.open_nodes.empty():
            await asyncio.sleep(0)
            node = self.open_nodes.get()[1]
            actions = node.next_move
            if self.problem.goal_test(node.state):
                print("pushes ", node.pushes)
                print("nodes ", self.num_nodes)
                return self.get_path(node)
            if node.depth <= limit:
                lnewnodes = []
                if node.next_move == None:
                    reachable_coords = get_reachable_positions(node.state, node.state.all_man[0])
                    actions = self.problem.domain.actions(node.state, reachable_coords)
                    if actions == []: continue
                    
                    # check for corral deadlocks
                    '''
                    # funcional mas com ligeiro atraso em relacao a sem esta detecao
                    unreachable_coords = self.floor_inside - (reachable_coords.union(set(node.state.all_boxes)))
                    if unreachable_coords != set():
                        # sub dividir as areas para facilitar a pesquisa
                        areas_despersed = get_unreachable_areas(node.state, unreachable_coords)
                        areas = aglomerate_areas(node.state, areas_despersed)
                        is_corral_deadlock = False
                        for area in areas:
                            border_boxes = get_boxes_border(node.state, area)
                            # preconditions to start the search
                            if len(border_boxes) > MAX_BORDER_BOXES: continue
                            blocked_by_entrance = False
                            for border in border_boxes:
                                if border in self.goal_room_borders:
                                    blocked_by_entrance = True
                                    break
                            if blocked_by_entrance: continue                    
                            # corral deadlock search
                            value = self.get_corral_info(border_boxes, node.state.all_man[0])
                            if value: continue
                            elif value == None:
                                is_corral_deadlock = await has_corral_deadlock(node.state, area, border_boxes, self.floor_inside, self.problem, self.heuristic_grid, depth_limit(CORRAL_DEPTH_LIMIT_PER_BOX, len(border_boxes)))
                                self.save_corral_info(border_boxes, reachable_coords, is_corral_deadlock)
                                if is_corral_deadlock: break
                        if is_corral_deadlock: continue                    
                    '''
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
                for node in lnewnodes: self.open_nodes.put((node.heuristic, node))
        return None

    def save_corral_info(self, border_boxes, reachable_coords, is_corral_deadlock):
        val1 = str(border_boxes)
        if val1 in self.corrals: self.corrals[val1].append((reachable_coords, is_corral_deadlock))
        else: self.corrals[val1] = [(reachable_coords, is_corral_deadlock)]

    def get_corral_info(self, border_boxes, keeper):
        val1 = str(border_boxes)
        if val1 in self.corrals:
            val2 = self.corrals[val1]
            for val in val2:
                if keeper in val[0]:
                    return val[1]
        return None

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

    def get_path(self, node):
        path = []
        while node.parent != None:
            parent_node = node.parent
            node_keeper = node.state.all_man[0]
            parent_node_keeper = parent_node.state.all_man[0]
            
            if parent_node_keeper in adjs(node_keeper):
                path = [node_keeper] + path
            else:
                path = get_best_path(parent_node.state, parent_node_keeper, node_keeper) + path
            node = parent_node
        return node.state.all_man + path

    def show_path(self, node):
        while node.parent != None:
            node = node.parent
            print(node.state)