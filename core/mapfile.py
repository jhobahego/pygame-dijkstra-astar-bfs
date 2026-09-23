"""Map file parser: plain-text ``.txt`` maps become Grid plus spawns.

File layout: optional leading ``key=value`` metadata lines, then the grid::

    name=Rodeo por el barro
    ###############
    #P..~~~~~~~..G#
    #.............#
    ###############

Symbols: ``.`` floor, ``~`` mud, ``w`` water, ``#`` wall, ``P`` player
spawn, ``G`` guard spawn, ``*`` objective. Spawns and objectives sit on
floor tiles. Every validation failure raises :class:`MapError` carrying
the offending 1-based line number.

This module is part of ``core/`` and must never import ``pygame``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .grid import Grid, TileType
from .types import Coord

VALID_SYMBOLS = frozenset(".~w#PG*")

_TERRAIN: dict[str, TileType] = {
    ".": TileType.FLOOR,
    "~": TileType.MUD,
    "w": TileType.WATER,
    "#": TileType.WALL,
}

_METADATA_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class MapError(ValueError):
    """Invalid map file, with the 1-based number of the offending line."""

    def __init__(self, line: int | None, message: str) -> None:
        self.line = line
        prefix = f"línea {line}: " if line is not None else ""
        super().__init__(prefix + message)


@dataclass
class MapData:
    """A parsed map: grid, spawns, goals and metadata."""

    name: str
    grid: Grid
    player: Coord
    guards: list[Coord] = field(default_factory=list)
    goals: list[Coord] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


def parse_map(text: str, default_name: str = "") -> MapData:
    """Parse map ``text`` and return the :class:`MapData`.

    Raises :class:`MapError` with a line number on any invalid input.
    """
    lines = text.splitlines()
    if not lines:
        raise MapError(None, "mapa vacío")

    metadata: dict[str, str] = {}
    grid_start: int | None = None
    for lineno, raw in enumerate(lines, start=1):
        if "=" in raw and grid_start is None:
            key, _, value = raw.partition("=")
            if not _METADATA_KEY.fullmatch(key):
                raise MapError(lineno, f"metadata inválida: {raw!r} (se esperaba clave=valor)")
            metadata[key] = value
        else:
            if grid_start is None:
                grid_start = lineno
    if grid_start is None:
        raise MapError(len(lines), "el mapa no tiene filas de grilla")

    rows = lines[grid_start - 1 :]
    width = len(rows[0])
    if width == 0:
        raise MapError(grid_start, "fila vacía")
    for offset, row in enumerate(rows):
        lineno = grid_start + offset
        if len(row) != width:
            raise MapError(
                lineno,
                f"ancho de fila {len(row)} distinto de {width}",
            )
        for ch in row:
            if ch not in VALID_SYMBOLS:
                raise MapError(lineno, f"símbolo desconocido: {ch!r}")

    height = len(rows)
    for r in range(height):
        for c in range(width):
            if r in (0, height - 1) or c in (0, width - 1):
                if rows[r][c] != "#":
                    raise MapError(
                        grid_start + r,
                        "el perímetro debe estar cerrado con muros '#'",
                    )

    player: Coord | None = None
    guards: list[Coord] = []
    goals: list[Coord] = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "P":
                if player is not None:
                    raise MapError(grid_start + r, "spawn de jugador 'P' duplicado")
                player = (r, c)
            elif ch == "G":
                guards.append((r, c))
            elif ch == "*":
                goals.append((r, c))
    if player is None:
        raise MapError(grid_start, "falta el spawn del jugador 'P'")
    if not goals:
        raise MapError(grid_start, "el mapa no tiene objetivos '*'")

    tiles = [[_TERRAIN.get(ch, TileType.FLOOR) for ch in row] for row in rows]
    return MapData(
        name=metadata.get("name", default_name),
        grid=Grid(tiles),
        player=player,
        guards=guards,
        goals=goals,
        metadata=metadata,
    )


def load_map(path: str | Path) -> MapData:
    """Read a ``.txt`` map file and return the :class:`MapData`."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    return parse_map(text, default_name=path.stem)
