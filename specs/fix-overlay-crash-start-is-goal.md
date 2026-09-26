# Fix crash overlay con path de un punto (start-is-goal)

## Contexto
- Qué existe hoy: juego Grid Chase en Python 3.11+ con `pygame-ce>=2.5.0`; lógica pura en `core/` (BFS/Dijkstra/A* vía `search_steps` → `SearchState`) y capa de dibujo en `game/` (`game/app.py` loop + `game/debug_overlay.py` overlay). Mapas en `maps/`, tests en `tests/` con `pytest>=8.0` y `mypy` sobre `core`.
- Patrones a seguir: `game/debug_overlay.py` usa funciones de dibujo stateless (`draw_search_state`, `draw_panel`); el `App` posee fuentes y estado de stepping. `tests/test_start_is_goal.py` ya fija el contrato que origina el bug: con `start == goal` el path es `[start]` con costo 0.
- Decisiones ya tomadas (no re-discutir): el flujo de reproducción y el punto de fix fueron aprobados por el usuario; el fix vive SOLO en `game/debug_overlay.py` con una guardia `len(path) < 2` que evita llamar `pygame.draw.lines` (con 1 punto no se dibuja línea adicional: la celda ya queda marcada por el rect de `current`). `core/` no se toca.

## Objetivo
Eliminar el `ValueError: points argument must contain 2 or more points` al mostrar el overlay (TAB) o cambiar de algoritmo (1/2/3) o avanzar stepping (ENTER + ESPACIO) cuando el guardia alcanzó al jugador (`start == goal`, path de 1 punto).

## Flujo
```
SECUENCIA (orden temporal ↓)
1. Jugador → App.update: guardia alcanza celda del jugador (start == goal)
2. App.render → Guard.last_state / _step_state: obtiene SearchState con path de 1 punto
3. App.render → draw_search_state: llama con ese estado (overlay TAB activo)
4. draw_search_state → pygame.draw.lines: CRASH ValueError (exige ≥2 puntos)
```
Diagrama de FLUJO (decisiones y ramas — acá viven los casos borde):
```
 render con overlay ON
    │
    ▼
 ¿hay state? ──no──▶ no dibujar búsqueda (solo panel)
    │ sí
    ▼
 ¿state.path es None o vacío? ──sí──▶ no dibujar línea de path
    │ no
    ▼
 ¿len(path) >= 2? ──no (0 o 1 punto)──▶ NO llamar draw.lines (sin línea; current ya marca la celda)
    │ sí
    ▼
 draw.lines(path) ──▶ ok
```
Casos borde cubiertos: (a) guardia sobre jugador (`path` de 1 celda — el crash reportado); (b) sin path (`None` o `[]`, objetivo inalcanzable); (c) sin guardias (`guards` vacía → `state` es `None`, solo panel); (d) cambio de algoritmo con 1/2/3 y ENTER + ESPACIO tras la captura (replan/stepping con `start == goal`).

## Restricciones
- No tocar `core/` (regla dura de pureza: nunca importar `pygame` ahí; la valida `tests/test_core_pure.py`) ni cambiar los contratos `SearchState` / `search_steps` / `find_path`.
- No tocar el punto 1 de `TODO.md` (transparencia/colorkey de sprites de entidades).
- No añadir dependencias nuevas; solo `pygame-ce` y stdlib ya en uso.
- No cambiar comportamiento de búsqueda ni de movimiento; solo evitar el crash de dibujo.

## Fuera de alcance
- Lógica de captura/game-over, desaparición o remoción del guardia al alcanzar al jugador.
- Rediseño del overlay, del panel de métricas o de los controles (TAB/ENTER/ESPACIO/1-2-3/R/M).
- Transparencia de sprites, assets nuevos y cambios en mapas.

## Tareas
### T1: Guardia anti-crash en `draw_search_state` + test repro
- **Hacer:** en `draw_search_state`, solo llamar `pygame.draw.lines` cuando `state.path` tiene 2 o más puntos (`if state.path and len(state.path) >= 2:`); con 0/1 punto no dibujar línea (el rect de `current` ya marca la celda). Añadir `tests/test_debug_overlay.py` con test repro: construir un `SearchState` finished con `path=[celda]` (caso `start == goal`) y llamar `draw_search_state` sobre una `Surface` con `SDL_VIDEODRIVER=dummy`, assert que no lanza excepción.
- **Archivos:** `game/debug_overlay.py`, `tests/test_debug_overlay.py`
- **Verify:** `SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest tests/test_debug_overlay.py tests/test_start_is_goal.py -v`

### T2: Cobertura de bordes del overlay
- **Hacer:** ampliar `tests/test_debug_overlay.py` con: `path=None` (no dibuja línea), `path=[]` (no dibuja línea), `path` de 2+ puntos (sí dibuja sin error), y regresión del reporte (estado final de `search_steps` con `start == goal` pasado directo a `draw_search_state`). Sin cambios de producción salvo ajustes menores si un borde falla.
- **Archivos:** `tests/test_debug_overlay.py`
- **Verify:** `SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest tests/test_debug_overlay.py -v` y luego suite completa `SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest`

## Done (validación final)
- [ ] `SDL_VIDEODRIVER=dummy .venv/bin/python -m pytest` pasa (incluye `test_debug_overlay.py`, `test_start_is_goal.py` y `test_core_pure.py`)
- [ ] ` .venv/bin/python -m mypy core` pasa (sin cambios en `core/`)
- [ ] Manual: jugar con `python main.py`, llevar al guardia sobre el jugador, pulsar TAB (overlay visible), 1/2/3 (cambio de algoritmo), ENTER + ESPACIO (stepping) — no se cierra la ventana ni hay `ValueError`; con path de 1 punto se ve la celda marcada sin línea de ruta
