"""Player: grid-walking entity with directional walk animation."""

from __future__ import annotations

from core.grid import Grid
from core.types import Coord
from game.camera import Camera
from game.config import FRAME_DURATION, MOVE_DURATION
from game.entities.entity import Entity

DIRECTION_BY_STEP: dict[Coord, str] = {
    (-1, 0): "up",
    (1, 0): "down",
    (0, -1): "left",
    (0, 1): "right",
}


class Player(Entity):
    """Tile-to-tile walker; never enters walls."""

    def __init__(self, cell: Coord) -> None:
        super().__init__(cell)
        self.direction = "down"
        self.frame = 0
        self._anim = 0.0

    def request_move(self, step: Coord, grid: Grid, camera: Camera) -> bool:
        """Step to the neighboring cell unless moving or blocked."""
        if self.is_moving:
            return False
        dest: Coord = (self.cell[0] + step[0], self.cell[1] + step[1])
        if not grid.is_walkable(dest):
            return False
        self.direction = DIRECTION_BY_STEP[step]
        self.move_to(dest, camera.cell_center(dest), MOVE_DURATION)
        return True

    def update(self, dt: float) -> None:
        """Interpolate position and cycle walk frames while moving."""
        super().update(dt)
        if self.is_moving:
            self._anim += dt
            self.frame = int(self._anim / FRAME_DURATION) % 4
        else:
            self._anim = 0.0
            self.frame = 0
