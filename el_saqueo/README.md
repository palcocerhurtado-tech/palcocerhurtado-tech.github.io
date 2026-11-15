# El saqueo: 40 años de corrupción

Vídeo vertical 9:16 (1080×1920, 30 fps, H.264) de **180,0 s exactos**, hecho con Manim CE y narrado
con edge-tts (`es-ES-AlvaroNeural`). Tiene estética de investigación periodística: sellos
CASO CERRADO / EN REVISIÓN / EN INVESTIGACIÓN, contadores de euros y pesetas, siluetas genéricas
(sin rasgos) y una línea de progreso que acumula las cifras hasta **">680 M€ · 27 ASESINATOS"**.

## Uso

```bash
pip install manim edge-tts            # + ffmpeg en el PATH
python narration.py                   # narration.mp3 (180,0 s) + timeline.json
manim -qh main.py FullVideo           # 1080x1920 @ 30 fps (fijado dentro de main.py)
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 \
       -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -t 180 output_final.mp4
```

Vista previa rápida: `PREVIEW=1 manim main.py FullVideo` (540×960, 15 fps).
Bloques sueltos: `Block0Hook`, `Block1Origenes`, `Block2ERE`, `Block3Regionales`,
`Block4EraSanchez`, `Block5Total`, `Block6Cierre`.

> Manim llama a la carpeta de salida según la altura en píxeles (`1920p30`). Si tu versión
> crea otra, ajusta la ruta del comando `ffmpeg`.

## Correcciones respecto a la tabla original (§1)

Antes de producir el vídeo se contrastó la tabla con prensa y fuentes judiciales (noviembre de 2026).
Estos cambios son los acordados:

| Dato original | En el vídeo |
|---|---|
| Caso Peugeot: 21 meses de prisión | **Eliminado.** Los 21 meses eran de investigación, no una condena. |
| Caso SEAT: 175 M pts pagados al PSOE | **Eliminado.** Los acusados fueron absueltos (Audiencia de Madrid en 2007, confirmado por el Supremo). |
| ERE: Chaves y Griñán condenados | Se añade que en 2024 el Constitucional anuló sus condenas y ordenó dictar sentencias nuevas. El sello es EN REVISIÓN. |
| Fitonovo: 32.000 € en prostíbulos, 6 años | Pasa a ser el caso **Faffe**: 6 años, rebajados después a 5 años y 3 meses. |
| Fondos reservados: 5 M pts desviados | **5 M pts al mes** en sobresueldos. Se quita «7 altos cargos», que no se pudo verificar. |
| GAL: Barrionuevo y Vera, 27 asesinatos | 27 asesinatos atribuidos al GAL. Barrionuevo y Vera, condenados por secuestro y malversación. |
| Filesa: «condenado el partido» | Se describe como financiación ilegal mediante empresas tapadera, sin decir que el partido fuera condenado. |
| Marea: 27 años y 3 meses acumulados | 5 condenados, con penas de hasta 9 años (cifra del Supremo). El acumulado no se pudo verificar. |
| Ábalos 24 años / Koldo 19 años | Cifras exactas: 24 años y 3 meses, y 19 años y 8 meses (Supremo, junio de 2026). |
| 13 M de mascarillas · 18 condenados | **Eliminados.** No se pudieron verificar. |
| «40 años de impunidad» / «El saqueo continúa» | «40 años de casos» / «Y causas que siguen abiertas». Los casos en investigación no son condenas. |

Los casos Plus Ultra (hijas de Zapatero), SEPI (Leire Díez), Santos Cerdán y Begoña Gómez aparecen
siempre con el sello **EN INVESTIGACIÓN**.

## Técnica

* **180,0 s exactos:** cada `play()` consume un número entero de fotogramas
  (`run_time=(n−0,5)/fps`, porque Manim genera `ceil(run_time·fps)` fotogramas) y cada plano
  termina en un fotograma absoluto. No hay `self.wait()`.
* **Sincronía:** `narration.py` sintetiza toda la voz en una sola petición, sin cortes entre
  bloques, y lee las marcas de palabra de edge-tts. `timeline.json` dice cuándo empieza cada plano.
* **8 palabras como máximo:** los textos de contenido se registran y se cuentan después de cada
  animación; el resultado queda en `render_report.txt`. El sello de la esquina y la etiqueta de
  la barra se tratan como interfaz fija y no cuentan.
* **Safe-zones:** cada texto pasa por `assert_safe()`.
