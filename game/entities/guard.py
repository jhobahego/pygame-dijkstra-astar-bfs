"""Guard: chases the player with an injected Pathfinder (any of them).

The guard only knows the :class:`Pathfinder` protocol, never a concrete
algorithm. It replans exclusively when the player's cell changes, keeps
the last result (and final search state, for the overlay) and walks the
route one tile at a time with the same interpolation as the player.
"""

from __future__ import annotations

import math

from core.grid import Grid
from core.pathfinding.base import Pathfinder, SearchResult, SearchState
from core.types import Coord
from game.camera import Camera
from game.config import FRAME_DURATION, MOVE_DURATION
from game.entities.entity import Entity
from game.entities.player import DIRECTION_BY_STEP


class Guard(Entity):
    """Pursuer driven by an interchangeable search algorithm."""

    def __init__(self, cell: Coord, pathfinder: Pathfinder) -> None:
        super().__init__(cell)
        self.pathfinder = pathfinder
        self.last_result: SearchResult | None = None
        self.last_state: SearchState | None = None
        self._route: list[Coord] = []
        self._tracked_player: Coord | None = None
        self.direction = "down"
        self.frame = 0
        self._anim = 0.0

    def set_pathfinder(self, pathfinder: Pathfinder) -> None:
        """Swap the algorithm; forces a replan on the next update."""
        self.pathfinder = pathfinder
        self._tracked_player = None

    def replan(self, grid: Grid, player_cell: Coord) -> None:
        """Run a full search now; store result, final state and route.

        Consumes ``search_steps`` instead of ``find_path`` so the overlay
        can draw the explored region; the numbers match ``find_path``.
        """
        expanded = 0
        final: SearchState | None = None
        for state in self.pathfinder.search_steps(grid, self.cell, player_cell):
            if not state.finished:
                expanded += 1
            final = state
        assert final is not None and final.finished
        self.last_state = final
        if final.path is None:
            self.last_result = SearchResult(
                path=[],
                nodes_expanded=expanded,
                total_cost=math.inf,
                cost_so_far=final.cost_so_far,
            )
            self._route = []
        else:
            goal = final.path[-1]
            self.last_result = SearchResult(
                path=final.path,
                nodes_expanded=expanded,
                total_cost=final.cost_so_far[goal],
                cost_so_far=final.cost_so_far,
            )
            self._route = list(final.path[1:])
        self._tracked_player = player_cell

    def update_guard(
        self, dt: float, grid: Grid, player_cell: Coord, camera: Camera
    ) -> None:
        """Replan on player-cell change; walk the route; animate."""
        if player_cell != self._tracked_player:
            self.replan(grid, player_cell)
        if not self.is_moving and self._route:
            nxt = self._route.pop(0)
            delta: Coord = (nxt[0] - self.cell[0], nxt[1] - self.cell[1])
            self.direction = DIRECTION_BY_STEP.get(delta, self.direction)
            self.move_to(nxt, camera.cell_center(nxt), MOVE_DURATION)
        super().update(dt)
        if self.is_moving:
            self._anim += dt
            self.frame = int(self._anim / FRAME_DURATION) % 4
        else:
            self._anim = 0.0
            self.frame = 0
