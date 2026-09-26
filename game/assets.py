"""AssetLoader: loads the bundled spritesheets once and slices 32x32 tiles.

All art lives in ``assets/`` and is never generated nor downloaded.
Sheets are loaded a single time at startup, cropped to the regions
documented in ``assets/README.md`` and cached. Nothing here may run
inside the game loop: callers reuse the cached surfaces.
"""

from __future__ import annotations

from pathlib import Path

import pygame

TILE_SIZE = 32

DIRECTIONS: tuple[str, ...] = ("down", "up", "left", "right")

#: Base keys served by :meth:`AssetLoader.get`.
BASE_KEYS: tuple[str, ...] = (
    "player",
    "guard",
    "target",
    "floor",
    "mud",
    "water",
    "wall",
)

Rect = tuple[int, int, int, int]  # (x, y, w, h) in sheet pixels


def _cells(x0: int, y0: int, w: int, h: int, n: int) -> list[Rect]:
    """Build ``n`` horizontal cell rects starting at ``(x0, y0)``."""
    return [(x0 + i * w, y0, w, h) for i in range(n)]


_PLAYER_SHEET = "sprites/player-spritesheet.jpeg"
_GUARD_SHEET = "sprites/guard-spritesheet.jpeg"
_TARGET_SHEET = "sprites/objective-sprites.png"
_TILES_SHEET = "tiles/spritesheet-tileset.jpeg"

#: Uniform 4x4 grids on the 500x500 removebg sheets (125 px cells, real
#: alpha). Rows are down / up / left / right from top to bottom.
PLAYER_FRAMES: dict[str, list[Rect]] = {
    direction: _cells(0, 125 * row, 125, 125, 4)
    for row, direction in enumerate(DIRECTIONS)
}

#: Same 4x4 grid layout as the player sheet.
GUARD_FRAMES: dict[str, list[Rect]] = {
    direction: _cells(0, 125 * row, 125, 125, 4)
    for row, direction in enumerate(DIRECTIONS)
}

#: Objective cells (star, red star, diamond, coin) on the 1000x250 sheet.
TARGET_FRAMES: list[Rect] = [
    (0, 0, 250, 250),
    (250, 0, 250, 250),
    (500, 0, 250, 250),
    (750, 0, 250, 250),
]

#: Terrain textures as (sheet, rect); 2x2 quadrants of 512 px.
TILE_RECTS: dict[str, Rect] = {
    "floor": (0, 0, 512, 512),
    "mud": (512, 0, 512, 512),
    "water": (0, 512, 512, 512),
    "wall": (512, 512, 512, 512),
}


class AssetLoader:
    """Loads ``assets/`` spritesheets once and serves cached surfaces."""

    def __init__(self, assets_dir: str | Path = "assets") -> None:
        self.assets_dir = Path(assets_dir)
        self._sheets: dict[str, pygame.Surface] = {}
        self._cache: dict[tuple[str, ...], pygame.Surface] = {}
        self.load_calls = 0

    def _sheet(self, filename: str) -> pygame.Surface:
        """Load a sheet on first use; return the cached surface after."""
        cached = self._sheets.get(filename)
        if cached is None:
            path = self.assets_dir / filename
            if not path.is_file():
                raise FileNotFoundError(f"missing spritesheet: {path}")
            cached = pygame.image.load(path).convert_alpha()
            self._sheets[filename] = cached
            self.load_calls += 1
        return cached

    def _slice(self, filename: str, rect: Rect) -> pygame.Surface:
        """Crop ``rect`` and fit it into a ``TILE_SIZE`` square.

        Aspect ratio is preserved: the art is scaled to fit and centered
        on a transparent tile. Nearest-neighbor scaling keeps pixels flat.
        """
        x, y, w, h = rect
        crop = self._sheet(filename).subsurface((x, y, w, h))
        scale = TILE_SIZE / max(w, h)
        fitted = pygame.transform.scale(crop, (max(1, round(w * scale)), max(1, round(h * scale))))
        tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        tile.blit(fitted, fitted.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2)))
        return tile

    def get(self, name: str) -> pygame.Surface:
        """Return the cached 32x32 surface for a base key (see ``BASE_KEYS``)."""
        cached = self._cache.get((name,))
        if cached is None:
            if name == "player":
                cached = self._slice(_PLAYER_SHEET, PLAYER_FRAMES["down"][0])
            elif name == "guard":
                cached = self._slice(_GUARD_SHEET, GUARD_FRAMES["down"][0])
            elif name == "target":
                cached = self._slice(_TARGET_SHEET, TARGET_FRAMES[0])
            elif name in TILE_RECTS:
                cached = self._slice(_TILES_SHEET, TILE_RECTS[name])
            else:
                raise KeyError(f"unknown asset: {name!r}")
            self._cache[(name,)] = cached
        return cached

    def frame(self, who: str, direction: str, index: int) -> pygame.Surface:
        """Return a cached 32x32 walk frame for ``player`` or ``guard``."""
        frames = PLAYER_FRAMES if who == "player" else GUARD_FRAMES if who == "guard" else None
        if frames is None:
            raise KeyError(f"unknown animated asset: {who!r}")
        if direction not in frames:
            raise KeyError(f"unknown direction: {direction!r}")
        if not 0 <= index < len(frames[direction]):
            raise IndexError(f"frame index out of range: {index}")
        key = (who, direction, str(index))
        cached = self._cache.get(key)
        if cached is None:
            sheet = _PLAYER_SHEET if who == "player" else _GUARD_SHEET
            cached = self._slice(sheet, frames[direction][index])
            self._cache[key] = cached
        return cached

    def target_frame(self, index: int) -> pygame.Surface:
        """Return a cached 32x32 objective frame (star, red star, diamond, coin)."""
        if not 0 <= index < len(TARGET_FRAMES):
            raise IndexError(f"target frame index out of range: {index}")
        key = ("target", str(index))
        cached = self._cache.get(key)
        if cached is None:
            cached = self._slice(_TARGET_SHEET, TARGET_FRAMES[index])
            self._cache[key] = cached
        return cached
