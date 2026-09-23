"""Pure grid model: tile types, costs and neighborhoods.

This module is part of ``core/`` and must never import ``pygame``.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from enum import Enum

from .types import Coord, Cost


class TileType(Enum):
    """Terrain types with variable movement costs."""

    FLOOR = "floor"
    MUD = "mud"
    WATER = "water"
    WALL = "wall"


TILE_COSTS: dict[TileType, Cost] = {
    TileType.FLOOR: 1.0,
    TileType.MUD: 5.0,
    TileType.WATER: 8.0,
    TileType.WALL: math.inf,
}

#: Characters accepted by :meth:`Grid.from_strings`.
TILE_SYMBOLS: dict[str, TileType] = {
    ".": TileType.FLOOR,
    "~": TileType.MUD,
    "w": TileType.WATER,
    "#": TileType.WALL,
}

#: Neighbor offsets in (row, column) deltas, clockwise from north.
_DIRS_4: tuple[Coord, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))
_DIRS_8: tuple[Coord, ...] = (
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
)


class Grid:
    """Rectangular grid of tiles with 4- or 8-direction connectivity.

    The connectivity mode is an attribute of the grid, not of the
    algorithms, so BFS, Dijkstra and A* all behave the same when it
    changes.
    """

    def __init__(self, tiles: list[list[TileType]], connectivity: int = 4) -> None:
        if connectivity not in (4, 8):
            raise ValueError(f"connectivity must be 4 or 8, got {connectivity}")
        if not tiles or any(len(row) != len(tiles[0]) for row in tiles):
            raise ValueError("tiles must be a non-empty rectangle")
        self._tiles: list[list[TileType]] = [list(row) for row in tiles]
        self.height: int = len(tiles)
        self.width: int = len(tiles[0])
        self.connectivity: int = connectivity

    @classmethod
    def from_strings(cls, rows: list[str], connectivity: int = 4) -> Grid:
        """Build a grid from text rows (``.``, ``~``, ``w``, ``#``)."""
        tiles: list[list[TileType]] = []
        for row in rows:
            try:
                tiles.append([TILE_SYMBOLS[ch] for ch in row])
            except KeyError as exc:
                raise ValueError(f"unknown tile symbol: {exc.args[0]!r}") from exc
        return cls(tiles, connectivity)

    def in_bounds(self, c: Coord) -> bool:
        """Return True if ``c`` lies inside the grid."""
        r, col = c
        return 0 <= r < self.height and 0 <= col < self.width

    def tile_at(self, c: Coord) -> TileType:
        """Return the tile type at ``c`` (raises ``IndexError`` outside)."""
        if not self.in_bounds(c):
            raise IndexError(f"coord out of bounds: {c!r}")
        r, col = c
        return self._tiles[r][col]

    def is_walkable(self, c: Coord) -> bool:
        """Return True if ``c`` is inside the grid and not a wall."""
        return self.in_bounds(c) and self.tile_at(c) is not TileType.WALL

    def cost(self, c: Coord) -> Cost:
        """Return the cost of ENTERING cell ``c`` (``inf`` for walls)."""
        return TILE_COSTS[self.tile_at(c)]

    def step_cost(self, a: Coord, b: Coord) -> Cost:
        """Return the cost of moving from ``a`` into adjacent ``b``.

        Diagonal steps multiply the entry cost by ``sqrt(2)``.
        """
        base = self.cost(b)
        if abs(a[0] - b[0]) == 1 and abs(a[1] - b[1]) == 1:
            return base * math.sqrt(2)
        return base

    def neighbors(self, c: Coord) -> Iterator[Coord]:
        """Yield walkable, in-bounds neighbors of ``c`` in fixed order.

        With 8-direction connectivity, a diagonal step is rejected when
        it would cut between two walls, i.e. when both orthogonal cells
        the diagonal passes between are walls.
        """
        dirs = _DIRS_8 if self.connectivity == 8 else _DIRS_4
        r, col = c
        for dr, dc in dirs:
            nxt: Coord = (r + dr, col + dc)
            if not self.is_walkable(nxt):
                continue
            if dr != 0 and dc != 0:
                # Diagonal: both orthogonal cells between are in bounds
                # whenever nxt is, so tile_at is safe here.
                if (
                    self.tile_at((r + dr, col)) is TileType.WALL
                    and self.tile_at((r, col + dc)) is TileType.WALL
                ):
                    continue
            yield nxt
