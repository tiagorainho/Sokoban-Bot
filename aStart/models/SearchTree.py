from models.SearchNode import SearchNode
from consts import Tiles
from models.Utils import get_clean_map, get_heuristic_grid, coords_distances
from models.OptimizedMap import OptimizedMap
from queue import PriorityQueue
from models.Search import get_best_path

GOTO = 1
PUSH = 2
MAN_TILES = [Tiles.MAN, Tiles.MAN_ON_GOAL]
BOX_TILES = [Tiles.BOX, Tiles.BOX_ON_GOAL]
GOAL_TILES = [Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL]
adjs = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]

class SearchTree:

    # construtor
    def __init__(self, problem):
        self.problem = problem
        mapa = problem.initial
        clean_map = get_clean_map(mapa)
        new_map = OptimizedMap((clean_map.hor_tiles, clean_map.ver_tiles), set(mapa.filter_tiles(MAN_TILES)), set(mapa.filter_tiles(BOX_TILES)), set(mapa.filter_tiles(GOAL_TILES)), set(mapa.filter_tiles([Tiles.WALL])))

        self.heuristic_grid = get_heuristic_grid(new_map)
        self.problem.prepare_static_deadlocks(new_map, self.heuristic_grid)
        self.problem.domain.read_priority_actions(new_map)
        root = SearchNode(new_map, None, 0, self.heuristic_grid)
        self.open_nodes = PriorityQueue()
        self.open_nodes.put((0, root))
        #self.distances = coords_distances(new_map)
        self.dict = {}
        self.num_nodes = 0
        
        
    # procurar a solucao
    def search(self, limit=800):
        corrar_borders = {}
        
        while not self.open_nodes.empty():
            node = self.open_nodes.get()[1]
            actions = node.next_move
            if self.problem.goal_test(node.state):
                return self.get_path(node)
            if node.depth <= limit:
                lnewnodes = []

                if node.next_move == None:
                    actions = self.problem.domain.actions(node.state)

                for action in actions:
                    next_action = None
                    
                    if len(action) == 3:
                        next_action = [action[2]]
                        action = (action[0], action[1])
                    
                    depth = node.depth# + self.distances[str(set([node.state.all_man[0],action[1]]))]
                    if action[0] == PUSH:
                        depth += 1
                        
                    newstate = self.problem.domain.result(node.state.deepcopy(), action)
                    newnode = SearchNode(newstate, node, depth, self.heuristic_grid, next_action)

                    if action[0] == PUSH:
                        if self.new_state(node.state, action[1]):
                            if self.problem.deadlocks_free(newnode.state):
                                lnewnodes.append(newnode)
                    else:
                        lnewnodes.append(newnode)
                self.num_nodes += len(lnewnodes)
                for node in lnewnodes: self.open_nodes.put((node.heuristic, node))
        return None

    def new_state(self, state, destination):
        val = str(state.all_boxes)
        val2 = (state.all_man[0], destination)
        if val in self.dict:
            if not val2 in self.dict[val]:
                self.dict[val].add(val2)
                return True
        else:
            self.dict[val] = set([val2])
            return True
        return False

    def get_path(self,node):
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

    '''
    priority_actions = []
                pushing_actions = []
                for action in actions:
                    if action[0] == PUSH and node.state.get_tile(action[1]) == Tiles.BOX:
                        pushing_actions.append(action[1])
                        if is_in_tunnel_with_box(node.state, node.state.all_man[0], action[1]): priority_actions.append(action)
                if priority_actions != []:
                    actions = priority_actions
                else:
                    found_coral = False
                    for action in pushing_actions:
                        if action in corrar_borders:
                            if corrar_borders[action]:
                                if found_coral:
                                    actions.append((PUSH, action))
                                else:
                                    actions = [(PUSH, action)]
                                    found_coral = True
                        else:
                            if is_in_corral_border(node.state, node.state.all_man[0], action):
                                corrar_borders[action] = True
                                if found_coral:
                                    actions.append((PUSH, action))
                                else:
                                    actions = [(PUSH, action)]
                                    found_coral = True
                            else: corrar_borders[action] = False
    '''











































    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    '''
    def add_to_open(self,lnewnodes):
        
        if self.strategy == BREADTH:
            self.open_nodes.extend(lnewnodes)


            
            priority = []
            for node in lnewnodes:
                if node.parent.score < node.score:
                    priority[:0] = node
                    lnewnodes.remove(node)
            if priority != []:
                self.open_nodes = priority + self.open_nodes
            self.open_nodes.extend(lnewnodes)
            
        elif self.strategy == DEPTH:
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == UNIFORM:
            pass
    '''

    '''
                        if action[0] == GOTO:
                            man_pos = node.man_coords
                            found_path = False
                            boxes = node.state.filter_tiles([Tiles.BOX, Tiles.BOX_ON_GOAL])
                            free_adjs = []
                            for box in boxes:
                                adjs = adjs_lambda(box)
                                if can_push_box(node.state, box, adjs[0]): free_adjs += [(adjs[0]), (adjs[1])] # horizontal
                                if can_push_box(node.state, box, adjs[2]): free_adjs += [(adjs[2]), (adjs[3])] # vertical
                            if free_adjs == []: continue
                            free_adjs = list(set(free_adjs))                            
                            if node.state.filter_tiles(self.MAN_TILES)[0] not in free_adjs:
                                for adj in free_adjs:
                                    if node.state.get_tile(adj) == Tiles.FLOOR:
                                        path = astar_get_path(node.state, man_pos, adj)
                                        if path != None and path[0] == action[1]:
                                            found_path = True
                                            break
                                if not found_path:
                                    #print("------------------")
                                    #print(action[1])
                                    #print(node.state)
                                    continue
                        #print("passou")
                        '''