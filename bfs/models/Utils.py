from copy import deepcopy
from operator import pos
from models.OptimizedMap import OptimizedMap
from consts import Tiles
from mapa import Map

BLOCKIVE_TILES = set([Tiles.WALL ,Tiles.BOX, Tiles.BOX_ON_GOAL])
coords_adjs = lambda x, y: [(x + 1, y), (x - 1, y), (x, y + 1), (x, y-1)]

def get_clean_map(mapa: Map):
    mapa = switch_tiles(mapa, [Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL], Tiles.GOAL)
    mapa = switch_tiles(mapa, [Tiles.MAN, Tiles.BOX], Tiles.FLOOR)
    return mapa

def can_push_box(game: OptimizedMap, keeper_position, box_position):
    '''
    coord = (box_position[0] - (keeper_position[0]-box_position[0]), box_position[1] - (keeper_position[1]-box_position[1]))
    if box_position in game.all_boxes and game.get_tile(keeper_position) not in BLOCKIVE_TILES:
        return game.get_tile(coord) not in BLOCKIVE_TILES
    return False
    '''
    (box_x, box_y) = box_position
    (kep_x, kep_y) = keeper_position
    if box_position in game.all_boxes and game.get_tile(keeper_position) not in BLOCKIVE_TILES:
        return game.get_tile((box_x - (kep_x-box_x), box_y - (kep_y-box_y))) not in BLOCKIVE_TILES
    return False

def get_keeper_pos(game: Map):
    return game.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]

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

#def get_reachable_coords(state: OptimizedMap):
#    fazer isto com bfs a correr para 1 sitio q n existe e receber o mapa todo


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
    from models.AStar import astar_get_path
    return astar_get_path(state_aux, links[0], links[1]) == None

def boxes_inside(state: Map):
    from models.AStar import astar_get_path
    boxes_inside = set()
    boxes = state.filter_tiles([Tiles.BOX])
    goals = state.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL])
    
    for box in state.filter_tiles([Tiles.BOX_ON_GOAL])[0]:
        boxes_inside.add(box)
    for box in boxes:
        box_is_inside = False
        for goal in goals:
            if astar_get_path(state, box, goal) != None:
                box_is_inside = True
                break
        if box_is_inside:
            boxes_inside.add(box)
    return boxes_inside