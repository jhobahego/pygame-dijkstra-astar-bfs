"""Tests for core.mapfile: metadata, validation with line numbers, maps."""

from collections import deque
from pathlib import Path

import pytest

from core.grid import TileType
from core.mapfile import MapData, MapError, load_map, parse_map
from core.types import Coord

VALID = """name=Sala de pruebas
guards=1
#######
#P.~wG#
#..*..#
#######
"""


def flood(grid: object, start: Coord) -> set[Coord]:
    """Test-only reachability check (not the product search algorithm)."""
    from core.grid import Grid

    assert isinstance(grid, Grid)
    seen = {start}
    queue = deque([start])
    while queue:
        for nxt in grid.neighbors(queue.popleft()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def test_no_pygame_import_in_mapfile() -> None:
    assert "import pygame" not in Path("core/mapfile.py").read_text()


def test_parse_valid_map() -> None:
    data = parse_map(VALID)
    assert isinstance(data, MapData)
    assert data.name == "Sala de pruebas"
    assert data.metadata["guards"] == "1"
    assert (data.grid.width, data.grid.height) == (7, 4)
    assert data.player == (1, 1)
    assert data.guards == [(1, 5)]
    assert data.goals == [(2, 3)]
    assert data.grid.tile_at((1, 2)) is TileType.FLOOR
    assert data.grid.tile_at((1, 3)) is TileType.MUD
    assert data.grid.tile_at((1, 4)) is TileType.WATER


def test_spawns_sit_on_walkable_floor() -> None:
    data = parse_map(VALID)
    for cell in [data.player, *data.guards, *data.goals]:
        assert data.grid.is_walkable(cell)
        assert data.grid.cost(cell) == 1.0


def test_default_name_is_empty_without_metadata() -> None:
    data = parse_map("####\n#P*#\n####")
    assert data.name == ""


def test_load_map_defaults_name_to_stem(tmp_path: Path) -> None:
    path = tmp_path / "arena.txt"
    path.write_text("####\n#P*#\n####", encoding="utf-8")
    assert load_map(path).name == "arena"


def test_unequal_row_width_reports_line() -> None:
    with pytest.raises(MapError, match="línea 3"):
        parse_map("name=X\n####\n###\n####")


def test_unknown_symbol_reports_line() -> None:
    with pytest.raises(MapError, match="línea 2"):
        parse_map("####\n#PX#\n####")


def test_open_perimeter_reports_line() -> None:
    with pytest.raises(MapError, match="línea 2"):
        parse_map("####\n#P.*\n####")


def test_missing_player_reports_first_grid_line() -> None:
    with pytest.raises(MapError, match="línea 1"):
        parse_map("###\n#*#\n###")


def test_duplicate_player_reports_second_spawn_line() -> None:
    with pytest.raises(MapError, match="línea 3"):
        parse_map("#####\n#P*##\n#P..#\n#####")


def test_missing_goal_reports_first_grid_line() -> None:
    with pytest.raises(MapError, match="línea 1"):
        parse_map("###\n#P#\n###")


def test_invalid_metadata_key_reports_line() -> None:
    with pytest.raises(MapError, match="línea 1"):
        parse_map("123=bad\n###\n#P*\n###")


def test_metadata_only_reports_error() -> None:
    with pytest.raises(MapError):
        parse_map("name=X\n")


def test_empty_file_reports_error() -> None:
    with pytest.raises(MapError):
        parse_map("")


def test_tutorial_map() -> None:
    data = load_map("maps/01_tutorial.txt")
    assert data.name == "Tutorial"
    assert data.guards and data.goals
    reachable = flood(data.grid, data.player)
    assert all(goal in reachable for goal in data.goals)
    for guard in data.guards:
        assert data.player in flood(data.grid, guard)


def test_mud_detour_map_structure() -> None:
    data = load_map("maps/02_mud_detour.txt")
    assert data.player[0] == data.guards[0][0] == 1  # same corridor row
    corridor = [data.grid.tile_at((1, c)) for c in range(4, 10)]
    assert corridor and all(tile is TileType.MUD for tile in corridor)
    detour_row = data.grid.height - 2
    assert all(
        data.grid.tile_at((detour_row, c)) is TileType.FLOOR
        for c in range(1, data.grid.width - 1)
    )
    mud = sum(
        1
        for r in range(data.grid.height)
        for c in range(data.grid.width)
        if data.grid.tile_at((r, c)) is TileType.MUD
    )
    assert mud >= 6
    reachable = flood(data.grid, data.player)
    assert all(goal in reachable for goal in data.goals)
    assert data.player in flood(data.grid, data.guards[0])


def test_maze_map() -> None:
    data = load_map("maps/03_maze.txt")
    assert data.name == "Laberinto"
    assert data.guards and len(data.goals) >= 2
    reachable = flood(data.grid, data.player)
    assert all(goal in reachable for goal in data.goals)
    for guard in data.guards:
        assert data.player in flood(data.grid, guard)
