"""Tests for game.assets: sheets exist, tiles are 32x32, loading is cached."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pathlib import Path

import pygame
import pytest

from game.assets import (
    BASE_KEYS,
    DIRECTIONS,
    TILE_SIZE,
    AssetLoader,
)

SHEETS = [
    "assets/spritesheet-dijkstra-game-example.jpeg",
    "assets/sprites/player-spritesheet.jpeg",
    "assets/sprites/guard-spritesheet.jpeg",
    "assets/sprites/objective-sprites.png",
    "assets/tiles/spritesheet-tileset.jpeg",
]


@pytest.fixture(scope="module")
def display() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture()
def loader(display: None) -> AssetLoader:
    return AssetLoader("assets")


def test_sheets_exist_on_disk() -> None:
    for sheet in SHEETS:
        assert Path(sheet).is_file(), f"missing spritesheet: {sheet}"


def test_base_keys_are_32x32(loader: AssetLoader) -> None:
    for key in BASE_KEYS:
        surface = loader.get(key)
        assert (surface.get_width(), surface.get_height()) == (TILE_SIZE, TILE_SIZE)


def test_tiles_differ_from_each_other(loader: AssetLoader) -> None:
    blobs = {
        name: pygame.image.tobytes(loader.get(name), "RGB") for name in ("floor", "mud", "water", "wall")
    }
    assert len(set(blobs.values())) == 4


def test_entities_differ_from_each_other(loader: AssetLoader) -> None:
    blobs = {name: pygame.image.tobytes(loader.get(name), "RGB") for name in ("player", "guard", "target")}
    assert len(set(blobs.values())) == 3


def test_walk_frames_are_32x32(loader: AssetLoader) -> None:
    for who in ("player", "guard"):
        for direction in DIRECTIONS:
            for index in range(4):
                surface = loader.frame(who, direction, index)
                assert (surface.get_width(), surface.get_height()) == (TILE_SIZE, TILE_SIZE)


def test_walk_animation_varies(loader: AssetLoader) -> None:
    first = pygame.image.tobytes(loader.frame("player", "down", 0), "RGB")
    second = pygame.image.tobytes(loader.frame("player", "down", 1), "RGB")
    assert first != second


def test_target_frames(loader: AssetLoader) -> None:
    for index in range(4):
        surface = loader.target_frame(index)
        assert (surface.get_width(), surface.get_height()) == (TILE_SIZE, TILE_SIZE)


def test_loading_happens_once(loader: AssetLoader, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0
    real_load = pygame.image.load

    def counting_load(*args: object, **kwargs: object) -> pygame.Surface:
        nonlocal calls
        calls += 1
        return real_load(*args, **kwargs)

    monkeypatch.setattr(pygame.image, "load", counting_load)
    for key in BASE_KEYS:
        loader.get(key)
    for direction in DIRECTIONS:
        for index in range(4):
            loader.frame("player", direction, index)
            loader.frame("guard", direction, index)
    for index in range(4):
        loader.target_frame(index)
    first_round = calls
    assert first_round == 4  # player, guard, target, tiles sheets
    assert loader.load_calls == 4
    # Second round serves everything from cache: no further loads.
    for key in BASE_KEYS:
        loader.get(key)
    assert calls == first_round
    assert loader.get("player") is loader.get("player")


def test_unknown_asset_raises(loader: AssetLoader) -> None:
    with pytest.raises(KeyError):
        loader.get("dragon")
    with pytest.raises(KeyError):
        loader.frame("dragon", "down", 0)
    with pytest.raises(KeyError):
        loader.frame("player", "northwest", 0)
    with pytest.raises(IndexError):
        loader.frame("player", "down", 4)
    with pytest.raises(IndexError):
        loader.target_frame(4)


def test_missing_sheet_raises(display: None, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        AssetLoader(tmp_path).get("player")
