"""
narration.py — Narración continua para "El saqueo: 40 años de corrupción".

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
import numpy as np

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
    ("b0_hook", "No es un caso aislado. Es un sistema."),
    ("b0_counter", "Cuarenta años. Millones de euros. Veintisiete asesinatos."),
    ("b0_files", "Esto es lo que los archivos revelan."),
    # BLOQUE 1
    ("b1_guerra",
     "Antes de los ERE, ya había un patrón. En 1990, Juan Guerra, hermano del "
     "vicepresidente Alfonso Guerra, usó su despacho oficial para negocios privados."),
    ("b1_filesa",
     "Le siguió Filesa: 1.200 millones de pesetas de financiación ilegal del PSOE a "
     "través de empresas tapadera, Filesa, Malesa y Time-Export, que cobraban por "
     "estudios falsos."),
    ("b1_fondos",
     "Después, los fondos reservados de la lucha antiterrorista acabaron en "
     "sobresueldos: 5 millones de pesetas al mes."),
    ("b1_gal",
     "Y el GAL: 27 asesinatos. El exministro José Barrionuevo y el exsecretario de "
     "Estado Rafael Vera fueron condenados por secuestro y malversación."),
    # BLOQUE 2
    ("b2_ere", "Pero el mayor caso llegó con los ERE de Andalucía: 679 millones de euros."),
    ("b2_chaves",
     "Los expresidentes de la Junta Manuel Chaves y José Antonio Griñán fueron "
     "condenados junto a otros altos cargos. En 2024, el Tribunal Constitucional "
     "anuló sus condenas y ordenó dictar sentencias nuevas."),
    ("b2_closed", "El mayor caso de corrupción de la democracia."),
    # BLOQUE 3
    ("b3_marea",
     "No solo los ERE. En Asturias, el caso Marea acabó con cinco condenados, entre "
     "ellos el exconsejero José Luis Iglesias Riopedre, con penas de hasta nueve años "
     "de prisión por desviar fondos públicos."),
    ("b3_faffe",
     "En la Faffe, en Sevilla, su exdirector gastó 32.000 euros públicos en "
     "prostíbulos: condenado a seis años de cárcel por malversación, rebajados "
     "después a cinco años y tres meses."),
    # BLOQUE 4
    ("b4_koldo",
     "La corrupción no terminó. Se reinventó. En 2026, el Tribunal Supremo condenó a "
     "José Luis Ábalos a 24 años y 3 meses de cárcel, y a Koldo García a 19 años y 8 "
     "meses, por la trama de las mascarillas: organización criminal, cohecho, "
     "malversación y tráfico de influencias."),
    ("b4_david",
     "David Sánchez, hermano del presidente, fue condenado a 9 años de inhabilitación "
     "por prevaricación en la Diputación de Badajoz."),
    ("b4_begona", "Begoña Gómez está investigada por tráfico de influencias."),
    ("b4_open",
     "Y siguen abiertos el caso Plus Ultra, con las hijas de Zapatero investigadas, el "
     "de la SEPI, con Leire Díez, y el de Santos Cerdán, por presuntos amaños de obra "
     "pública."),
    # BLOQUE 5
    ("b5_sum",
     "Súmalo. 679 millones de euros en los ERE. 1.200 millones de pesetas de Filesa. "
     "27 asesinatos del GAL."),
    ("b5_stamps", "Décadas de prisión acumuladas. Cuarenta años de casos."),
    ("b5_open", "Y causas que siguen abiertas."),
    # BLOQUE 6
    ("b6_recap", "679 millones. 27 asesinatos. Una pregunta: ¿hasta cuándo?"),
    ("b6_cta",
     "Si quieres que analice los archivos completos, sígueme. Y dime en comentarios: "
     "¿cuál es el caso que más te impacta?"),
]

# Planos sin frase propia: arrancan a una fracción del plano anterior.
SPLITS = {"b0_cta": ("b0_files", 0.40)}

# Orden canónico de planos (debe coincidir con main.py)
BEAT_ORDER = [
    "b0_hook", "b0_counter", "b0_files", "b0_cta",
    "b1_guerra", "b1_filesa", "b1_fondos", "b1_gal",
    "b2_ere", "b2_chaves", "b2_closed",
    "b3_marea", "b3_faffe",
    "b4_koldo", "b4_david", "b4_begona", "b4_open",
    "b5_sum", "b5_stamps", "b5_open",
    "b6_recap", "b6_cta",
]

TICKS = 10_000_000  # edge-tts usa unidades de 100 ns
SR = 24000
MAX_PAUSE = 0.30    # ninguna pausa interna supera 0,30 s («sin silencios»)
SIL_DB = -40.0


def decode(path: str) -> np.ndarray:
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                                   "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


def compress_pauses(x: np.ndarray):
    """Acorta los silencios (< -40 dB) de más de MAX_PAUSE. Devuelve audio y mapa de tiempos."""
    win = int(SR * 0.01)
    n = len(x) // win
    db = 20 * np.log10(np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(axis=1)) + 1e-9)
    sil = db < SIL_DB
    keep = np.ones(len(x), dtype=bool)
    cuts = []  # (t_original, segundos eliminados)
    mw = int(MAX_PAUSE / 0.01)
    i = 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            if j - i > mw:
                a, b = (i + mw // 2) * win, (j - (mw - mw // 2)) * win
                keep[a:b] = False
                cuts.append((a / SR, (b - a) / SR))
            i = j
        else:
            i += 1
    return x[keep], cuts


def remap(t: float, cuts) -> float:
    return t - sum(d for t0, d in cuts if t0 < t)



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
    ap.add_argument("--rate", default="-14%", help="velocidad inicial de edge-tts")
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
        audio, cuts = compress_pauses(decode(raw))
        for w in words:
            w["t0"], w["t1"] = remap(w["t0"], cuts), remap(w["t1"], cuts)
        comp = os.path.join(tmp, "comp.f32")
        audio.tofile(comp)
        lead = max(0.0, words[0]["t0"] - 0.03)
        tail = min(len(audio) / SR, words[-1]["t1"] + 0.20)
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
        ["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", comp, "-af", filt,
         "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k",
         OUT_MP3])

    # --- timeline
    locate_words(full, words)
    raw_starts = segment_starts(seg_chars, words)
    starts = {key: max(0.0, (t - lead) / factor)
              for (key, _), t in zip(SEGMENTS, raw_starts)}
    starts["b0_hook"] = 0.0
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
        if starts[k] < prev + MIN_BEAT and k != "b0_hook":
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
