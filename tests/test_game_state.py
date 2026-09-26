"""Game states (PLAYING/WON/LOST) and frozen search path.

Covers TODO "Estados de juego (victoria/derrota) y congelado del camino":
defeat when a guard shares the player's cell, victory when the player
steps on a goal, frozen movement/replanning afterwards, overlay behavior
(LOST keeps the frozen path, WON hides it) and restart. Works with the
overlay on or off.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from game.app import App
from game.state import GameState


@pytest.fixture()
def app():
    pygame.init()
    pygame.display.set_mode((1, 1))
    game = App()
    yield game
    pygame.quit()


def _walkable_neighbor(game: App):
    """A walkable cell adjacent to the player (or the player cell)."""
    grid = game.data.grid
    r, c = game.player.cell
    for step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        dest = (r + step[0], c + step[1])
        if grid.is_walkable(dest):
            return dest, step
    return (r, c), None


def test_initial_state_is_playing(app: App) -> None:
    assert app.state is GameState.PLAYING
    assert not app.state.is_over


def test_defeat_when_guard_shares_player_cell(app: App) -> None:
    guard = app.guards[0]
    guard.cell = app.player.cell
    app._update_state()
    assert app.state is GameState.LOST
    assert app.state.is_over


def test_victory_when_player_on_goal(app: App) -> None:
    goal = app.data.goals[0]
    # Keep a guard away so defeat does not trigger first.
    app.guards[0].cell = app.data.player
    app.player.cell = goal
    # If the goal equals the guard cell the test setup is bad; guard is
    # on the spawn, goals never are, so this holds on shipped maps.
    assert app.player.cell != app.guards[0].cell
    app._update_state()
    assert app.state is GameState.WON


def test_defeat_has_priority_over_victory(app: App) -> None:
    goal = app.data.goals[0]
    app.player.cell = goal
    app.guards[0].cell = goal
    app._update_state()
    assert app.state is GameState.LOST


def test_terminal_states_are_sticky_without_reload(app: App) -> None:
    app.player.cell = app.data.goals[0]
    app._update_state()
    assert app.state is GameState.WON
    # Moving away must not resurrect the game.
    app.player.cell = app.data.player
    app._update_state()
    assert app.state is GameState.WON


def test_frozen_entities_do_not_move_or_replan(app: App) -> None:
    # Force a search so last_state/last_result exist, then lose.
    app.guards[0].replan(app.data.grid, app.player.cell)
    before_state = app.guards[0].last_state
    before_result = app.guards[0].last_result
    app.guards[0].cell = app.player.cell
    app._update_state()
    assert app.state is GameState.LOST

    frozen_player = app.player.cell
    frozen_guard = app.guards[0].cell
    # Even with a movement intent, update must not move or replan.
    dest, _ = _walkable_neighbor(app)
    # Teleport the player elsewhere *logically* to try to force a replan;
    # update() must still ignore it because the game is over. Restore
    # afterwards to keep the frozen positions.
    app.player.cell = dest
    app.update(0.016)
    # The manual teleport above is test setup, not game movement: the
    # point is the guard did not follow nor recompute.
    assert app.guards[0].cell == frozen_guard
    assert app.guards[0].last_state is before_state
    assert app.guards[0].last_result is before_result
    # Restore frozen player cell for consistency.
    app.player.cell = frozen_player


def test_frozen_update_drains_without_replan(app: App) -> None:
    app.guards[0].replan(app.data.grid, app.player.cell)
    before = app.guards[0].last_state
    app.guards[0].cell = app.player.cell
    app._update_state()
    assert app.state is GameState.LOST
    for _ in range(10):
        app.update(0.05)
    assert app.guards[0].last_state is before
    assert app.state is GameState.LOST


def test_switch_algorithm_frozen_after_game_over(app: App) -> None:
    app.guards[0].replan(app.data.grid, app.player.cell)
    before = app.guards[0].last_state
    app.guards[0].cell = app.player.cell
    app._update_state()
    assert app.state is GameState.LOST
    app._switch_algorithm("bfs")
    assert app.algorithm_name == "dijkstra"  # unchanged while frozen
    assert app.guards[0].last_state is before


def test_stepping_blocked_after_game_over(app: App) -> None:
    app.player.cell = app.data.goals[0]
    app._update_state()
    assert app.state is GameState.WON
    app._begin_stepping()
    assert app._steps is None
    assert app._step_state is None
    app._advance_step()  # must not crash nor start anything
    assert app._steps is None


def test_reload_resets_to_playing(app: App) -> None:
    app.player.cell = app.data.goals[0]
    app._update_state()
    assert app.state is GameState.WON
    app._load_map(app.map_path)
    assert app.state is GameState.PLAYING
    assert not app.step_mode


def test_state_works_with_overlay_off(app: App) -> None:
    app.overlay = False
    app.guards[0].cell = app.player.cell
    app._update_state()
    assert app.state is GameState.LOST
    app.update(0.016)
    app.render()  # must not crash with overlay off


def test_lost_keeps_frozen_path_in_overlay(app: App, monkeypatch) -> None:
    import game.app as app_module

    app.overlay = True
    app.guards[0].replan(app.data.grid, app.player.cell)
    frozen = app.guards[0].last_state
    assert frozen is not None
    app.guards[0].cell = app.player.cell
    app._update_state()
    assert app.state is GameState.LOST

    calls = []
    orig = app_module.draw_search_state

    def spy(screen, camera, state, font):
        calls.append(state)
        return orig(screen, camera, state, font)

    monkeypatch.setattr(app_module, "draw_search_state", spy)
    app.render()
    assert calls and calls[0] is frozen


def test_won_hides_search_path_in_overlay(app: App, monkeypatch) -> None:
    import game.app as app_module

    app.overlay = True
    app.guards[0].replan(app.data.grid, app.player.cell)
    assert app.guards[0].last_state is not None
    app.player.cell = app.data.goals[0]
    app._update_state()
    assert app.state is GameState.WON

    calls = []
    monkeypatch.setattr(
        app_module, "draw_search_state", lambda *a, **k: calls.append(a)
    )
    app.render()
    assert calls == []


def test_end_banner_and_panel_do_not_crash(app: App) -> None:
    app.overlay = True
    app.player.cell = app.data.goals[0]
    app._update_state()
    assert any("GANASTE" in line for line in app._panel_lines())
    app.render()
    app._load_map(app.map_path)
    app.overlay = True
    app.guards[0].replan(app.data.grid, app.player.cell)
    app.guards[0].cell = app.player.cell
    app._update_state()
    assert any("PERDISTE" in line for line in app._panel_lines())
    app.render()


def test_single_point_path_renders_when_lost(app: App) -> None:
    """Guard on player -> 1-cell path must not crash the overlay."""
    app.overlay = True
    app.guards[0].cell = app.player.cell
    app.guards[0].replan(app.data.grid, app.player.cell)
    assert app.guards[0].last_state is not None
    assert app.guards[0].last_state.path == [app.player.cell]
    app._update_state()
    assert app.state is GameState.LOST
    app.render()
