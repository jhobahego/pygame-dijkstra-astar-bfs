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
