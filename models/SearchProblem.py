from models.DeadlockDetection import has_deadlocks_dynamic
from mapa import Map


class SearchProblem:
    
    def __init__(self, domain, initial):
        self.domain = domain
        self.initial = initial
    
    def goal_test(self, state : Map):
        return self.domain.satisfies(state)

    def deadlocks_free(self, state : Map):
        # static deadblocks
        for box in state.boxes:
            if box in self.domain.deadlocks:
                return False

        #dynamic deadblocks
        return not has_deadlocks_dynamic(state)