"""Tests for BFS: shortest steps on a hand-computed 5x5 grid."""

import math

from core.grid import Grid
from core.pathfinding import BFS, BreadthFirstSearch, Pathfinder

OPEN_5X5 = [
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
]

WALL_COLUMN = [
    ".....",
    ".###.",
    ".....",
]

MUD_BAND = [
    ".....",
    "~~~~~",
    ".....",
    ".....",
    ".....",
]


def steps_are_valid(grid: Grid, path: list[tuple[int, int]]) -> bool:
    for cell in path:
        if not grid.is_walkable(cell):
            return False
    return all(b in set(grid.neighbors(a)) for a, b in zip(path, path[1:]))


def test_implements_pathfinder_protocol() -> None:
    bfs = BreadthFirstSearch()
    assert isinstance(bfs, Pathfinder)
    assert bfs.name == "bfs"


def test_open_grid_takes_manhattan_steps() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    result = BFS().find_path(grid, (0, 0), (4, 4))
    assert len(result.path) - 1 == 8
    assert result.total_cost == 8.0
    assert steps_are_valid(grid, result.path)
    assert result.nodes_expanded > 0
    assert result.cost_so_far[(4, 4)] == 8


def test_detours_around_wall() -> None:
    grid = Grid.from_strings(WALL_COLUMN)
    result = BFS().find_path(grid, (0, 0), (2, 4))
    assert len(result.path) - 1 == 6
    assert steps_are_valid(grid, result.path)


def test_ignores_costs_and_crosses_mud() -> None:
    grid = Grid.from_strings(MUD_BAND)
    result = BFS().find_path(grid, (0, 0), (4, 4))
    assert len(result.path) - 1 == 8
    assert any(grid.cost(cell) == 5.0 for cell in result.path)


def test_find_path_consumes_search_steps() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    bfs = BFS()
    states = list(bfs.search_steps(grid, (0, 0), (4, 4)))
    assert states
    assert not states[0].finished
    assert states[-1].finished
    assert states[-1].path == bfs.find_path(grid, (0, 0), (4, 4)).path
    assert all(isinstance(n, tuple) for n in states[-1].frontier)


def test_states_are_independent_snapshots() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    states = list(BFS().search_steps(grid, (0, 0), (4, 4)))
    assert states[0].visited != states[-1].visited
    assert states[0].visited is not states[-1].visited


def test_unwalkable_start_or_goal_has_no_path() -> None:
    grid = Grid.from_strings(["#.", ".."])
    assert BFS().find_path(grid, (0, 0), (1, 1)).path == []
    assert BFS().find_path(grid, (1, 1), (0, 0)).path == []
    assert BFS().find_path(grid, (0, 0), (0, 0)).total_cost == math.inf
