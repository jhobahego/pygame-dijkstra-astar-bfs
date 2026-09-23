"""Renderer: draws tiles, goals, guards and the player from cached art."""

from __future__ import annotations

import pygame

from core.grid import Grid, TileType
from core.mapfile import MapData
from core.types import Coord
from game.assets import AssetLoader
from game.camera import Camera
from game.entities.guard import Guard
from game.entities.player import Player

_TILE_ASSETS: dict[TileType, str] = {
    TileType.FLOOR: "floor",
    TileType.MUD: "mud",
    TileType.WATER: "water",
    TileType.WALL: "wall",
}


class Renderer:
    """Blits loader surfaces; holds no game state."""

    def __init__(
        self, screen: pygame.Surface, loader: AssetLoader, camera: Camera
    ) -> None:
        self.screen = screen
        self.loader = loader
        self.camera = camera

    def draw_tile(self, cell: Coord, grid: Grid) -> None:
        """Draw one terrain tile at its grid position."""
        self.screen.blit(
            self.loader.get(_TILE_ASSETS[grid.tile_at(cell)]),
            self.camera.cell_to_pixel(cell),
        )

    def draw_map(self, data: MapData) -> None:
        """Draw terrain and objectives (guards are moving entities)."""
        grid = data.grid
        for row in range(grid.height):
            for col in range(grid.width):
                self.draw_tile((row, col), grid)
        for goal in data.goals:
            self.screen.blit(
                self.loader.target_frame(0), self.camera.cell_to_pixel(goal)
            )

    def draw_guard(self, guard: Guard) -> None:
        """Draw the guard frame centered on its interpolated position."""
        surface = self.loader.frame("guard", guard.direction, guard.frame)
        self.screen.blit(
            surface,
            surface.get_rect(center=(int(guard.pixel[0]), int(guard.pixel[1]))),
        )

    def draw_player(self, player: Player) -> None:
        """Draw the player frame centered on its interpolated position."""
        surface = self.loader.frame("player", player.direction, player.frame)
        self.screen.blit(
            surface,
            surface.get_rect(center=(int(player.pixel[0]), int(player.pixel[1]))),
        )
