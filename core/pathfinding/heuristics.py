"""Admissible grid heuristics for A*.

All heuristics assume a minimum cell-entry cost of 1 (floor), so they
never overestimate the true cheapest cost and A* stays optimal:

- ``zero``: always 0. A* with ``zero`` behaves exactly like Dijkstra.
- ``manhattan``: ``|dr| + |dc|``. Admissible only with 4-direction
  movement: with diagonals allowed it overestimates (e.g. one diagonal
  step costs ``sqrt(2)`` but ``manhattan`` reports 2), breaking
  optimality. Never use it on 8-direction grids.
- ``octile``: ``max + (sqrt(2) - 1) * min``. Admissible for 8-direction
  movement (and safe, though less informed, for 4-direction).
- ``euclidean``: straight-line distance. Admissible for 8-direction
  movement.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from ..types import Coord, Cost

Heuristic = Callable[[Coord, Coord], Cost]


def zero(_a: Coord, _b: Coord) -> Cost:
    """Zero heuristic: A* degrades to Dijkstra."""
    return 0.0


def manhattan(a: Coord, b: Coord) -> Cost:
    """Manhattan distance. Only admissible with 4-direction movement."""
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))


def octile(a: Coord, b: Coord) -> Cost:
    """Octile distance. The default choice for 8-direction movement."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return float(max(dr, dc) + (math.sqrt(2) - 1) * min(dr, dc))


def euclidean(a: Coord, b: Coord) -> Cost:
    """Straight-line distance. Admissible for 8-direction movement."""
    return float(math.hypot(a[0] - b[0], a[1] - b[1]))
