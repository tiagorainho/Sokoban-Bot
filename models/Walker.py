from consts import Tiles
from mapa import Map
from typing import List, Tuple

class Walker():

    def __init__(self):
        self.pointer = 0
        self.moves = []
        self.keeper_positions = []

    def add_solution(self, solution):
        if solution == None:
            return
        for i in range(len(solution)-1):
            self.keeper_positions.append(list(solution[i].filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]))
            self.moves.append(self._get_direction(solution[i].filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0], solution[i+1].filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]))
        self.keeper_positions.append(list(solution[len(solution)-1].filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]))
            
    def next_move(self, state):
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
    
    def clean(self):
        self.__init__()


    def has_next_move(self):
        return len(self.moves) > self.pointer

    def _get_direction(self, origin: Tuple[int, int], destiny: Tuple[int, int]) -> "w" or "s" or "a" or "d" or None:
        if origin[0] != destiny[0]:
            if origin[0] > destiny[0]:
                return "a"
            elif origin[0] < destiny[0]:
                return "d"
            else:
                return None
        else:
            if origin[1] > destiny[1]:
                return "w"
            elif origin[1] < destiny[1]:
                return "s"
            else:
                return None