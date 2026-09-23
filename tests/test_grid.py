"""Tests for core.types and core.grid: bounds, walls, costs, diagonals."""

import math
from pathlib import Path

import pytest

from core.grid import TILE_COSTS, Grid, TileType

OPEN_3X3 = [
    "...",
    "...",
    "...",
]


def test_no_pygame_import_in_core() -> None:
    for path in (Path("core/types.py"), Path("core/grid.py")):
        assert "import pygame" not in path.read_text()


def test_corner_has_two_neighbors_4dir() -> None:
    grid = Grid.from_strings(OPEN_3X3)
    assert set(grid.neighbors((0, 0))) == {(1, 0), (0, 1)}


def test_all_corners_have_two_neighbors_4dir() -> None:
    grid = Grid.from_strings(OPEN_3X3)
    assert set(grid.neighbors((0, 2))) == {(1, 2), (0, 1)}
    assert set(grid.neighbors((2, 0))) == {(1, 0), (2, 1)}
    assert set(grid.neighbors((2, 2))) == {(1, 2), (2, 1)}


def test_edge_has_three_neighbors_4dir() -> None:
    grid = Grid.from_strings(OPEN_3X3)
    assert set(grid.neighbors((0, 1))) == {(0, 0), (0, 2), (1, 1)}


def test_neighbor_order_is_deterministic() -> None:
    grid = Grid.from_strings(OPEN_3X3)
    assert list(grid.neighbors((1, 1))) == [(0, 1), (2, 1), (1, 0), (1, 2)]


def test_walls_are_excluded_from_neighbors() -> None:
    grid = Grid.from_strings([".#.", "...", "..."])
    assert not grid.is_walkable((0, 1))
    assert set(grid.neighbors((0, 0))) == {(1, 0)}
    assert set(grid.neighbors((1, 1))) == {(2, 1), (1, 0), (1, 2)}


def test_wall_cost_is_infinite() -> None:
    grid = Grid.from_strings(["#"])
    assert grid.cost((0, 0)) == math.inf


def test_variable_terrain_costs() -> None:
    grid = Grid.from_strings([".~w"])
    assert grid.cost((0, 0)) == 1.0
    assert grid.cost((0, 1)) == 5.0
    assert grid.cost((0, 2)) == 8.0
    assert TILE_COSTS[TileType.FLOOR] == 1.0
    assert TILE_COSTS[TileType.MUD] == 5.0
    assert TILE_COSTS[TileType.WATER] == 8.0


def test_no_diagonals_with_4dir_connectivity() -> None:
    grid = Grid.from_strings(OPEN_3X3, connectivity=4)
    assert set(grid.neighbors((1, 1))) == {(0, 1), (2, 1), (1, 0), (1, 2)}


def test_center_has_eight_neighbors_8dir() -> None:
    grid = Grid.from_strings(OPEN_3X3, connectivity=8)
    assert set(grid.neighbors((1, 1))) == {
        (0, 1),
        (0, 2),
        (1, 2),
        (2, 2),
        (2, 1),
        (2, 0),
        (1, 0),
        (0, 0),
    }


def test_corner_has_three_neighbors_8dir() -> None:
    grid = Grid.from_strings(OPEN_3X3, connectivity=8)
    assert set(grid.neighbors((0, 0))) == {(0, 1), (1, 1), (1, 0)}


def test_diagonal_cutting_between_two_walls_is_rejected() -> None:
    grid = Grid.from_strings([".#.", "#..", "..."], connectivity=8)
    # From (1, 1) the diagonal to (0, 0) passes between two walls.
    assert (0, 0) not in set(grid.neighbors((1, 1)))
    # Other diagonals remain available.
    assert (0, 2) in set(grid.neighbors((1, 1)))
    assert (2, 0) in set(grid.neighbors((1, 1)))
    assert (2, 2) in set(grid.neighbors((1, 1)))


def test_diagonal_past_single_wall_is_allowed() -> None:
    grid = Grid.from_strings([".#.", "...", "..."], connectivity=8)
    # Only one of the orthogonal cells is a wall, so the diagonal is kept.
    assert (0, 0) in set(grid.neighbors((1, 1)))


def test_diagonal_step_cost_uses_sqrt2() -> None:
    grid = Grid.from_strings(["..", ".~"], connectivity=8)
    assert grid.step_cost((0, 0), (0, 1)) == 1.0
    assert math.isclose(grid.step_cost((0, 0), (1, 1)), 5.0 * math.sqrt(2))


def test_invalid_connectivity_raises() -> None:
    with pytest.raises(ValueError):
        Grid.from_strings(OPEN_3X3, connectivity=5)


def test_ragged_rows_raise() -> None:
    with pytest.raises(ValueError):
        Grid.from_strings(["...", ".."])


def test_unknown_symbol_raises() -> None:
    with pytest.raises(ValueError):
        Grid.from_strings([".P."])


def test_out_of_bounds_helpers() -> None:
    grid = Grid.from_strings(OPEN_3X3)
    assert not grid.in_bounds((3, 0))
    assert not grid.in_bounds((0, -1))
    assert not grid.is_walkable((3, 3))
    with pytest.raises(IndexError):
        grid.tile_at((9, 9))
