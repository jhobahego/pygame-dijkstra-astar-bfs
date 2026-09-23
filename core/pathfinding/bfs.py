"""Breadth-first search: fewest steps, ignoring terrain costs.

The goal is checked when a cell is popped from the queue (uniform with
Dijkstra and A*, which cut on extraction), so ``nodes_expanded`` counts
popped cells excluding the final goal pop.
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Iterator

from ..grid import Grid
from ..types import Coord, Cost
from .base import Pathfinder, SearchResult, SearchState, reconstruct_path


class BreadthFirstSearch(Pathfinder):
    """BFS baseline: shortest in steps, blind to mud/water costs.

    Decisions ignore terrain, but ``total_cost`` reports the true
    terrain cost of the path found, so it stays comparable with
    Dijkstra and A* (which would otherwise look more expensive).
    """

    name: str = "bfs"

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
        came_from: dict[Coord, Coord | None] = {start: None}
        depth: dict[Coord, Cost] = {start: 0.0}
        seen: set[Coord] = {start}
        queue: deque[Coord] = deque([start])
        while queue:
            current = queue.popleft()
            if current == goal:
                yield SearchState(
                    current=current,
                    frontier=list(queue),
                    visited=set(seen),
                    cost_so_far=dict(depth),
                    came_from=dict(came_from),
                    finished=True,
                    path=reconstruct_path(came_from, start, goal),
                )
                return
            for nxt in grid.neighbors(current):
                if nxt not in seen:
                    seen.add(nxt)
                    came_from[nxt] = current
                    depth[nxt] = depth[current] + 1
                    queue.append(nxt)
            yield SearchState(
                current=current,
                frontier=list(queue),
                visited=set(seen),
                cost_so_far=dict(depth),
                came_from=dict(came_from),
                finished=False,
                path=None,
            )
        yield SearchState(
            current=None,
            frontier=[],
            visited=set(seen),
            cost_so_far=dict(depth),
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
            total_cost=float(
                sum(grid.step_cost(a, b) for a, b in zip(last.path, last.path[1:]))
            ),
            cost_so_far=last.cost_so_far,
        )


BFS = BreadthFirstSearch
