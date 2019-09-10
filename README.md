# Halite Bot

This is my submission for the [_Halite AI Programming Challenge_](https://halite.io).  _Halite III_ is a resource management game. The goal is to build a bot that efficiently navigates the seas collecting __halite__, a luminous energy resource. Check the [rulebook](https://2018.halite.io/learn-programming-challenge/game-overview) here.

## The bot

Navigating through the map involves traditional algorithms for searching the best path combined with a unique way of ranking the value of each cell on the map.

**Ships' status**
Each ship has a given status at any turn of the game:
* _Collecting_ - the ship is mining for halite
* _Returning_ -  the ship is full of halite and returns to the shipyard
* _Free_ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  - the ship just returned the halite to the shipyard
*  _Ending_ &nbsp;&nbsp;&nbsp; - in the final turns of the game, all the ships return to the shipyard


**Navigating**
Each cell has a value according to the ship who wants to visit it. The general formula is:

<img src="https://imgur.com/SPjYlBk.png"/>

where:
 - `x` is the cell's position on the grid,
 - `s` is the ship's poisiton on the grid
 - `H(x)` is the amount of halite at the given position
 - `D(s, x)` is the Manhattan distance from the ship to the cell
 - `E(x, r)` is the number of enemy ships in an `r` radius around position `x`
 - `C` is a variable which grows proportional to the enemy's number of ship
 
At each turn of the game, each  ship "books" a cell they want to visit (obviously the one with the highest Γ value). A cell can't be chosen if another ship already has booked it this turn.

_Lee's algorithm_ is applied to find the shortest route from the ship to the cell.  To avoid ships colliding, each other ship's **next** position is considered an obstacle when computing the route to the cell.

To avoid colliding with the enemy, if a friendly ship has more halite stored than the enemy ship, then all the possible next positions an enemy could take are considered obstacles. Otherwise, collision with the enemy is in our favor and the route computes without the taking the enemy into acocunt.
