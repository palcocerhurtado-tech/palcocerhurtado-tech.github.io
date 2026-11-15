# La verdadera historia oculta: de Lira a QAnon

Vídeo vertical 9:16 (1080×1920, 30 fps, H.264) de **180,0 s exactos**, generado por código con
Manim Community Edition y narrado con edge-tts (`es-ES-AlvaroNeural`). Es un recorrido
especulativo y simbólico por la mitología conspirativa: lirianos y dracos, Anunnaki,
sociedades secretas, Vril/Base 211 y QAnon. En pantalla aparece la etiqueta permanente
"RELATO ESPECULATIVO".

## Archivos

| Archivo | Qué hace |
|---|---|
| `main.py` | 7 escenas (`Block0Hook` … `Block6QAnon`) + `FullVideo`, helper `kinetic_text()`, reloj por fotogramas |
| `narration.py` | Genera `narration.mp3` (180,0 s, voz continua) y `timeline.json` (arranque real de cada plano) |
| `timeline.json` | Sincronía voz↔imagen. Si no existe, `main.py` usa la escaleta de §4 |
| `narration.mp3` | Narración ya generada |

## Uso

```bash
pip install manim edge-tts          # + ffmpeg en el PATH

# 1) Narración + timeline (opcional: ya están incluidos)
python narration.py

# 2) Vídeo (1080x1920 @ 30 fps; la resolución está fijada dentro de main.py)
manim -qh main.py FullVideo
#    vista previa rápida 540x960 @ 15 fps:
PREVIEW=1 manim -ql main.py FullVideo

# 3) Fusionar audio y vídeo
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 \
       -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -t 180 output_final.mp4
```

> La carpeta de salida de Manim se llama según la altura en píxeles (`1920p30`).
> Si tu versión crea otra (p. ej. `1080p30`), ajusta la ruta del comando `ffmpeg`.

## Cómo se consiguen los 180,0 s exactos

* **Audio:** toda la narración se sintetiza en **una sola petición**, así que no hay silencios
  entre bloques. El script ajusta la velocidad (`rate`, ~+22 %) hasta que la duración hablada
  ronda los 180 s, corrige el resto con `atempo`, quita los silencios del principio y del final
  y recorta a 180,000 s.
* **Vídeo:** cada `play()` consume un número entero de fotogramas (`run_time=(n-0.5)/fps`,
  porque Manim genera `ceil(run_time·fps)` fotogramas). Cada plano termina en un fotograma
  absoluto, así que el total es siempre 5400 fotogramas, sin deriva. No se usa `self.wait()`:
  las pausas son derivas lentas del fondo estelar con un leve acercamiento.

## Sincronía con la voz

La narración de §5 dura unos 220 s a velocidad natural, y el bloque 6 de la escaleta solo tiene
15 s para un texto de unos 37 s. Por eso `narration.py` lee las marcas de palabra de edge-tts y
escribe en `timeline.json` cuándo empieza cada frase. `main.py` arranca cada plano en ese
instante. Los bloques duran lo que dura su texto (p. ej. el gancho, unos 9 s; el bloque 6,
unos 31 s), pero cada imagen coincide con lo que se está diciendo. Si borras `timeline.json`,
el vídeo sigue la escaleta de §4 al segundo, pero la voz se desincroniza.

## Normas de diseño aplicadas

* Paleta: `#0A0A0A`, `#E8E6E3`, `#5AC8FA`, `#C9A227`, `#8B0000` (más azul/verde para las
  mutaciones del ADN).
* Fuentes DejaVu Sans (datos) y DejaVu Sans Mono (términos técnicos). `font_size` ≥ 48.
* Como máximo 8 palabras por pantalla: las frases largas se parten en fragmentos sucesivos.
  `Write` solo con ≤ 4 palabras; con más, entrada en cascada palabra a palabra.
* Zonas seguras: x ∈ [60, 1020] px, y ∈ [230, 1536] px.
* Hélice de ADN recurrente: cian → roja (gancho) → azul lirano → azul + verde (Andrómeda) →
  dorada (Anunnaki) → rojo oscuro (nobleza negra) → se fragmenta en sellos "CLASIFICADO"
  apilados.
