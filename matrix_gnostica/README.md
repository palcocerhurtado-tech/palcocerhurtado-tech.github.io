# El código gnóstico: de Nag Hammadi a Matrix

Video vertical **9:16 (1080×1920, 30 fps, H.264)** de **180 s exactos**, hecho solo con código
(Manim CE, estilo poligonal facetado) y narrado con edge-tts (`es-ES-AlvaroNeural`).

## Uso

```bash
pip install manim edge-tts            # y ffmpeg en el PATH
python narration.py                   # → narration.mp3 (180 s, se ajusta sola a cada bloque)
manim -qh --disable_caching main.py FullVideo     # o: python main.py
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest output_final.mp4
```

Para una vista previa rápida a 540×960: `KABALA_PREVIEW=1 manim --disable_caching main.py Block3`.
El proyecto usa el motor de `../kabala_video/utils.py` (reloj por frames, texto cinético, glitch
y wipe) y las mallas low-poly de `../thule_video/poly.py`, así que esas dos carpetas tienen que
estar al lado.

## La malla «Matrix» (recurso recurrente)

`MatrixMesh` es una lámina de unos 360 triángulos sombreados que late durante todo el video.
Así cambia bloque a bloque:

| Bloque | Estado de la malla |
|---|---|
| 0 | Se dibuja en cian y pasa a púrpura (ilusión). |
| 1 | Se ilumina en oro con la chispa divina y vuelve al púrpura. |
| 2 | Se agrieta: aparecen grietas doradas y un núcleo de luz debajo. |
| 3 | Se tiñe de verde bajo la lluvia binaria. |
| 4 | Se fragmenta alrededor de Neo y acaba convertida en luz dorada. |
| 5 | Se desintegra en partículas. |
| 6 | Se convierte en una lluvia de código que se disuelve. |

## Cambios respecto al guion

- **Frases de más de 8 palabras**, repartidas en dos pantallas: «Tu película favorita está
  basada…» → «…en la segunda venida de Cristo.» → «Y no lo sabías.»; «El mundo no fue creado
  por Dios.» → «Fue creado por un carcelero.»; el CTA de apertura; «Nag Hammadi. El Demiurgo.
  Los Arcontes.» → «Matrix. Una pregunta.».
- **Demiurgo:** se dibuja como serpiente con cabeza de león, como lo describen los textos
  gnósticos, y no como león con cabeza de serpiente. No lleva ninguna etiqueta que lo afirme.
- **Datos de §1 que faltaban en la narración**, añadidos: *La Hipóstasis de los Arcontes*
  (también en pantalla) y el *Evangelio de Tomás*, «esferas planetarias», «ciclo de
  reencarnación», «Cristo interior» y la definición de gnosis.
- **Bibliografía:** Jonas, Pagels y Wilson se mencionan solo en la narración (bloque 5), porque
  el guion prohíbe citar fuentes en pantalla.
- **Apóstoles:** los nombres Tomás, Felipe y María Magdalena vienen de tu §4.
- **El verde del código** (`#3BD16F`) no está en la paleta de §3. Se usa solo en la lluvia
  binaria, porque §4 pide «código binario verde».
