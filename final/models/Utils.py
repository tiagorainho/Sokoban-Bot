from copy import deepcopy
from models.OptimizedMap import OptimizedMap
from consts import Tiles
from mapa import Map

BLOCKIVE_TILES = set([Tiles.WALL ,Tiles.BOX, Tiles.BOX_ON_GOAL])
coords_adjs = lambda x, y: [(x + 1, y), (x - 1, y), (x, y + 1), (x, y-1)]
wider_adjs = lambda x, y: [(x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
box_movement_rules = lambda state, current_node, new_node: state.get_tile((current_node[0] - (new_node[0]-current_node[0]), current_node[1] - (new_node[1]-current_node[1]))) != Tiles.WALL
GOTO = 1
PUSH = 2

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

def get_unreachable_areas(state: OptimizedMap, unreachable_coords):
    from models.Search import get_reachable_positions
    areas = []
    while len(unreachable_coords) > 0:
        neighbors = get_reachable_positions(state, unreachable_coords.pop())
        areas.append(neighbors)
        unreachable_coords = unreachable_coords - neighbors
    return areas

def aglomerate_areas(state: OptimizedMap, areas):
    if len(areas) <= 1: return areas
    change_happened = True
    while change_happened:
        change_happened = False
        for area in areas:
            extended_area = set()
            for coord in area:
                adjs = coords_adjs(coord[0], coord[1]) + wider_adjs(coord[0], coord[1])
                for adj in adjs: extended_area.add(adj)
            for area2 in areas:
                if area == area2: continue
                for coord in area2:
                    if coord in extended_area:
                        areas.append(area.union(area2))
                        areas.remove(area)
                        areas.remove(area2)
                        change_happened = True
                        break
                if change_happened: break
            if change_happened: break
    return areas

def extend_boxes_border(state: OptimizedMap, border_boxes):
    all_borders = set()
    all_boxes = set(state.all_boxes)
    for box in border_boxes:
        all_borders.add(box)
        adjs = coords_adjs(box[0], box[1]) + wider_adjs(box[0], box[1])
        for adj in adjs:
            if adj in all_boxes:
                all_borders.add(adj)
    return all_borders

def get_boxes_border(state: OptimizedMap, unreachable_coords):
    boxes = set(state.all_boxes)
    border_boxes = set()
    for coord in unreachable_coords:
        adjs = coords_adjs(coord[0], coord[1]) + wider_adjs(coord[0], coord[1])
        for adj in adjs:
            if adj in boxes:
                border_boxes.add(adj)
    return border_boxes

def get_heuristic_grid(state: OptimizedMap):
    from models.Search import astar_get_path
    heuristic_grid = {}
    goals = state.all_goals
    state = state.deepcopy()
    state._boxes = state._goals = state._keeper = set()
    floor = state.floor
    for coord in floor:
        heuristic_grid[coord] = []
        for goal in goals:
            path = astar_get_path(state, coord, goal, box_movement_rules)            
            if path == None: continue
            heuristic_grid[coord].append(path)
        heuristic_grid[coord].sort(key = lambda path: len(path))
    return heuristic_grid

def get_deadlock_areas(heuristic_grid, state: OptimizedMap):
    goals = state.all_goals
    box_areas = {}
    coords = list(heuristic_grid.keys())
    for coord in coords:
        paths = heuristic_grid[coord]
        for path in paths:
            if path == []: add_to_dict(box_areas, coord, coord)
            else: add_to_dict(box_areas, path[-1], coord)

    areas = list(box_areas.values())
    all_areas = []
    for area1 in areas:
        for area2 in areas:
            if area1 == area2: continue
            area1_only = area1 - area2
            if area1_only != None and area1_only not in all_areas: all_areas.append(area1_only)
    area_max = []
    for area in all_areas:
        counter = 0
        for goal in goals:
            if goal in area: counter += 1
        if counter > 0: area_max.append((area, counter))
    sets_aux = improve_sets(area_max, goals)
    sets = []
    for s in sets_aux:
        area = s[0]
        goals_reached = set()
        for goal in goals:
            if goal in area: goals_reached.add(goal)
        for coord in area:
            if coord in goals_reached: continue
            adjs = coords_adjs(coord[0], coord[1])
            for adj in adjs:
                if adj not in goals_reached and adj in goals:
                    if state.get_tile(adj) not in BLOCKIVE_TILES and state.get_tile(get_oposite_coord(adj, coord)) not in BLOCKIVE_TILES:
                        goals_reached.add(adj)
        sets.append((area, len(goals_reached)))
    return sets

def improve_sets(area_max, goals):
    aux = set()
    while area_max != aux:
        aux = deepcopy(area_max)
        for area1 in area_max:
            for area2 in area_max:
                if area1 == area2: continue
                diff = area1[0].symmetric_difference(area2[0])
                all_goals = True
                for d in diff:
                    if d not in goals:
                        all_goals = False
                if all_goals:
                    diff = list(diff)
                    union = area1[0].union(area2[0])
                    counter = 0
                    for goal in goals:
                        if goal in union: counter += 1
                    area_max.append((union, counter))
                    if area1 in area_max: area_max.remove(area1)
                    if area2 in area_max: area_max.remove(area2)
                elif area1[0].issubset(area2[0]):
                    if area2 in area_max:
                        area_max.remove(area2)
    return area_max

def add_to_dict(dictionary, val1, val2):
    val1 = str(val1)
    val2 = val2
    if val1 in dictionary:
        if not val2 in dictionary[val1]:
            dictionary[val1].add(val2)
    else:
        dictionary[val1] = set([val2])

def is_in_cave_border(state: OptimizedMap, man_coords, box_coords):
    man_x, man_y = man_coords
    box_x, box_y = box_coords
    box_right, box_left, box_down, box_up = coords_adjs(box_x, box_y)
    links = []
    if man_x == box_x:
        # vertical
        if state.get_tile(box_left) == Tiles.WALL and state.get_tile(box_right) == Tiles.WALL:
            links = [box_down, box_up]
    else:
        # horizontal
        if state.get_tile(box_up) == Tiles.WALL and state.get_tile(box_down) == Tiles.WALL:
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
                if val not in distances: distances[val] = len(path)
    return distances