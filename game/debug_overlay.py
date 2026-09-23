"""Debug overlay: search states and metrics drawn over the map.

Shows visited cells (cold fill), frontier (warm fill), current cell
(border), accumulated costs (corner numbers), parent links (short
lines), the final path (thick line) and a metrics panel. Stateless
drawing functions; the App owns fonts and search progress.
"""

from __future__ import annotations

import pygame

from core.pathfinding.base import SearchState
from core.types import Coord, Cost
from game.camera import Camera

_VISITED = (70, 140, 255, 80)
_FRONTIER = (255, 170, 60, 110)
_CURRENT = (255, 235, 120)
_PATH = (255, 240, 140)
_ARROW = (30, 30, 40)
_COST_INK = (20, 26, 40)
_PANEL_BG = (8, 10, 18, 205)
_PANEL_FG = (235, 240, 250)


def format_cost(cost: Cost) -> str:
    """Compact cost label; infinities stay readable on the panel."""
    if cost == float("inf"):
        return "inf"
    if cost == int(cost):
        return str(int(cost))
    return f"{cost:.1f}"


def _fill(screen: pygame.Surface, camera: Camera, cell: Coord, color: tuple[int, ...]) -> None:
    tile = pygame.Surface((camera.tile_size, camera.tile_size), pygame.SRCALPHA)
    tile.fill(color)
    screen.blit(tile, camera.cell_to_pixel(cell))


def _center(camera: Camera, cell: Coord) -> tuple[int, int]:
    x, y = camera.cell_center(cell)
    return (int(x), int(y))


def draw_search_state(
    screen: pygame.Surface,
    camera: Camera,
    state: SearchState,
    small_font: pygame.font.Font,
) -> None:
    """Draw frontier, visited, costs, parents, current cell and path."""
    for cell in state.visited:
        _fill(screen, camera, cell, _VISITED)
    for cell in state.frontier:
        _fill(screen, camera, cell, _FRONTIER)
    for cell, cost in state.cost_so_far.items():
        if cell in state.visited:
            label = small_font.render(format_cost(cost), True, _COST_INK)
            x, y = camera.cell_to_pixel(cell)
            screen.blit(label, (x + 2, y + 1))
    for cell, parent in state.came_from.items():
        if parent is not None:
            pygame.draw.line(screen, _ARROW, _center(camera, cell), _center(camera, parent), 1)
    if state.current is not None:
        x, y = camera.cell_to_pixel(state.current)
        pygame.draw.rect(
            screen, _CURRENT, (x, y, camera.tile_size, camera.tile_size), 2
        )
    if state.path:
        pygame.draw.lines(
            screen, _PATH, False, [_center(camera, c) for c in state.path], 4
        )


def draw_panel(
    screen: pygame.Surface, font: pygame.font.Font, lines: list[str]
) -> None:
    """Draw a metrics box in the top-left corner."""
    rendered = [font.render(line, True, _PANEL_FG) for line in lines]
    width = max(surface.get_width() for surface in rendered) + 16
    height = sum(surface.get_height() + 2 for surface in rendered) + 12
    box = pygame.Surface((width, height), pygame.SRCALPHA)
    box.fill(_PANEL_BG)
    screen.blit(box, (8, 8))
    y = 14
    for surface in rendered:
        screen.blit(surface, (16, y))
        y += surface.get_height() + 2
