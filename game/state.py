"""Game states: playing, won and lost.

``PLAYING`` is the only state where actors move and searches are
(re)computed. ``WON`` (player stepped on a goal) and ``LOST`` (a guard
shares the player's cell) freeze movement and replanning so the path
stays frozen. The states work with the debug overlay on or off; only
the drawing of the search path depends on the overlay.

This module lives in ``game/`` and never touches ``core/`` logic.
"""

from __future__ import annotations

from enum import Enum


class GameState(Enum):
    """High-level App state machine."""

    PLAYING = "playing"
    WON = "won"
    LOST = "lost"

    @property
    def is_over(self) -> bool:
        """True for terminal states (no more movement or replanning)."""
        return self is not GameState.PLAYING
