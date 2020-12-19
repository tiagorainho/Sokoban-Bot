class Walker():

    def __init__(self):
        self.moves = []
        self.solution = []

    def add_solution(self, solution):
        self.solution = solution
        if solution == None: return
        for i in range(0, len(solution)-1): self.moves.append(self._get_direction(solution[i], solution[i+1]))

    def next_move(self, state):
        return self.moves.pop(0)
    
    def clean(self):
        self.moves = []
        self.solution = []

    def has_next_move(self):
        return self.moves != []

    def _get_direction(self, origin, destiny):
        if origin[0] != destiny[0]:
            # horizontal
            if origin[0] > destiny[0]:
                return "a"
            elif origin[0] < destiny[0]:
                return "d"
            else:
                return None
        else:
            # vertical
            if origin[1] > destiny[1]:
                return "w"
            elif origin[1] < destiny[1]:
                return "s"
            else:
                return None