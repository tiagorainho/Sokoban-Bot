from models.OptimizedMap import OptimizedMap
from consts import Tiles

class SearchNode:
    def __init__(self,state: OptimizedMap, parent, depth, heuristic_grid, next_move = None):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.next_move = next_move
        self.heuristic = self.apply_heuristic_grid(heuristic_grid) + self.depth*0.2

    def apply_heuristic_grid(self, heuristic_grid):
        heuristic = 0
        for box in self.state.boxes:
            if box in heuristic_grid:
                heuristic += heuristic_grid[box]
        return heuristic
    
    def manhatan_distance(self):
        distance = 0
        radius = 2
        for box in self.state.boxes:
            near_boxes = 0
            for x_rad in range(int(-radius / 2), int(radius / 2)):
                for y_rad in range(int(-radius / 2), int(radius / 2)):
                    box_rad = (box[0] + x_rad, box[1] + y_rad)
                    if(box_rad[0] < self.state.width and box_rad[1] < self.state.height and box_rad[0] > 0 and box_rad[1] > 0):
                        if self.state.get_tile(box_rad) == Tiles.WALL:
                            near_boxes += 1
            minor = 1000
            for goal in self.state.all_goals:
                heuristic = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
                if heuristic < minor:
                    minor = heuristic
            distance += minor + near_boxes
        return distance

    def manhatan_distance_focused(self):
        distance = 0
        radius = 2
        for box in self.state.boxes:
            minor = 1000
            for goal in self.state.all_goals:
                near_boxes = 0
                left = right = up = down = 0
                if box[0] > goal[0]: left = radius
                elif box[0] < goal[0]: right = radius
                else: left = right = radius

                if box[1] > goal[1]: down = radius
                elif box[1] < goal[1]: up = radius
                else: down = up = radius

                for x_rad in range(left, right):
                    for y_rad in range(up, down):
                        box_rad = (box[0] + x_rad, box[1] + y_rad)
                        if(box_rad[0] < self.state.width and box_rad[1] < self.state.height and box_rad[0] > 0 and box_rad[1] > 0):
                            if self.state.get_tile(box_rad) == Tiles.WALL:
                                near_boxes += 1
                heuristic = abs(box[0] - goal[0]) + abs(box[1] - goal[1]) + near_boxes
                if heuristic < minor:
                    minor = heuristic
            distance += minor
        return distance
        
    
    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def in_parent(self,state):
        if str(self.state) == str(state):
            return True
        if self.parent == None:
            return False
        return self.parent.in_parent(state)

    def __str__(self):
        return "no({0}, {1}, {2})\n".format(self.state, self.depth, self.parent)

    def __repr__(self):
        return str(self)