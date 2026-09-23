"""BFS == Dijkstra on uniform costs; Dijkstra wins on mud."""

from core.grid import Grid
from core.mapfile import load_map
from core.pathfinding import BFS
from core.pathfinding.dijkstra import Dijkstra

OPEN_5X5 = [
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
]

UNIFORM_MAZE = [
    "#######",
    "#.....#",
    "#.###.#",
    "#.#...#",
    "#.#.###",
    "#.....#",
    "#######",
]


def test_open_grid_equal_costs() -> None:
    grid = Grid.from_strings(OPEN_5X5)
    for start, goal in [((0, 0), (4, 4)), ((0, 4), (4, 0)), ((2, 2), (0, 0))]:
        bfs = BFS().find_path(grid, start, goal)
        dijkstra = Dijkstra().find_path(grid, start, goal)
        assert dijkstra.total_cost == bfs.total_cost == len(bfs.path) - 1


def test_uniform_maze_equal_costs() -> None:
    grid = Grid.from_strings(UNIFORM_MAZE)
    bfs = BFS().find_path(grid, (1, 1), (5, 5))
    dijkstra = Dijkstra().find_path(grid, (1, 1), (5, 5))
    assert dijkstra.total_cost == bfs.total_cost


def test_tutorial_map_equal_costs() -> None:
    data = load_map("maps/01_tutorial.txt")
    bfs = BFS().find_path(data.grid, data.guards[0], data.player)
    dijkstra = Dijkstra().find_path(data.grid, data.guards[0], data.player)
    assert dijkstra.total_cost == bfs.total_cost


def test_maze_map_equal_costs() -> None:
    data = load_map("maps/03_maze.txt")
    bfs = BFS().find_path(data.grid, data.guards[0], data.player)
    dijkstra = Dijkstra().find_path(data.grid, data.guards[0], data.player)
    assert dijkstra.total_cost == bfs.total_cost


def test_mud_detour_dijkstra_cheaper_with_more_cells() -> None:
    data = load_map("maps/02_mud_detour.txt")
    start, goal = data.guards[0], data.player
    bfs = BFS().find_path(data.grid, start, goal)
    dijkstra = Dijkstra().find_path(data.grid, start, goal)
    assert dijkstra.total_cost < bfs.total_cost
    assert len(dijkstra.path) > len(bfs.path)
