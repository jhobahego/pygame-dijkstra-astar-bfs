"""No-path case: a goal walled off returns an empty path, no hang."""

import math

from core.grid import Grid
from core.pathfinding import BFS


def test_walled_off_goal_returns_empty_path() -> None:
    grid = Grid.from_strings(["#####", "#.#.#", "#####"])
    result = BFS().find_path(grid, (1, 1), (1, 3))
    assert result.path == []
    assert result.total_cost == math.inf


def test_no_path_steps_end_finished_without_path() -> None:
    grid = Grid.from_strings(["#####", "#.#.#", "#####"])
    states = list(BFS().search_steps(grid, (1, 1), (1, 3)))
    assert states
    assert states[-1].finished
    assert states[-1].path is None
    assert states[-1].frontier == []
