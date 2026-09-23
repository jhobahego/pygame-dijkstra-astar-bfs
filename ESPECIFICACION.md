# Especificación técnica — *Grid Chase*

Juego top-down por tiles para aprender algoritmos de búsqueda de caminos implementándolos desde cero.

---

## 1. Objetivo del proyecto

El objetivo **no** es publicar un juego. Es entender Dijkstra implementándolo, visualizándolo paso a paso y comparándolo contra BFS y A\* dentro de un entorno donde sus diferencias sean observables.

Criterio de éxito: poder pausar el juego, avanzar la búsqueda iteración por iteración con una tecla, y ver en pantalla la frontera, los nodos cerrados y el costo acumulado de cada celda.

### Restricciones de diseño

| Restricción | Razón |
|---|---|
| Sin engine (Unity, Godot, GameMaker) | El game loop lo escribe el autor |
| El paquete `core/` no importa `pygame` | Portabilidad y testeabilidad del algoritmo |
| Terreno con costos variables, no solo muros | Sin pesos, Dijkstra ≡ BFS y la lección se pierde |
| Los algoritmos son intercambiables en runtime | Comparar es el mecanismo de aprendizaje |

---

## 2. Concepto de juego

Vista cenital sobre una grilla. El jugador se mueve celda a celda recogiendo objetivos. Uno o más guardias lo persiguen calculando su ruta con el algoritmo seleccionado.

El mapa tiene cuatro tipos de terreno con costo distinto. El jugador puede cruzar el barro tan rápido como el guardia, pero el guardia **calcula** que le sale caro y lo rodea. Esa asimetría es la que hace visible el comportamiento del algoritmo.

**Bucle de juego:** recoger los N objetivos del mapa sin ser alcanzado. Si un guardia te toca, pierdes.

### Terrenos

| Tile | Símbolo | Costo | Transitable |
|---|---|---|---|
| Piso | `.` | 1 | Sí |
| Barro | `~` | 5 | Sí |
| Agua | `w` | 8 | Sí |
| Muro | `#` | ∞ | No |
| Spawn jugador | `P` | 1 | Sí |
| Spawn guardia | `G` | 1 | Sí |
| Objetivo | `*` | 1 | Sí |

---

## 3. Stack y dependencias

- **Python 3.11+** (se usan `match`, tipos nativos `list[int]`, `tuple[int, int]`)
- **pygame-ce 2.5+** — fork mantenido de Pygame, mejor rendimiento y compatibilidad
- **pytest** — solo para desarrollo
- **pygbag** *(opcional, fase final)* — compila a WASM si se quiere publicar en navegador

`requirements.txt`
```
pygame-ce>=2.5.0
```

`requirements-dev.txt`
```
-r requirements.txt
pytest>=8.0
mypy>=1.8
```

> No se usan librerías de pathfinding, grafos ni estructuras de datos externas. `heapq` y `collections.deque` de la stdlib están permitidos.

---

## 4. Estructura del proyecto

```
grid-chase/
├── core/                      # Lógica pura — NO importa pygame
│   ├── __init__.py
│   ├── types.py               # Coord, Path, alias de tipos
│   ├── grid.py                # Grid, TileType, costos, vecinos
│   ├── mapfile.py             # Parseo de mapas .txt
│   └── pathfinding/
│       ├── __init__.py
│       ├── base.py            # Protocol Pathfinder, SearchState
│       ├── bfs.py
│       ├── dijkstra.py
│       ├── astar.py
│       ├── heuristics.py      # manhattan, euclidean, octile, zero
│       └── flowfield.py       # Fase 7
│
├── game/                      # Capa pygame
│   ├── __init__.py
│   ├── app.py                 # Game loop, máquina de estados
│   ├── config.py              # Constantes
│   ├── camera.py              # Conversión grid ↔ píxeles
│   ├── renderer.py            # Dibujo de tiles y entidades
│   ├── debug_overlay.py       # Visualización de la búsqueda
│   ├── input.py
│   └── entities/
│       ├── __init__.py
│       ├── entity.py          # Base: posición lógica + interpolada
│       ├── player.py
│       └── guard.py           # Consume un Pathfinder
│
├── assets/
│   ├── sprites/
│   ├── tiles/
│   └── fonts/
│
├── maps/
│   ├── 01_tutorial.txt
│   ├── 02_mud_detour.txt      # Diseñado para que BFS ≠ Dijkstra
│   └── 03_maze.txt
│
├── tests/
│   ├── test_grid.py
│   ├── test_bfs.py
│   ├── test_dijkstra.py
│   ├── test_astar.py
│   └── test_equivalence.py    # BFS ≡ Dijkstra en mapas sin pesos
│
├── main.py
├── requirements.txt
└── README.md
```

**Regla arquitectónica dura:** ningún archivo bajo `core/` puede contener `import pygame`. Se verifica con un test:

```python
def test_core_no_depende_de_pygame():
    for path in Path("core").rglob("*.py"):
        assert "import pygame" not in path.read_text()
```

---

## 5. Contratos de la capa `core`

### 5.1 Tipos base — `core/types.py`

```python
Coord = tuple[int, int]        # (fila, columna)
Path  = list[Coord]            # incluye start y goal
Cost  = float
```

Coordenadas siempre en `(fila, columna)`, nunca `(x, y)`. La conversión a píxeles vive exclusivamente en `game/camera.py`.

### 5.2 Grid — `core/grid.py`

```python
class Grid:
    width: int
    height: int

    def in_bounds(self, c: Coord) -> bool: ...
    def is_walkable(self, c: Coord) -> bool: ...
    def cost(self, c: Coord) -> Cost: ...          # costo de ENTRAR a la celda
    def neighbors(self, c: Coord) -> Iterator[Coord]: ...
```

`neighbors` devuelve solo celdas transitables y dentro de límites. El modo de conectividad (4 u 8 direcciones) es un atributo del `Grid`, no del algoritmo — así los tres algoritmos funcionan igual al cambiarlo.

Con 8 direcciones: el costo de un paso diagonal se multiplica por `√2`, y no se permite cortar entre dos muros en diagonal.

### 5.3 Interfaz de búsqueda — `core/pathfinding/base.py`

```python
@dataclass(frozen=True)
class SearchState:
    """Snapshot de una iteración, para el visualizador."""
    current: Coord | None
    frontier: list[Coord]
    visited: set[Coord]
    cost_so_far: dict[Coord, Cost]
    came_from: dict[Coord, Coord | None]
    finished: bool
    path: Path | None

@dataclass
class SearchResult:
    path: Path                      # vacío si no hay ruta
    nodes_expanded: int
    total_cost: Cost
    cost_so_far: dict[Coord, Cost]

class Pathfinder(Protocol):
    name: str
    def find_path(self, grid: Grid, start: Coord, goal: Coord) -> SearchResult: ...
    def search_steps(self, grid: Grid, start: Coord, goal: Coord) -> Iterator[SearchState]: ...
```

`find_path` debe implementarse consumiendo `search_steps` hasta el final. Así existe una sola versión de la lógica y el modo paso a paso nunca se desincroniza del modo normal.

`nodes_expanded` es obligatorio: es la métrica con la que se compara Dijkstra contra A\*.

### 5.4 Algoritmos requeridos

| Módulo | Estructura | Notas |
|---|---|---|
| `bfs.py` | `deque` | Ignora costos. Sirve de baseline |
| `dijkstra.py` | `heapq` | Prioridad = `costo acumulado` |
| `astar.py` | `heapq` | Prioridad = `costo + h(n)`; heurística inyectada |
| `flowfield.py` | `heapq` | Dijkstra desde el jugador a todo el mapa |

Requisitos de implementación:

- Entradas del heap como `(prioridad, contador, coord)`. El contador incremental evita que Python compare tuplas de coordenadas al empatar.
- Sin `decrease-key`. Se usa *lazy deletion*: se permiten duplicados en el heap y al extraer se descarta si `prioridad > cost_so_far[coord]`.
- Corte temprano al **extraer** el objetivo del heap, nunca al insertarlo.
- Reconstrucción del camino recorriendo `came_from` desde el goal hacia atrás.
- Si no existe ruta, `path` es una lista vacía. No se lanza excepción.

`astar.py` debe ser un diff mínimo sobre `dijkstra.py` — idealmente ambos delegan en una función compartida parametrizada por la heurística, donde Dijkstra pasa `zero_heuristic`. Escribir primero los dos por separado y refactorizar después es parte del ejercicio.

**Heurísticas** (`heuristics.py`): `manhattan` para 4 direcciones, `octile` para 8, `euclidean`, y `zero`. Documentar en el código que la heurística debe ser admisible (nunca sobreestimar) y por qué `manhattan` deja de serlo si se permiten diagonales.

---

## 6. Formato de mapa

Archivo de texto plano en `maps/`. Primera línea opcional con metadata `key=value`, luego la grilla.

```
name=Rodeo por el barro
guards=2
###############
#P..~~~~~~~...#
#...~~~~~~~..*#
#.G.........#.#
###############
```

Reglas: todas las filas de la grilla tienen el mismo ancho; el mapa está cerrado por muros en el perímetro; debe haber exactamente un `P` y al menos un `*`.

El parser (`core/mapfile.py`) valida esto y lanza un error descriptivo con número de línea si falla.

### Mapa obligatorio: `02_mud_detour.txt`

Debe existir al menos un mapa donde BFS y Dijkstra produzcan rutas **visiblemente distintas**: un corredor recto de barro entre guardia y jugador, y un rodeo de piso más largo en celdas pero más barato en costo. Sin este mapa el proyecto no cumple su objetivo pedagógico.

---

## 7. Capa `game`

### 7.1 Game loop

Timestep fijo para la lógica, render desacoplado.

```
dt = clock.tick(60) / 1000
procesar eventos
actualizar entidades (dt)
render
```

### 7.2 Entidades

`Entity` mantiene dos posiciones:

- `cell: Coord` — posición lógica, la única que usa el pathfinding
- `visual: tuple[float, float]` — posición interpolada en píxeles para el render

El movimiento es: elegir celda destino → interpolar `visual` hacia ella durante `move_duration` segundos → al llegar, actualizar `cell`. Nunca se hace pathfinding sobre `visual`.

### 7.3 Guard

```python
class Guard(Entity):
    def __init__(self, cell: Coord, pathfinder: Pathfinder): ...
```

El guardia recibe el `Pathfinder` por inyección y no conoce su tipo concreto. Recalcula la ruta únicamente cuando cambia la celda del jugador, no cada frame. Guarda la última `SearchResult` para que el overlay pueda dibujarla.

A partir de la fase 7, si hay más de un guardia, todos leen un único `FlowField` recalculado una vez por movimiento del jugador.

### 7.4 Debug overlay — el componente más importante

Se activa con `TAB`. Dibuja sobre el mapa:

| Elemento | Representación |
|---|---|
| Nodos cerrados (visited) | Relleno semitransparente frío |
| Frontera (en el heap) | Relleno semitransparente cálido |
| Nodo actual | Borde resaltado |
| Costo acumulado | Número en la esquina de cada celda visitada |
| Camino final | Línea gruesa de centro a centro |
| Dirección `came_from` | Flecha corta hacia el padre |

Panel de texto en esquina: algoritmo activo, `nodes_expanded`, `total_cost`, longitud del camino.

**Modo paso a paso:** con `ENTER` la búsqueda se congela y `ESPACIO` avanza una sola iteración del generador `search_steps`. Esto es lo que convierte el proyecto en una herramienta de aprendizaje y no en un juego más.

### 7.5 Controles

| Tecla | Acción |
|---|---|
| Flechas / WASD | Mover jugador |
| `TAB` | Alternar overlay de debug |
| `1` `2` `3` | Cambiar a BFS / Dijkstra / A\* en caliente |
| `ENTER` | Alternar modo paso a paso |
| `ESPACIO` | Avanzar una iteración (en modo paso a paso) |
| `R` | Reiniciar mapa |
| `M` | Siguiente mapa |
| `ESC` | Salir |

Cambiar de algoritmo con `1`/`2`/`3` sin reiniciar el nivel es un requisito: comparar en el mismo estado es donde se ve la diferencia.

---

## 8. Assets

### Fase de placeholders

Las fases 0 a 1 usan `pygame.draw.rect` con colores planos. No se descarga ningún asset hasta que el movimiento por tiles funcione.

| Elemento | Color placeholder |
|---|---|
| Piso | gris claro |
| Barro | marrón |
| Agua | azul |
| Muro | gris oscuro |
| Jugador | verde |
| Guardia | rojo |
| Objetivo | amarillo |

### Assets finales

- **Tile size:** 32×32 px. Toda la grilla y los sprites usan esta medida.
- **Ventana:** 960×640 (30×20 tiles). Configurable en `game/config.py`.
- **Escalado:** entero (×2) con `pygame.transform.scale` y `pygame.SCALED`, nunca interpolado — el pixel art se ve borroso si se escala con suavizado.

| Recurso | Formato | Cantidad |
|---|---|---|
| Tileset de terreno | PNG, spritesheet 32px | 4 tiles mínimo |
| Sprite jugador | PNG, 4 direcciones × 4 frames | 16 frames |
| Sprite guardia | PNG, 4 direcciones × 4 frames | 16 frames |
| Objetivo | PNG, 32×32, animación opcional | 1–4 frames |
| Fuente | TTF monoespaciada | 1 |

### Fuentes de assets con licencia libre

- **kenney.nl** — CC0, sin atribución. El pack *Roguelike/RPG* encaja exactamente con este proyecto
- **opengameart.org** — filtrar por CC0 o CC-BY
- **itch.io** — sección de game assets gratuitos
- **fonts.google.com** — JetBrains Mono o similar para el overlay de debug

Guardar el archivo de licencia de cada pack en `assets/LICENSES.md`.

### Carga

Un `AssetLoader` carga todo al inicio y cachea las `Surface` en un diccionario. Nunca se llama a `pygame.image.load` dentro del game loop. Aplicar `.convert_alpha()` a cada superficie después de cargarla.

---

## 9. Tests

Los algoritmos se testean sin abrir una ventana de Pygame.

| Test | Qué verifica |
|---|---|
| `test_grid.py` | Vecinos en bordes y esquinas, muros excluidos, costo diagonal |
| `test_bfs.py` | Camino mínimo en pasos sobre grilla 5×5 calculada a mano |
| `test_dijkstra.py` | Rodea el barro cuando conviene; costo total correcto |
| `test_astar.py` | Mismo camino óptimo que Dijkstra, con `nodes_expanded` menor o igual |
| `test_equivalence.py` | En mapas sin pesos, BFS y Dijkstra dan el mismo costo total |
| `test_no_path.py` | Objetivo encerrado por muros devuelve camino vacío sin colgarse |
| `test_start_is_goal.py` | Devuelve `[start]`, costo 0 |
| `test_core_pure.py` | Ningún archivo de `core/` importa pygame |

Usar grillas de 5×5 o 7×7 escritas como strings dentro del propio test, para poder verificar el resultado esperado a mano.

---

## 10. Fases de desarrollo

Cada fase tiene un criterio de aceptación verificable. No avanzar sin cumplirlo.

| # | Fase | Criterio de aceptación |
|---|---|---|
| 0 | Grilla y render | Se abre ventana, se ve un mapa cargado desde `.txt` con rectángulos de colores, cierra con ESC |
| 1 | Movimiento por tiles | El jugador se mueve con interpolación suave, no atraviesa muros |
| 2 | Sprites y animación | Sprites animados con dirección correcta; tileset reemplaza los rectángulos |
| 3 | Algoritmos aislados | BFS y Dijkstra pasan todos sus tests; Pygame no se ha tocado en esta fase |
| 4 | Guardia + overlay | El guardia persigue; `TAB` muestra la búsqueda; `ESPACIO` avanza paso a paso |
| 5 | Terrenos con peso | En `02_mud_detour`, BFS cruza el barro y Dijkstra lo rodea, y se ve en pantalla |
| 6 | A\* | `1`/`2`/`3` cambian algoritmo en caliente; el panel muestra que A\* expande menos nodos |
| 7 | Flow field | 5 guardias con una sola corrida de Dijkstra por movimiento del jugador |

La fase 3 es el núcleo del proyecto. Si el tiempo se acaba, es preferible tener las fases 0, 3, 4 y 5 completas con gráficos feos que un juego bonito con pathfinding a medias.

---

## 11. Errores comunes a evitar

- **Escribir un heap propio en la fase 3.** Usar `heapq` primero. Reemplazarlo por una implementación propia es un ejercicio posterior, no simultáneo — si se mezclan, al fallar no se sabe cuál de los dos está roto.
- **Cortar al insertar el goal en el heap.** Da rutas subóptimas. Se corta al extraerlo.
- **Olvidar el contador en la tupla del heap.** Funciona hasta el primer empate de costos y entonces revienta con `TypeError`.
- **Hacer pathfinding sobre la posición visual interpolada.** Produce rutas erráticas. Solo `cell` entra al algoritmo.
- **Recalcular la ruta cada frame.** Con un mapa grande baja el framerate y oculta el problema real.
- **Filtrar colores, `Rect` o `Surface` hacia `core/`.** Es la vía más rápida a un módulo imposible de testear y de portar.
- **Heurística no admisible en A\*.** `manhattan` con movimiento diagonal permitido sobreestima y rompe la optimalidad. Con 8 direcciones va `octile`.

---

## 12. Extensiones posteriores

- **Fog of war:** el guardia solo conoce las celdas que ha visto, y replanifica al descubrir muros. Puerta de entrada a D\* Lite.
- **Jump Point Search:** optimización de A\* para grillas uniformes.
- **Costos dinámicos:** el jugador deja charcos que encarecen las celdas, forzando replanificación.
- **Benchmark:** modo headless que corre los tres algoritmos sobre los mapas y emite una tabla de tiempo y nodos expandidos.
- **Port a navegador:** `pygbag` para WASM, o reescribir solo `game/` en TypeScript reutilizando la lógica de `core/` traducida.
