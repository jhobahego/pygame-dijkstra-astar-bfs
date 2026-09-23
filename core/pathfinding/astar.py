"""A*: Dijkstra guided by an injected admissible heuristic.

Minimal variation over :mod:`dijkstra`: the heap orders by
``f = g + h`` instead of ``g``. Entries stay ``(priority, counter,
coord)``; staleness is detected by recomputing ``dist + h`` with the
same operands, so the comparison is bit-exact. ``cost_so_far`` keeps
true ``g`` costs, and the goal still cuts on extraction.
"""

from __future__ import annotations

import heapq
import itertools
import math
from collections.abc import Iterator

from ..grid import Grid
from ..types import Coord, Cost
from .base import Pathfinder, SearchResult, SearchState, reconstruct_path
from .heuristics import Heuristic, octile


class AStar(Pathfinder):
    """A* search with an injectable heuristic (default: ``octile``)."""

    name: str = "astar"

    def __init__(self, heuristic: Heuristic = octile) -> None:
        self.heuristic = heuristic

    def search_steps(self, grid: Grid, start: Coord, goal: Coord) -> Iterator[SearchState]:
        heuristic = self.heuristic
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
        heap: list[tuple[Cost, int, Coord]] = [(heuristic(start, goal), next(counter), start)]
        while heap:
            priority, _, current = heapq.heappop(heap)
            if priority > dist[current] + heuristic(current, goal):
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
                if dist[current] + step < dist.get(nxt, math.inf):
                    dist[nxt] = dist[current] + step
                    came_from[nxt] = current
                    seen.add(nxt)
                    heapq.heappush(
                        heap,
                        (dist[nxt] + heuristic(nxt, goal), next(counter), nxt),
                    )
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
