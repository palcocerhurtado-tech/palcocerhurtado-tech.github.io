"""
narration.py — «25 MILLONES DE AÑOS DE GUERRA OCULTA»

  python narration.py                 -> narration.wav, audio_final.wav, timings.json
  python narration.py --mux <mp4>     -> historia_oculta_final.mp4

Voz es-ES-AlvaroNeural (pitch -4Hz). Un clip por bloque (B0…B10), silencios
extremos recortados (-45 dB) con 0,06 s de cola, pausas internas largas acotadas
a 0,28 s, concatenación sin huecos, calibración automática de `rate` para
clavar 180 s y un drone ambiental (55 + 110 Hz con LFO) a -26 dB bajo la voz.

Requisitos: pip install edge-tts numpy · ffmpeg/ffprobe en el PATH.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np
import edge_tts

VOICE = "es-ES-AlvaroNeural"
PITCH = "-4Hz"
SR = 44100
TARGET = 180.0
LO, HI = 178.5, 181.5
RATE_MIN, RATE_MAX = -5, 25
TAIL = 0.06          # cola tras la última sílaba de cada bloque
MAX_PAUSE = 0.28     # pausa interna máxima (criterio §6: ningún hueco > 0,35 s)
SIL_DB = -45.0

HERE = os.path.dirname(os.path.abspath(__file__))
P_NARR = os.path.join(HERE, "narration.wav")
P_FINAL = os.path.join(HERE, "audio_final.wav")
P_TIMINGS = os.path.join(HERE, "timings.json")
P_MP4 = os.path.join(HERE, "historia_oculta_final.mp4")

# ── §5 · texto literal ─────────────────────────────────────────────────────
BLOQUES = {
"B0": "Veinticinco millones de años de guerra oculta. Lira, Atlántida, Saturno, Illuminati, Epstein. No son historias distintas: es una sola.",
"B1": "Las crónicas de Lira cuentan que hace veintidós millones de años los humanos estelares ya cruzaban la galaxia. Hasta que el Imperio Draco, desde la estrella Thuban, arrasó Bila, Teka y Merck: cincuenta millones de muertos en un solo asalto. Los supervivientes huyeron a Pléyades, Sirio y Orión.",
"B2": "La guerra bajó a la Tierra. Los reptilianos tomaron Lemuria, en el Pacífico; los atlantes, Atlántida. Maldek, el planeta que hoy sería el cinturón de asteroides, envió refugiados a Asia. En Andrómeda se firmó la paz: una raza híbrida de doce linajes humanos y uno reptiliano. Nosotros.",
"B3": "Hace trescientos mil años llegaron los Anunnaki. Enki, el genetista, mezcló su sangre con la del homínido. Enlil, el comandante, desató el diluvio hacia el diez mil quinientos antes de Cristo: Atlántida se hundió. La memoria quedó en piedra: Göbekli Tepe, y templos que resuenan a ciento diez hercios.",
"B4": "El Libro de la Sabiduría apunta a Saturno: Cronos, el dios que devora a sus hijos, el cubo negro de este mundo. En su polo norte gira un hexágono real de catorce mil quinientos kilómetros por lado. Y la gnosis hiperbórea de Nimrod de Rosario sentencia: tu espíritu es eterno; tu alma, una batería.",
"B5": "El uno de mayo de 1776, en Ingolstadt, Adam Weishaupt funda los Illuminati. En 1785 Baviera los prohíbe. Pero El libro negro de los Illuminati sostiene que no murieron: mutaron. Skull and Bones, Yale, 1832. [OPCIONAL]El Bohemian Grove, cada julio.[/OPCIONAL] Bilderberg, desde 1954.",
"B6": "El mapa del poder dibuja tres ciudades por encima de toda nación. Londres controla el dinero; el Vaticano, el dogma; Washington, la espada, convertida en corporación en 1871. [OPCIONAL]Tres obeliscos las marcan.[/OPCIONAL] Encima, la pirámide: entidades, linajes, sociedades secretas. En la base, nosotros.",
"B7": "Después, la guerra fue por la mente. En El Instituto Tavistock, Daniel Estulin sigue el rastro: Wellington House, 1914; la clínica, 1920; el instituto, 1947. Y un hecho desclasificado: el trece de abril de 1953, la CIA aprueba MK Ultra. Drogas e hipnosis en más de ochenta instituciones.",
"B8": "Bajo tus pies, la guerra sigue. Phil Schneider habló de ciento treinta bases subterráneas en Estados Unidos, casi mil cuatrocientas en el mundo, y de un tiroteo en Dulce en 1979. Desde 1945, la Operación Paperclip importó ciencia nazi. Y la Orden del Sol Negro, cuentan, escapó a la Antártida.",
"B9": "Y entonces, Epstein. Los hechos: en 2008 pacta en Florida y cumple trece meses. El seis de julio de 2019 es arrestado; el diez de agosto aparece muerto en su celda. Ghislaine Maxwell: veinte años de condena. En 2025 se publica su libro de cumpleaños, doscientas treinta y ocho páginas. Una ley votada cuatrocientos veintisiete a uno libera tres millones y medio de páginas. La gnosis hiperbórea lo llama gerente del chantaje.",
"B10": "En octubre de 2017 aparece Q con su promesa: una Alianza contra la Cábala, una tormenta, la revelación total. [OPCIONAL]Ovnis, energía libre, juicios.[/OPCIONAL] En este mapa todo converge: Lira, Atlántida, Saturno, Illuminati, túneles, Epstein. La misma guerra durante veinticinco millones de años, por un solo botín: tu espíritu. Ahora ya lo sabes. Sigue la cuenta: llega la segunda parte.",
}
ORDER = [f"B{i}" for i in range(11)]

# Pronunciación (solo audio, §5)
PHONETIC = [("MK Ultra", "eme ka Ultra"), ("Skull and Bones", "Skal an Bons")]

OPT_RE = re.compile(r"\[OPCIONAL\](.*?)\[/OPCIONAL\]")


def optional_slots() -> list[tuple[str, int]]:
    """(bloque, índice) de cada fragmento opcional, en orden de eliminación (del final hacia atrás)."""
    slots = []
    for b in ORDER:
        for i, _ in enumerate(OPT_RE.findall(BLOQUES[b])):
            slots.append((b, i))
    return list(reversed(slots))


def tts_text(block: str, dropped: set[tuple[str, int]], phonetic: bool) -> str:
    counter = {"i": 0}

    def repl(m):
        i = counter["i"]
        counter["i"] += 1
        return "" if (block, i) in dropped else m.group(1)

    txt = OPT_RE.sub(repl, BLOQUES[block])
    txt = re.sub(r"\s{2,}", " ", txt).strip()
    if phonetic:
        for a, b in PHONETIC:
            txt = txt.replace(a, b)
    return txt


# ── audio helpers ──────────────────────────────────────────────────────────
async def _synth(text: str, rate: str, path: str) -> None:
    await edge_tts.Communicate(text, VOICE, rate=rate, pitch=PITCH).save(path)


def synth(text: str, rate: int, path: str) -> None:
    r = f"+{rate}%" if rate >= 0 else f"{rate}%"
    for attempt in range(4):
        try:
            asyncio.run(_synth(text, r, path))
            return
        except Exception as exc:  # red inestable: reintento
            if attempt == 3:
                raise
            print(f"   reintento TTS ({exc})")


def trim_clip(src: str) -> np.ndarray:
    """silenceremove + areverse (-45 dB) y decodificación a float32 mono 44,1 kHz."""
    th = f"{SIL_DB}dB"
    af = (f"silenceremove=start_periods=1:start_threshold={th}:start_silence=0,"
          f"areverse,silenceremove=start_periods=1:start_threshold={th}:start_silence=0,"
          f"areverse")
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", src, "-af", af, "-ac", "1", "-ar", str(SR),
         "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


def cap_pauses(x: np.ndarray, max_pause=MAX_PAUSE) -> np.ndarray:
    """Acorta pausas internas (< -45 dB) más largas que max_pause."""
    win = int(SR * 0.01)
    n = len(x) // win
    if n == 0:
        return x
    frames = x[: n * win].reshape(n, win)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    silent = db < SIL_DB
    keep = np.ones(len(x), dtype=bool)
    i = 0
    max_w = int(max_pause / 0.01)
    while i < n:
        if silent[i]:
            j = i
            while j < n and silent[j]:
                j += 1
            if j - i > max_w:
                cut0 = (i + max_w // 2) * win
                cut1 = (j - (max_w - max_w // 2)) * win
                keep[cut0:cut1] = False
            i = j
        else:
            i += 1
    return x[keep]


def write_wav(path: str, x: np.ndarray, channels=1) -> None:
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def ffprobe_duration(path: str) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        text=True).strip())


def drone(n: int, voice: np.ndarray) -> np.ndarray:
    t = np.arange(n) / SR
    lfo1 = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    lfo2 = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t + 1.3)
    d = 0.6 * np.sin(2 * np.pi * 55 * t) * lfo1 + 0.4 * np.sin(2 * np.pi * 110 * t) * lfo2
    fade = int(SR * 3.0)
    env = np.ones(n)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    d *= env
    v_rms = np.sqrt(np.mean(voice[np.abs(voice) > 0.01] ** 2))
    d_rms = np.sqrt(np.mean(d ** 2))
    return d * (v_rms * 10 ** (-26 / 20) / d_rms)


# ── pipeline ───────────────────────────────────────────────────────────────
def build(rate: int, dropped: set, phonetic: bool, tmp: str) -> dict[str, np.ndarray]:
    clips = {}
    for b in ORDER:
        mp3 = os.path.join(tmp, f"{b}.mp3")
        synth(tts_text(b, dropped, phonetic), rate, mp3)
        x = cap_pauses(trim_clip(mp3))
        clips[b] = np.concatenate([x, np.zeros(int(TAIL * SR), dtype=np.float32)])
    return clips


def total_of(clips) -> float:
    return sum(len(c) for c in clips.values()) / SR


def main_generate(start_rate: int, phonetic: bool) -> None:
    tmp = tempfile.mkdtemp(prefix="narr25_")
    rate, dropped = start_rate, set()
    opt_queue = optional_slots()
    clips = None
    for it in range(1, 6):
        clips = build(rate, dropped, phonetic, tmp)
        tot = total_of(clips)
        print(f"[iter {it}] rate={rate:+d}%  total={tot:.2f}s")
        if LO <= tot <= HI:
            break
        new = int(np.clip(rate + round((tot / TARGET - 1) * 100), RATE_MIN, RATE_MAX))
        if new == rate:
            break
        rate = new
    # A +25 % y aún largo: quitar [OPCIONAL] de uno en uno
    while total_of(clips) > HI and opt_queue:
        slot = opt_queue.pop(0)
        dropped.add(slot)
        print(f"[ajuste] se elimina el fragmento opcional {slot}")
        clips = build(rate, dropped, phonetic, tmp)
        print(f"         total={total_of(clips):.2f}s")

    voice = np.concatenate([clips[b] for b in ORDER])
    write_wav(P_NARR, voice)
    mix = voice + drone(len(voice), voice).astype(np.float32)
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak
    stereo = np.repeat(mix[:, None], 2, axis=1).reshape(-1)
    write_wav(P_FINAL, stereo, channels=2)

    blocks, t = [], 0.0
    for b in ORDER:
        d = len(clips[b]) / SR
        blocks.append({"id": b, "start": round(t, 4), "dur": round(d, 4)})
        t += d
    data = {"blocks": blocks, "total": round(t, 4), "voice": VOICE, "pitch": PITCH,
            "rate": f"{rate:+d}%", "dropped_optional": sorted([f"{b}#{i}" for b, i in dropped])}
    with open(P_TIMINGS, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"OK narration.wav / audio_final.wav ({ffprobe_duration(P_FINAL):.3f}s) · timings.json")
    for bl in blocks:
        print(f"   {bl['id']:>3}  start={bl['start']:7.2f}  dur={bl['dur']:6.2f}")


def main_mux(mp4: str) -> None:
    with open(P_TIMINGS, encoding="utf-8") as fh:
        total = json.load(fh)["total"]
    subprocess.check_call(
        ["ffmpeg", "-y", "-v", "error", "-i", mp4, "-i", P_FINAL, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", P_MP4])
    print(f"OK {P_MP4} ({ffprobe_duration(P_MP4):.3f}s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mux", metavar="MP4", help="une el MP4 renderizado con audio_final.wav")
    ap.add_argument("--rate", type=int, default=15, help="velocidad inicial en %% (por defecto +15)")
    ap.add_argument("--no-phonetic", action="store_true",
                    help="no sustituir 'MK Ultra'/'Skull and Bones' por su versión fonética")
    a = ap.parse_args()
    if a.mux:
        main_mux(a.mux)
    else:
        main_generate(a.rate, not a.no_phonetic)
    sys.exit(0)
