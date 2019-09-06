from hlt import constants
from hlt import Position
from hlt import game_map

global RESERVED, FREE
RESERVED = 1
FREE     = 0

def find_best_cell(ship, marked_map, game_map):
    """
    Finds best cell for a ship to mine, regarding the (energy/distance) ratio
    :param ship: the ship for which the cell is to be found
    :param marked_map: map filled with RESERVED or FREE
    :game_map: the actual game map
    :return: a Position of the best cell
    """

    cell_rank = []                      # lista cu rapoarte energie/distanta

    for i in range(constants.WIDTH):    # generarea de distante
        for j in range(constants.HEIGHT):
            if Position(i,j) != ship.position:
                distan = game_map[Position(i,j)].halite_amount  / game_map.calculate_distance(ship.position, Position(i,j))
                cell_rank.insert(0, (Position(i, j), distan))



    cell_rank.sort(reverse = True, key = (lambda a: a[1])) # sortare descrescatoare

    for i in cell_rank:
        if marked_map[i[0].x][i[0].y] == FREE:
            return i[0]                                    # returneaza prima celula care nu este deja rezervata pentru alt ship
