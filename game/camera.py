"""Grid <-> pixel conversion. The ONLY place this happens.

``core/`` works in ``(row, column)`` cells and never sees pixels;
everything else converts through :class:`Camera`.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.types import Coord

Pixel = tuple[float, float]


@dataclass
class Camera:
    """Maps grid cells to screen pixels with a fixed origin offset."""

    tile_size: int = 32
    origin_x: float = 0.0
    origin_y: float = 0.0

    @classmethod
    def centered(
        cls, cols: int, rows: int, screen_w: int, screen_h: int, tile_size: int = 32
    ) -> Camera:
        """Build a camera with the grid centered on the screen."""
        return cls(
            tile_size=tile_size,
            origin_x=(screen_w - cols * tile_size) / 2,
            origin_y=(screen_h - rows * tile_size) / 2,
        )

    def cell_to_pixel(self, cell: Coord) -> tuple[int, int]:
        """Top-left pixel of ``cell``."""
        row, col = cell
        return (
            int(self.origin_x + col * self.tile_size),
            int(self.origin_y + row * self.tile_size),
        )

    def cell_center(self, cell: Coord) -> Pixel:
        """Center pixel of ``cell`` (entity anchor point)."""
        row, col = cell
        half = self.tile_size / 2
        return (
            self.origin_x + col * self.tile_size + half,
            self.origin_y + row * self.tile_size + half,
        )
