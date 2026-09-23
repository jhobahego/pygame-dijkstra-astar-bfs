"""Start-is-goal case: path is [start] with zero cost."""

from core.grid import Grid
from core.pathfinding import BFS


def test_start_is_goal() -> None:
    grid = Grid.from_strings([".....", ".....", "....."])
    result = BFS().find_path(grid, (1, 2), (1, 2))
    assert result.path == [(1, 2)]
    assert result.total_cost == 0.0
    assert result.nodes_expanded == 0


def test_start_is_goal_steps_finish_at_once() -> None:
    grid = Grid.from_strings([".....", ".....", "....."])
    states = list(BFS().search_steps(grid, (1, 2), (1, 2)))
    assert len(states) == 1
    assert states[0].finished
    assert states[0].path == [(1, 2)]
