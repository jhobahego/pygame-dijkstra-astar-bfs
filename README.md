# Grid Chase

Juego educativo top-down por tiles para **ver y comparar BFS, Dijkstra y A\***
sobre una grilla con costos variables. El guardia persigue al jugador con el
algoritmo seleccionado, y el overlay de depuración muestra frontera, nodos
visitados, costos, padres y ruta final paso a paso.

## Requisitos

- Python 3.11+
- Las dependencias están fijadas en `requirements.txt` (juego: `pygame-ce`)
  y `requirements-dev.txt` (`pytest`, `mypy`)

## Instalación (entorno limpio)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Uso

```bash
python main.py          # jugar (carga maps/01_tutorial.txt)
python -m pytest -q     # suite completa
python -m mypy core     # tipos del núcleo puro
```

## Controles

| Tecla | Acción |
|---|---|
| Flechas / WASD | Mover al jugador por celdas |
| `TAB` | Mostrar/ocultar overlay de búsqueda |
| `1` `2` `3` | BFS / Dijkstra / A\* en caliente |
| `ENTER` | Congelar la búsqueda (paso a paso) |
| `ESPACIO` | Avanzar una iteración |
| `R` | Reiniciar el mapa |
| `M` | Siguiente mapa |
| `ESC` | Salir |

## Mapas (`maps/`)

Coordenadas `(fila, columna)`; el costo es el de **entrar** en la celda
(piso 1, barro 5, agua 8, muro intransitable).

| Mapa | Idea pedagógica |
|---|---|
| `01_tutorial.txt` | Movimiento y primer objetivo |
| `02_mud_detour.txt` | BFS cruza el barro (12 celdas, costo 35); Dijkstra lo rodea (16 celdas, costo 15) |
| `03_maze.txt` | Laberinto con 2 objetivos |

## Sprites (`assets/`)

Solo se usan los spritesheets ya incluidos en el repo (nada se genera ni se
descarga): jugador y guardia (4 direcciones × 4 frames), 4 objetivos y tiles
de piso/barro/agua/muro, recortados a 32x32 px por el `AssetLoader`
(`game/assets.py`, carga única al inicio). Detalle de regiones en
`assets/README.md`.

## Arquitectura

- `core/` — lógica pura y testeable (**nunca** importa `pygame`):
  tipos, grilla con costos, parser de mapas y algoritmos (`BFS`, `Dijkstra`,
  `AStar` intercambiables vía el protocolo `Pathfinder`). Cada `find_path`
  consume su generador `search_steps`.
- `game/` — loop pygame, cámara (única conversión grilla↔píxeles), entrada,
  renderer, entidades y overlay de depuración.
- `tests/` — grilla, parser, algoritmos, equivalencias, casos borde
  (sin ruta, inicio==meta) y pureza de `core/`.
