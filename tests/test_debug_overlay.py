"""Regression: draw_search_state must not crash on single-point paths.

When the guard reaches the player (start == goal) the search state
carries a one-cell path; pygame.draw.lines requires >= 2 points.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from core.grid import Grid
from core.pathfinding.base import SearchState
from core.pathfinding.bfs import BreadthFirstSearch
from game.camera import Camera
from game.debug_overlay import draw_search_state


def _draw(camera_cells: int, state: SearchState, small_font) -> None:
    camera = Camera(tile_size=32, origin_x=0.0, origin_y=0.0)
    size = camera_cells * 32
    screen = pygame.Surface((size, size))
    draw_search_state(screen, camera, state, small_font)


@pytest.fixture(scope="module")
def pygame_font():
    pygame.init()
    pygame.display.set_mode((1, 1))
    font = pygame.font.SysFont("dejavusansmono", 12)
    yield font
    pygame.quit()


def test_single_point_path_does_not_crash(pygame_font) -> None:
    """Repro from TODO: guard on player cell -> path with one point."""
    state = SearchState(
        current=(1, 1),
        frontier=[],
        visited={(1, 1)},
        cost_so_far={(1, 1): 0.0},
        came_from={(1, 1): None},
        finished=True,
        path=[(1, 1)],
    )
    _draw(3, state, pygame_font)


def test_none_path_does_not_crash(pygame_font) -> None:
    """Unreachable goal -> path is None, no line to draw."""
    state = SearchState(
        current=None,
        frontier=[],
        visited={(0, 0)},
        cost_so_far={(0, 0): 0.0},
        came_from={(0, 0): None},
        finished=True,
        path=None,
    )
    _draw(3, state, pygame_font)


def test_empty_path_does_not_crash(pygame_font) -> None:
    """Empty path list -> no line to draw."""
    state = SearchState(
        current=None,
        frontier=[],
        visited={(0, 0)},
        cost_so_far={(0, 0): 0.0},
        came_from={(0, 0): None},
        finished=True,
        path=[],
    )
    _draw(3, state, pygame_font)


def test_multi_point_path_draws_without_error(pygame_font) -> None:
    """Normal case: path with 2+ points draws the route line."""
    grid = Grid.from_strings(["...", "...", "..."])
    states = list(BreadthFirstSearch().search_steps(grid, (0, 0), (0, 2)))
    final = states[-1]
    assert final.finished and final.path is not None and len(final.path) >= 2
    _draw(3, final, pygame_font)


def test_start_is_goal_search_state_regression(pygame_font) -> None:
    """End-to-end repro: real search_steps with start == goal into overlay."""
    grid = Grid.from_strings(["...", "...", "..."])
    states = list(BreadthFirstSearch().search_steps(grid, (1, 1), (1, 1)))
    assert len(states) == 1 and states[0].finished
    assert states[0].path == [(1, 1)]
    _draw(3, states[0], pygame_font)
