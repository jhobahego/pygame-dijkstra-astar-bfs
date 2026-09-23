"""Tests for A*: optimal cost like Dijkstra, fewer or equal expansions."""

import math

from core.grid import Grid
from core.mapfile import load_map
from core.pathfinding import Pathfinder
from core.pathfinding.astar import AStar
from core.pathfinding.dijkstra import Dijkstra
from core.pathfinding.heuristics import euclidean, manhattan, octile, zero

OPEN_5X5 = [
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
]


def optimal_pair(grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> None:
    dijkstra = Dijkstra().find_path(grid, start, goal)
    astar = AStar().find_path(grid, start, goal)
    assert astar.total_cost == dijkstra.total_cost
    assert astar.nodes_expanded <= dijkstra.nodes_expanded


def test_implements_pathfinder_protocol() -> None:
    astar = AStar()
    assert isinstance(astar, Pathfinder)
    assert astar.name == "astar"
    assert astar.heuristic is octile


def test_optimal_cost_open_grid() -> None:
    optimal_pair(Grid.from_strings(OPEN_5X5), (0, 0), (4, 4))


def test_optimal_cost_open_grid_8dir() -> None:
    grid = Grid.from_strings(OPEN_5X5, connectivity=8)
    optimal_pair(grid, (0, 0), (4, 4))
    assert math.isclose(AStar().find_path(grid, (0, 0), (4, 4)).total_cost, 4 * math.sqrt(2))


def test_optimal_cost_mud_detour_with_fewer_expansions() -> None:
    data = load_map("maps/02_mud_detour.txt")
    dijkstra = Dijkstra().find_path(data.grid, data.guards[0], data.player)
    astar = AStar().find_path(data.grid, data.guards[0], data.player)
    assert astar.total_cost == dijkstra.total_cost == 15.0
    assert astar.nodes_expanded < dijkstra.nodes_expanded


def test_optimal_cost_maze() -> None:
    data = load_map("maps/03_maze.txt")
    optimal_pair(data.grid, data.guards[0], data.player)


def test_zero_heuristic_matches_dijkstra() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    dijkstra = Dijkstra().find_path(grid, (0, 0), (4, 4))
    astar = AStar(zero).find_path(grid, (0, 0), (4, 4))
    assert astar.total_cost == dijkstra.total_cost
    assert astar.nodes_expanded == dijkstra.nodes_expanded
    assert astar.path == dijkstra.path


def test_heuristic_values() -> None:
    assert zero((0, 0), (3, 4)) == 0.0
    assert manhattan((0, 0), (3, 4)) == 7.0
    assert math.isclose(octile((0, 0), (3, 4)), 4 + (math.sqrt(2) - 1) * 3)
    assert math.isclose(euclidean((0, 0), (3, 4)), 5.0)


def test_manhattan_overestimates_diagonals() -> None:
    # One diagonal step costs sqrt(2) < 2: manhattan is inadmissible
    # with 8-direction movement and must not be used there.
    assert manhattan((0, 0), (1, 1)) > math.sqrt(2)
    assert math.isclose(octile((0, 0), (1, 1)), math.sqrt(2))
    assert math.isclose(euclidean((0, 0), (1, 1)), math.sqrt(2))


def test_find_path_consumes_search_steps() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    astar = AStar()
    states = list(astar.search_steps(grid, (0, 0), (4, 4)))
    assert states and states[-1].finished
    assert states[-1].path == astar.find_path(grid, (0, 0), (4, 4)).path


def test_no_path_returns_empty() -> None:
    grid = Grid.from_strings(["#####", "#.#.#", "#####"])
    result = AStar().find_path(grid, (1, 1), (1, 3))
    assert result.path == []
    assert result.total_cost == math.inf


def test_start_is_goal() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    result = AStar().find_path(grid, (2, 2), (2, 2))
    assert result.path == [(2, 2)]
    assert result.total_cost == 0.0
    assert result.nodes_expanded == 0
