# Assets

Grid Chase uses only the spritesheets already included in this directory.
Nothing is generated and nothing is downloaded at runtime.

## Inventory

| File | Size | Content |
|---|---|---|
| `spritesheet-dijkstra-game-example.jpeg` | 1408x768 | Reference composite: tileset, player, guard and objective on one canvas |
| `sprites/player-spritesheet.jpeg` | 500x500 | Player, 4 directions (down, up, left, right) x 4 walk frames, transparent background |
| `sprites/guard-spritesheet.jpeg` | 500x500 | Guard, 4 directions x 4 walk frames, transparent background |
| `sprites/objective-sprites.png` | 1000x250 | Objective: star, red star, diamond, coin (4 cells), transparent background |
| `tiles/spritesheet-tileset.jpeg` | 1024x1024 | Terrain 2x2: floor (`.`), mud (`~`), water (`w`), wall (`#`), no captions |

`assets/fonts/` holds local font files when the game needs them.

## Regions (sheet pixels)

The loader (`game/assets.py`, `AssetLoader`) crops these regions and fits
each one into a 32x32 px tile preserving aspect ratio (centered, transparent
background, nearest-neighbor scaling):

- **Player** (`player-spritesheet.jpeg`): uniform 4x4 grid of 125 px
  cells. Rows are down / up / left / right from top to bottom.
- **Guard** (`guard-spritesheet.jpeg`): same 4x4 grid of 125 px cells.
- **Objective** (`objective-sprites.png`): cells `(0, 0, 250, 250)`,
  `(250, 0, 250, 250)`, `(500, 0, 250, 250)`, `(750, 0, 250, 250)`.
- **Tiles** (`tiles/spritesheet-tileset.jpeg`): 2x2 quadrants of 512 px:
  floor `(0, 0, 512, 512)`, mud `(512, 0, 512, 512)`,
  water `(0, 512, 512, 512)`, wall `(512, 512, 512, 512)`.

Entity and objective surfaces carry real alpha (transparent background);
only the terrain JPEG is opaque (tiles need no transparency).

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
