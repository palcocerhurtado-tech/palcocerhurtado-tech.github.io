# Hermes Trismegisto: el código del 3 y el 33

Video vertical **9:16 (1080×1920, 30 fps, H.264)** de **180 s exactos**, con geometría sagrada
hecha solo con código (Manim CE) y narrado con edge-tts (`es-ES-AlvaroNeural`).

## Uso

```bash
pip install manim edge-tts            # y ffmpeg en el PATH
python narration.py                   # → narration.mp3 (180 s, se ajusta sola a cada bloque)
manim -qh --disable_caching main.py FullVideo     # o: python main.py
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest output_final.mp4
```

Para una vista previa rápida a 540×960: `KABALA_PREVIEW=1 manim --disable_caching main.py Block4`.
El proyecto usa el motor de `../kabala_video/utils.py` y las mallas de `../thule_video/poly.py`,
así que esas dos carpetas tienen que estar al lado.

## El sello recurrente

En la esquina superior izquierda gira un sello que gana una capa en cada bloque:

| Bloque | Capa que se añade |
|---|---|
| 0 | Triángulo |
| 1 | Círculo |
| 2 | Las tres cuerdas de la lira |
| 4 | Las 33 cuentas de la misbaha y el segundo triángulo (Estrella de David) |
| 6 | El sello completo se dibuja en grande, colapsa en un «33» estilizado y recibe el sello «HERMES» |

## Cambios respecto al guion

- **Si-o-se-pol** es *un* puente de **33 arcos**, no «33 puentes»; así aparece en pantalla y en
  la narración.
- **Cadena de la sabiduría:** Hermes → Zoroastro → Orfeo → Pitágoras → Ficino, que son los
  transmisores de la Prisca Theologia según §1. Platón no está en §1 y se ha quitado.
- **Frases de más de 8 palabras**, repartidas en dos pantallas: el gancho del bloque 2, el CTA
  de apertura, «Lo que está arriba…» → «…es como lo que está abajo.», la frase del Islam, la de
  la gnosis («33 años de Cristo» → «33 emanaciones»), la de las matemáticas y «La base de la
  geometría, la música y la astrología». En el CTA final, la burbuja de comentario muestra solo
  «¿Crees que el 33 es solo un número?».
- **Datos de §1 que no cabían en la narración**, puestos en pantalla:
  - «aa aa → grande, grande»
  - «griego · siglos I–III · Dios · cosmos · hombre»
  - «3 sinfonías · 3 quaterniones»
  - los tres mundos (inteligible, celeste y sublunar)
  - TASBIH, TAHMID y TAKBIR ×33
  - «33 = 3 × 11», «1+3+11 = 15 < 33 · defectivo», «semiprimo · libre de cuadrados»,
    «repdigit · primo nº 33 = 137»
  - «REAA · grado 33 · Consejo Supremo: máx. 33 · 32 sendas + el gran círculo»
- **Fuentes:** no se citan en pantalla.
