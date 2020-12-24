from copy import deepcopy
from models.OptimizedMap import OptimizedMap
from consts import Tiles
from mapa import Map

BLOCKIVE_TILES = set([Tiles.WALL ,Tiles.BOX, Tiles.BOX_ON_GOAL])
coords_adjs = lambda x, y: [(x + 1, y), (x - 1, y), (x, y + 1), (x, y-1)]
box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL

def get_clean_map(mapa: Map):
    mapa = switch_tiles(mapa, [Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL], Tiles.GOAL)
    mapa = switch_tiles(mapa, [Tiles.MAN, Tiles.BOX], Tiles.FLOOR)
    return mapa

def can_push_box(game: OptimizedMap, keeper_position, box_position):
    if box_position in game.all_boxes and game.get_tile(keeper_position) not in BLOCKIVE_TILES:
        return game.get_tile(get_oposite_coord(keeper_position, box_position)) not in BLOCKIVE_TILES
    return False

def get_oposite_coord(keeper, box):
    (box_x, box_y) = box
    (kep_x, kep_y) = keeper
    return (box_x - (kep_x-box_x), box_y - (kep_y-box_y))

def get_adjs_pos(game: OptimizedMap, position):
    adjs = []
    (x, y) = position
    if x + 1 < game.width:
        adjs.append((x + 1, y))
    if x - 1 > 0:
        adjs.append((x - 1, y))
    if y + 1 < game.height:
        adjs.append((x, y + 1))
    if y - 1 > 0:
        adjs.append((x, y - 1))
    return adjs

def clean_map_from(state: Map, tiles: Tiles):
    return switch_tiles(state, tiles, Tiles.FLOOR)

def switch_tiles(state: Map, tiles_to_switch: Tiles, tile: Tiles):
    state = deepcopy(state)
    for coord in state.filter_tiles(tiles_to_switch):
        state.clear_tile(coord)
        state.set_tile(coord, tile)
    return state

def manhatan_distance(start_position, goal_position):
    return abs(goal_position[0] - start_position[0]) + abs(goal_position[1] - start_position[1])

def is_in_tunnel_with_box(state: OptimizedMap, man_coords, box_coords):
    man_x, man_y = man_coords
    box_x, box_y = box_coords
    man_right, man_left, man_down, man_up = coords_adjs(man_x, man_y)
    box_right, box_left, box_down, box_up = coords_adjs(box_x, box_y)
    if man_x == box_x:
        # vertical
        if state.get_tile(man_left) == Tiles.WALL and state.get_tile(man_right) == Tiles.WALL:
            if state.get_tile(box_left) == Tiles.WALL and state.get_tile(box_right) == Tiles.WALL:
                return True
    else:
        # horizontal
        if state.get_tile(man_up) == Tiles.WALL and state.get_tile(man_down) == Tiles.WALL:
            if state.get_tile(box_up) == Tiles.WALL and state.get_tile(box_down) == Tiles.WALL:
                return True
    return False

def get_heuristic_grid(state: OptimizedMap):
    from models.Search import astar_get_path
    heuristic_grid = {}
    goals = state.all_goals
    state = state.deepcopy()
    state._boxes = set()
    state._goals = set()
    state._keeper = set()
    floor = state.floor + state.all_man
    random = 10000000
    for goal in goals:
        heuristic_grid[goal] = 0
    for coord in floor:
        minor = random
        for goal in goals:
            path = astar_get_path(state, coord, goal, box_movement_rules)
            if path == None: continue
            if len(path) < minor: minor = len(path)
        if minor != random: heuristic_grid[coord] = minor
    return heuristic_grid

def is_in_corral_border(state: OptimizedMap, man_coords, box_coords):
    man_x, man_y = man_coords
    box_x, box_y = box_coords
    box_right, box_left, box_down, box_up = coords_adjs(box_x, box_y)
    links = []
    if man_x == box_x:
        # vertical
        if state.get_tile(box_left) == Tiles.WALL and state.get_tile(box_right) == Tiles.WALL:
            #if state.get_tile(box_down) == Tiles.FLOOR and state.get_tile(box_up) == Tiles.FLOOR:
            links = [box_down, box_up]
    else:
        # horizontal
        if state.get_tile(box_up) == Tiles.WALL and state.get_tile(box_down) == Tiles.WALL:
            #if state.get_tile(box_left) == Tiles.FLOOR and state.get_tile(box_right) == Tiles.FLOOR:
            links = [box_left, box_right]
    if links == []: return False

    state_aux = state.deepcopy()
    state_aux._boxes = set(box_coords)
    from models.Search import astar_get_path
    return astar_get_path(state_aux, links[0], links[1]) == None

def coords_distances(state: OptimizedMap):
    from models.Search import get_reachable_positions, astar_get_path
    state = state.deepcopy()
    keeper = state.all_man[0]
    state._boxes = state._keeper = state._goals = set()
    floor_inside = get_reachable_positions(state, keeper)
    distances = {}
    for coord in floor_inside:
        for coord2 in floor_inside:
            if coord == coord2: continue
            path = astar_get_path(state, coord, coord2)
            if path != None:
                val = str(set([coord, coord2]))
                val2 = str(set([coord2, coord]))
                if val not in distances: distances[val] = len(path)
                if val2 not in distances: distances[val2] = len(path)
    return distances