# El Sol Negro: Thule, Vril y la Base 211

Video vertical **9:16 (1080×1920, 30 fps, H.264)** de **180 s exactos**, con estilo **low-poly 3D
oscuro**, hecho solo con código (Manim CE) y narrado con edge-tts (`es-ES-AlvaroNeural`).

## Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Escenas `Block0` a `Block6` y `FullVideo`. Comprueba que cada bloque termina en su frame exacto. |
| `poly.py` | El motor low-poly. `low_poly()` triangula cualquier contorno en anillos con ruido y sombrea cada cara según una luz arriba-izquierda, con un velo blanco al 20 % en las caras iluminadas. `Revolve` crea sólidos de revolución en 3D real (caras ocultas descartadas, orden del pintor, rotación). También contiene las figuras: Sol Negro de 12 runas Sig extruidas, médiums, Alemania, Thule, Antártida, martillo, barco, avión, malla Victalen y sello. |
| `narration.py` | Narración por bloques con ajuste automático de velocidad; genera `narration.mp3` de 180 s. |

Reutiliza `../kabala_video/utils.py`: reloj por frames, texto cinético palabra a palabra, glitch y wipe.

## Uso

```bash
pip install manim edge-tts            # y ffmpeg en el PATH
python narration.py                   # → narration.mp3 (180 s)
manim -qh --disable_caching main.py FullVideo
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest output_final.mp4
```

Para una vista previa rápida a 540×960: `KABALA_PREVIEW=1 manim --disable_caching main.py Block3`.

## Recurso recurrente

Un **Sol Negro facetado** gira detrás de todo el video. Sus runas se encienden en rojo de dos
en dos con cada bloque, se reconstruye en oro y se fragmenta en el bloque 3, y al final se
convierte en una malla de alambre cian que se disuelve.

## Cambios respecto al guion

- **Encuadre «según la leyenda».** El relato de Maria Orsic y Aldebarán, las naves Haunebu y la
  Base 211 se presentan como leyenda: una etiqueta «SEGÚN LA LEYENDA» en los bloques 2, 4 y 5, y
  «según la leyenda / dice el mito» en la narración. No hay documentos de la época que lo
  respalden; el mito se difundió después de la guerra. Thule, Sebottendorf, Wewelsburg y la
  Operación Highjump sí son hechos históricos y se cuentan como tales.
- **Sin esvástica.** No se dibuja el emblema de Thule. El Sol Negro aparece porque es el eje
  del guion, pero se fragmenta y se disuelve; no se presenta como emblema que celebrar.
- **Frases de más de 8 palabras**, repartidas en dos pantallas: «El ocultismo no era un mito.» →
  «Era un arma.»; «Thule. Vril. Sol Negro.» → «Una Alemania que buscaba dioses en el hielo.»; el
  CTA de apertura; «Buscaban el origen de la raza aria.» → «En Thule o en la Atlántida.»;
  «Almirante Richard Byrd.» → «¿Destruir la base o enfrentarse a ella?».
- **«Haunebu-II: 31 metros»** no está en §1. En pantalla aparece «Haunebu: de 25 a 40 metros»
  y «Haunebu-II: 6.000 km/h».
- **Gancho del bloque 3:** «El símbolo que Himmler hizo esculpir en el suelo» (9 palabras)
  pasa a «Himmler lo hizo esculpir en el suelo.».
- **Narración:** es la de §5, con datos literales de §1 añadidos para llenar cada ventana de
  30 s (nombres de las cinco médiums, «energía de torsión», versión oficial de Highjump,
  «Schwarze Sonne», «25 a 40 metros»).
- **Datos que no están en §1 y vienen de tu §5**, mantenidos: Heinrich Himmler y «muchos nazis
  huyeron en 1945».
- **Fuentes:** no se citan en pantalla, como pedía el guion.
