# Cábala: el código oculto del universo

Video vertical **9:16 (1080×1920, 30 fps, H.264)** de **180 s exactos**, generado solo con código
(**Manim Community Edition**) y narrado con **edge-tts** (voz `es-ES-AlvaroNeural`).
Sin assets externos: fondo, partículas, diagramas, letras hebreas e iconos se generan por código.

## Estructura

| Archivo | Contenido |
|---|---|
| `main.py` | Escenas `Block0` … `Block6` y `FullVideo` (concatena los 7 bloques). Comprueba con `assert` que cada bloque termina en su frame exacto y que el total es 5400 frames. |
| `utils.py` | Configuración 1080×1920 a 30 fps, paleta, safe zones, `kinetic_text()`, `TreeOfLife`, fondo de archivo (numpy), polvo, glitch, wipe de pergamino y reloj por frames (`KabalaScene`). |
| `blocks.py` | Guion de §4, segundo a segundo, en tiempos absolutos. |
| `shapes.py` | Iconografía vectorial: ojo de la providencia, Merkavá, hekhalot, Adam Kadmón, kamea, qlifot, Gólem, Templo, escuadra y compás, fichas, burbuja de comentario. |
| `narration.py` | TTS por bloques, ajuste automático de velocidad y montaje de `narration.mp3` (180 s). |

## Requisitos

```bash
# Python 3.11 (también probado con 3.13) · Manim CE 0.18+ (probado con 0.22.1)
pip install manim edge-tts
# ffmpeg y ffprobe en el PATH. En Linux, Manim necesita además: libcairo2-dev libpango1.0-dev pkg-config
```

Fuentes usadas: **DejaVu Sans / DejaVu Serif / DejaVu Sans Mono** (incluyen hebreo). Si no están
instaladas, Pango usa una fuente de reserva.

## 1 · Narración

```bash
python narration.py
```

- Genera `audio/bloque_0.mp3` … `audio/bloque_6.mp3` con
  `edge-tts --voice "es-ES-AlvaroNeural" --text "FRASE" --write-media "bloque_X.mp3"`.
- Mide cada bloque y lo vuelve a sintetizar con `--rate=±N%` hasta que llena su ventana
  (15/30/30/30/30/30/15 s) menos 0,35 s de respiración, así que no quedan huecos largos.
- Coloca cada bloque en su segundo exacto (0, 15, 45, 75, 105, 135, 165) y exporta
  **`narration.mp3` de 180 s**. El informe de tiempos queda en `audio/timing.json`.
- Si hay proxy: `export EDGE_TTS_PROXY=http://host:puerto`.

## 2 · Video

```bash
manim -qh --disable_caching main.py FullVideo
# salida: media/videos/main/1920p30/FullVideo.mp4
```

`utils.py` fija 1080×1920 a 30 fps, por encima de lo que digan los flags `-q*`. Alternativas:

```bash
python main.py                         # mismo resultado que el comando anterior
python main.py --scene Block4          # un bloque suelto, con el estado del HUD de ese momento
KABALA_PREVIEW=1 manim --disable_caching main.py FullVideo   # vista previa 540×960
```

## 3 · Fusionar audio y video

```bash
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest output_final.mp4
```

(Forma genérica: `ffmpeg -i output_video.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest output_final.mp4`.)

## Línea de tiempo

| Bloque | Tiempo | Visual principal | Sefirá del HUD |
|---|---|---|---|
| 0 · Gancho + CTA | 0:00–0:15 | El contorno dorado del árbol se dibuja, se ilumina y se repliega al HUD; ojo de la providencia; cintillo «Quédate» con flecha parpadeante | Kéter |
| 1 · Merkavá | 0:15–0:45 | Carro de fuego con ruedas giratorias; 7 palacios (hekhalot) con guardianes; Séptimo Palacio en oro con zoom; el carro se transforma en el árbol | Jojmá |
| 2 · Árbol de la Vida | 0:45–1:15 | 10 sefirot numeradas; 22 senderos con sus letras; 10 + 22 = 32; zoom a la Álef; Adam Kadmón | Biná |
| 3 · Ein Sof y nombres | 1:15–1:45 | EIN SOF con anillos infinitos; letras flotando; rejilla de 72 con 40 en oro; kamea con אדני | Jésed |
| 4 · Árbol de la Muerte | 1:45–2:15 | El árbol se voltea y se vuelve rojo; cáscaras rotas en desequilibrio; Gólem de barro animado por letras | Guevurá |
| 5 · Masonería | 2:15–2:45 | Templo de Salomón; escuadra y compás sobre el árbol; fichas de Pico della Mirandola y Robert Fludd | Tiféret |
| 6 · Cierre + CTA | 2:45–3:00 | ETZ JAIM y QLIFOT superpuestos; el HUD completa las 10 sefirot y se invierte en rojo; CTA final y burbuja de comentario | Nétsaj → Maljut |

## Reglas aplicadas

- **Duración exacta**: cada `play()` usa `run_time = (n − 0,5)/30`, con lo que Manim genera
  exactamente *n* frames. Los rellenos (`until()`) siempre llevan movimiento (respiración del
  foco, polvo, ruedas, anillos), nunca un `wait` estático.
- **Texto**: como máximo 8 palabras por pantalla (`kinetic_text` lanza un error si se supera),
  aparición palabra a palabra sin `Write`. Tamaños en px reales: cuerpo 56, fuentes 48,
  ganchos 66–80, EIN SOF 96 (`px()` convierte a `font_size` de Manim).
  Dos frases de §4 tienen 9 palabras y se reparten en dos pantallas seguidas:
  «Quédate.» → «El nombre del árbol invertido aparece al final.» y
  «La Cábala está…» → «…en la base de la masonería.»
- **Safe zones**: todo el contenido queda dentro de x ∈ [60, 1020] px e y ∈ [230, 1536] px.
- **Hebreo**: Pango no dibuja un párrafo que empieza por un carácter RTL, así que `T()` antepone
  una marca LRM invisible.

## Notas sobre los datos

- La narración de §5 se usa tal cual, con añadidos tomados **literalmente de §1** para que todos
  los datos aparezcan en video o en voz: *hekhalot*, la definición de Cábala, «Árbol Infernal»,
  «pieles», Durán/Zenit, «clave simbólica» y el nombre del árbol invertido (Qlifot), que cumple
  la promesa del CTA de apertura.
- En pantalla aparecen como etiquetas: Éxodo 14:19-21, curación · protección, Kabbalah Ma’asit,
  kameot, Sefer Raziel HaMalakh, Hashem · Adonai y R∴E∴A∴A∴.
- El texto de §4/§5 que escribiste incluye algunos elementos que no están en la tabla de §1 y que
  se han mantenido por venir de tu guion: el ojo de la providencia, la ruptura de los vasos,
  Pico della Mirandola y Robert Fludd, «Libro de la Formación» y Maljut como Reino y pies.
- En el diagrama, la asignación de letras a senderos sigue el orden clásico de 22 senderos
  y es solo decorativa: no se enuncia como dato.
