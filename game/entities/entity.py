"""Base entity: logical tile cell plus interpolated pixel position.

Pathfinding only ever sees ``cell``; ``pixel`` is the visual center in
screen pixels, interpolated toward the destination during ``update``.
"""

from __future__ import annotations

import math

from core.types import Coord


class Entity:
    """An actor standing on a cell and drawn at an interpolated point."""

    def __init__(self, cell: Coord) -> None:
        self.cell = cell
        self.pixel: tuple[float, float] = (0.0, 0.0)
        self._target: tuple[float, float] = self.pixel
        self._speed = 0.0

    @property
    def is_moving(self) -> bool:
        """True while the visual position chases another cell."""
        return self.pixel != self._target

    def snap_to(self, point: tuple[float, float]) -> None:
        """Place the visual position exactly on ``point``."""
        self.pixel = (float(point[0]), float(point[1]))
        self._target = self.pixel
        self._speed = 0.0

    def move_to(self, cell: Coord, target: tuple[float, float], duration: float) -> None:
        """Start interpolating toward ``cell`` (centered on ``target``)."""
        self.cell = cell
        self._target = (float(target[0]), float(target[1]))
        distance = math.hypot(
            self._target[0] - self.pixel[0], self._target[1] - self.pixel[1]
        )
        if duration <= 0 or distance == 0:
            self.snap_to(self._target)
        else:
            self._speed = distance / duration

    def update(self, dt: float) -> None:
        """Advance the visual position toward its target cell center."""
        if not self.is_moving:
            return
        dx = self._target[0] - self.pixel[0]
        dy = self._target[1] - self.pixel[1]
        remaining = math.hypot(dx, dy)
        step = self._speed * dt
        if step >= remaining:
            self.snap_to(self._target)
        else:
            self.pixel = (
                self.pixel[0] + dx / remaining * step,
                self.pixel[1] + dy / remaining * step,
            )
