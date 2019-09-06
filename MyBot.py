#!/usr/bin/env python3
# Python 3.6
# comment

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
from hlt.positionals import Position

# This library allows you to generate random numbers.
import random
import pathfind as pf
import collision as cl
import numpy as np
import cluster

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

def check_still_returning(return_status, ship):
    """
    :return: (status, position) pair
    """

    if game.turn_number > constants.MAX_TURNS - constants.MAX_TURNS * 0.08:
        return ("Ending", me.shipyard.position)

    if ship.halite_amount == 0 and ship.position == me.shipyard.position and\
        return_status[str(ship.id)][0] == "Returning":
        return ("Free", me.shipyard.position)

    if return_status[str(ship.id)][0] == "Returning" and ship.halite_amount > 700:  # daca se intorcea baza si inca are peste 700
        return return_status[str(ship.id)]                                          # atunci se intoarce in continuare
    else:
        if ship.halite_amount > 980:                                               # daca nu se intorcea, dar are peste 980
            marked_map[return_status[str(ship.id)][1].x][return_status[str(ship.id)][1].y] = cluster.FREE
            return ("Returning", me.shipyard.position)                        # atunci se incepe sa se intoarca
        else:
            return return_status[str(ship.id)]                                      # daca nu, colecteaza in continuare


""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
fd = open('errlog.my', 'w')
fe = open('other.my', 'w')
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.

TOTAL_HALITE = 0

for i in range(0, constants.HEIGHT):    #  se calculculeaza energy-ul total
    for j in range(0, constants.WIDTH):
        TOTAL_HALITE += game.game_map[Position(i,j)].halite_amount

game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
return_status = dict()
for i in range(500):
    return_status[str(i)] = ("Free", Position(0,0))

marked_map = np.zeros([constants.HEIGHT, constants.WIDTH]) # map pentru reservarea celulelor pentru ship-uri

while True:
    game.update_frame()

    me = game.me
    game_map = game.game_map
    game_status = "Collecting"

    CURRENT_HALITE = 0

    for i in range(0, constants.HEIGHT):        # se calculeaza energy-ul ramas pe harta
        for j in range(0, constants.WIDTH):
            CURRENT_HALITE += game.game_map[Position(i,j)].halite_amount

    command_queue   = []                                              # lista finala pentru miscari
    direction_queue = []                                              # lista cu directiile finale
    collision_map   = np.zeros([constants.HEIGHT, constants.WIDTH])   # map cu obstacolele pentru Lee

    return_status = cl.free_ships_collided(me.get_ships(), return_status, marked_map)

    for ship in reversed(me.get_ships()):                                        # parcurge ship-urile in ordinea crescatoare a indecsilor
        return_status[str(ship.id)] = check_still_returning(return_status, ship) # update ship status
        status = return_status[str(ship.id)]

        if status[0] == 'Collecting':
            if game_map[status[1]].halite_amount <= 30 and ship.position == status[1]:  # elibereaza ship-ul daca nu mai merita sa ramana
                return_status[str(ship.id)] = ('Free', me.shipyard.position)            # pe celula spre care a fost directionat
                status = return_status[str(ship.id)] = ('Free', me.shipyard.position)
            else:
                if ship.halite_amount < game_map[ship.position].halite_amount / 10 or ship.position == status[1]: # daca nu are ergie sa se miste
                    move = Direction.Still                                                                        # sau a ajuns pe celula respectiva
                else:
                    move = pf.pathfinder(ship, status[1], collision_map)[0]                                       # se misca catre target

                collision_map[ship.position.directional_offset(move).x][ship.position.directional_offset(move).y] = pf.OCCUPIED # ocupa celula viitoare
                marked_map[status[1].x][status[1].y] = cluster.RESERVED                                                         # reserva celula target

                direction_queue.insert(0, move) # insereaza miscarea finala

        if return_status[str(ship.id)][0] == 'Free':
            return_status[str(ship.id)] = ('Collecting', cluster.find_best_cell(ship,marked_map, game_map))                  # gaseste cea mai buna celula
            move = pf.pathfinder(ship, return_status[str(ship.id)][1], collision_map)[0]                                     # gaseste directia catrea celula
            collision_map[ship.position.directional_offset(move).x][ship.position.directional_offset(move).y] = pf.OCCUPIED  # ocupa celula viitoare
            marked_map[return_status[str(ship.id)][1].x][return_status[str(ship.id)][1].y] = cluster.RESERVED                # rezerva celula target

            direction_queue.insert(0, move) # insereaza miscarea finala
            continue

        if status[0] == 'Returning':
            move = pf.pathfinder(ship, status[1], collision_map)    # gaseste directia catre baza
            if move is None:                                        # eroare
                move = Direction.Still                              # atunci sta
            else:
                move = move[0]
            collision_map[ship.position.directional_offset(move).x][ship.position.directional_offset(move).y] = pf.OCCUPIED # ocupa celula viitoare
            direction_queue.insert(0, move) # insereaza miscarea finala
            continue

        if status[0] == 'Ending':
            game_status = 'Ending'

            if pf.is_neighbour(ship.position, me.shipyard.position)[0]:                             # daca este langa baza
                direction_queue.insert(0, pf.is_neighbour(ship.position, me.shipyard.position)[1])  # atunci intra in baza
            elif ship.position == me.shipyard.position:                                             # daca este deja in baza
                direction_queue.insert(0, Direction.Still)                                          # sta acolo
            else:
                move = pf.pathfinder(ship, status[1], collision_map)                                # daca nu este langa baza se deplaseaza acolo
                if move is None:                                                                    # eroare
                    move = Direction.Still                                                          # atunci sta
                else:
                    move = move[0]
                collision_map[ship.position.directional_offset(move).x][ship.position.directional_offset(move).y] = pf.OCCUPIED # ocupa celula viitoare
                direction_queue.insert(0, move) # insereaza miscarea finala

    if  game_status != 'Ending':                                                 # daca nu se termina jocul
        direction_queue = cl.resolve_conflicts(direction_queue, me.get_ships())  # rezolva conflictele

    # Send your moves back to the game environment, ending this turn.
    for dir_m in range(len(direction_queue)):                                    # adauga miscarile in lista finala
        command_queue.append(me.get_ships()[dir_m].move(direction_queue[dir_m]))


    # const down == ships up
    if CURRENT_HALITE > 0.8 * TOTAL_HALITE and me.halite_amount >= constants.SHIP_COST and\
        not game_map[me.shipyard].is_occupied and\
        collision_map[me.shipyard.position.x][me.shipyard.position.y] == cluster.FREE: # conditie spawn ship
            command_queue.append(me.shipyard.spawn())


    game.end_turn(command_queue)                                                 # termina tura
