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

#: Tight sprite boxes per direction (row) and walk frame (column).
#: Measured on the 1024x1024 sheets; captions and labels excluded.
PLAYER_FRAMES: dict[str, list[Rect]] = {
    "down": [(152, 92, 116, 168), (364, 92, 122, 168), (592, 92, 120, 168), (812, 92, 120, 168)],
    "up": [(152, 322, 116, 170), (364, 322, 124, 170), (592, 322, 120, 170), (810, 322, 124, 170)],
    "left": [(152, 566, 176, 166), (372, 566, 178, 166), (596, 566, 106, 166), (766, 566, 160, 166)],
    "right": [(154, 802, 174, 168), (372, 802, 178, 168), (602, 802, 106, 168), (766, 802, 160, 168)],
}

#: Full grid cells; the guard sheet carries no captions inside cells.
GUARD_FRAMES: dict[str, list[Rect]] = {
    "down": _cells(150, 94, 200, 202, 4),
    "up": _cells(150, 310, 200, 196, 4),
    "left": _cells(150, 522, 200, 204, 4),
    "right": _cells(150, 742, 200, 204, 4),
}
# Guard columns share the sheet grid lines: fix exact widths.
GUARD_FRAMES = {
    direction: [
        (150, y, 200, h),
        (362, y, 192, h),
        (566, y, 188, h),
        (766, y, 200, h),
    ]
    for direction, (_, y, _, h) in [
        ("down", GUARD_FRAMES["down"][0]),
        ("up", GUARD_FRAMES["up"][0]),
        ("left", GUARD_FRAMES["left"][0]),
        ("right", GUARD_FRAMES["right"][0]),
    ]
}

#: Objective cells (star, red star, diamond, coin) on the 1107x293 sheet.
TARGET_FRAMES: list[Rect] = [
    (18, 19, 263, 258),
    (294, 19, 263, 258),
    (570, 19, 262, 258),
    (845, 19, 262, 258),
]

#: Terrain textures as (sheet, rect); 2x2 block starting at (352, 48).
TILE_RECTS: dict[str, Rect] = {
    "floor": (352, 48, 352, 336),
    "mud": (704, 48, 352, 336),
    "water": (352, 384, 352, 384),
    "wall": (704, 384, 352, 384),
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
