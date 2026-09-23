"""Search contracts shared by all pathfinding algorithms.

``find_path`` must always be implemented by consuming ``search_steps``,
so the step-by-step visualization can never diverge from normal search.

This module is part of ``core/`` and must never import ``pygame``.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..grid import Grid
from ..types import Coord, Cost, Path


@dataclass(frozen=True)
class SearchState:
    """Snapshot of one search iteration, for the visualizer.

    ``visited`` holds every cell seen so far (enqueued), ``frontier``
    the cells still waiting, and ``current`` the cell just popped
    (``None`` when the search ends with no current cell).
    Containers are snapshots: later iterations never mutate them.
    """

    current: Coord | None
    frontier: list[Coord]
    visited: set[Coord]
    cost_so_far: dict[Coord, Cost]
    came_from: dict[Coord, Coord | None]
    finished: bool
    path: Path | None


@dataclass
class SearchResult:
    """Outcome of a finished search (empty ``path`` when unreachable)."""

    path: Path
    nodes_expanded: int
    total_cost: Cost
    cost_so_far: dict[Coord, Cost]


@runtime_checkable
class Pathfinder(Protocol):
    """Interchangeable search algorithm (BFS, Dijkstra, A*)."""

    name: str

    def find_path(self, grid: Grid, start: Coord, goal: Coord) -> SearchResult:
        """Run the whole search and return the result."""
        ...

    def search_steps(self, grid: Grid, start: Coord, goal: Coord) -> Iterator[SearchState]:
        """Yield one state per expanded node, ending with ``finished=True``."""
        ...


def reconstruct_path(
    came_from: dict[Coord, Coord | None], start: Coord, goal: Coord
) -> Path:
    """Rebuild the start-to-goal path by walking ``came_from`` backwards."""
    if goal not in came_from:
        return []
    path: Path = [goal]
    while path[-1] != start:
        parent = came_from[path[-1]]
        if parent is None:
            return []
        path.append(parent)
    return path[::-1]
