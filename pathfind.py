from queue import Queue
import numpy as np
from hlt import Position
from hlt import Direction
from hlt import constants


global FREE, OCCUPIED
FREE     = 0
OCCUPIED = 1

def pathfinder(ship, end_position, collision_map):
    """
    Lee Algorithm
    :param ship: the ship to move
    :param end_position: the position to find the path to
    :collision_map: map filled with FREE or OCCUPIED with future movements
    :return: a list with Directions to be followed
    """

    dx = [-1, 0, 1, 0]  # vectori de directie
    dy = [0, 1, 0, -1]

    if all(collision_map[ship.position.directional_offset(curr).x][ship.position.directional_offset(curr).y] == OCCUPIED \
        for curr in [Direction.West, Direction.East, Direction.North, Direction.South]):  # daca toate directiile invecinate sunt ocupate
        return [Direction.Still]

    if end_position == ship.position:   # daca este deja pe pozitia indicata
        return [Direction.Still]

    q = Queue()

    path_matrix = np.full_like(collision_map, 0, dtype = int)                    # matrice Lee
    parents_matrix = np.full_like(collision_map, Position(0, 0), dtype=Position) # matrice reconstrcutie solutie
    q.put_nowait(ship.position)

    while not q.empty():   # Lee
        current = q.get_nowait()
        for direct in range(4):
            next_dir = Position(current.x + dx[direct], current.y + dy[direct], normalize = True) # normalize = sa faca wrap pe margini

            if next_dir == end_position and path_matrix[next_dir.x][next_dir.y] == FREE:          # sfarsit
                path_matrix[next_dir.x][next_dir.y] = path_matrix[current.x][current.y] + 1       # marcheaza pozitia finala
                parents_matrix[next_dir.x][next_dir.y] = current                                  # marcheaza parintele pozitiei finale
                return traceback(end_position, path_matrix, parents_matrix, ship.position, ship)  # reconstrcutie solutie

            if collision_map[next_dir.x][next_dir.y] == FREE and path_matrix[next_dir.x][next_dir.y] == 0\
                and next_dir != ship.position:                                                    # daca nu are obstacol

                path_matrix[next_dir.x][next_dir.y] = path_matrix[current.x][current.y] + 1 # incrementeaza distanta
                parents_matrix[next_dir.x][next_dir.y] = current                            # parintele pt traceback
                q.put_nowait(next_dir)                                                      # adauga in coada

def traceback(end_position, path_matrix, parents_matrix, start_position,ship):
    """
    Tracebacks on Lee path map
    :param end_position: the position where the path was found to
    :param path_matrix: the map filled with step numbers
    :parents_matrix: the map filled with position for traceback
    :return: a list with Directions to be followed
    """

    solution = []
    current = end_position

    while path_matrix[current.x][current.y] != 0:      # reconstructie solutie
        solution.insert(0, current)
        current = parents_matrix[current.x][current.y]

    for sol_index in range(len(solution) - 1, -1, -1): # parcurgem in reverse solutia
        if sol_index == 0:                             # transforma lista de Position in lista de Direction
            solution[sol_index] = (solution[sol_index].x - start_position.x,
                                   solution[sol_index].y - start_position.y)
        else:
            solution[sol_index] = (solution[sol_index].x - solution[sol_index - 1].x,
                                   solution[sol_index].y - solution[sol_index - 1].y)

        # in caz ca se duce prin margini, actualizeaza directiile

        if solution[sol_index][0] < -1:
            solution[sol_index] = (solution[sol_index][0] + constants.WIDTH, solution[sol_index][1])
        if solution[sol_index][0] > 1:
            solution[sol_index] = (solution[sol_index][0] - constants.WIDTH, solution[sol_index][1])

        if solution[sol_index][1] < -1:
            solution[sol_index] = (solution[sol_index][0], solution[sol_index][1] + constants.HEIGHT)
        if solution[sol_index][1] > 1:
            solution[sol_index] = (solution[sol_index][0], solution[sol_index][1] - constants.HEIGHT)

    if len(solution) == 0:
        return [Direction.Still]

    return solution

def is_neighbour(position, end_position):
    """
    Checks whether the two position given are neighbours (distance is 1)
    :param position: starting position
    :param end_position: ending position
    :return: a tuple (True/False, direction_from_start_to_end_if_true/Still)
    """
    for diri in [Direction.North, Direction.South, Direction.East, Direction.West]:
        if position.directional_offset(diri) == end_position:
            return (True, diri)

    return (False, Direction.Still)
