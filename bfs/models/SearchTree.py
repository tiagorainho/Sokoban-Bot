from models.SearchNode import SearchNode
from consts import Tiles
from models.Utils import is_in_tunnel_with_box, is_in_corral_border, get_clean_map
from models.OptimizedMap import OptimizedMap
from mapa import Map


PUSH = 1
GOTO = 2
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
        root = SearchNode(new_map, None, 0)
        self.open_nodes = [root]
        self.dict = {}
        self.new_state(root)
        self.num_nodes = 0
        self.problem.prepare_static_deadlocks(new_map)
        
    # procurar a solucao
    def search(self, limit=1000):
        corrar_borders = {}
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                return self.get_path(node)
            if node.depth <= limit:
                lnewnodes = []
                actions = self.problem.domain.actions(node.state)
                
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
                
                for action in actions:
                    newstate = self.problem.domain.result(node.state.deepcopy(), action)
                    newnode = SearchNode(newstate, node, node.depth + 1)
                    
                    if self.new_state(newnode):
                        if action[0] == PUSH and not self.problem.deadlocks_free(newnode.state):
                            continue
                        lnewnodes.append(newnode)
                self.num_nodes += len(lnewnodes)
                self.open_nodes.extend(lnewnodes)

        return None

    def new_state(self, node):
        state = node.state
        val = str(state.all_boxes)
        keeper = state.all_man
        if val in self.dict:
            if not keeper[0] in self.dict[val]:
                self.dict[val].add(keeper[0])
                return True
        else:
            self.dict[val] = set(keeper)
            return True
        return False
    
    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return (path)

    def show_path(self, node):
        while node.parent != None:
            node = node.parent
            print(node.state)