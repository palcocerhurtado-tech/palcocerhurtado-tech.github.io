"""
narration.py — Narración en primera persona con edge-tts (voz es-ES-AlvaroNeural).

1. Sintetiza un MP3 por bloque:  bloque_0.mp3 … bloque_6.mp3
     edge-tts --voice "es-ES-AlvaroNeural" --text "FRASE" --write-media "bloque_X.mp3"
2. AUTO-AJUSTE: mide cada bloque con ffprobe y, si no cabe en su ventana del
   video (o deja demasiado hueco), lo vuelve a sintetizar con --rate=±N% hasta
   ocupar ≈ ventana − 0.35 s. Así no hay silencios largos ni solapes.
3. Coloca cada bloque EXACTAMENTE en su segundo de inicio (0, 15, 45, 75, 105, 135, 165) y exporta narration.mp3 de 180.000 s (ffmpeg).

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
import time

VOICE = "es-ES-AlvaroNeural"
TOTAL = 180.0
TAIL = 0.25            # respiración al final de cada bloque (s)
MAX_GAP = 0.7          # hueco máximo tolerado antes de ralentizar (s)
RATE_MIN, RATE_MAX = -15, 35
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "audio")

# (inicio, fin, texto) — narración en primera persona; solo datos de las capturas.
BLOCKS = [
    (0, 15,
     "El ocultismo no era un mito. Era un arma. Thule, Vril, el Sol Negro. Una Alemania "
     "que buscaba dioses en el hielo. Esto es lo que los archivos desclasificados ocultan."),
    (15, 45,
     "1918. Múnich. Rudolf von Sebottendorf funda la Sociedad Thule. Un grupo ocultista y "
     "racista que llegó a tener dos mil miembros. Ocultistas, racistas, buscadores del "
     "origen de la raza aria. Lo buscaban en una isla mítica del norte, Thule. Y si no "
     "estaba allí, en la Atlántida. Creían que ese lugar perdido guardaba el secreto de los "
     "arios. Una sociedad secreta, en plena Alemania de posguerra. Y no estaban solos."),
    (45, 75,
     "Según la leyenda, en 1919, Maria Orsic, médium principal de la Sociedad Vril, junto a "
     "Sigrun, Traute, Gudrun y Heike, comenzó a recibir transmisiones en dos idiomas que "
     "nadie conocía. Uno, sumerio antiguo. El otro, un dialecto de Aldebarán, a sesenta y "
     "cuatro años luz. Contenían instrucciones técnicas para una nave de disco con "
     "propulsión antigravitatoria, por energía de torsión. De ahí, dice el mito, nacieron "
     "los proyectos Haunebu y Vril."),
    (75, 105,
     "Heinrich Himmler ordenó construir un mosaico en el suelo del castillo de Wewelsburg, "
     "el centro de culto de las SS. Doce runas Sig, radiales, como doce relámpagos "
     "alrededor de un mismo centro. El Sol Negro. Schwarze Sonne. Para ellos, el "
     "símbolo del renacimiento ario, la fuente de poder de los arios. Un sol que, según "
     "ellos, iluminaba el camino hacia el poder. Y hacia la muerte."),
    (105, 135,
     "Según la leyenda, en 1945, con la guerra perdida, muchos nazis huyeron hacia la "
     "Antártida, a una base secreta bajo el hielo: la Base 211, en Nueva Suabia. En 1947, el "
     "almirante Richard E. Byrd lideró la Operación Highjump: trece barcos y cuatro mil "
     "hombres. La versión oficial: probar equipo militar en el frío. La teoría "
     "conspirativa: destruir la Base 211 y enfrentarse a tecnología nazi."),
    (135, 165,
     "Y las naves. Los discos Haunebu, los mismos que, según el mito, nacieron de las "
     "transmisiones de Maria Orsic. Discos de veinticinco a cuarenta metros de diámetro. "
     "El Haunebu dos alcanzaba los seis mil kilómetros por hora en la atmósfera. "
     "Propulsión antigravitatoria, energía de torsión, y un blindaje llamado Victalen: "
     "humo congelado. "
     "Tecnología de otro mundo. O de otro tiempo."),
    (165, 180,
     "Thule. Vril. Sol Negro. Base 211. Una pregunta. Si quieres que analice los archivos "
     "completos, sígueme. Y dime en comentarios: ¿crees que la base sigue ahí?"),
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
    for attempt in range(4):                 # reintentos ante cortes de red
        if subprocess.run(cmd).returncode == 0 and os.path.getsize(path) > 0:
            return
        time.sleep(2 * (attempt + 1))
    sys.exit(f"ERROR: edge-tts falló 4 veces generando {os.path.basename(path)}.")


def trim_silence(path: str):
    """Recorta el silencio que edge-tts deja al inicio y al final de cada clip
    (≈0.5 s por lado), para que no se acumulen pausas entre bloques."""
    tmp = path + ".trim.mp3"
    sr = "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-af",
                    f"{sr},areverse,{sr},areverse", "-c:a", "libmp3lame", "-b:a", "192k", tmp],
                   check=True)
    os.replace(tmp, path)


def synth(text: str, path: str, rate: int) -> float:
    tts(text, path, rate)
    trim_silence(path)
    return duration(path)


def fit_block(i: int, start: float, end: float, text: str) -> dict:
    """Sintetiza y ajusta la velocidad hasta que el bloque llena su ventana."""
    path = os.path.join(OUT_DIR, f"bloque_{i}.mp3")
    target = (end - start) - TAIL
    rate = 0
    dur = synth(text, path, rate)
    for _ in range(5):
        if dur <= target and (target - dur) <= MAX_GAP:
            break
        if dur > target:                                   # demasiado largo → acelerar
            rate += max(1, math.ceil((dur / target - 1) * 100))
        else:                                              # demasiado corto → ralentizar
            rate -= max(1, math.floor((1 - dur / target) * 100))
        rate = max(RATE_MIN, min(RATE_MAX, rate))
        dur = synth(text, path, rate)
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
