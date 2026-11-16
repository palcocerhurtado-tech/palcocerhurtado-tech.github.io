# 11-M: la operación oculta

Vídeo vertical 9:16 (1080×1920, 30 fps, H.264) de **180,0 s exactos**, hecho con Manim CE y narrado
con edge-tts (`es-ES-AlvaroNeural`). Tono de investigación clandestina, estética poligonal, sellos
CLASIFICADO / DESCLASIFICADO y una línea de tiempo con cuatro hitos (Perejil 2002, Praga 2002,
11-M 2004, Villarejo 2019). Al final la línea se fragmenta y forma el sello **«¿OPERACIÓN OCULTA?»**.

## Uso

```bash
pip install manim edge-tts numpy      # + ffmpeg en el PATH
python narration.py                   # narration.mp3 (180,0 s, pausas ≤ 0,30 s) + timeline.json
manim -qh main.py FullVideo           # 1080x1920 @ 30 fps (fijado dentro de main.py)
ffmpeg -i media/videos/main/1920p30/FullVideo.mp4 -i narration.mp3 \
       -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -t 180 output_final.mp4
```

Vista previa: `PREVIEW=1 manim main.py FullVideo` (540×960, 15 fps). Bloques sueltos: `Block0Hook`,
`Block1Perejil`, `Block2Praga`, `Block3Villarejo`, `Block4Tedax`, `Block5Pruebas`, `Block6Cierre`.

## Contraste de datos (noviembre de 2026)

El guion mantiene el tono conspirativo. Cada afirmación se atribuye a quien la hizo y se acompaña
de lo que consta en fuentes judiciales o de prensa.

| Dato del prompt original | En el vídeo |
|---|---|
| Villarejo: Francia y Marruecos organizaron el 11-M | Se mantiene, atribuido a él: escrito de 15 páginas entregado en 2019 a la Audiencia Nacional. El juez García-Castellón y la Fiscalía lo rechazaron por ser «conjeturas» sin base documental. Se añade la grabación de 2009 de mandos policiales que hablaban de esa hipótesis. |
| TEDAX: el tren se revisó cuatro veces | Fueron **dos** revisiones, según la declaración del jefe de los TEDAX de Madrid. |
| Radiografía ocultada al juez cuatro meses | Tardó **más de tres meses** en llegar al juez (las fuentes dicen «más de tres» y «más de cuatro»; se usa la cifra mínima). El jefe de los TEDAX lo atribuyó a un error. |
| El carrete «desapareció» | Un agente de la Científica declaró en el juicio que el carrete se entregó a los TEDAX para un revelado urgente y se perdió. |
| La bolsa no figuraba en el inventario | **Eliminado.** No se pudo verificar. |
| Todos los intérpretes de árabe, destituidos | Aparece como pregunta («¿Sin intérpretes de árabe?») con el rótulo «Ningún documento lo prueba». |
| «Beneplácito» del PSOE | **Eliminado.** No existe ninguna prueba. Se menciona solo el hecho: elecciones generales tres días después. |
| «El 11-M no fue un atentado islamista. Fue una operación de Estado.» | Pasa a ser una pregunta: «¿Y si el 11-M esconde algo más?». La sentencia de 2007 condenó a 21 personas de una célula yihadista, y el vídeo lo dice. |

Se añaden hechos documentados para completar los 180 s sin silencios: las cuatro estaciones,
193 muertos y casi 2.000 heridos, la Operación Romeo-Sierra, la cumbre de las Azores, la pista del
teléfono hasta Jamal Zougam y Leganés.

## Técnica

* **180,0 s exactos:** cada animación consume un número entero de fotogramas
  (`run_time=(n−0,5)/fps`) y cada plano termina en un fotograma absoluto. No hay `self.wait()`.
* **Narración continua:** se sintetiza en una sola petición y las pausas entre frases se acortan
  a 0,30 s como máximo. Las marcas de palabra de edge-tts se recalculan sobre el audio recortado
  y dan `timeline.json`.
* **8 palabras como máximo:** el render las cuenta después de cada animación y lo anota en
  `render_report.txt`. El sello de la esquina y las fechas de la línea de tiempo son interfaz fija
  y no cuentan.
* **Safe-zones:** cada texto pasa por `assert_safe()`.
