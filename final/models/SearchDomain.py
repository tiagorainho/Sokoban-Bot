from models.Utils import get_adjs_pos, can_push_box, get_oposite_coord, add_to_dict, PUSH, GOTO
from models.OptimizedMap import OptimizedMap
from consts import Tiles

coords_adjs = lambda box: [(box[0]+1,box[1]), (box[0]-1, box[1]), (box[0], box[1]+1), (box[0], box[1]-1)]
class SearchDomain():

    def __init__(self):
        self.deadlocks = set()
        self.tunnels = {}
        self.caves_entry = {}
        self.areas = []

    def read_priority_actions(self, state: OptimizedMap):
        floor = set(state.floor + state.all_man + state.all_boxes + state.all_goals)
        state_aux = state.deepcopy()
        state_aux._goals = state_aux._boxes = state_aux._keeper = set()
        
        for x in range(0, state.width):
            for y in range(0, state.height):
                # tunnels
                man_coords = (x,y)
                
                if man_coords not in floor: continue
                adjs = coords_adjs(man_coords)
                for box_coords in adjs:
                    
                    man_x, man_y = man_coords
                    box_x, box_y = box_coords
                    man_right, man_left, man_down, man_up = adjs
                    box_right, box_left, box_down, box_up = coords_adjs(box_coords)
                    if state.get_tile(man_coords) == Tiles.GOAL: continue
                    if man_x == box_x:
                        # vertical
                        if state.get_tile(man_left) == Tiles.WALL and state.get_tile(man_right) == Tiles.WALL:
                            if state.get_tile(box_left) == Tiles.WALL and state.get_tile(box_right) == Tiles.WALL:
                                add_to_dict(self.tunnels, [man_coords, box_coords], box_coords)
                                continue
                    else:
                        # horizontal
                        if state.get_tile(man_up) == Tiles.WALL and state.get_tile(man_down) == Tiles.WALL:
                            if state.get_tile(box_up) == Tiles.WALL and state.get_tile(box_down) == Tiles.WALL:
                                add_to_dict(self.tunnels, [man_coords, box_coords], box_coords)
                                continue
                '''
                # caves
                box_coords = (x,y)
                box_x, box_y = box_coords
                man_x, man_y = man_coords
                box_right, box_left, box_down, box_up = coords_adjs(box_coords)
                links = []
                if man_x == box_x:
                    # vertical
                    if state.get_tile(box_left) == Tiles.WALL and state.get_tile(box_right) == Tiles.WALL:
                        links = [box_down, box_up]
                else:
                    # horizontal
                    if state.get_tile(box_up) == Tiles.WALL and state.get_tile(box_down) == Tiles.WALL:
                        links = [box_left, box_right]
                
                if links == []: continue

                if astar_get_path(state_aux, links[0], links[1]) == None:
                    print(links[0], links[1])
                    self.add_to_dict(self.caves_entry, [links[0], box_coords], box_coords)
        print(self.caves_entry)
        print("----")
        '''

    def actions(self, state : OptimizedMap, reachable_coords):
        actions = []
        keeper = state.all_man[0]
        boxes = state.all_boxes

        priority_actions = []
        # check tunnels
        for box in boxes:
            if get_oposite_coord(keeper, box) in self.deadlocks: continue
            if str([keeper, box]) in self.tunnels and can_push_box(state, keeper, box) and state.get_tile(box) != Tiles.BOX_ON_GOAL:
                priority_actions.append((PUSH, box))

        if priority_actions != []: return priority_actions
        
        # normal
        for box in boxes:
            for adj in get_adjs_pos(state, box):
                if get_oposite_coord(adj, box) in self.deadlocks: continue
                if adj in reachable_coords and can_push_box(state, adj, box):
                    if keeper == adj: actions.append((PUSH, box))
                    else: actions.append((GOTO, adj, (PUSH, box)))        
        return actions

    def result(self, state: OptimizedMap, action):
        (name, pos) = action
        if name == GOTO:
            state.create_move(pos)
        elif name == PUSH:
            state.create_push(pos)
        return state