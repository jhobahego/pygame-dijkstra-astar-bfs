"""Keyboard input: arrows/WASD movement intents from key events.

Movement is tracked from ``KEYDOWN``/``KEYUP`` events (reliable keycodes),
not from ``get_pressed`` state polling, whose keycode mapping proved
unreliable for letters on some systems. The most recently pressed held
key wins, so changing direction feels immediate.
"""

from __future__ import annotations

import pygame

from core.types import Coord

_UP: Coord = (-1, 0)
_DOWN: Coord = (1, 0)
_LEFT: Coord = (0, -1)
_RIGHT: Coord = (0, 1)

_KEY_TO_STEP: dict[int, Coord] = {
    pygame.K_UP: _UP,
    pygame.K_w: _UP,
    pygame.K_DOWN: _DOWN,
    pygame.K_s: _DOWN,
    pygame.K_LEFT: _LEFT,
    pygame.K_a: _LEFT,
    pygame.K_RIGHT: _RIGHT,
    pygame.K_d: _RIGHT,
}


class Input:
    """Holds the currently pressed movement keys, most recent last."""

    def __init__(self) -> None:
        self._held: dict[int, None] = {}

    def handle_event(self, event: pygame.event.Event) -> None:
        """Track movement keys; every other event is ignored."""
        if event.type == pygame.KEYDOWN and event.key in _KEY_TO_STEP:
            self._held.pop(event.key, None)
            self._held[event.key] = None
        elif event.type == pygame.KEYUP and event.key in _KEY_TO_STEP:
            self._held.pop(event.key, None)

    def move_direction(self) -> Coord | None:
        """Step of the most recently pressed held key, or None."""
        if not self._held:
            return None
        return _KEY_TO_STEP[next(reversed(self._held))]
