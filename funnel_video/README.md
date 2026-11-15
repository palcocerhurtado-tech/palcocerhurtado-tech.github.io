# 313 $: el bot que me hizo resolver 9 acertijos

Video vertical **9:16 (1080×1920, 30 fps)** de **180 s exactos**, contado en primera persona.
Un bot de Telegram («Sol13») me hace resolver 9 acertijos y al final me lleva a una página de
Whop que pide **313 US$** sin explicar qué se compra. El video usa las capturas reales como
pruebas y señala en cada paso en qué etapa del embudo de ventas estamos.

Reutiliza el motor de `../kabala_video/utils.py`: reloj por frames, texto cinético, glitch,
wipe y fondo. La narración usa edge-tts con la voz `es-ES-AlvaroNeural`.

## Privacidad

- Las capturas originales (`evidence_src/`) y los recortes (`assets/`) **no se suben al
  repositorio** (están en `.gitignore`), porque el repositorio es público.
- `prepare_assets.py` **difumina tu foto de perfil de Google Drive** y el contador de chats
  «28720» de Telegram antes de recortar.
- Solo aparecen los nombres que figuran en las capturas: el bot «Sol13», el producto
  «MALZIRN / The Sol Initiate» en whop.com y el canal de YouTube no se muestra. Las valoraciones
  («no dice qué vende», «ni sus cifras cuadran») se apoyan en el texto literal de las capturas.

## Pasos

```bash
pip install manim edge-tts
# 1) Pon las capturas en evidence_src/ con su nombre original (IMG_9585.png … IMG_9634.png)
python prepare_assets.py          # difumina, recorta y genera assets/ + clips.json
# 2) Narración (180 s, se ajusta sola a cada bloque)
python narration.py
# 3) Video
manim -qh --disable_caching main.py FullVideo
# 4) Unir audio y video
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 -c:v copy -c:a aac -shortest output_final.mp4
```

Para una vista previa rápida a 540×960: `KABALA_PREVIEW=1 manim --disable_caching main.py Block3`.

## Línea de tiempo

| Bloque | Tiempo | Contenido | Etapa del embudo |
|---|---|---|---|
| 0 | 0:00–0:12 | 313 $ · 9 acertijos · 68 minutos · 1 bot; el embudo filtra a casi todos; CTA «al final, las 5 señales» | — |
| 1 | 0:12–0:36 | 10:29, `/start`: «No hagas capturas» (sello «HICE 47»), «48 horas, ya vas tarde», «elegido», Walk away / Step through | 1 · Atracción |
| 2 | 0:36–1:16 | Acertijos 1–4: CHOSEN 10:40, POWER 10:45, ALARIC 10:47, ASCEND 11:03, con el halago de cada premio | 2 · Compromiso |
| 3 | 1:16–1:52 | Acertijos 5–8: DANCE 11:05, 1933 11:17 (este lo saqué yo), MANIFEST 11:22, CLARITY 11:34 (imagen hecha con Gemini) | 3 · Escalada |
| 4 | 1:52–2:16 | «The Sunk Cost of your journey demands completion»; IGNITE 11:36, 9/9 | 4 · Coste hundido |
| 5 | 2:16–2:44 | 130 plazas, 48 h, «High standards require high friction», CLAIM YOUR SEAT → Whop 313 US$; 1/1000 ≠ 99 % | 5 · Conversión |
| 6 | 2:44–3:00 | «No pagué», las 5 señales y CTA | — |

La parte de arriba de la pantalla (HUD) se mantiene todo el video: el embudo se va llenando por
etapas, el reloj sigue las horas reales de los mensajes y una barra va sumando las 9 llaves.

## Datos y supuestos

- **Todas las horas, frases y cifras salen de las capturas.** Las citas en pantalla son
  traducciones fieles del inglés y la captura original aparece al lado, ampliada con una lupa.
- **«68 minutos»** va de `/start` (10:29) al pitch final (11:37). No es «3 horas»: eso no consta
  en las capturas.
- **«No pagué»** es un supuesto, porque no lo dijiste de forma explícita. Si no es así, hay que
  cambiar el bloque 6 de `main.py` y el último texto de `narration.py`.
