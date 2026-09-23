# Grid Chase

## Contexto

- El repositorio contiene `ESPECIFICACION.md`, que define un juego educativo top-down en Python 3.11+ para comparar BFS, Dijkstra y A* sobre una grilla con costos variables.
- El proyecto se dividirá en `core/` para lógica pura y testeable, y `game/` para el loop, render y entrada de pygame-ce. Ningún archivo bajo `core/` puede importar pygame.
- La ejecución se realizará con pygame-ce 2.5+; pytest y mypy serán dependencias de desarrollo.
- Los mapas viven en `maps/` y usan coordenadas `(fila, columna)`. El costo de una celda es el costo de entrar en ella.
- Se respetan los contratos descritos en `ESPECIFICACION.md`: `Grid`, `SearchState`, `SearchResult`, `Pathfinder`, búsqueda paso a paso, contador en heaps, lazy deletion y corte al extraer el objetivo.
- El patrón de separación a seguir es `core/` frente a `game/`: los algoritmos no conocerán superficies, colores, píxeles ni eventos de pygame; `game/camera.py` será el único lugar que convierta coordenadas de grilla a píxeles.
- Los sprites ya existen en el repositorio dentro de `assets/` (`assets/spritesheet-dijkstra-game-example.jpeg`, `assets/sprites/player-spritesheet.jpeg`, `assets/sprites/guard-spritesheet.jpeg`, `assets/sprites/objective-sprites.png`, `assets/tiles/spritesheet-tileset.jpeg`). No se genera ni descarga ningún asset: los frames se recortan/escalan a tiles de 32 px y se cargan una sola vez al inicio mediante un `AssetLoader`.
- La finalidad es pedagógica: poder pausar una búsqueda, avanzar una iteración y observar frontera, nodos cerrados, costos, padres y ruta final en el mismo mapa.

## Objetivo

Construir un prototipo jugable y testeable de Grid Chase que use los spritesheets existentes en `assets/`, permita comparar BFS, Dijkstra y A* en mapas con costos variables, y visualice cada búsqueda paso a paso.

## Flujo

### Secuencia

```text
SECUENCIA (orden temporal ↓)
1. Autor → Proyecto: ejecuta el juego
2. Proyecto → AssetLoader: carga los spritesheets de assets/ y recorta frames a tiles de 32 px
3. AssetLoader → Proyecto: entrega superficies cacheadas de jugador, guardia, objetivo y tiles
4. Proyecto → MapLoader: carga y valida el mapa .txt
5. MapLoader → Proyecto: devuelve grid, jugador, guardias y objetivos
6. Jugador → GameLoop: se mueve por celdas
7. GameLoop → Pathfinder: calcula la ruta del guardia
8. Pathfinder → DebugOverlay: emite estados de búsqueda
9. Autor → Juego: pausa, cambia algoritmo o avanza una iteración
10. Juego → Autor: muestra frontera, visitados, costos y ruta final
```

### Flujo

```text
inicio
   │
   ▼
cargar spritesheets de assets/ y recortar frames a 32 px
                   ▼
           ¿Mapa válido?
             │ sí             │ no
             ▼                ▼
       iniciar partida   mostrar error de línea
             │
             ▼
      ¿Jugador se mueve?
        │ sí             │ no
        ▼                ▼
 recalcular ruta    mantener estado
        │
        ▼
 ¿Modo paso a paso?
   │ no              │ sí
   ▼                 ▼
 avanzar juego   esperar ESPACIO
   │                 │
   │                 ▼
   │          avanzar una iteración
   │                 │
   └─────────┬───────┘
             ▼
     ¿Ruta encontrada?
       │ sí              │ no
       ▼                 ▼
 seguir ruta       mostrar sin ruta
       │
       ▼
¿Guardia alcanzó al jugador?
   │ no                       │ sí
   ▼                          ▼
continuar             mostrar derrota
   │
   ▼
¿Quedan objetivos?
   │ sí                       │ no
   └────── volver al juego    ▼
                         mostrar victoria
```

## Restricciones

- No usar Unity, Godot, GameMaker ni otra engine.
- No importar pygame desde ningún módulo bajo `core/`.
- No usar librerías externas de pathfinding, grafos o estructuras de datos; solo la biblioteca estándar para `heapq`, `deque` y tipos auxiliares.
- Mantener los algoritmos intercambiables mediante el protocolo `Pathfinder`; `Guard` no debe depender de una implementación concreta.
- Representar coordenadas internas como `(fila, columna)` y convertirlas a píxeles únicamente en `game/camera.py`.
- Usar costos variables: piso 1, barro 5, agua 8 y muro no transitable.
- Para 8 direcciones, multiplicar pasos diagonales por `sqrt(2)` y rechazar diagonales que corten entre dos muros.
- En heaps usar `(prioridad, contador, coord)`, lazy deletion y corte temprano al extraer el objetivo.
- `find_path` debe consumir `search_steps`; no habrá una segunda implementación divergente de la búsqueda.
- No generar ni descargar assets en ningún caso: usar exclusivamente los spritesheets ya incluidos en `assets/`. El recorte/escalado a tiles de 32 px vive en el `AssetLoader`, nunca en el game loop.
- Los spritesheets existentes son `assets/spritesheet-dijkstra-game-example.jpeg`, `assets/sprites/player-spritesheet.jpeg`, `assets/sprites/guard-spritesheet.jpeg`, `assets/sprites/objective-sprites.png` y `assets/tiles/spritesheet-tileset.jpeg`. El loader los carga una sola vez al inicio (nunca `pygame.image.load` dentro del game loop) y cachea las superficies con `.convert_alpha()`.
- Tile de 32x32 px con convención documentada en `assets/README.md`: qué región de cada sheet corresponde a jugador, guardia, objetivo, piso, barro, agua y muro.
- No añadir pygbag ni publicación web en esta entrega.

## Fuera de alcance

- Publicación del juego, empaquetado para navegador o soporte WASM.
- Assets descargados de Kenney, OpenGameArt, itch.io u otras fuentes externas.
- Sistema de audio, partículas, inventario, combate o progresión.
- Fog of war, costos dinámicos, Jump Point Search y D* Lite.
- Flow field multi-guardia como requisito de la primera entrega; puede quedar preparado como extensión posterior.
- Editor visual de mapas.
- Refactorizaciones no relacionadas con la separación `core/`/`game/` o con la generación y carga de recursos.

## Tareas

### T1: Preparar estructura y dependencias

- **Hacer:** Crear la estructura base de paquetes, archivos de dependencias, entrypoint y directorios `core/`, `game/`, `maps/`, `tests/` y `assets/`. Añadir configuración mínima para Python 3.11+ y pygame-ce.
- **Archivos:** `requirements.txt`, `requirements-dev.txt`, `main.py`, `core/__init__.py`, `game/__init__.py`, `assets/README.md`.
- **Verify:** `python --version` confirma Python 3.11+ y `python -m compileall core game main.py` termina sin errores.

### T2: Implementar tipos y grilla pura

- **Hacer:** Implementar `Coord`, `Path`, `Cost`, `TileType` y `Grid` con límites, transitabilidad, costos, vecinos de 4/8 direcciones y validación de diagonales.
- **Archivos:** `core/types.py`, `core/grid.py`, `tests/test_grid.py`.
- **Verify:** `python -m pytest tests/test_grid.py -q` cubre esquinas, bordes, muros, costos y diagonales sin importar pygame.

### T3: Usar los spritesheets existentes y cargarlos con AssetLoader

- **Hacer:** Inventariar los spritesheets ya incluidos en `assets/` y crear un `AssetLoader` que los cargue una sola vez al inicio, recorte/escale los frames a tiles de 32x32 px y cachee las superficies (jugador, guardia, objetivo, piso, barro, agua, muro). Documentar en `assets/README.md` qué región de cada sheet corresponde a cada entidad/tile, las dimensiones y el uso desde el juego. Queda prohibido crear scripts generadores de PNG o descargar assets: todo el juego debe usar estos sprites.
- **Archivos:** `game/assets.py`, `assets/README.md`, `tests/test_assets.py`.
- **Verify:** `python -m pytest tests/test_assets.py -q` comprueba que cada sheet existe, que el loader entrega superficies de 32x32 px para jugador, guardia, objetivo y los cuatro tiles, y que la carga ocurre una sola vez (cacheada, sin `pygame.image.load` en el game loop).

### T4: Parsear mapas y crear mapas pedagógicos

- **Hacer:** Implementar metadata, validación de filas, perímetro, símbolos, spawn único de jugador, objetivos y errores con número de línea. Crear tutorial, rodeo de barro y laberinto; `02_mud_detour.txt` debe producir rutas visiblemente diferentes entre BFS y Dijkstra.
- **Archivos:** `core/mapfile.py`, `maps/01_tutorial.txt`, `maps/02_mud_detour.txt`, `maps/03_maze.txt`, `tests/test_mapfile.py`.
- **Verify:** `python -m pytest tests/test_mapfile.py -q`; mapas inválidos comprueban que el error incluye la línea problemática.

### T5: Implementar contrato de búsqueda y BFS

- **Hacer:** Crear `SearchState`, `SearchResult`, `Pathfinder`, reconstrucción de caminos y BFS con `deque`. Cubrir start igual a goal y ausencia de ruta.
- **Archivos:** `core/pathfinding/base.py`, `core/pathfinding/bfs.py`, `core/pathfinding/__init__.py`, `tests/test_bfs.py`, `tests/test_no_path.py`, `tests/test_start_is_goal.py`.
- **Verify:** `python -m pytest tests/test_bfs.py tests/test_no_path.py tests/test_start_is_goal.py -q` pasa y `find_path` se obtiene consumiendo el generador.

### T6: Implementar Dijkstra y comparación de costos

- **Hacer:** Implementar Dijkstra con heap, contador incremental, lazy deletion, corte al extraer el objetivo y costos de entrada. Añadir pruebas de rodeo del barro, costo total y equivalencia con BFS cuando todos los costos son uniformes.
- **Archivos:** `core/pathfinding/dijkstra.py`, `tests/test_dijkstra.py`, `tests/test_equivalence.py`.
- **Verify:** `python -m pytest tests/test_dijkstra.py tests/test_equivalence.py -q`; Dijkstra elige el rodeo más barato aunque tenga más celdas.

### T7: Implementar heurísticas y A*

- **Hacer:** Añadir `zero`, `manhattan`, `octile` y `euclidean`, documentando admisibilidad y la incompatibilidad de Manhattan con diagonales. Crear A* como variación mínima de la lógica compartida con Dijkstra e inyección de heurística.
- **Archivos:** `core/pathfinding/heuristics.py`, `core/pathfinding/astar.py`, `tests/test_astar.py`.
- **Verify:** `python -m pytest tests/test_astar.py -q`; A* devuelve un costo óptimo igual a Dijkstra y `nodes_expanded` es menor o igual en los casos definidos.

### T8: Construir loop, cámara y movimiento por tiles

- **Hacer:** Implementar ventana de 960x640, timestep, cámara, carga del mapa, dibujo de tiles y entidades, entrada WASD/flechas y movimiento interpolado entre celdas sin atravesar muros. Animar jugador y guardia con los frames direccionales del `AssetLoader` (`game/assets.py`).
- **Archivos:** `game/config.py`, `game/camera.py`, `game/input.py`, `game/renderer.py`, `game/assets.py`, `game/entities/entity.py`, `game/entities/player.py`, `game/app.py`.
- **Verify:** `python main.py` abre un mapa; el jugador se mueve con WASD/flechas, no cruza muros y ESC cierra la ventana. La carga usa los spritesheets de `assets/` a través del `AssetLoader` de T3.

### T9: Añadir guardia, selección de algoritmo y overlay

- **Hacer:** Implementar `Guard` con `Pathfinder` inyectado, recalcular solo al cambiar la celda del jugador, conservar el último resultado y moverlo por la ruta. Añadir TAB, ENTER, ESPACIO, 1/2/3, R, M y overlay con frontera, visitados, nodo actual, costos, padres, ruta y métricas.
- **Archivos:** `game/entities/guard.py`, `game/debug_overlay.py`, `game/app.py`, `game/renderer.py`.
- **Verify:** ejecución manual de `python main.py`: TAB activa el overlay; ENTER pausa; ESPACIO avanza exactamente una iteración; 1/2/3 cambia el algoritmo sin reiniciar el mapa; el panel muestra algoritmo, nodos expandidos, costo y longitud de ruta.

### T10: Integrar pruebas y validación final

- **Hacer:** Añadir la prueba de pureza de `core`, revisar imports, integrar todos los mapas y documentar instalación, uso de los spritesheets existentes, controles y propósito pedagógico.
- **Archivos:** `tests/test_core_pure.py`, `README.md`, `ESPECIFICACION.md` solo si se necesita corregir una contradicción de integración.
- **Verify:** `python -m pytest -q`; `python -m mypy core` no introduce errores nuevos; el juego inicia desde un entorno limpio con las dependencias documentadas.

## Done (validación final)

- [ ] `python -m pytest -q` pasa incluyendo pureza de `core`, grilla, parser, BFS, Dijkstra, A*, equivalencias y casos borde.
- [ ] El `AssetLoader` carga los spritesheets existentes en `assets/` y entrega tiles de 32x32 px para jugador, guardia, objetivo, piso, barro, agua y muro, sin generar ni descargar nada.
- [ ] `python main.py` abre la ventana de 960x640, carga un mapa `.txt`, dibuja los sprites de `assets/` y cierra con ESC.
- [ ] Manual: el jugador se mueve por tiles, recoge objetivos, no atraviesa muros y puede reiniciar o cambiar de mapa.
- [ ] Manual: un guardia persigue al jugador y recalcula solo cuando cambia la celda del jugador.
- [ ] Manual: TAB muestra el overlay; ENTER congela la búsqueda; ESPACIO avanza una iteración; se ven frontera, visitados, costos, padres y ruta.
- [ ] Manual: en `02_mud_detour.txt`, BFS cruza el barro y Dijkstra elige el rodeo de menor costo; A* conserva el costo óptimo y reporta sus expansiones.
- [ ] Ningún archivo bajo `core/` contiene `import pygame`.
