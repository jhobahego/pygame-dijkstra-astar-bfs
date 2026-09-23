# TODO — trabajo futuro (fuera de las tareas T1–T10)

## Transparencia en sprites de entidades (máscara/colorkey)

- **Contexto:** `game/assets.py` (`AssetLoader`, T3) recorta los sprites de
  jugador y guardia desde los sheets JPEG de `assets/`, que son opacos. Las
  superficies de 32x32 conservan el fondo gris de la celda y el renderer las
  blitea tal cual.
- **Problema:** al dibujar una entidad sobre un tile se ve el recuadro gris
  del fondo en lugar del tile que hay debajo.
- **Alternativas:**
  1. `Surface.set_colorkey`: barata, pero el fondo JPEG tiene ruido y los
     grises del sprite ( Guardia ) pueden coincidir con el fondo.
  2. Máscara por distancia de color con tolerancia + limpieza de bordes, o
     regenerar los recortes desde una fuente con alfa real.
- **Criterio de aceptación:** jugador y guardia se dibujan sobre cualquier
  tile sin halo ni recuadro visible, y `tests/test_assets.py` lo cubre
  (p. ej. esquinas de la superficie con alfa 0).
- **Restricción:** no descargar assets nuevos; trabajar solo con los
  spritesheets ya incluidos en `assets/`.

## Error al cambiar algoritmo y abrir tab

- **Contexto** En alguna se dispara una acción al presionar la tecla tab o
  1/2/3 para seleccionar los algoritmos de busqueda del guardia.
- **Problema** En el momento en el que el guardia deja desaparece al alcanzar
  al jugador si presiono tab o 1/2/3 se me cierra la ventana del juego y me
  lanza un error por consola relaciona con la función `draw_search_state` en 
  `game/debug_overlay.py` especificamente en la función `pygame.draw.lines` con
  el mensaje "ValueError: points argument must contain 2 or more points".
  Supongo que esto es porque se perdio la referencia del guardia y no se puede
  dibujar la lineas porque no se tiene un origen, si me deja reiniciar, cambiar el
  el mapa y mostrar el overlay con tab. Cuando doy enter e intento avanzar una
  iteración con espacio despues de que desaparece el guardia entonces se reproduce
  el error. Este es un posible edge case para ser testeado.

## Estados de juego (victoria / derrota) y congelado del camino

- **Contexto:** `game/app.py` (`App.update`) no tiene estados de juego: tras
  ser alcanzado por el guardia el jugador puede seguir moviéndose y el guardia
  sigue replanificando (`Guard.replan` ante cada cambio de celda), por lo que
  el overlay recalcula y repinta el camino indefinidamente. Los objetivos del
  mapa (`MapData.goals`, dibujados como estrella por `Renderer.draw_map`)
  tampoco detienen la partida al alcanzarlos.
- **Problema:** no hay condición de fin: ni la victoria (llegar al objetivo sin
  ser alcanzado) ni la derrota (guardia alcanza al jugador) detienen el juego.
- **Propuesta:**
  1. Crear los estados del juego (p. ej. `PLAYING` / `WON` / `LOST`) con sus
     transiciones en `App`: derrota cuando guardia y jugador comparten celda,
     victoria cuando el jugador pisa un `goal` sin haber sido alcanzado.
  2. Al entrar en `WON` o `LOST`: bloquear el movimiento del jugador y del
     guardia (y el replanificado/stepping), de modo que el camino quede
     congelado.
  3. En derrota (con overlay activo): mostrar el camino hasta el punto donde se
     alcanzó al jugador. En victoria: dejar de pintar el camino.
  4. Opcional: mostrar leyenda "ganaste" / "perdiste" según el estado.
- **Criterio de aceptación:** tras victoria o derrota las entidades no se
  mueven, el camino ya no se recalcula, y el overlay (si está activo) refleja
  lo descrito en el punto 3.
- **Restricción:** los estados deben funcionar tanto con el debug/overlay
  activo como sin él (el fin del juego no depende del overlay; solo lo del
  dibujado del camino aplica al debug).
