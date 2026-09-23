# Contexto y Guía del Agente — Grid Chase

Este repositorio contiene el proyecto **Grid Chase**, un videojuego educativo *top-down* por tiles desarrollado en Python y Pygame (fork `pygame-ce`), cuyo propósito principal es comprender y comparar visualmente algoritmos de búsqueda de caminos (BFS, Dijkstra, A*, FlowField) en grillas con terrenos de costos variables.

---

## 1. Especificaciones del Proyecto y Documentación de Referencia

- **Especificación principal:** Consulte [ESPECIFICACION.md](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/ESPECIFICACION.md) para todos los detalles del diseño del juego, contratos de clases, algoritmos, mapas, controles y fases de desarrollo.
- **Especificación de Tareas:** Consulte [specs/grid-chase.md](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/specs/grid-chase.md) para la división en tareas ejecutables (T1 a T10).
- **Dirección de Arte y Assets:** Consulte [direccion_de_arte.html](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/direccion_de_arte.html) para la guía de estilo y dirección visual del proyecto.
  > [!IMPORTANT]
  > Los sprites que se muestran en el documento `direccion_de_arte.html` son únicamente de muestra. Los assets reales del juego se encuentran en un spritesheet dentro de la carpeta [assets](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/assets) (`assets/spritesheet-dijkstra-game-example.jpeg`), los cuales deben utilizarse obligatoriamente en el desarrollo.

---

## 2. Stack Tecnológico y Dependencias

- **Lenguaje:** Python 3.11+ (uso de `match`, `tuple[int, int]`, `list[Coord]`).
- **Librería gráfica:** `pygame-ce>=2.5.0` (definida en [requirements.txt](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/requirements.txt)).
- **Dependencias de Desarrollo:**
  - `pytest>=8.0`
  - `mypy>=1.11`
  (definidas en [requirements-dev.txt](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/requirements-dev.txt)).
- **Restricción de dependencias:** No se utilizan librerías externas de pathfinding o grafos (como NetworkX o SciPy). Se utiliza únicamente la biblioteca estándar (`heapq`, `collections.deque`).

---

## 3. Reglas Arquitectónicas de Obligado Cumplimiento

1. **Pureza de `core/` (Regla Dura):**
   - El módulo `core/` contiene la lógica pura del juego y los algoritmos.
   - **NUNCA** importar `pygame` ni módulos de `game/` dentro de `core/`. Esto se valida mediante el test automatizado `test_core_pure.py`.
2. **Sistema de Coordenadas:**
   - En `core/`, las coordenadas se manejan estrictamente como `Coord = tuple[int, int]` en formato `(fila, columna)`.
   - La conversión entre coordenadas de grilla y píxeles en pantalla vive exclusivamente en `game/camera.py`.
3. **Contratos de Algoritmo:**
   - La búsqueda consume iteradores `search_steps(...) -> Iterator[SearchState]` para permitir la visualización paso a paso y el cálculo directo en `find_path(...)`.
   - En heappush, las tuplas deben incluir un contador incremental: `(prioridad, contador, coord)` para evitar comparaciones directas de coordenadas al empatar costos.
   - Usar *lazy deletion* y corte temprano al **extraer** el objetivo del heap (nunca al insertarlo).

---

## 4. Estructura de Directorios

```
grid-chase/
├── core/                      # Lógica pura (SIN pygame)
│   ├── types.py               # Coord, Path, Cost
│   ├── grid.py                # Grid, TileType, costos y vecinos
│   ├── mapfile.py             # Parser de mapas .txt
│   └── pathfinding/           # BFS, Dijkstra, A*, Heurísticas
├── game/                      # Capa Pygame (Game loop, render, overlay, entidades)
│   ├── app.py, camera.py, debug_overlay.py, renderer.py, ...
├── assets/                    # Recursos visuales (spritesheet-dijkstra-game-example.jpeg, README.md)
├── maps/                      # Archivos de mapa .txt (01_tutorial.txt, 02_mud_detour.txt, etc.)
├── specs/                     # Specs ejecutables por el agente (grid-chase.md)
├── tests/                     # Test suite (pytest)
├── direccion_de_arte.html     # Documento de dirección de arte
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias de producción
└── requirements-dev.txt       # Dependencias de desarrollo
```

---

## 5. Flujo de Trabajo y Buenas Prácticas (.agents/skills)

Todo agente que trabaje en este repositorio debe aplicar rigurosamente las habilidades ubicadas en [.agents/skills](file:///home/jhobadev/Escritorio/Dev/dijkstra-game-example/.agents/skills):

- **`using-superpowers`:** Activar e invocar la habilidad adecuada antes de realizar cambios significativos.
- **`scope`:** Convertir ideas o requerimientos en specs claras con diagramas ASCII y tareas bien definidas (`specs/<slug>.md`).
- **`writing-plans` / `executing-plans`:** Planificar cambios antes de codificar y registrar el avance paso a paso.
- **`test-driven-development` (TDD):** Implementar o ajustar módulos en `core/` escribiendo o ejecutando primero los tests unitarios correspondientes en `tests/`.
- **`systematic-debugging`:** Investigar metódicamente cualquier error o falla de test antes de proponer cambios acelerados.
- **`audit`:** Revisar el `git diff` contra la especificación verificando alcance, simplicidad y adherencia a las reglas de pureza.
- **`prove` / `verification-before-completion`:** No asumir que el código funciona. Ejecutar la suite de pruebas real y verificar la salida antes de declarar una tarea completada.
- **`ship`:** Crear mensajes de commit estandarizados con Conventional Commits explicando el motivo del cambio.

---

## 6. Comandos Frecuentes

- **Crear el entorno virtual `.venv` (paso obligatorio antes de instalar nada):**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
  Todo lo que sigue se ejecuta con el `.venv` activado. El Python del sistema está gestionado externamente (PEP 668) y no admite `pip install` directo.
- **Instalar dependencias de desarrollo:**
  ```bash
  pip install -r requirements-dev.txt
  ```
- **Ejecutar la suite de pruebas:**
  ```bash
  pytest
  ```
- **Verificar análisis estático y tipos:**
  ```bash
  mypy core
  ```
- **Ejecutar el juego:**
  ```bash
  python main.py
  ```
