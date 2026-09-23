"""Base types shared by the pure game logic in ``core/``.

Coordinates are always ``(row, column)`` tuples, never ``(x, y)``.
The conversion to screen pixels lives exclusively in ``game/camera.py``.
"""

Coord = tuple[int, int]  # (row, column)
Path = list[Coord]  # includes start and goal
Cost = float
