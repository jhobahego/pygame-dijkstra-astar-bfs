"""Dijkstra: cheapest path over variable terrain costs.

Heap entries are ``(priority, counter, coord)``: the incremental counter
keeps Python from comparing coordinates on cost ties. There is no
``decrease-key``: stale heap entries are skipped on pop (*lazy deletion*).
The goal cuts on extraction, never on insertion. Diagonal steps cost the
entry cost times ``sqrt(2)`` via :meth:`Grid.step_cost`.
"""

from __future__ import annotations

import heapq
import itertools
import math
from collections.abc import Iterator

from ..grid import Grid
from ..types import Coord, Cost
from .base import Pathfinder, SearchResult, SearchState, reconstruct_path


class Dijkstra(Pathfinder):
    """Cheapest-cost search; blind to steps, loyal to terrain."""

    name: str = "dijkstra"

    def search_steps(self, grid: Grid, start: Coord, goal: Coord) -> Iterator[SearchState]:
        if not grid.is_walkable(start) or not grid.is_walkable(goal):
            yield SearchState(
                current=None,
                frontier=[],
                visited=set(),
                cost_so_far={},
                came_from={},
                finished=True,
                path=None,
            )
            return
        dist: dict[Coord, Cost] = {start: 0.0}
        came_from: dict[Coord, Coord | None] = {start: None}
        seen: set[Coord] = {start}
        counter = itertools.count()
        heap: list[tuple[Cost, int, Coord]] = [(0.0, next(counter), start)]
        while heap:
            cost, _, current = heapq.heappop(heap)
            if cost > dist[current]:
                continue  # lazy deletion: a cheaper entry already won
            if current == goal:
                yield SearchState(
                    current=current,
                    frontier=[coord for _, _, coord in heap],
                    visited=set(seen),
                    cost_so_far=dict(dist),
                    came_from=dict(came_from),
                    finished=True,
                    path=reconstruct_path(came_from, start, goal),
                )
                return
            for nxt in grid.neighbors(current):
                step = grid.step_cost(current, nxt)
                if cost + step < dist.get(nxt, math.inf):
                    dist[nxt] = cost + step
                    came_from[nxt] = current
                    seen.add(nxt)
                    heapq.heappush(heap, (dist[nxt], next(counter), nxt))
            yield SearchState(
                current=current,
                frontier=[coord for _, _, coord in heap],
                visited=set(seen),
                cost_so_far=dict(dist),
                came_from=dict(came_from),
                finished=False,
                path=None,
            )
        yield SearchState(
            current=None,
            frontier=[],
            visited=set(seen),
            cost_so_far=dict(dist),
            came_from=dict(came_from),
            finished=True,
            path=None,
        )

    def find_path(self, grid: Grid, start: Coord, goal: Coord) -> SearchResult:
        expanded = 0
        last: SearchState | None = None
        for state in self.search_steps(grid, start, goal):
            if not state.finished:
                expanded += 1
            last = state
        assert last is not None and last.finished
        if last.path is None:
            return SearchResult(
                path=[],
                nodes_expanded=expanded,
                total_cost=math.inf,
                cost_so_far=last.cost_so_far,
            )
        return SearchResult(
            path=last.path,
            nodes_expanded=expanded,
            total_cost=last.cost_so_far[goal],
            cost_so_far=last.cost_so_far,
        )
