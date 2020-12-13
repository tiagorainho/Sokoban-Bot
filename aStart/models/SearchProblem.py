from models.DeadlockDetection import has_deadlocks_dynamic
from models.OptimizedMap import OptimizedMap

class SearchProblem:
    
    def __init__(self, domain, initial):
        self.domain = domain
        self.initial = initial
    
    def prepare_static_deadlocks(self, mapa: OptimizedMap, heuristic_grid):
        self.domain.read_deadlocks(mapa, heuristic_grid)

    def goal_test(self, state : OptimizedMap):
        return state.boxes == []

    def deadlocks_free(self, state : OptimizedMap):
        # static deadblocks
        for box in state.boxes:
            if box in self.domain.deadlocks:
                return False
                
        #dynamic deadblocks
        return not has_deadlocks_dynamic(state)