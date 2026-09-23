"""Tests for Dijkstra: mud detour, total cost, heap discipline."""

import math

from core.grid import Grid
from core.pathfinding import Pathfinder
from core.pathfinding.dijkstra import Dijkstra

MUD_CHOICE = [
    ".....",
    ".~~~.",
    ".....",
]

WATER_CORRIDOR = [
    ".",
    "w",
    ".",
]

OPEN_5X5 = [
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
]


def test_implements_pathfinder_protocol() -> None:
    dijkstra = Dijkstra()
    assert isinstance(dijkstra, Pathfinder)
    assert dijkstra.name == "dijkstra"


def test_avoids_mud_for_cheaper_detour() -> None:
    grid = Grid.from_strings(MUD_CHOICE)
    result = Dijkstra().find_path(grid, (0, 0), (2, 4))
    assert result.total_cost == 6.0
    assert len(result.path) - 1 == 6
    assert all(grid.cost(cell) == 1.0 for cell in result.path)


def test_total_cost_counts_water_entry() -> None:
    grid = Grid.from_strings(WATER_CORRIDOR)
    result = Dijkstra().find_path(grid, (2, 0), (0, 0))
    assert result.total_cost == 9.0
    assert result.path[1] == (1, 0)


def test_diagonal_cost_uses_sqrt2() -> None:
    grid = Grid.from_strings(["..", ".."], connectivity=8)
    result = Dijkstra().find_path(grid, (0, 0), (1, 1))
    assert result.path == [(0, 0), (1, 1)]
    assert math.isclose(result.total_cost, math.sqrt(2))


def test_cost_ties_do_not_raise() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    result = Dijkstra().find_path(grid, (0, 0), (4, 4))
    assert result.total_cost == 8.0


def test_find_path_consumes_search_steps() -> None:
    grid = Grid.from_strings(MUD_CHOICE)
    dijkstra = Dijkstra()
    states = list(dijkstra.search_steps(grid, (0, 0), (2, 4)))
    assert states and states[-1].finished
    assert states[-1].path == dijkstra.find_path(grid, (0, 0), (2, 4)).path


def test_no_path_returns_empty() -> None:
    grid = Grid.from_strings(["#####", "#.#.#", "#####"])
    result = Dijkstra().find_path(grid, (1, 1), (1, 3))
    assert result.path == []
    assert result.total_cost == math.inf
    states = list(Dijkstra().search_steps(grid, (1, 1), (1, 3)))
    assert states[-1].finished and states[-1].path is None


def test_start_is_goal() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    result = Dijkstra().find_path(grid, (2, 2), (2, 2))
    assert result.path == [(2, 2)]
    assert result.total_cost == 0.0
    assert result.nodes_expanded == 0
