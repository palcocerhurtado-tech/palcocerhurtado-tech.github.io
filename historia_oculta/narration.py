"""
narration.py — Narración continua para "La verdadera historia oculta: de Lira a QAnon".

Genera:
  * narration.mp3   -> voz es-ES-AlvaroNeural, exactamente 180.0 s, sin silencios
  * timeline.json   -> instante (s) en que arranca cada plano del vídeo,
                       sacado de las marcas de palabra de edge-tts.
                       main.py lo lee para sincronizar imagen y voz.

Método:
  1. Todo el texto se sintetiza en UNA sola petición (flujo continuo, sin cortes
     entre bloques).
  2. Se mide la duración hablada real (primera -> última palabra) y se ajusta el
     parámetro `rate` de edge-tts hasta quedar cerca de 180 s.
  3. El pequeño resto se corrige con ffmpeg `atempo` y se recorta/rellena a
     180.000 s exactos.

Uso:
  python narration.py            # genera narration.mp3 + timeline.json
  python narration.py --rate +20%  # fuerza la velocidad inicial

Requisitos: pip install edge-tts   +   ffmpeg/ffprobe en el PATH.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile

import edge_tts

VOICE = "es-ES-AlvaroNeural"
TOTAL = 180.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MP3 = os.path.join(HERE, "narration.mp3")
OUT_TIMELINE = os.path.join(HERE, "timeline.json")

# ---------------------------------------------------------------------------
# Texto (§5). Cada tupla = (plano de main.py que arranca con este fragmento, texto)
# ---------------------------------------------------------------------------
SEGMENTS: list[tuple[str, str]] = [
    # BLOQUE 0
    ("b0_helix", "Tu ADN no es solo humano."),
    ("b0_mutate", "Liranos, dracos, anunnaki. Una guerra de millones de años."),
    ("b0_map", "Esto es lo que los archivos ocultan."),
    # BLOQUE 1
    ("b1_alliance",
     "Hace 22 millones de años, los humanoides de Lira dominaban la galaxia. "
     "Se aliaron con Vega y sembraron Sirio, Altair, Alfa Centauri y Orión."),
    ("b1_draco",
     "Pero en Alpha Draconis, a 270 años luz, el Imperio Alfa Draconiano, con siete "
     "especies y una casta real de piel blanca, los observaba."),
    ("b1_war",
     "Hace 20 millones de años, los dracos atacaron Lira. Tres planetas, Bila, Teka "
     "y Merck, fueron destruidos."),
    ("b1_genocide", "50 millones de liranos murieron en el primer asalto."),
    # BLOQUE 2
    ("b2_continents",
     "Los supervivientes se dispersaron. Los Atlans, refugiados de las Pléyades, "
     "colonizaron Atlántida. Los reptilianos reclamaron Lemuria."),
    ("b2_extinction",
     "Los maldekianos, vengativos, bombardearon la Tierra y provocaron la extinción "
     "de los dinosaurios hace 65 millones de años."),
    ("b2_treaty",
     "Para detener el caos, se firmó el Tratado de Paz de Andrómeda: se crearía una "
     "raza híbrida con ADN de 12 grupos humanoides y 1 reptiliano. Pero los dracos "
     "sabotearon el experimento para controlar telepáticamente a los híbridos."),
    # BLOQUE 3
    ("b3_anunnaki",
     "Hace 300.000 años, los Anunnaki llegaron desde Nibiru en busca de oro."),
    ("b3_sapiens",
     "Encontraron a los homínidos creados por los reptilianos y los mezclaron con su "
     "propia genética."),
    ("b3_gold", "Así nació el Homo sapiens. Todos llevamos su huella."),
    ("b3_enoc",
     "Y esta historia resuena en el Libro de Enoc, donde los Vigilantes descendieron "
     "y engendraron a los Nefilim, y en los textos hindúes, donde los Vimanas "
     "surcaban los cielos."),
    # BLOQUE 4
    ("b4_weishaupt",
     "Los híbridos se organizaron. En 1776, Adam Weishaupt fundó los Illuminati de "
     "Baviera. En 1782, se infiltraron en la masonería."),
    ("b4_obelisks",
     "Hoy, un triunvirato oculto controla el mundo: la City de Londres, Washington "
     "D.C. y el Vaticano. Los tres tienen un obelisco egipcio en su centro."),
    ("b4_nobility",
     "La nobleza negra, trece familias como los Orsini, los Aldobrandini y los "
     "Farnese, preserva la línea de sangre reptiliana."),
    ("b4_papa",
     "El Papa Gris, Pepe Orsini, es la figura más poderosa, por encima del Papa "
     "Blanco y el Papa Negro."),
    # BLOQUE 5
    ("b5_orsic",
     "En 1919, la médium Maria Orsic contactó con Aldebarán. Recibió transmisiones en "
     "sumerio antiguo y un dialecto desconocido. Eran instrucciones para construir "
     "una nave de disco."),
    ("b5_haunebu",
     "En 1922 se construyó el primer prototipo. En 1934 voló el RFZ-1. Los modelos "
     "Haunebu y Vril usaban propulsión antigravitatoria."),
    ("b5_thule",
     "La Sociedad Thule y la Sociedad Vril, con su culto al Sol Negro, canalizaron "
     "este conocimiento."),
    ("b5_base",
     "Tras la guerra, la Alemania nazi estableció la Base 211 en la Antártida. En "
     "1947, el almirante Richard Byrd dirigió la Operación Highjump para destruirla."),
    # BLOQUE 6
    ("b6_dumbs",
     "Y esta historia continúa hoy. QAnon, el movimiento que ha absorbido todos estos "
     "mitos, habla de las DUMBs: ciudades subterráneas donde, según QAnon, las élites "
     "torturarían a niños para extraer adrenocromo."),
    ("b6_awaken",
     "Habla de un Gran Despertar, de una Tormenta, de un rompecabezas que, pieza a "
     "pieza, revela la verdad."),
    ("b6_recap", "22 millones de años. Siete especies. Una guerra."),
    ("b6_cta",
     "Una pregunta: ¿crees que somos híbridos? Si quieres que analice los archivos "
     "completos, sígueme. Y dime en comentarios: ¿crees que somos híbridos?"),
]

# Planos sin frase propia: arrancan a una fracción del plano anterior.
# (el CTA de apertura se superpone a "Esto es lo que los archivos ocultan")
SPLITS = {"b0_cta": ("b0_map", 0.40)}

# Orden canónico de planos (debe coincidir con main.py)
BEAT_ORDER = [
    "b0_helix", "b0_mutate", "b0_map", "b0_cta",
    "b1_alliance", "b1_draco", "b1_war", "b1_genocide",
    "b2_continents", "b2_extinction", "b2_treaty",
    "b3_anunnaki", "b3_sapiens", "b3_gold", "b3_enoc",
    "b4_weishaupt", "b4_obelisks", "b4_nobility", "b4_papa",
    "b5_orsic", "b5_haunebu", "b5_thule", "b5_base",
    "b6_dumbs", "b6_awaken", "b6_recap", "b6_cta",
]

TICKS = 10_000_000  # edge-tts usa unidades de 100 ns


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], text=True)
    return float(out.strip())


async def synth(text: str, rate: str, mp3_path: str) -> list[dict]:
    """Sintetiza y devuelve las marcas de palabra [{'t0','t1','text'}] en segundos."""
    comm = edge_tts.Communicate(text, VOICE, rate=rate, boundary="WordBoundary")
    words: list[dict] = []
    with open(mp3_path, "wb") as fh:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                fh.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                t0 = chunk["offset"] / TICKS
                words.append({"t0": t0, "t1": t0 + chunk["duration"] / TICKS,
                              "text": chunk["text"]})
    if not words:
        raise RuntimeError("edge-tts no devolvió marcas de palabra.")
    return words


def locate_words(full: str, words: list[dict]) -> None:
    """Asigna a cada palabra su posición de carácter en el texto completo."""
    low = full.lower()
    cur = 0
    for w in words:
        token = w["text"].lower().strip()
        pos = low.find(token, cur) if token else -1
        if pos < 0 and token:
            first = token.split()[0]
            pos = low.find(first, cur)
        if pos < 0 or pos - cur > 80:  # no encontrado: lo dejamos en el cursor
            pos = cur
        w["char"] = pos
        cur = pos + max(1, len(token))


def segment_starts(full_starts: list[int], words: list[dict]) -> list[float]:
    starts = []
    for c in full_starts:
        t = next((w["t0"] for w in words if w["char"] >= c), words[-1]["t0"])
        starts.append(t)
    return starts


def rate_str(pct: float) -> str:
    pct = int(round(pct))
    return f"+{pct}%" if pct >= 0 else f"{pct}%"


def atempo_chain(f: float) -> str:
    parts = []
    while f > 2.0:
        parts.append("atempo=2.0")
        f /= 2.0
    while f < 0.5:
        parts.append("atempo=0.5")
        f /= 0.5
    parts.append(f"atempo={f:.6f}")
    return ",".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", default="+22%", help="velocidad inicial de edge-tts")
    args = ap.parse_args()

    full = ""
    seg_chars = []
    for _, txt in SEGMENTS:
        if full:
            full += " "
        seg_chars.append(len(full))
        full += txt

    pct = float(args.rate.replace("%", ""))
    tmp = tempfile.mkdtemp(prefix="narr_")
    raw = os.path.join(tmp, "raw.mp3")

    for attempt in range(4):
        print(f"[narration] síntesis con rate={rate_str(pct)} ...")
        words = asyncio.run(synth(full, rate_str(pct), raw))
        lead = max(0.0, words[0]["t0"] - 0.03)
        tail = min(ffprobe_duration(raw), words[-1]["t1"] + 0.20)
        spoken = tail - lead
        factor = spoken / TOTAL  # atempo necesario
        print(f"[narration]   duración hablada {spoken:.2f}s -> factor {factor:.4f}")
        if 0.97 <= factor <= 1.03:
            break
        pct = (1 + pct / 100.0) * factor * 100.0 - 100.0

    # --- audio final: recorte de silencios extremos + atempo + 180.000 s exactos
    filt = (f"atrim=start={lead:.4f}:end={tail:.4f},asetpts=PTS-STARTPTS,"
            f"{atempo_chain(factor)},apad,atrim=end={TOTAL:.3f}")
    subprocess.check_call(
        ["ffmpeg", "-y", "-v", "error", "-i", raw, "-af", filt,
         "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
         OUT_MP3])

    # --- timeline
    locate_words(full, words)
    raw_starts = segment_starts(seg_chars, words)
    starts = {key: max(0.0, (t - lead) / factor)
              for (key, _), t in zip(SEGMENTS, raw_starts)}
    starts["b0_helix"] = 0.0
    ordered = [k for k in BEAT_ORDER if k in starts or k in SPLITS]
    # inserta los planos "split"
    for key, (parent, frac) in SPLITS.items():
        i = BEAT_ORDER.index(parent)
        nxt = next(starts[k] for k in BEAT_ORDER[i + 1:] if k in starts)
        starts[key] = starts[parent] + frac * (nxt - starts[parent])
    # monotonía + duración mínima de 1.2 s por plano
    MIN_BEAT = 1.2
    prev = -MIN_BEAT
    for k in ordered:
        if starts[k] < prev + MIN_BEAT and k != "b0_helix":
            starts[k] = prev + MIN_BEAT
        prev = starts[k]
    timeline = {"total": TOTAL, "voice": VOICE, "rate": rate_str(pct),
                "atempo": round(factor, 5),
                "beats": [{"key": k, "start": round(starts[k], 3)} for k in ordered]}
    with open(OUT_TIMELINE, "w", encoding="utf-8") as fh:
        json.dump(timeline, fh, ensure_ascii=False, indent=2)

    dur = ffprobe_duration(OUT_MP3)
    print(f"[narration] OK -> {OUT_MP3} ({dur:.3f}s)")
    print(f"[narration] OK -> {OUT_TIMELINE}")
    for b in timeline["beats"]:
        print(f"    {b['start']:7.2f}s  {b['key']}")


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        sys.exit("Python 3.9+ requerido")
    main()
