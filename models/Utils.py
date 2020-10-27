from copy import deepcopy
from consts import Tiles
from mapa import Map

def create_move(game: Map, dest_position):
    origin_position = game.keeper
    dest_tile = game.get_tile(dest_position)
    next_dest_tile = 0
    next_origin_tile = 0
    if dest_tile == Tiles.GOAL:
        next_dest_tile = Tiles.MAN_ON_GOAL
    else:
        next_dest_tile = Tiles.MAN
    if len(game.filter_tiles([Tiles.MAN_ON_GOAL])) == 1:
        next_origin_tile = Tiles.GOAL
    else:
        next_origin_tile = Tiles.FLOOR
        
    game.clear_tile(dest_position)
    game.clear_tile(origin_position)
    game.set_tile(dest_position, next_dest_tile)
    game.set_tile(origin_position, next_origin_tile)

def create_push(game: Map, box_position):
    (kep_x, kep_y) = game.keeper
    (box_x, box_y) = box_position
    dest_position = (0, 0)
    if kep_x > box_x and kep_y == box_y: #box pushed to left
        dest_position = (box_x - 1, box_y)
    elif kep_x < box_x and kep_y == box_y: #box pushed to right
        dest_position = (box_x + 1, box_y)
    elif kep_x == box_x and kep_y > box_y: #box pushed to top
        dest_position = (box_x, box_y - 1)
    elif kep_x == box_x and kep_y < box_y: #box pushed to bottom
        dest_position = (box_x, box_y + 1)

    origin_tile = game.get_tile(game.keeper)
    origin_box_tile = game.get_tile(box_position)
    dest_tile = game.get_tile(dest_position)
    next_origin_tile = 0
    next_origin_box_tile = 0
    next_dest_tile = 0

    if origin_tile == Tiles.MAN_ON_GOAL:
        next_origin_tile = Tiles.GOAL
    else:
        next_origin_tile = Tiles.FLOOR

    if origin_box_tile == Tiles.BOX_ON_GOAL:
        next_origin_box_tile = Tiles.MAN_ON_GOAL
    else:
        next_origin_box_tile = Tiles.MAN
    
    if dest_tile == Tiles.GOAL:
        next_dest_tile = Tiles.BOX_ON_GOAL
    else:
        next_dest_tile = Tiles.BOX

    tmp = game.keeper
    game.clear_tile(game.keeper)
    game.clear_tile(box_position)
    game.clear_tile(dest_position)
    game.set_tile(tmp, next_origin_tile)
    game.set_tile(box_position, next_origin_box_tile)
    game.set_tile(dest_position, next_dest_tile)

def can_push_box(game: Map, box_position, keeper_position):
    (box_x, box_y) = box_position
    (kep_x, kep_y) = keeper_position
    blockive_tiles = [Tiles.WALL ,Tiles.BOX, Tiles.BOX_ON_GOAL]
    if kep_x > box_x and kep_y == box_y: #box can be pushed to left
        return game.get_tile((box_x - 1, box_y)) not in blockive_tiles
    elif kep_x < box_x and kep_y == box_y: #box can be pushed to right
        return game.get_tile((box_x + 1, box_y)) not in blockive_tiles
    elif kep_x == box_x and kep_y > box_y: #box can be pushed to top
        return game.get_tile((box_x, box_y - 1)) not in blockive_tiles
    elif kep_x == box_x and kep_y < box_y: #box can be pushed to bottom
        return game.get_tile((box_x, box_y + 1)) not in blockive_tiles
    return False

def get_keeper_pos(game: Map):
    return game.filter_tiles([Tiles.MAN, Tiles.MAN_ON_GOAL])[0]

def get_adjs_pos(game: Map, position):
    adjs = []
    (x, y) = position
    if x + 1 < game.hor_tiles:
        adjs.append((x + 1, y))
    if x - 1 > 0:
        adjs.append((x - 1, y))
    if y + 1 < game.ver_tiles:
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

def is_in_tunnel_with_box(state: Map, man_coords, box_coords):
    coords_adjs = lambda x, y: [(x + 1, y), (x - 1, y), (x, y + 1), (x, y-1)]
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