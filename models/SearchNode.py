from mapa import Map
from consts import Tiles

class SearchNode:
    def __init__(self,state : Map,parent,depth): 
        self.state = state
        self.parent = parent
        self.depth = depth

    def in_parent(self,state):
        if str(self.state) == str(state):
            return True
        if self.parent == None:
            return False
        return self.parent.in_parent(state)
    
    @property
    def man_coords(self):
        return self.state.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]

    def __str__(self):
        return "no({0}, {1}, {2})\n".format(self.state, self.depth, self.parent)

    def __repr__(self):
        return str(self)