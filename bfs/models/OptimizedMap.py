from consts import Tiles

class OptimizedMap():

    def __init__(self, measures, keeper, boxes, goals, walls):
        self._measures = measures
        self._keeper = keeper
        self._boxes = boxes
        self._goals = goals
        self._walls = walls        

    @property
    def width(self):
        return self._measures[0]
    
    @property
    def height(self):
        return self._measures[1]

    @property
    def boxes(self):
        return [box for box in self._boxes if box not in self._goals]

    @property
    def boxes_on_goal(self):
        return [box for box in self._boxes if box in self._goals]

    @property
    def man(self):
        return list(self._keeper) if self._keeper not in self._goals else []

    @property
    def man_on_goal(self):
        return list(self._keeper) if self._keeper in self._goals else []

    @property
    def all_boxes(self):
        return list(self._boxes)

    @property
    def all_man(self):
        return list(self._keeper)
    
    @property
    def all_goals(self):
        return list(self._goals)

    @property
    def goals(self):
        extra = self.all_boxes + self.all_man
        return [goal for goal in self._goals if goal not in extra]

    @property
    def walls(self):
        return list(self._walls)

    @property
    def floor(self):
        others = set(self.all_boxes + self.all_goals + self.all_man + self.walls)
        return [
            (x, y)
            for x in range(0, self.width)
            for y in range(0, self.height)
            if (x,y) not in others
        ]
        '''
        floor = []
        others = set(self.all_boxes + self.all_goals + self.all_man + self.walls)
        for x in range(0, self.width):
            for y in range(0, self.height):
                coord = (x,y)
                if coord not in others: floor.append(coord)
        #floor = self.map.filter_tiles([Tiles.FLOOR])
        #for coord in self.all_boxes + self.all_man: floor.remove(coord)
        return floor
        '''
    
    def get_tile(self, coord):
        if coord in self._walls: return Tiles.WALL
        elif coord in self._goals:
            if coord in self._keeper: return Tiles.MAN_ON_GOAL
            if coord in self._boxes: return Tiles.BOX_ON_GOAL
            else: return Tiles.GOAL
        elif coord in self._keeper: return Tiles.MAN
        elif coord in self._boxes: return Tiles.BOX
        return Tiles.FLOOR
    
    def create_push(self, box_position):
        (kep_x, kep_y) = self.all_man[0]
        (box_x, box_y) = box_position
        self._boxes.remove(box_position)
        self._boxes.add((box_x - (kep_x-box_x), box_y - (kep_y-box_y)))
        self._keeper = set([box_position])
    
    def create_move(self, dest_position):
        self._keeper = set([dest_position])

    def deepcopy(self):
        return OptimizedMap(self._measures, set(self.all_man), set(self.all_boxes), self._goals, self._walls)

    def __str__(self):
        return str(self._keeper) + str(self._boxes) + str(self._goals)

    def __repr__(self):
        return str(self)