from consts import Tiles
from typing import List, Tuple
from models.OptimizedMap import OptimizedMap

class Walker():

    def __init__(self):
        self.pointer = 0
        self.moves = []
        self.keeper_positions = []

    def add_solution(self, solution):
        if solution == None:
            return
        for i in range(len(solution)-1):
            self.keeper_positions.append(solution[i].all_man[0])
            move = self._get_direction(solution[i].all_man[0], solution[i+1].all_man[0])
            self.moves.append(move)
        self.keeper_positions.append(solution[len(solution)-1].all_man[0])

    def next_move(self, state):
        key = self.moves[self.pointer]
        self.pointer += 1
        return key
        '''
        if self.moves != []:
            if state["keeper"] == self.keeper_positions[self.pointer]:
                key = self.moves[self.pointer]
                self.pointer += 1
                return key
            elif state["keeper"] == self.keeper_positions[self.pointer-1]:
                return self.moves[self.pointer-1]
            else:
                return "ERROR"
        return ""
        '''
    
    def has_moves(self):
        return self.moves != []
    
    def clean(self):
        self.pointer = 0
        self.moves = []
        self.keeper_positions = []

    def has_next_move(self):
        return len(self.moves) > self.pointer

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