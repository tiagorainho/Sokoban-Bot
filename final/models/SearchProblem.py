from models.OptimizedMap import OptimizedMap

class SearchProblem:
    
    def __init__(self, domain, initial):
        self.domain = domain
        self.initial = initial        

    def goal_test(self, state : OptimizedMap):
        return state.boxes == []

    def deadlocks_free(self, state : OptimizedMap, action):
        from models.DeadlockDetection import has_freeze_deadlock, has_area_deadlock
        if has_area_deadlock(state, self.domain.areas): return False
        if has_freeze_deadlock(state, action, self.domain.deadlocks): return False
        return True