# 25 millones de años de guerra oculta

Vídeo vertical 9:16 (1080×1920, 30 fps, H.264 + AAC) de unos 180 s, hecho solo con geometría
generada en Manim CE y narrado con edge-tts (`es-ES-AlvaroNeural`, pitch −4 Hz).

## Pipeline

```bash
pip install manim edge-tts numpy          # + ffmpeg/ffprobe en el PATH
python narration.py                       # narration.wav, audio_final.wav (voz + drone), timings.json
manim render main.py HistoriaOculta -r 1080,1920 --fps 30
python narration.py --mux media/videos/main/1920p30/HistoriaOculta.mp4   # -> historia_oculta_final.mp4
```

Vista previa rápida (540×960, 15 fps): `PREVIEW=1 manim render main.py HistoriaOculta`.

## Archivos

| Archivo | Contenido |
|---|---|
| `narration.py` | Un clip por bloque; recorte de silencios a −45 dB con 0,06 s de cola; pausas internas acotadas a 0,28 s; calibración de `rate` (+15 % → rango −5…+25 %; si no basta, quita los `[OPCIONAL]`); drone de 55 + 110 Hz a −26 dB; `--mux` |
| `main.py` | Escena `HistoriaOculta` con `block_B0` … `block_B10`, helper `Timeline`, `assert_safe`, pirámide recurrente, polvo estelar de 220 partículas con `updater(dt)` y viñeta |
| `timings.json` | Inicio y duración reales de cada bloque |
| `render_report.txt` | Lo genera el render: error de inicio de cada bloque (en fotogramas), `renderer.time` y pico de palabras visibles |

## Cómo se cumplen las reglas

* **Tiempo exacto:** `Timeline` reparte cada bloque por pesos (los segundos nominales del guion) en
  fotogramas enteros. Como Manim genera `ceil(run_time·fps)` fotogramas, se usa
  `run_time=(n−0,5)/fps`. Cada bloque termina en su fotograma absoluto de `timings.json` y no hay
  `self.wait()`.
* **8 palabras como máximo:** cada texto se registra con su número de palabras (los «·» cuentan).
  Después de cada `play` se suman los textos visibles y el informe muestra el pico y las
  infracciones.
* **Safe-zone:** `assert_safe()` se ejecuta en cada texto. Si alguno se sale, el render se detiene.
* **Fuentes:** se busca en orden Bebas Neue → Oswald → Montserrat → DejaVu Sans; la terminal usa
  DejaVu Sans Mono. Nunca falla si falta una.
* **Bucle:** el primer fotograma es un punto dorado en la posición del ojo, y el último es ese
  mismo punto al colapsar el ojo.
