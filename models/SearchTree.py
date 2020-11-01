from copy import deepcopy
from models.SearchNode import SearchNode
from consts import Tiles
from models.Utils import is_in_tunnel_with_box

class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.solutions = []
        self.MAN_TILES = [Tiles.MAN, Tiles.MAN_ON_GOAL]
        self.BOX_TILES = [Tiles.BOX, Tiles.BOX_ON_GOAL]
        self.dict = {(str(root.state.filter_tiles(self.MAN_TILES)),str(root.state.filter_tiles(self.BOX_TILES))): True}
        self.num_nodes = 0

    def found_solutions(self):
        return self.solutions != []

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return (path)
        
    # procurar a solucao
    def search(self, limit=1000):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.solution = node
                self.solutions.append(self.get_path(node))
                return self.solutions[0]
            if node.depth <= limit:
                lnewnodes = []
                actions = self.problem.domain.actions(node.state)

                tunnel_actions = []
                for action in actions:
                    if action[0] == 'push':
                        if not action[1] in node.state.filter_tiles([Tiles.BOX_ON_GOAL]):
                            if is_in_tunnel_with_box(node.state, node.man_coords,action[1]):
                                tunnel_actions.append(action)
                if tunnel_actions != []:
                    actions = tunnel_actions
                
                for action in actions:
                    newstate = self.problem.domain.result(deepcopy(node.state), action)
                    newnode = SearchNode(newstate, node, node.depth + 1)
                    if self.new_on_hashtable(newnode.state):
                        if action[0] == 'push' and not self.problem.deadlocks_free(newnode.state):
                            continue
                        lnewnodes.append(newnode)
                        self.num_nodes += 1
                lnewnodes.sort(key=lambda n: self.problem.domain.heuristic(n.state))
                self.add_to_open(lnewnodes)
        return None if self.solutions == [] else self.solutions

    def new_on_hashtable(self, state):
        val = (str(state.filter_tiles(self.MAN_TILES)),str(state.filter_tiles(self.BOX_TILES)))
        if self.dict.get(val) == None:
            self.dict[val] = True
            return True
        return False

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            pass