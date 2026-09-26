# Estados de juego (victoria / derrota) y congelado del camino

## Contexto

- Existe `game/app.py` (`App` con `update`/`render`/`handle_events`) sin estados: tras ser alcanzado, el jugador se sigue moviendo y `Guard.replan` recalcula ante cada cambio de celda; los `MapData.goals` no detienen la partida.
- Existe `game/entities/guard.py` (`Guard.update_guard`: replan solo si cambia la celda del jugador + avanza `_route` + anima) y `game/debug_overlay.py` (`draw_search_state` ya tolera `path` de 1 punto con `len >= 2`).
- Patrón a seguir: `game/entities/guard.py` ya separa lógica (`cell`) de visual (`pixel` + interpolación `dt`); `game/app.py` ya hace `fill → draw_map → overlay → actores → panel → flip`.
- Decisión tomada: skill `/pygame-core` (`.agents/skills/pygame-core/SKILL.md`) es la referencia obligatoria para el loop y movimiento — un solo loop eventos → update → draw → flip, `dt = clock.tick(FPS) / 1000` en segundos, posiciones float + blit entero, `Sprite/Rect`, orden pintor (fondo primero, banner último). Toda la feature se implementa bajo esas prácticas, sin romper `core/` (puro, sin `pygame`).
- Decisión tomada: derrota prioritaria sobre victoria si coinciden en la misma celda.

## Objetivo

Añadir `PLAYING / WON / LOST` a `App` con transiciones por celdas y congelado total del camino al terminar.

## Flujo

```text
SECUENCIA (orden temporal ↓)
1. Jugador → App.update: request_move + player.update(dt)
2. Guardia → App.update: update_guard (replan si cambió celda jugador + avanza ruta)
3. App → App: _update_state() (derrota si guard.cell == player.cell, sino victoria si player.cell en goals)
4. App → App: si terminal, state=WON/LOST + _exit_step_mode() (congela stepping)
5. App → Overlay: LOST dibuja last_state congelado, WON no dibuja search_state
6. App → Pantalla: banner ¡GANASTE!/¡PERDISTE! + panel con estado
7. Jugador → App: R/M recarga mapa y vuelve a PLAYING
```

```text
update (PLAYING, no step_mode)
   │
   ▼
mover jugador + guardias (replan solo si cambió celda)
   │
   ▼
¿guard.cell == player.cell? ──sí──▶ LOST → _exit_step_mode → congelar (solo update_visual) → overlay muestra path congelado + banner
   │ no
   ▼
¿player.cell en goals? ──sí──▶ WON → _exit_step_mode → congelar → overlay oculta path + banner
   │ no
   ▼
seguir en PLAYING
   │
   ▼
casos borde:
- derrota gana si ambos en goal
- step_mode activo → update retorna, la partida no puede terminar
- overlay on/off no afecta la transición (solo el dibujado)
- en terminal: 1/2/3, ENTER, SPACE ignorados; TAB/R/M/ESC siguen
- en terminal: interpolación se drena (update_visual) sin replan ni avance de ruta
- path de 1 celda (guardia sobre jugador) no crashea draw_search_state
- R/M desde cualquier estado → PLAYING
```

## Restricciones

- No tocar `core/` ni su contrato (`Grid`, `Pathfinder`, `search_steps`); la transición solo lee `cell` y `data.goals`.
- Seguir `/pygame-core`: `dt` en segundos para `update(dt)`, sin `pygame.image.load` en el loop, orden pintor con banner al final, `event.get()` drenado cada frame.
- No recalcular búsqueda en `WON`/`LOST`: ni `replan`, ni `_begin/_advance_step`, ni `_switch_algorithm`.
- No añadir dependencias nuevas; `GameState` con stdlib (`enum`).
- Conservar `TAB` (overlay), `R` (retry) y `M` (siguiente mapa) operativos en estados terminales.

## Fuera de alcance

- Transparencia/colorkey de sprites (TODO aparte en `TODO.md`).
- Recolección múltiple de objetivos / contador de goles (victoria = pisar cualquier `goal`).
- Persistencia, audio, partículas, menú principal o pausa separada de `step_mode`.
- Cambios al crash `draw_search_state` más allá del `len >= 2` ya existente.

## Tareas

### T1: Estado y transiciones en App

- **Hacer:** Crear `game/state.py` (`GameState.PLAYING/WON/LOST` + `is_over`); añadir `App.state`, reset a `PLAYING` en `_load_map` y método `_update_state()` (derrota primero, luego victoria, con `_exit_step_mode()`).
- **Archivos:** `game/state.py`, `game/app.py`
- **Verify:** `.venv/bin/pytest tests/test_game_state.py -q -k "initial or defeat_when or victory_when or priority or sticky"` pasa.

### T2: Congelado de movimiento y búsqueda

- **Hacer:** Extraer `Guard.update_visual(dt)` (interpolación + animación sin replan/ruta); en `App.update` drenar solo visual si terminal; blindar `_begin_stepping`, `_advance_step`, `_switch_algorithm` y teclas `ENTER/SPACE/1-2-3` en `handle_events` cuando no `PLAYING`.
- **Archivos:** `game/entities/guard.py`, `game/app.py`
- **Verify:** `.venv/bin/pytest tests/test_game_state.py -q -k "frozen or switch_frozen or stepping_blocked or reload"` pasa.

### T3: Overlay diferenciado y leyenda

- **Hacer:** En `render`, si `WON` no dibujar `search_state`; si `LOST` dibujar `last_state` congelado; añadir `_draw_end_banner()` centrada (pintor último) y líneas `¡GANASTE!/¡PERDISTE!` en `_panel_lines()`.
- **Archivos:** `game/app.py`
- **Verify:** `.venv/bin/pytest tests/test_game_state.py -q -k "overlay or banner or single_point"` pasa; manual: `python main.py`, TAB activo, provocar derrota → se ve path congelado + `¡PERDISTE!`; provocar victoria → sin path + `¡GANASTE!`.

### T4: Tests de estados y validación final

- **Hacer:** Añadir `tests/test_game_state.py` (derrota/victoria, prioridad, sticky, congelado sin replan, switch/step bloqueados, reload, overlay on/off, `WON` oculta / `LOST` conserva, banner/panel, path 1-celda).
- **Archivos:** `tests/test_game_state.py`
- **Verify:** `.venv/bin/pytest -q` pasa (102 tests) y `.venv/bin/mypy core` + `.venv/bin/mypy game/state.py game/app.py game/entities/guard.py` sin errores.

## Done (validación final)

- [ ] `.venv/bin/pytest -q` pasa incluyendo `tests/test_game_state.py`.
- [ ] `.venv/bin/mypy game/state.py game/app.py game/entities/guard.py` sin errores nuevos.
- [ ] Manual: tras victoria o derrota las entidades no se mueven, el camino no se recalcula, y el overlay refleja `LOST` = path congelado / `WON` = sin path, con leyenda visible; `R`/`M` reinician a `PLAYING`.
