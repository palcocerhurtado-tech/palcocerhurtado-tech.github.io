"""
narration.py — Narración continua con edge-tts (voz es-ES-AlvaroNeural).

1. Sintetiza un MP3 por bloque:  bloque_0.mp3 … bloque_6.mp3
     edge-tts --voice "es-ES-AlvaroNeural" --text "FRASE" --write-media "bloque_X.mp3"
2. AUTO-AJUSTE: mide cada bloque con ffprobe y, si no cabe en su ventana del
   video (o deja demasiado hueco), lo vuelve a sintetizar con --rate=±N% hasta
   ocupar ≈ ventana − 0.35 s. Así no hay silencios largos ni solapes.
3. Coloca cada bloque EXACTAMENTE en su segundo de inicio (0, 15, 45, 75, 105,
   135, 165) y exporta narration.mp3 de 180.000 s (ffmpeg).

Requisitos:  pip install edge-tts   ·   ffmpeg/ffprobe en el PATH.
Proxy opcional: export EDGE_TTS_PROXY=http://host:puerto
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys

VOICE = "es-ES-AlvaroNeural"
TOTAL = 180.0
TAIL = 0.35            # respiración al final de cada bloque (s)
MAX_GAP = 1.2          # hueco máximo tolerado antes de ralentizar (s)
RATE_MIN, RATE_MAX = -15, 35
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "audio")

# (inicio, fin, texto) — el texto base es el de §5; se añadieron solo datos
# literales de §1 (hekhalot, definición de Cábala, «Árbol Infernal», «pieles»,
# Durán/Zenit, «clave simbólica», y el nombre prometido del árbol: Qlifot).
BLOCKS = [
    (0, 15,
     "Hay un código que la humanidad olvidó. Un sistema que dice que el universo fue "
     "creado con letras, números y sonidos. Se llama Cábala. Y esto es lo que los "
     "archivos, los libros y los foros nos cuentan sobre ella."),
    (15, 45,
     "Antes de la Cábala, estaba la Merkavá. El misticismo del Carro divino. Según la "
     "visión del profeta Ezequiel, los practicantes ‘descendían’ a los palacios "
     "celestiales, los hekhalot, atravesando ángeles hostiles y pruebas, hasta llegar al "
     "Séptimo Palacio, donde se encuentra el Trono de Yahvé. Esa experiencia extática, "
     "ese viaje al corazón de lo divino, es la semilla de la que nacería siglos después "
     "la Cábala: el sistema esotérico del judaísmo que busca comprender la estructura "
     "del universo, el lenguaje sagrado y la creación de la realidad."),
    (45, 75,
     "La Cábala se organiza en el Árbol de la Vida, el Etz Jaim. Diez esferas, las "
     "sefirot, que son emanaciones de Dios. Veintidós senderos, las letras del alfabeto "
     "hebreo, que conectan esas esferas. El Sefer Yetzirah, el Libro de la Formación, "
     "describe cómo el universo fue creado mediante estos treinta y dos senderos de "
     "sabiduría. Y a veces, el Árbol se representa como el cuerpo del Adam Kadmón, el "
     "Hombre Celeste: Kéter es la corona, Jojmá y Biná son los hemisferios, y así hasta "
     "Maljut, el Reino, los pies."),
    (75, 105,
     "En la cima de todo está el Ein Sof, el Infinito, el Dios sin nombre. Porque en el "
     "judaísmo, pronunciar el nombre de Dios es imposible. Solo se le puede llamar "
     "mediante epítetos: Hashem, Adonai. Pero la tradición cabalística habla de setenta y "
     "dos nombres divinos, los Shemot, derivados del Éxodo, y de cuarenta nombres que son "
     "subconjuntos de poder. Cada letra hebrea es un jeroglífico, un código. Y la Cábala "
     "práctica usa esos nombres en amuletos, sellos y meditaciones para influir en la "
     "realidad."),
    (105, 135,
     "Pero hay un lado oscuro. Los cabalistas hablan de las Qlifot, las ‘cáscaras’, o "
     "‘pieles’. Es el Árbol de la Muerte, también llamado Árbol Infernal: la estructura "
     "inversa del Árbol de la Vida. Representa las fuerzas del desequilibrio, las sefirot "
     "malignas, el caos que surgió de la ruptura de los vasos durante la creación. Y de "
     "esa tradición nace la leyenda del Gólem de Praga: un ser creado con el poder del "
     "lenguaje sagrado, un recordatorio de que las palabras pueden dar vida… o quitarla."),
    (135, 165,
     "Y esta sabiduría no se quedó encerrada en las sinagogas. La masonería, con su Templo "
     "de Salomón y su escuadra y compás, se sostiene sobre hombros de gigantes "
     "cabalistas, como escribe Joan-Josep Durán, grado treinta y uno, en Zenit. El Templo "
     "de Salomón es la clave simbólica del Rito Escocés Antiguo y Aceptado, un rito "
     "impregnado de simbolismo cabalístico. Desde Pico della Mirandola hasta Robert "
     "Fludd, siglos de tradición oculta confluyen en la masonería."),
    (165, 180,
     "Diez sefirot. Veintidós senderos. Setenta y dos nombres. Y un árbol invertido con "
     "nombre propio: Qlifot. Una pregunta: ¿sigue viva la Cábala hoy? Si quieres que "
     "analice el Sefer Yetzirah, sígueme. Y dime en comentarios: ¿crees que la Cábala "
     "sigue siendo un código oculto?"),
]
assert BLOCKS[-1][1] == TOTAL and all(a[1] == b[0] for a, b in zip(BLOCKS, BLOCKS[1:]))


def need(tool: str):
    if shutil.which(tool) is None:
        sys.exit(f"ERROR: no se encuentra '{tool}' en el PATH.")


def duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def tts(text: str, path: str, rate: int = 0):
    cmd = ["edge-tts", "--voice", VOICE, "--text", text, "--write-media", path]
    if rate:
        cmd.append(f"--rate={rate:+d}%")
    if os.environ.get("EDGE_TTS_PROXY"):
        cmd += ["--proxy", os.environ["EDGE_TTS_PROXY"]]
    subprocess.run(cmd, check=True)


def fit_block(i: int, start: float, end: float, text: str) -> dict:
    """Sintetiza y ajusta la velocidad hasta que el bloque llena su ventana."""
    path = os.path.join(OUT_DIR, f"bloque_{i}.mp3")
    target = (end - start) - TAIL
    rate = 0
    tts(text, path, rate)
    dur = duration(path)
    for _ in range(5):
        if dur <= target and (target - dur) <= MAX_GAP:
            break
        if dur > target:                                   # demasiado largo → acelerar
            rate += max(1, math.ceil((dur / target - 1) * 100))
        else:                                              # demasiado corto → ralentizar
            rate -= max(1, math.floor((1 - dur / target) * 100))
        rate = max(RATE_MIN, min(RATE_MAX, rate))
        tts(text, path, rate)
        dur = duration(path)
        if rate in (RATE_MIN, RATE_MAX):
            break
    if dur > (end - start):
        sys.exit(f"ERROR: el bloque {i} dura {dur:.2f}s y no cabe en {end - start:.0f}s "
                 f"ni a {rate:+d}%. Acorta su texto.")
    print(f"  bloque_{i}.mp3  {dur:6.2f}s / ventana {end - start:4.0f}s  (rate {rate:+d}%)")
    return {"bloque": i, "inicio": start, "fin": end, "duracion": round(dur, 3),
            "rate": f"{rate:+d}%", "hueco_final": round((end - start) - dur, 3)}


def assemble(report: list[dict], out_path: str):
    """Cada bloque se rellena con silencio hasta su ventana exacta y se
    concatenan → 180.000 s, cada frase arranca en su segundo del guion."""
    inputs, filters = [], []
    for k, r in enumerate(report):
        inputs += ["-i", os.path.join(OUT_DIR, f"bloque_{r['bloque']}.mp3")]
        win = r["fin"] - r["inicio"]
        filters.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,"
                       f"apad=whole_dur={win},atrim=0:{win},asetpts=PTS-STARTPTS[a{k}]")
    chain = "".join(f"[a{k}]" for k in range(len(report)))
    filters.append(f"{chain}concat=n={len(report)}:v=0:a=1,atrim=0:{TOTAL}[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[out]", "-ar", "48000", "-ac", "1", "-c:a", "libmp3lame",
                    "-b:a", "192k", out_path], check=True)


def main():
    need("edge-tts")
    need("ffmpeg")
    need("ffprobe")
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Voz: {VOICE}")
    report = [fit_block(i, a, b, t) for i, (a, b, t) in enumerate(BLOCKS)]
    out = os.path.join(HERE, "narration.mp3")
    assemble(report, out)
    total = duration(out)
    with open(os.path.join(OUT_DIR, "timing.json"), "w", encoding="utf-8") as fh:
        json.dump({"total": total, "bloques": report}, fh, ensure_ascii=False, indent=2)
    print(f"narration.mp3 → {total:.3f}s  (objetivo {TOTAL:.0f}s)")
    if abs(total - TOTAL) > 0.06:
        print("AVISO: la duración difiere de 180 s más de 60 ms (relleno de trama MP3).")


if __name__ == "__main__":
    main()
