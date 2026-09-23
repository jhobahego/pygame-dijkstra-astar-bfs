"""Game loop: guards chase the player; overlay inspects the search."""

from __future__ import annotations

from collections.abc import Iterator

import pygame

from core.mapfile import load_map
from core.pathfinding.astar import AStar
from core.pathfinding.base import Pathfinder, SearchState
from core.pathfinding.bfs import BreadthFirstSearch
from core.pathfinding.dijkstra import Dijkstra
from game.assets import AssetLoader
from game.camera import Camera
from game.config import (
    BACKGROUND,
    DEFAULT_MAP,
    FPS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from game.debug_overlay import draw_panel, draw_search_state, format_cost
from game.entities.guard import Guard
from game.entities.player import Player
from game.input import Input
from game.renderer import Renderer

MAP_FILES = (
    "maps/01_tutorial.txt",
    "maps/02_mud_detour.txt",
    "maps/03_maze.txt",
)

_ALGORITHM_KEYS = {
    pygame.K_1: "bfs",
    pygame.K_2: "dijkstra",
    pygame.K_3: "astar",
}


class App:
    """Owns window, map, actors and the search inspector.

    TAB toggles the overlay, ENTER freezes into step mode, SPACE advances
    one search iteration, 1/2/3 swap the algorithm without reloading the
    map, R restarts the map and M cycles maps. ESC or close quits.
    """

    def __init__(self, map_path: str = DEFAULT_MAP) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.loader = AssetLoader("assets")
        self.algorithms: dict[str, Pathfinder] = {
            "bfs": BreadthFirstSearch(),
            "dijkstra": Dijkstra(),
            "astar": AStar(),
        }
        self.algorithm_name = "dijkstra"
        self.map_index = MAP_FILES.index(map_path) if map_path in MAP_FILES else 0
        self.small_font = pygame.font.SysFont("dejavusansmono", 12)
        self.panel_font = pygame.font.SysFont("dejavusansmono", 15)
        self.input = Input()
        self.overlay = False
        self.step_mode = False
        self._steps: Iterator[SearchState] | None = None
        self._step_state: SearchState | None = None
        self._step_expanded = 0
        self.running = True
        self._load_map(MAP_FILES[self.map_index])

    @property
    def active(self) -> Pathfinder:
        """The currently selected search algorithm."""
        return self.algorithms[self.algorithm_name]

    def _load_map(self, map_path: str) -> None:
        """Load a map and reset actors; keep algorithm and overlay flag."""
        self.map_path = map_path
        self.data = load_map(map_path)
        grid = self.data.grid
        self.camera = Camera.centered(
            grid.width, grid.height, WINDOW_WIDTH, WINDOW_HEIGHT
        )
        self.renderer = Renderer(self.screen, self.loader, self.camera)
        self.player = Player(self.data.player)
        self.player.snap_to(self.camera.cell_center(self.data.player))
        self.guards = [Guard(cell, self.active) for cell in self.data.guards]
        for guard, cell in zip(self.guards, self.data.guards):
            guard.snap_to(self.camera.cell_center(cell))
        self._exit_step_mode()

    def _begin_stepping(self) -> None:
        """Freeze a fresh guard-to-player search for SPACE stepping."""
        if self.guards:
            guard = self.guards[0]
            self._steps = self.active.search_steps(
                self.data.grid, guard.cell, self.player.cell
            )
        else:
            self._steps = None
        self._step_state = None
        self._step_expanded = 0

    def _exit_step_mode(self) -> None:
        """Leave step mode and drop the stepping iterator."""
        self.step_mode = False
        self._steps = None
        self._step_state = None
        self._step_expanded = 0

    def _advance_step(self) -> None:
        """Advance the frozen search by exactly one iteration."""
        if self._steps is None:
            return
        try:
            state = next(self._steps)
        except StopIteration:
            return
        self._step_state = state
        if state.finished:
            if self.guards:
                self.guards[0].replan(self.data.grid, self.player.cell)
        else:
            self._step_expanded += 1

    def _switch_algorithm(self, name: str) -> None:
        """Swap every guard to another algorithm without reloading."""
        if name == self.algorithm_name:
            return
        self.algorithm_name = name
        for guard in self.guards:
            guard.set_pathfinder(self.active)
        if self.step_mode:
            self._begin_stepping()

    def handle_events(self) -> None:
        """Dispatch window, inspector and movement keys."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                self.overlay = not self.overlay
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.step_mode:
                    self._exit_step_mode()
                else:
                    self.step_mode = True
                    self._begin_stepping()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.step_mode:
                    self._advance_step()
            elif event.type == pygame.KEYDOWN and event.key in _ALGORITHM_KEYS:
                self._switch_algorithm(_ALGORITHM_KEYS[event.key])
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self._load_map(self.map_path)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.map_index = (self.map_index + 1) % len(MAP_FILES)
                self._load_map(MAP_FILES[self.map_index])
            else:
                self.input.handle_event(event)

    def update(self, dt: float) -> None:
        """Advance player and guards; frozen while stepping the search."""
        if self.step_mode:
            return
        step = self.input.move_direction()
        if step is not None:
            self.player.request_move(step, self.data.grid, self.camera)
        self.player.update(dt)
        for guard in self.guards:
            guard.update_guard(dt, self.data.grid, self.player.cell, self.camera)

    def _panel_lines(self) -> list[str]:
        """Metrics for the overlay panel, from live or finished search."""
        head = [
            f"algo: {self.algorithm_name}",
            "TAB overlay | ENTER step | 1/2/3 algo | R retry | M map",
        ]
        if self.step_mode:
            state = self._step_state
            if state is None:
                return head + ["SPACE: avanzar una iteracion"]
            if state.finished and state.path is not None:
                cost = format_cost(state.cost_so_far[state.path[-1]])
                length: int | str = len(state.path)
            else:
                current_cost = (
                    state.cost_so_far[state.current]
                    if state.current in state.cost_so_far
                    else None
                )
                cost = format_cost(current_cost) if current_cost is not None else "-"
                length = "..."
            return head + [
                f"step: expanded {self._step_expanded}",
                f"cost: {cost} | len: {length}",
            ]
        if not self.guards or self.guards[0].last_result is None:
            return head + ["sin busqueda todavia"]
        result = self.guards[0].last_result
        assert result is not None
        return head + [
            f"expanded: {result.nodes_expanded}",
            f"cost: {format_cost(result.total_cost)} | len: {len(result.path)}",
        ]

    def render(self) -> None:
        """Draw world, search overlay, actors and panel."""
        self.screen.fill(BACKGROUND)
        self.renderer.draw_map(self.data)
        if self.overlay:
            state = self._step_state if self.step_mode else None
            if state is None and self.guards:
                state = self.guards[0].last_state
            if state is not None:
                draw_search_state(
                    self.screen, self.camera, state, self.small_font
                )
        for guard in self.guards:
            self.renderer.draw_guard(guard)
        self.renderer.draw_player(self.player)
        if self.overlay:
            draw_panel(self.screen, self.panel_font, self._panel_lines())
        pygame.display.flip()

    def run(self) -> None:
        """Main loop until ESC or window close."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()
