# Assets

Grid Chase uses only the spritesheets already included in this directory.
Nothing is generated and nothing is downloaded at runtime.

## Inventory

| File | Size | Content |
|---|---|---|
| `spritesheet-dijkstra-game-example.jpeg` | 1408x768 | Reference composite: tileset, player, guard and objective on one canvas |
| `sprites/player-spritesheet.jpeg` | 1024x1024 | Player, 4 directions (down, up, left, right) x 4 walk frames |
| `sprites/guard-spritesheet.jpeg` | 1024x1024 | Guard, 4 directions x 4 walk frames |
| `sprites/objective-sprites.png` | 1107x293 | Objective: star, red star, diamond, coin (4 cells) |
| `tiles/spritesheet-tileset.jpeg` | 1408x768 | Terrain 2x2: floor (`.`), mud (`~`), water (`w`), wall (`#`) |

`assets/fonts/` holds local font files when the game needs them.

## Regions (sheet pixels)

The loader (`game/assets.py`, `AssetLoader`) crops these regions and fits
each one into a 32x32 px tile preserving aspect ratio (centered, transparent
background, nearest-neighbor scaling):

- **Player** (`player-spritesheet.jpeg`): tight sprite boxes per cell, e.g.
  down `[(152, 92, 116, 168), (364, 92, 122, 168), ...]`. Rows are
  down / up / left / right from top to bottom. Captions and direction labels
  are excluded.
- **Guard** (`guard-spritesheet.jpeg`): full grid cells, e.g. down row
  `(150, 94, 200, 202)` with columns at x `150 / 362 / 566 / 766`.
  The sheet carries no captions inside cells.
- **Objective** (`objective-sprites.png`): cells `(18, 19, 263, 258)`,
  `(294, 19, 263, 258)`, `(570, 19, 262, 258)`, `(845, 19, 262, 258)`.
- **Tiles** (`tiles/spritesheet-tileset.jpeg`): 2x2 block from `(352, 48)`:
  floor `(352, 48, 352, 336)`, mud `(704, 48, 352, 336)`,
  water `(352, 384, 352, 384)`, wall `(704, 384, 352, 384)`.

Entity surfaces keep the sheet background (JPEG sheets are opaque); only the
objective PNG carries alpha.

## Usage

```python
loader = AssetLoader("assets")  # once, at startup
loader.get("floor")             # 32x32 tile: player/guard/target/floor/mud/water/wall
loader.frame("player", "down", 0)  # walk animation frame
loader.target_frame(2)             # diamond
```

Sheets are loaded with a single `pygame.image.load` each and cached with
`.convert_alpha()`. Never call `pygame.image.load` inside the game loop;
reuse the loader surfaces.
