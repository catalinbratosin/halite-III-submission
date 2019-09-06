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
import pathfinder

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

def is_worth(final_energy, ship, game_map):
    if 0.25 * final_energy - 0.1 * game_map[ship.position].halite_amount > 0.25 * game_map[ship.position].halite_amount: #formiula mariei
        return True
    return False

def find_direction(ship, game_map, possible_directions, must_move):
    max_halite = -1
    final_direction = None
    if possible_directions is None:
        return Direction.Still

    for directi in possible_directions:                                                    # pentru fiecare directie, la care nu s-a gasit coliziune
        if game_map[ship.position.directional_offset(directi)].halite_amount > max_halite: # daca maximul e in celula respectiva
            max_halite =  game_map[ship.position.directional_offset(directi)].halite_amount # atunci face update la maxim
            final_direction = directi                                                       # si la directie

 # daca eroare (None = null)  sau          nu merita sa mearga acolo       sau              nu are energie sa mearga acolo
    if not must_move and\
    (final_direction is None or not is_worth(max_halite, ship, game_map) or (ship.halite_amount < 0.1 * game_map[ship.position].halite_amount)):
        return Direction.Still
    else:
        return final_direction

def check_still_returning(is_returning, ship_index, ship):
    if game.turn_number > constants.MAX_TURNS - 30:
        return "Ending"

    if is_returning[str(ship.id)] == "Returning" and ship.halite_amount > 700:  # daca se intorcea baza si inca are peste 700
        return "Returning"                                                      # atunci se intoarce in continuare
    else:
        if ship.halite_amount > 980:                                            # daca nu se intorcea, dar are peste 980
            return "Returning"                                                  # atunci se incepe sa se intoarca
        else:
            return "Collecting"                                                 # daca nu, colecteaza in continuare

def check_collision(ships, ship_index, game_map, future_direction, direction_queue):
    possible_directions = [Direction.North, Direction.East, Direction.West, Direction.South]

    for ship_f_index, ship_f in enumerate(ships): # iteram prin ships
        if ship_f_index < ship_index:             # pentru ship-urile de dinainte
            if ship_f.position.directional_offset(direction_queue[ship_f_index]) == ships[ship_index].position.directional_offset(future_direction):
               # daca pozitia viitoare a ship-ului curent (ship_index) este aceeasi cu viitoare miscare a unui ship din urma
                if future_direction == Direction.Still: # daca vine alt ship peste pozitia unde vrea sa ramana
                    future_direction = find_direction(ships[ship_index], game_map, possible_directions, True)
                else:
                   #TODO: se sa se duca la urmatorul maxim, nu sa stea pe location
                   future_direction = find_direction(ships[ship_index], game_map, possible_directions.remove(future_direction), direction_queue)

        else:
            break

    return future_direction

def final_move(ships, ship, ship_index, game_map, direction_queue):
    f_dir = find_direction(ship, game_map, [Direction.North, Direction.South, Direction.West, Direction.East, Direction.Still], False)
    move = check_collision(ships, ship_index, game_map, f_dir, direction_queue)

    return move

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
fd = open('errlog.my', 'w')
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
is_returning = dict()
for i in range(100):
    is_returning[str(i)] = "Collecting"

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    direction_queue = []

    if game.turn_number < (400 * 2 / 3) and me.halite_amount >= constants.SHIP_COST and\
        not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    for ship_index, ship in enumerate(me.get_ships()):
        is_returning[str(ship.id)] = check_still_returning(is_returning, ship_index, ship)
        wasHere = False
        if is_returning[str(ship.id)] != "Collecting": # se intoarce
            for diri in  [Direction.North, Direction.East, Direction.West, Direction.South]:
                if ship.position.directional_offset(diri) == me.shipyard.position:
                    wasHere = True
            if wasHere:
                fd.write('was here\n')
                if me.shipyard.spawn() in command_queue: # dar o sa spawnez un ship
                    command_queue.append(ship.stay_still()) #atunci asteapta
                    direction_queue.append(Direction.Still)
                else:
                    move = game_map.get_unsafe_moves(ship.position, me.shipyard.position)

                    if len(move) == 0:
                        move = Direction.Still
                    else:
                        move = move[0]

                    move = check_collision(me.get_ships(), ship_index, game_map, move, direction_queue)
                    command_queue.append(ship.move(move)) # se duce in shipyard

                    direction_queue.append(move)

            else:
                # move = game_map.naive_navigate(ship, me.shipyard.position)
                move = game_map.get_unsafe_moves(ship.position, me.shipyard.position)

                if len(move) == 0:
                    move = Direction.Still
                else:
                    move = move[0]

                move = check_collision(me.get_ships(), ship_index, game_map, move, direction_queue)

                command_queue.append(ship.move(move)) # se apropie de shipyard

                direction_queue.append(move)
        else:
            move = final_move(me.get_ships(), ship, ship_index, game_map, direction_queue)

            command_queue.append(ship.move(move))
            direction_queue.append(move)

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
