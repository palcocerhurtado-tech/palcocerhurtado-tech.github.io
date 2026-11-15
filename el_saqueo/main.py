"""
main.py — «EL SAQUEO: 40 AÑOS DE CORRUPCIÓN»
Vídeo vertical 9:16 · 1080x1920 · 30 fps · 180.0 s exactos · Manim CE 0.18+

Render completo:   manim -qh main.py FullVideo
Bloques sueltos:   manim -qh main.py Block2ERE   (etc.)
Vista previa:      PREVIEW=1 manim main.py FullVideo  (540x960, 15 fps)

Sincronía: si existe timeline.json (lo genera narration.py) cada plano arranca
cuando la voz dice su frase; si no, se usa la escaleta nominal de §4.
Todo el material gráfico se genera por código (siluetas genéricas, sin rostros).
"""

from __future__ import annotations

import json
import os
import random
import subprocess

import numpy as np
from manim import *  # noqa: F401,F403

# ════════════════════════════════════════════════════════════════════════════
# CONFIG 9:16
# ════════════════════════════════════════════════════════════════════════════
PREVIEW = os.environ.get("PREVIEW") == "1"
config.pixel_width = 540 if PREVIEW else 1080
config.pixel_height = 960 if PREVIEW else 1920
config.frame_rate = 15 if PREVIEW else 30
config.frame_height = 16.0
config.frame_width = 9.0
config.background_color = "#0A0A0A"
FPS = config.frame_rate
TOTAL = 180.0

BG = "#0A0A0A"
TXT = "#E8E6E3"
DATA = "#5AC8FA"
GOLD = "#C9A227"
ALERT = "#8B0000"
ALERT_HI = "#D2232A"   # rojo legible derivado de #8B0000
PANEL = "#16161A"
DIM = "#4A4A50"


def _pick_font(cands, fallback):
    try:
        out = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout
    except Exception:
        return fallback
    fams = {f.strip() for line in out.splitlines() for f in line.split(",")}
    return next((c for c in cands if c in fams), fallback)


SANS = _pick_font(["Montserrat", "DejaVu Sans"], "Sans")
MONO = _pick_font(["DejaVu Sans Mono"], "Monospace")
MIN_FS = 48

# Zonas seguras (120 px = 1 u): x ∈ [60,1020] px -> [-4, 4] ; y ∈ [230,1536] px -> [6.08, -4.8]
SAFE = (-4.0, 4.0, -4.80, 6.08)
MAX_W = 7.6
Y_STAMP = 5.55
HEAD_TOP = 4.85
Y_VIS = 0.35
Y_CAP = -2.62
Y_BAR_LBL = -3.78
Y_BAR = -4.32
BAR_W = 7.8
CORNER_TR = np.array([3.75, 5.85, 0])

HERE = os.path.dirname(os.path.abspath(__file__))

# ════════════════════════════════════════════════════════════════════════════
# ESCALETA (§4) — sobrescrita por timeline.json si existe
# ════════════════════════════════════════════════════════════════════════════
DEFAULT_BEATS = [
    ("b0_hook", 0), ("b0_counter", 3), ("b0_files", 8), ("b0_cta", 12),
    ("b1_guerra", 15), ("b1_filesa", 22), ("b1_fondos", 30), ("b1_gal", 35),
    ("b2_ere", 45), ("b2_chaves", 55), ("b2_closed", 65),
    ("b3_marea", 75), ("b3_faffe", 88),
    ("b4_koldo", 105), ("b4_david", 117), ("b4_begona", 124), ("b4_open", 130),
    ("b5_sum", 135), ("b5_stamps", 150), ("b5_open", 158),
    ("b6_recap", 165), ("b6_cta", 172),
]
BLOCK_START = ["b0_hook", "b1_guerra", "b2_ere", "b3_marea", "b4_koldo", "b5_sum", "b6_recap"]


def load_timeline():
    beats = list(DEFAULT_BEATS)
    p = os.path.join(HERE, "timeline.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            got = {b["key"]: float(b["start"]) for b in json.load(fh)["beats"]}
        if all(k in got for k, _ in DEFAULT_BEATS):
            beats = [(k, got[k]) for k, _ in DEFAULT_BEATS]
    return {k: (s, beats[i + 1][1] if i + 1 < len(beats) else TOTAL) for i, (k, s) in enumerate(beats)}


TL = load_timeline()


# ════════════════════════════════════════════════════════════════════════════
# RELOJ POR FOTOGRAMAS (180.0 s exactos)
# ════════════════════════════════════════════════════════════════════════════
class Beat:
    """Plano con fin absoluto. Manim genera ceil(run_time·fps) fotogramas, así que
    run_time=(n−0,5)/fps produce exactamente n. `f` = fracción del plano."""

    def __init__(self, scene: "SaqueoBase", key: str):
        self.s = scene
        start, end = TL[key]
        self.end_frame = int(round(end * FPS))
        self.span = max(2, self.end_frame - scene.frame_no)

    def left(self):
        return self.end_frame - self.s.frame_no

    def play(self, *anims, f=0.1, **kw):
        n = max(2, int(round(f * self.span)))
        if self.left() >= 2:
            n = min(n, self.left())
        self.s.play(*anims, run_time=(n - 0.5) / FPS, **kw)
        self.s.frame_no += n
        self.s.check_words()

    def finish(self, mob: Mobject | None = None):
        n = self.left()
        if n <= 0:
            return
        n = max(n, 2)
        rt = (n - 0.5) / FPS
        anims = [self.s.grain.animate(rate_func=linear).shift(DOWN * 0.05 * rt)]
        if mob is not None:
            anims.append(mob.animate(rate_func=linear).scale(1 + 0.012 * rt))
        self.s.play(*anims, run_time=rt)
        self.s.frame_no += n
        self.s.check_words()


# ════════════════════════════════════════════════════════════════════════════
# TEXTO CINÉTICO
# ════════════════════════════════════════════════════════════════════════════
def kinetic_text(text: str, fs=72, color=TXT, font=None, max_w=MAX_W, max_lines=3) -> VGroup:
    """Texto partido en palabras (submobjects) con ajuste de líneas al ancho seguro.
    Nunca baja de font_size 48. Los signos sueltos (· → + –) se centran en altura."""
    font = font or SANS
    words = text.split()
    fs = max(fs, MIN_FS)
    while True:
        mobs = [Text(w, font=font, font_size=fs, color=color, weight=BOLD) for w in words]
        sp = Text("n", font=font, font_size=fs, weight=BOLD).width * 0.6
        lines, cur, cw = [], [], 0.0
        for m in mobs:
            add = m.width + (sp if cur else 0)
            if cur and cw + add > max_w:
                lines.append(cur)
                cur, cw = [m], m.width
            else:
                cur.append(m)
                cw += add
        lines.append(cur)
        widest = max(sum(x.width for x in ln) + sp * (len(ln) - 1) for ln in lines)
        if (len(lines) <= max_lines and widest <= max_w) or fs <= MIN_FS:
            break
        fs = max(MIN_FS, fs - 4)
    rows = VGroup()
    for ln in lines:
        row = VGroup(*ln).arrange(RIGHT, buff=sp, aligned_edge=DOWN)
        hmax = max(m.height for m in ln)
        refs = [m for m in ln if m.height > 0.5 * hmax]
        cy = np.mean([m.get_center()[1] for m in refs])
        for m in ln:
            if m.height < 0.45 * hmax:
                m.set_y(cy)
        rows.add(row)
    rows.arrange(DOWN, buff=0.2 * fs / 48)
    if rows.width > max_w:
        rows.scale_to_fit_width(max_w)
    rows.nwords = len(words)
    rows.text = text
    return rows


def reveal(m: VGroup):
    """Write para ≤4 palabras; cascada palabra a palabra para el resto (§2)."""
    if getattr(m, "nwords", 1) <= 4:
        return Write(m)
    return LaggedStart(*[FadeIn(w, shift=0.25 * UP, scale=1.12) for row in m for w in row],
                       lag_ratio=0.12)


def assert_safe(m: Mobject, what=""):
    x0, x1, y0, y1 = SAFE
    e = 0.02
    ok = (m.get_left()[0] >= x0 - e and m.get_right()[0] <= x1 + e and
          m.get_bottom()[1] >= y0 - e and m.get_top()[1] <= y1 + e)
    assert ok, f"fuera de safe-zone: {what!r}"
    return m


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICOS
# ════════════════════════════════════════════════════════════════════════════
def stamp(text="CASO CERRADO", color=ALERT_HI, fs=54, angle=4) -> VGroup:
    t = Text(text, font=MONO, font_size=fs, color=color, weight=BOLD)
    if t.width > 6.8:
        t.scale_to_fit_width(6.8)
    box = SurroundingRectangle(t, buff=0.16, color=color, stroke_width=6, corner_radius=0.08)
    return VGroup(box, t).rotate(angle * DEGREES)


STAMP_COL = {"CASO CERRADO": ALERT_HI, "EN INVESTIGACIÓN": DATA, "EN REVISIÓN": GOLD}


def official(h=2.6, color=TXT, tie=ALERT_HI) -> VGroup:
    """Silueta genérica de cargo público (sin rasgos)."""
    s = h / 2.6
    head = Circle(radius=0.42 * s, color=color, fill_opacity=0.92, stroke_width=0).move_to([0, 0.75 * s, 0])
    body = RoundedRectangle(width=1.9 * s, height=1.25 * s, corner_radius=0.45 * s, color=color,
                            fill_opacity=0.92, stroke_width=0).move_to([0, -0.55 * s, 0])
    collar = Polygon([-0.32 * s, 0.07 * s, 0], [0.32 * s, 0.07 * s, 0], [0, -0.35 * s, 0],
                     color=BG, fill_opacity=1, stroke_width=0)
    tie_ = Polygon([-0.08 * s, -0.05 * s, 0], [0.08 * s, -0.05 * s, 0], [0.12 * s, -0.75 * s, 0],
                   [0, -0.9 * s, 0], [-0.12 * s, -0.75 * s, 0], color=tie, fill_opacity=1, stroke_width=0)
    return VGroup(body, collar, tie_, head)


def official_f(h=2.6, color=TXT) -> VGroup:
    s = h / 2.6
    hair = Ellipse(width=1.1 * s, height=1.25 * s, color=color, fill_opacity=0.6, stroke_width=0).move_to([0, 0.62 * s, 0])
    head = Circle(radius=0.4 * s, color=color, fill_opacity=0.92, stroke_width=0).move_to([0, 0.75 * s, 0])
    body = RoundedRectangle(width=1.8 * s, height=1.25 * s, corner_radius=0.5 * s, color=color,
                            fill_opacity=0.92, stroke_width=0).move_to([0, -0.55 * s, 0])
    neck = Polygon([-0.3 * s, 0.07 * s, 0], [0.3 * s, 0.07 * s, 0], [0, -0.3 * s, 0], color=BG,
                   fill_opacity=1, stroke_width=0)
    return VGroup(hair, body, neck, head)


def jail_bars(w=2.2, h=2.6, color=GOLD) -> VGroup:
    g = VGroup(*[Line([x, -h / 2, 0], [x, h / 2, 0], color=color, stroke_width=7)
                 for x in np.linspace(-w / 2, w / 2, 6)])
    g.add(Line([-w / 2, h / 2, 0], [w / 2, h / 2, 0], color=color, stroke_width=7),
          Line([-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], color=color, stroke_width=7))
    return g


def company_box(name: str, color=DATA) -> VGroup:
    t = Text(name, font=MONO, font_size=50, color=color, weight=BOLD)
    box = RoundedRectangle(width=max(3.6, t.width + 0.6), height=0.95, corner_radius=0.12,
                           color=color, stroke_width=4, fill_color=PANEL, fill_opacity=1)
    g = VGroup(box, t.move_to(box))
    g.word = t
    return g


def vault(color=DATA) -> VGroup:
    body = RoundedRectangle(width=2.4, height=2.4, corner_radius=0.18, color=color, stroke_width=6,
                            fill_color=PANEL, fill_opacity=1)
    dial = Circle(radius=0.62, color=color, stroke_width=5)
    spokes = VGroup(*[Line(ORIGIN, 0.55 * np.array([np.cos(a), np.sin(a), 0]), color=color, stroke_width=4)
                      for a in np.linspace(0, TAU, 6, endpoint=False)])
    hinge = VGroup(*[Rectangle(width=0.12, height=0.35, color=color, fill_opacity=1).move_to([-1.26, y, 0])
                     for y in (0.7, -0.7)])
    return VGroup(body, dial, spokes, hinge)


def banknote(color=GOLD) -> VGroup:
    r = Rectangle(width=0.9, height=0.45, color=color, fill_color=PANEL, fill_opacity=1, stroke_width=3)
    return VGroup(r, Circle(radius=0.12, color=color, stroke_width=3))


def cross_mark(color=ALERT_HI, s=0.22) -> VGroup:
    return VGroup(Line([0, -s, 0], [0, s, 0], color=color, stroke_width=5),
                  Line([-s * 0.6, s * 0.35, 0], [s * 0.6, s * 0.35, 0], color=color, stroke_width=5))


def region_blob(seed=3, r=1.9, color=DATA) -> VMobject:
    rnd = random.Random(seed)
    pts = []
    for i in range(16):
        a = TAU * i / 16
        rr = r * (1 + rnd.uniform(-0.22, 0.22))
        pts.append([rr * np.cos(a), 0.55 * rr * np.sin(a), 0])
    m = VMobject(stroke_color=color, stroke_width=4, fill_color=color, fill_opacity=0.12)
    m.set_points_smoothly(pts + [pts[0]])
    return m


def club_icon(color=ALERT_HI) -> VGroup:
    house = Polygon([-1.4, -1.0, 0], [1.4, -1.0, 0], [1.4, 0.5, 0], [0, 1.4, 0], [-1.4, 0.5, 0],
                    color=TXT, stroke_width=5, fill_color=PANEL, fill_opacity=1)
    door = Rectangle(width=0.6, height=0.9, color=TXT, stroke_width=4).move_to([0, -0.55, 0])
    heart = VGroup(Circle(radius=0.2, color=color, fill_opacity=1).move_to([-0.16, 0.42, 0]),
                   Circle(radius=0.2, color=color, fill_opacity=1).move_to([0.16, 0.42, 0]),
                   Polygon([-0.36, 0.36, 0], [0.36, 0.36, 0], [0, -0.05, 0], color=color, fill_opacity=1))
    glow = heart.copy().set_stroke(color, width=18, opacity=0.25).set_fill(opacity=0)
    return VGroup(house, door, glow, heart)


def mask_icon(color=DATA) -> VGroup:
    body = RoundedRectangle(width=1.8, height=1.0, corner_radius=0.35, color=color, stroke_width=5,
                            fill_color=PANEL, fill_opacity=1)
    pleats = VGroup(*[Line([-0.65, y, 0], [0.65, y, 0], color=color, stroke_width=3) for y in (-0.2, 0, 0.2)])
    ears = VGroup(Arc(radius=0.35, start_angle=PI / 2, angle=PI, color=color, stroke_width=4).move_to([-1.05, 0, 0]),
                  Arc(radius=0.35, start_angle=-PI / 2, angle=PI, color=color, stroke_width=4).move_to([1.05, 0, 0]))
    return VGroup(ears, body, pleats)


def magnifier(color=DATA, s=0.45) -> VGroup:
    return VGroup(Circle(radius=s, color=color, stroke_width=5),
                  Line([s * 0.7, -s * 0.7, 0], [s * 1.5, -s * 1.5, 0], color=color, stroke_width=7))


def grain_field(n=110, seed=5) -> VGroup:
    rnd = random.Random(seed)
    return VGroup(*[Dot([rnd.uniform(-4.6, 4.6), rnd.uniform(-8.4, 8.4), 0], radius=rnd.uniform(0.008, 0.022),
                        color=TXT, fill_opacity=rnd.uniform(0.08, 0.3)) for _ in range(n)])


def doc_grid() -> VGroup:
    """Trama de archivo: líneas horizontales tenues (papel pautado)."""
    return VGroup(*[Line([-4.6, y, 0], [4.6, y, 0], color=TXT, stroke_width=1, stroke_opacity=0.04)
                    for y in np.arange(-8, 8, 0.5)])


def fmt_es(v: float, dec=0) -> str:
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ════════════════════════════════════════════════════════════════════════════
# ESCENA BASE
# ════════════════════════════════════════════════════════════════════════════
class SaqueoBase(Scene):
    """Persistentes: grano, trama, sello (esquina sup. izq.) y LÍNEA DE PROGRESO."""

    # estado de la barra al INICIO de cada bloque (para escenas sueltas)
    BAR_STATE = [(0.0, ""), (0.04, ""), (0.20, "≈7,2 M€"), (0.80, "≈686 M€"), (0.84, "≈686 M€"),
                 (0.93, "≈686 M€"), (1.0, ">680 M€ · 27 ASESINATOS")]

    def setup_persistent(self, block: int):
        self.frame_no = int(round(TL[BLOCK_START[block]][0] * FPS))
        self.texts: list[tuple[Mobject, int]] = []
        self.violations: list[str] = []
        self.peak = (0, 0.0, [])
        self.grain = grain_field()
        self.add(doc_grid(), self.grain)
        self.stamp_mob = None
        self.cta_overlay = None
        # línea de progreso
        self.bar_frac = ValueTracker(self.BAR_STATE[block][0])
        self.bar_frame = RoundedRectangle(width=BAR_W + 0.12, height=0.46, corner_radius=0.08,
                                          color=TXT, stroke_width=3, stroke_opacity=0.7).move_to([0, Y_BAR, 0])
        x0 = -BAR_W / 2
        self.bar_color = DATA

        def fill():
            w = max(0.001, BAR_W * self.bar_frac.get_value())
            return Rectangle(width=w, height=0.34, stroke_width=0, fill_color=self.bar_color,
                             fill_opacity=0.95).move_to([x0 + w / 2, Y_BAR, 0])

        self.bar_fill = always_redraw(fill)
        ticks = VGroup(*[Line([x0 + BAR_W * k / 10, Y_BAR - 0.23, 0], [x0 + BAR_W * k / 10, Y_BAR - 0.3, 0],
                              color=TXT, stroke_width=2, stroke_opacity=0.5) for k in range(11)])
        self.bar = VGroup(self.bar_frame, ticks)
        self.bar_lbl = None
        if block > 0:
            self.add(self.bar, self.bar_fill)
            lbl = self.BAR_STATE[block][1]
            if lbl:
                self.bar_lbl = self._bar_label(lbl)
                self.add(self.bar_lbl)

    # ── utilidades ───────────────────────────────────────────────────────
    def _bar_label(self, text, color=TXT):
        t = Text(text, font=MONO, font_size=48, color=color, weight=BOLD)
        if t.width > BAR_W:
            t.scale_to_fit_width(BAR_W)
        return t.move_to([0, Y_BAR_LBL, 0]).align_to([-BAR_W / 2, 0, 0], LEFT)

    def bar_to(self, frac, text=None, color=TXT) -> list[Animation]:
        anims = [self.bar_frac.animate.set_value(frac)]
        if text is not None:
            new = self._bar_label(text, color)
            if self.bar_lbl is None:
                anims.append(FadeIn(new, shift=UP * 0.2))
            else:
                anims.append(ReplacementTransform(self.bar_lbl, new))
            self.bar_lbl = new
        return anims

    def reg(self, m, n=None):
        self.texts.append((m, n if n is not None else getattr(m, "nwords", 1)))
        assert_safe(m, getattr(m, "text", ""))
        return m

    def head(self, text, color=TXT, fs=76, top=HEAD_TOP):
        m = kinetic_text(text, fs=fs, color=color)
        m.move_to([0, 0, 0]).shift(UP * (top - m.get_top()[1]))
        return self.reg(m)

    def cap(self, text, color=DATA, fs=48, y=Y_CAP, font=None, max_w=MAX_W):
        m = kinetic_text(text, fs=fs, color=color, font=font or MONO, max_w=max_w, max_lines=2)
        return self.reg(m.move_to([0, y, 0]))

    def big(self, text, color=TXT, fs=96, y=Y_VIS, font=None):
        m = kinetic_text(text, fs=fs, color=color, font=font or SANS, max_lines=2)
        return self.reg(m.move_to([0, y, 0]))

    def name(self, text, at, color=TXT, fs=48):
        t = Text(text, font=MONO, font_size=fs, color=color, weight=BOLD)
        if t.width > 3.7:
            t.scale_to_fit_width(3.7)
        t.move_to(at)
        t.nwords, t.text = len(text.split()), text
        return self.reg(t)

    def counter(self, tracker, fmt, color=GOLD, fs=110, y=Y_VIS):
        def mk():
            t = Text(fmt(tracker.get_value()), font=MONO, font_size=fs, color=color, weight=BOLD)
            if t.width > MAX_W:
                t.scale_to_fit_width(MAX_W)
            return t.move_to([0, y, 0])
        m = always_redraw(mk)
        self.texts.append((m, 1))
        return m

    def check_words(self):
        """Cuenta las palabras de contenido visibles (sello y etiqueta de barra = cromo)."""
        fam = {id(m) for m in self.get_mobject_family_members()}
        n, who = 0, []
        for m, k in self.texts:
            if id(m) in fam:
                ops = [sm.get_fill_opacity() for sm in m.family_members_with_points()]
                if ops and max(ops) > 0.3:
                    n += k
                    who.append(getattr(m, "text", "#"))
        if n > self.peak[0]:
            self.peak = (n, self.frame_no / FPS, who)
        if n > 8:
            self.violations.append(f"{self.frame_no / FPS:7.2f}s {n}: {who}")

    def keep(self):
        k = [self.grain, self.bar, self.bar_fill, self.bar_frac]
        for m in (self.bar_lbl, self.stamp_mob, self.cta_overlay):
            if m is not None:
                k.append(m)
        k += [m for m in self.mobjects if isinstance(m, Line) is False and m.__class__ is VGroup
              and len(m) and isinstance(m[0], Line) and m[0].get_stroke_opacity() <= 0.05]  # trama
        return k

    def clear(self, extra_keep=(), **kw) -> list[Animation]:
        ids = set()
        for m in list(self.keep()) + list(extra_keep):
            ids.update(id(x) for x in m.get_family())
        return [FadeOut(m, **kw) for m in self.mobjects if not any(id(x) in ids for x in m.get_family())]

    def slam(self, text="CASO CERRADO") -> list[Animation]:
        new = stamp(text, STAMP_COL[text])
        new.move_to([0, Y_STAMP, 0]).align_to([SAFE[0] + 0.05, 0, 0], LEFT)
        anims = [FadeIn(new, scale=1.8, rate_func=rush_into)]
        if self.stamp_mob is not None:
            anims.append(FadeOut(self.stamp_mob, scale=0.7))
        self.stamp_mob = new
        return anims

    def report(self):
        exp = int(round(TOTAL * FPS))
        lines = [f"fotogramas={self.frame_no} esperados={exp}",
                 f"pico de palabras: {self.peak[0]} a {self.peak[1]:.2f}s {self.peak[2]}",
                 f"violaciones >8: {len(self.violations)}"] + self.violations[:30]
        print("\n".join(lines))
        try:
            with open(os.path.join(HERE, "render_report.txt"), "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
        except OSError:
            pass


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 0 — GANCHO + CTA
# ════════════════════════════════════════════════════════════════════════════
def block0(s: SaqueoBase):
    b = Beat(s, "b0_hook")
    t1 = s.big("No es un caso aislado.", fs=88, y=1.6)
    b.play(Create(s.bar_frame), FadeIn(s.bar[1]), *s.slam("CASO CERRADO"), f=0.25)
    s.add(s.bar)
    b.play(reveal(t1), f=0.3)
    t2 = s.big("Es un sistema.", color=ALERT_HI, fs=104, y=-0.3)
    b.play(reveal(t2), f=0.3)
    b.finish(t2)

    b = Beat(s, "b0_counter")
    tr = ValueTracker(0)
    cnt = s.counter(tr, lambda v: fmt_es(v) + " €", color=GOLD, fs=110, y=0.2)
    s.add(s.bar_fill)
    w1 = s.big("40 años.", fs=96, y=2.6)
    b.play(FadeOut(t1, shift=UP * 0.4), FadeOut(t2, shift=UP * 0.4), FadeIn(cnt), reveal(w1),
           *s.bar_to(0.04), f=0.25)
    w2 = s.big("Millones de euros.", color=GOLD, fs=84, y=2.6)
    b.play(tr.animate(rate_func=rate_functions.ease_in_quad).set_value(679_000_000),
           FadeOut(w1, shift=UP * 0.3), reveal(w2), f=0.4)
    cnt.clear_updaters()
    w3 = s.big("27 asesinatos.", color=ALERT_HI, fs=96, y=-1.7)
    crosses = VGroup(*[cross_mark(s=0.16) for _ in range(27)]).arrange_in_grid(3, 9, buff=0.28).move_to([0, -0.3, 0])
    b.play(cnt.animate.shift(UP * 0.7).scale(0.85), reveal(w3),
           LaggedStart(*[FadeIn(c, scale=2) for c in crosses], lag_ratio=0.03), f=0.3)
    b.finish(cnt)

    b = Beat(s, "b0_files")
    people = VGroup(*[official(1.5, TXT if i % 2 else "#BDB9B3") for i in range(5)]).arrange(RIGHT, buff=0.1)
    people.move_to([0, -0.6, 0])
    mini = VGroup(*[stamp("CASO CERRADO", ALERT_HI, fs=48, angle=-12).scale(0.32).move_to(p.get_center() + DOWN * 0.15)
                    for p in people])
    h = s.head("Esto es lo que los archivos revelan.", fs=72, top=HEAD_TOP)
    b.play(*s.clear(), LaggedStart(*[FadeIn(p, shift=UP * 0.3) for p in people], lag_ratio=0.12), reveal(h), f=0.6)
    b.play(LaggedStart(*[FadeIn(m, scale=2.5) for m in mini], lag_ratio=0.15), f=0.4)
    b.finish(people)

    b = Beat(s, "b0_cta")
    c1 = kinetic_text("Quédate: la cifra total", fs=60, color=BG, max_w=7.2)
    s.reg(c1.move_to([0, Y_CAP + 0.1, 0]))
    bar_ = Rectangle(width=8.0, height=c1.height + 0.5, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(c1)
    arrow = Arrow(bar_.get_top() + RIGHT * 2.7, CORNER_TR, color=GOLD, stroke_width=8, buff=0.1,
                  max_tip_length_to_length_ratio=0.1)
    s.cta_overlay = VGroup(bar_, c1, arrow)
    b.play(FadeOut(h, shift=UP * 0.3), FadeIn(VGroup(bar_, c1), shift=UP * 0.5), GrowArrow(arrow), f=0.55)
    b.play(Indicate(mini, color=GOLD), f=0.3)
    b.finish(people)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 — LOS ORÍGENES
# ════════════════════════════════════════════════════════════════════════════
def block1(s: SaqueoBase):
    b = Beat(s, "b1_guerra")
    cta = s.cta_overlay
    if cta is None:  # escena suelta
        c1 = kinetic_text("Quédate: la cifra total", fs=60, color=BG, max_w=7.2).move_to([0, Y_CAP + 0.1, 0])
        bar_ = Rectangle(width=8.0, height=c1.height + 0.5, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(c1)
        cta = VGroup(bar_, c1, Arrow(bar_.get_top() + RIGHT * 2.7, CORNER_TR, color=GOLD, stroke_width=8))
        s.add(cta)
    s.cta_overlay = None
    c2 = kinetic_text("te va a impactar.", fs=60, color=BG, max_w=7.2).move_to(cta[1])
    s.reg(c2)
    b.play(*s.clear(extra_keep=[cta]), FadeTransform(cta[1], c2), f=0.1)
    hook = s.head("Antes de los ERE, ya había un patrón.", fs=74)
    b.play(FadeOut(VGroup(cta[0], c2, cta[2]), shift=DOWN * 0.3), reveal(hook), f=0.2)
    jg = official(2.9).move_to([0, 0.2, 0])
    h2 = s.head("1990: Juan Guerra.", color=GOLD, fs=84)
    c = s.cap("TRÁFICO DE INFLUENCIAS", color=ALERT_HI)
    b.play(FadeOut(hook, shift=UP * 0.4), reveal(h2), FadeIn(jg, shift=UP * 0.3), FadeIn(c), f=0.2)
    desk = VGroup(Rectangle(width=3.4, height=0.18, color=TXT, fill_opacity=0.9).move_to([0, -1.25, 0]),
                  Rectangle(width=0.16, height=0.7, color=TXT, fill_opacity=0.9).move_to([-1.4, -1.68, 0]),
                  Rectangle(width=0.16, height=0.7, color=TXT, fill_opacity=0.9).move_to([1.4, -1.68, 0]))
    c2b = s.cap("DESPACHO OFICIAL → NEGOCIOS PRIVADOS", color=DATA)
    b.play(FadeIn(desk, shift=UP * 0.2), FadeOut(c, shift=UP * 0.2), FadeIn(c2b, shift=UP * 0.2), f=0.2)
    c3 = s.cap("HERMANO DEL VICEPRESIDENTE", color=TXT)
    b.play(FadeOut(c2b, shift=UP * 0.2), FadeIn(c3, shift=UP * 0.2), f=0.15)
    b.finish(jg)

    b = Beat(s, "b1_filesa")
    boxes = VGroup(*[company_box(n) for n in ("FILESA", "MALESA", "TIME-EXPORT")]).arrange(DOWN, buff=0.3)
    boxes.scale(0.8).move_to([0, 0.55, 0])
    for bx in boxes:
        s.texts.append((bx.word, 1))
    h = s.head("Filesa: 1.200 millones de pesetas.", color=GOLD, fs=72)
    boxes.shift(DOWN * max(0, boxes.get_top()[1] - (h.get_bottom()[1] - 0.3)))
    b.play(*s.clear(), reveal(h), LaggedStart(*[FadeIn(x, shift=RIGHT * 0.5) for x in boxes], lag_ratio=0.25),
           f=0.3)
    tr = ValueTracker(0)
    cnt = s.counter(tr, lambda v: fmt_es(v) + " PTS", color=GOLD, fs=84, y=boxes.get_bottom()[1] - 0.55)
    s.add(cnt)
    c = s.cap("FALSOS ESTUDIOS", color=DATA, y=-2.7)
    b.play(tr.animate.set_value(1_200_000_000), *s.bar_to(0.10, "≈7,2 M€"), f=0.35)
    cnt.clear_updaters()
    b.play(FadeIn(c, shift=UP * 0.2), *[Indicate(x, color=GOLD, scale_factor=1.05) for x in boxes], f=0.2)
    b.finish(cnt)

    b = Beat(s, "b1_fondos")
    v = vault().move_to([-1.6, 0.4, 0])
    notes = VGroup(*[banknote().move_to(v.get_center()) for _ in range(6)])
    env = VGroup(*[Rectangle(width=1.0, height=0.65, color=TXT, stroke_width=3, fill_color=PANEL, fill_opacity=1)
                   .move_to([2.3, 1.3 - 0.85 * k, 0]) for k in range(3)])
    h = s.head("Fondos reservados:", color=DATA, fs=80)
    b.play(*s.clear(), reveal(h), DrawBorderThenFill(v), FadeIn(env), f=0.25)
    s.add(notes)
    h2 = s.head("5 millones de pesetas al mes.", color=GOLD, fs=72)
    b.play(LaggedStart(*[n.animate.move_to(env[k % 3].get_center()) for k, n in enumerate(notes)], lag_ratio=0.15),
           Rotate(v[2], angle=PI, about_point=v[1].get_center()), FadeOut(h, shift=UP * 0.3), reveal(h2), f=0.4)
    c = s.cap("LUCHA ANTITERRORISTA → SOBRESUELDOS", color=ALERT_HI)
    b.play(FadeIn(c, shift=UP * 0.2), f=0.2)
    b.finish(v)

    b = Beat(s, "b1_gal")
    h = s.head("GAL: 27 asesinatos.", color=ALERT_HI, fs=86)
    crosses = VGroup(*[cross_mark(s=0.2) for _ in range(27)]).arrange_in_grid(3, 9, buff=0.33).move_to([0, 1.5, 0])
    b.play(*s.clear(), reveal(h), LaggedStart(*[FadeIn(c, scale=2) for c in crosses], lag_ratio=0.05),
           *s.bar_to(0.16, "≈7,2 M€ · 27 ASESINATOS"), f=0.3)
    p1 = official(2.0).move_to([-1.9, -0.6, 0])
    p2 = official(2.0).move_to([1.9, -0.6, 0])
    n1 = s.name("BARRIONUEVO", [-1.9, -1.8, 0], color=GOLD)
    n2 = s.name("VERA", [1.9, -1.8, 0], color=GOLD)
    b.play(FadeIn(p1, shift=UP * 0.3), FadeIn(p2, shift=UP * 0.3), FadeIn(n1), FadeIn(n2),
           crosses.animate.scale(0.7).shift(UP * 0.4), f=0.25)
    c = s.cap("SECUESTRO Y MALVERSACIÓN", color=GOLD, y=Y_CAP - 0.2)
    jb = VGroup(jail_bars(1.9, 2.1).move_to(p1), jail_bars(1.9, 2.1).move_to(p2))
    b.play(FadeIn(c), Create(jb), f=0.2)
    end = s.head("El primer saqueo.", color=TXT, fs=86)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(end), *s.slam("CASO CERRADO"), f=0.2)
    b.finish(jb)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 — EL ERE
# ════════════════════════════════════════════════════════════════════════════
def block2(s: SaqueoBase):
    b = Beat(s, "b2_ere")
    h = s.head("El mayor caso de corrupción de la democracia.", fs=70)
    b.play(*s.clear(), reveal(h), f=0.3)
    tr = ValueTracker(0)
    cnt = s.counter(tr, lambda v: fmt_es(v) + " €", color=GOLD, fs=120, y=0.6)
    s.add(cnt)
    h2 = s.head("ERE Andalucía: 679 millones de euros.", color=GOLD, fs=72)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), tr.animate(rate_func=rate_functions.ease_out_cubic)
           .set_value(679_000_000), *s.bar_to(0.80, "≈686 M€ · 27 ASESINATOS"), f=0.5)
    cnt.clear_updaters()
    b.play(Flash(s.bar_frame.get_right() + LEFT * 1.6, color=GOLD, line_length=0.6, num_lines=14),
           Indicate(cnt, color=ALERT_HI, scale_factor=1.06), f=0.15)
    b.finish(cnt)

    b = Beat(s, "b2_chaves")
    p1 = official(2.3).move_to([-1.8, 0.7, 0])
    p2 = official(2.3).move_to([1.8, 0.7, 0])
    n1 = s.name("CHAVES", [-1.8, -0.85, 0], color=GOLD)
    n2 = s.name("GRIÑÁN", [1.8, -0.85, 0], color=GOLD)
    crowd = VGroup(*[official(0.75, DIM, tie=DIM) for _ in range(16)]).arrange_in_grid(2, 8, buff=0.12)
    crowd.move_to([0, -2.05, 0])
    h = s.head("Chaves y Griñán: condenados.", fs=74)
    b.play(*s.clear(), *s.slam("EN REVISIÓN"), reveal(h), FadeIn(p1, shift=UP * 0.3), FadeIn(p2, shift=UP * 0.3),
           FadeIn(n1), FadeIn(n2), f=0.25)
    b.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in crowd], lag_ratio=0.04), f=0.2)
    h2 = s.head("2024: el Constitucional anula sus condenas.", color=GOLD, fs=70)
    strike = VGroup(Line(p1.get_corner(UL), p1.get_corner(DR), color=GOLD, stroke_width=8),
                    Line(p2.get_corner(UL), p2.get_corner(DR), color=GOLD, stroke_width=8))
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), Create(strike), f=0.25)
    c = s.cap("NUEVAS SENTENCIAS ORDENADAS", color=DATA, y=Y_CAP - 0.05)
    b.play(FadeOut(crowd), FadeIn(c, shift=UP * 0.2), f=0.15)
    b.finish(VGroup(p1, p2))

    b = Beat(s, "b2_closed")
    h = s.head("El mayor caso de corrupción de la democracia.", fs=70)
    x0 = -3.3
    bars_ = [("ERE", 679, GOLD), ("FILESA", 7.2, DATA)]
    grp = VGroup()
    for k, (lab, val, col) in enumerate(bars_):
        y = 0.9 - 1.5 * k
        w = max(0.06, 6.6 * val / 679)
        r = Rectangle(width=w, height=0.75, fill_color=col, fill_opacity=0.95, stroke_width=0)
        r.move_to([x0 + w / 2, y, 0])
        t = Text(lab, font=MONO, font_size=48, color=TXT, weight=BOLD).next_to([x0, y + 0.62, 0], RIGHT, buff=0)
        v = Text(("679 M€" if k == 0 else "7,2 M€"), font=MONO, font_size=48, color=col, weight=BOLD)
        v.next_to(r, RIGHT, buff=0.2) if k else v.move_to(r).set_color(BG)
        for m, txt in ((t, lab), (v, "x")):
            m.nwords, m.text = 1, txt
            s.reg(m)
        grp.add(VGroup(r, t, v))
    b.play(*s.clear(), reveal(h), f=0.3)
    b.play(*[GrowFromEdge(g[0], LEFT) for g in grp], *[FadeIn(g[1:]) for g in grp], f=0.4)
    b.finish(grp)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — ESCÁNDALOS REGIONALES
# ════════════════════════════════════════════════════════════════════════════
def block3(s: SaqueoBase):
    b = Beat(s, "b3_marea")
    hook = s.head("No solo los ERE.", fs=90)
    b.play(*s.clear(), *s.slam("CASO CERRADO"), reveal(hook), f=0.15)
    reg = region_blob(seed=7, r=2.6).move_to([0, 0.9, 0])
    rl = s.name("ASTURIAS", [0, 0.9, 0], color=DATA, fs=56)
    pin = VGroup(Circle(radius=0.22, color=ALERT_HI, fill_opacity=1), Triangle(color=ALERT_HI, fill_opacity=1)
                 .scale(0.2).rotate(PI).shift(DOWN * 0.28)).move_to([1.2, 1.5, 0])
    b.play(DrawBorderThenFill(reg), FadeIn(rl), f=0.18)
    h2 = s.head("Caso Marea: 5 condenados.", color=GOLD, fs=76)
    people = VGroup(*[official(1.1, TXT) for _ in range(5)]).arrange(RIGHT, buff=0.15).move_to([0, -1.35, 0])
    b.play(FadeOut(hook, shift=UP * 0.3), reveal(h2), FadeIn(pin, shift=DOWN * 0.4),
           LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in people], lag_ratio=0.1), f=0.22)
    h3 = s.head("Penas de hasta 9 años.", color=ALERT_HI, fs=80)
    c = s.cap("IGLESIAS RIOPEDRE · EXCONSEJERO", color=TXT)
    jb = jail_bars(6.8, 1.4).move_to(people)
    b.play(FadeOut(h2, shift=UP * 0.3), reveal(h3), FadeIn(c), Create(jb), *s.bar_to(0.82), f=0.25)
    b.finish(reg)

    b = Beat(s, "b3_faffe")
    icon = club_icon().move_to([0, 1.0, 0])
    h = s.head("Faffe: 32.000 € en prostíbulos.", color=TXT, fs=76)
    b.play(*s.clear(), reveal(h), FadeIn(icon, shift=UP * 0.3), f=0.25)
    tr = ValueTracker(0)
    cnt = s.counter(tr, lambda v: fmt_es(v) + " €", color=ALERT_HI, fs=100, y=-0.95)
    s.add(cnt)
    b.play(tr.animate.set_value(32_000), Indicate(icon[3], color=ALERT_HI, scale_factor=1.3), f=0.2)
    cnt.clear_updaters()
    sent = s.big("6 años → 5 años y 3 meses", color=GOLD, fs=66, y=-1.0)
    c = s.cap("MALVERSACIÓN", color=ALERT_HI)
    b.play(FadeOut(cnt, shift=UP * 0.3), reveal(sent), FadeIn(c), *s.bar_to(0.84), f=0.3)
    b.finish(icon)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — LA ERA SÁNCHEZ
# ════════════════════════════════════════════════════════════════════════════
def block4(s: SaqueoBase):
    b = Beat(s, "b4_koldo")
    hook = s.head("La corrupción no terminó. Se reinventó.", fs=74)
    b.play(*s.clear(), *s.slam("CASO CERRADO"), reveal(hook), f=0.15)
    m = mask_icon().move_to([0, 2.0, 0])
    p1 = official(2.2).move_to([-1.8, 0.1, 0])
    p2 = official(2.2).move_to([1.8, 0.1, 0])
    n1 = s.name("ÁBALOS", [-1.8, -1.35, 0], color=GOLD)
    n2 = s.name("KOLDO", [1.8, -1.35, 0], color=GOLD)
    b.play(FadeIn(m, scale=0.5), FadeIn(p1, shift=UP * 0.3), FadeIn(p2, shift=UP * 0.3), FadeIn(n1), FadeIn(n2), f=0.12)
    h2 = s.head("Ábalos: 24 años y 3 meses.", color=GOLD, fs=76)
    jb1 = jail_bars(2.1, 2.3).move_to(p1)
    b.play(FadeOut(hook, shift=UP * 0.3), reveal(h2), Create(jb1), FadeOut(m), f=0.18)
    h3 = s.head("Koldo: 19 años y 8 meses.", color=GOLD, fs=76)
    jb2 = jail_bars(2.1, 2.3).move_to(p2)
    b.play(FadeOut(h2, shift=UP * 0.3), reveal(h3), Create(jb2), f=0.18)
    c1 = s.cap("ORGANIZACIÓN CRIMINAL · COHECHO", color=ALERT_HI)
    b.play(FadeIn(c1, shift=UP * 0.2), *s.bar_to(0.90), f=0.12)
    c2 = s.cap("MALVERSACIÓN · TRÁFICO DE INFLUENCIAS", color=ALERT_HI)
    b.play(FadeOut(c1, shift=UP * 0.2), FadeIn(c2, shift=UP * 0.2), f=0.12)
    b.finish(VGroup(p1, p2))

    b = Beat(s, "b4_david")
    p = official(2.8).move_to([0, 0.5, 0])
    h = s.head("David Sánchez: 9 años de inhabilitación.", color=GOLD, fs=72)
    b.play(*s.clear(), reveal(h), FadeIn(p, shift=UP * 0.3), f=0.3)
    c = s.cap("PREVARICACIÓN · DIPUTACIÓN DE BADAJOZ", color=DATA)
    seal = stamp("CASO CERRADO", ALERT_HI, fs=48, angle=-10).scale(0.8).move_to(p.get_center() + DOWN * 0.4)
    s.reg(seal[1], 2)
    b.play(FadeIn(c, shift=UP * 0.2), FadeIn(seal, scale=2, rate_func=rush_into), *s.bar_to(0.93), f=0.3)
    b.finish(p)

    b = Beat(s, "b4_begona")
    p = official_f(2.8).move_to([0, 0.5, 0])
    h = s.head("Begoña Gómez: tráfico de influencias.", color=TXT, fs=74)
    b.play(*s.clear(), *s.slam("EN INVESTIGACIÓN"), reveal(h), FadeIn(p, shift=UP * 0.3), f=0.35)
    mg = magnifier(DATA, 0.55).move_to(p.get_center() + RIGHT * 1.2 + UP * 0.6)
    b.play(FadeIn(mg, scale=0.4), mg.animate.shift(LEFT * 0.4 + DOWN * 0.3), f=0.35)
    b.finish(p)

    b = Beat(s, "b4_open")
    cards_def = [("PLUS ULTRA", "HIJAS DE ZAPATERO INVESTIGADAS"), ("SEPI", "LEIRE DÍEZ"),
                 ("SANTOS CERDÁN", "PRESUNTOS AMAÑOS")]
    cards = VGroup()
    titles, subs = [], []
    for k, (t_, sub) in enumerate(cards_def):
        y = 2.3 - 1.55 * k
        box = RoundedRectangle(width=7.6, height=1.3, corner_radius=0.15, color=DATA, stroke_width=4,
                               fill_color=PANEL, fill_opacity=1).move_to([0, y, 0])
        mg = magnifier(DATA, 0.26).move_to([-3.25, y + 0.1, 0])
        tt = Text(t_, font=SANS, font_size=58, color=TXT, weight=BOLD)
        if tt.width > 5.8:
            tt.scale_to_fit_width(5.8)
        tt.move_to([0.25, y, 0])
        tt.nwords, tt.text = len(t_.split()), t_
        s.reg(tt)
        titles.append(tt)
        cards.add(VGroup(box, mg, tt))
        subs.append(sub)
    b.play(*s.clear(), FadeIn(cards[0], shift=LEFT * 0.6), f=0.12)
    cur = s.cap(subs[0], color=DATA, y=-2.55)
    b.play(FadeIn(cur, shift=UP * 0.2), f=0.15)
    for k in (1, 2):
        nxt = s.cap(subs[k], color=DATA, y=-2.55)
        b.play(FadeIn(cards[k], shift=LEFT * 0.6), FadeOut(cur, shift=UP * 0.2), FadeIn(nxt, shift=UP * 0.2), f=0.2)
        cur = nxt
    b.play(*[Indicate(c[1], color=GOLD, scale_factor=1.4) for c in cards], f=0.15)
    b.finish(cards)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — EL TOTAL
# ════════════════════════════════════════════════════════════════════════════
def block5(s: SaqueoBase):
    b = Beat(s, "b5_sum")
    h = s.big("Súmalo.", color=TXT, fs=120, y=2.9)
    b.play(*s.clear(), *s.slam("CASO CERRADO"), reveal(h), f=0.12)
    items = [("679 M€ · ERE", GOLD), ("1.200 M PTS · FILESA", DATA), ("27 ASESINATOS · GAL", ALERT_HI)]
    shown = None
    for k, (txt, col) in enumerate(items):
        m = s.big(txt, color=col, fs=84, y=0.6, font=MONO)
        anims = [reveal(m)]
        if shown is not None:
            anims.append(FadeOut(shown, shift=UP * 0.5))
        b.play(*anims, f=0.2)
        shown = m
    b.play(*s.bar_to(1.0, ">680 M€ · 27 ASESINATOS", GOLD), FadeOut(shown, shift=UP * 0.4),
           Flash(s.bar_frame.get_right(), color=GOLD, line_length=0.5), f=0.2)
    b.finish(s.bar_lbl)

    b = Beat(s, "b5_stamps")
    rnd = random.Random(12)
    pile = VGroup()
    for k in range(7):
        txt = "CASO CERRADO" if k % 3 != 2 else "EN INVESTIGACIÓN"
        st = stamp(txt, STAMP_COL[txt], fs=54, angle=rnd.uniform(-14, 14))
        st.move_to([rnd.uniform(-0.6, 0.6), 0.2 + rnd.uniform(-1.2, 1.2), 0])
        pile.add(st)
    h1 = s.head("Décadas de prisión.", color=GOLD, fs=84)
    b.play(FadeOut(h), reveal(h1), LaggedStart(*[FadeIn(st, scale=2.2, rate_func=rush_into) for st in pile[:4]],
                                               lag_ratio=0.3), f=0.4)
    for st in pile[:4]:
        st.set_opacity(0.25)
    h2 = s.head("40 años de casos.", color=TXT, fs=88)
    b.play(FadeOut(h1, shift=UP * 0.3), reveal(h2),
           LaggedStart(*[FadeIn(st, scale=2.2, rate_func=rush_into) for st in pile[4:]], lag_ratio=0.3),
           *[st.animate.set_opacity(0.25) for st in pile[:4]], f=0.4)
    for st in pile[4:6]:
        st.set_opacity(0.25)
    s.reg(pile[6][1], 2)
    b.finish(pile)

    b = Beat(s, "b5_open")
    h = s.head("Y causas que siguen abiertas.", color=ALERT_HI, fs=80)
    red = Rectangle(width=BAR_W, height=0.34, fill_color=ALERT_HI, fill_opacity=1, stroke_width=0).move_to([0, Y_BAR, 0])
    b.play(FadeOut(h2, shift=UP * 0.3), reveal(h), FadeIn(red), s.bar_frame.animate.set_stroke(ALERT_HI),
           pile.animate.set_opacity(0.2), f=0.5)
    s.bar_red = red
    b.play(Indicate(red, color=ALERT, scale_factor=1.04), f=0.3)
    b.finish(h)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 — CIERRE + CTA
# ════════════════════════════════════════════════════════════════════════════
def block6(s: SaqueoBase):
    b = Beat(s, "b6_recap")
    if not hasattr(s, "bar_red"):  # escena suelta
        s.bar_red = Rectangle(width=BAR_W, height=0.34, fill_color=ALERT_HI, fill_opacity=1,
                              stroke_width=0).move_to([0, Y_BAR, 0])
        s.add(s.bar_red)
    frozen = [s.bar_red, s.bar_fill]
    seq = [("679 millones.", GOLD), ("27 asesinatos.", ALERT_HI), ("1 pregunta:", TXT), ("¿Hasta cuándo?", TXT)]
    prev = None
    first = True
    for txt, col in seq:
        m = s.big(txt, color=col, fs=104, y=1.0)
        anims = [FadeIn(m, scale=1.25)]
        if first:
            anims += s.clear(extra_keep=frozen)
            first = False
        if prev is not None:
            anims.append(FadeOut(prev, scale=0.8))
        b.play(*anims, f=0.2)
        prev = m
    b.finish(prev)

    b = Beat(s, "b6_cta")
    c1 = kinetic_text("Si quieres que analice", fs=62, color=BG, max_w=7.2)
    s.reg(c1)
    ban = Rectangle(width=8.0, height=c1.height + 0.5, fill_color=GOLD, fill_opacity=1, stroke_width=0)
    ban.move_to([0, -1.3, 0])
    c1.move_to(ban)
    b.play(FadeOut(prev, shift=UP * 0.3), FadeOut(s.bar_lbl), FadeIn(ban, shift=UP * 0.4), reveal(c1), f=0.14)
    s.bar_lbl = None
    c2 = s.reg(kinetic_text("los archivos completos,", fs=62, color=BG, max_w=7.2).move_to(ban))
    b.play(FadeOut(c1, shift=UP * 0.3), FadeIn(c2, shift=UP * 0.3), f=0.12)
    c3 = s.reg(kinetic_text("sígueme.", fs=90, color=BG, max_w=7.2).move_to(ban))
    arrow = Arrow(ban.get_top() + RIGHT * 2.6, CORNER_TR, color=GOLD, stroke_width=9, buff=0.1,
                  max_tip_length_to_length_ratio=0.08)
    b.play(FadeOut(c2, shift=UP * 0.3), FadeIn(c3, scale=1.4), GrowArrow(arrow), f=0.14)
    q = kinetic_text("¿Cuál es el caso que más te impacta?", fs=56, color=BG, max_w=6.4)
    box = RoundedRectangle(width=q.width + 0.6, height=q.height + 0.5, corner_radius=0.3, color=TXT,
                           fill_color=TXT, fill_opacity=1).move_to([0, 2.2, 0])
    tail = Polygon(box.get_corner(DL) + RIGHT * 0.6, box.get_corner(DL) + RIGHT * 1.3,
                   box.get_corner(DL) + RIGHT * 0.3 + DOWN * 0.45, color=TXT, fill_color=TXT, fill_opacity=1)
    q.move_to(box)
    s.reg(q)
    bubble = VGroup(tail, box, q)
    follow = VGroup(Circle(radius=0.2, color=BG, fill_opacity=1).move_to([-0.25, 0.2, 0]),
                    RoundedRectangle(width=0.7, height=0.4, corner_radius=0.18, color=BG, fill_opacity=1)
                    .move_to([-0.25, -0.25, 0]),
                    Line([0.35, 0, 0], [0.85, 0, 0], color=BG, stroke_width=8),
                    Line([0.6, -0.25, 0], [0.6, 0.25, 0], color=BG, stroke_width=8)).move_to(ban)
    b.play(FadeIn(bubble, shift=UP * 0.4, scale=0.85), FadeOut(c3, scale=0.6), FadeIn(follow, scale=1.6), f=0.16)
    b.play(arrow.animate(rate_func=there_and_back).shift(UR * 0.15), Indicate(follow, color=PANEL, scale_factor=1.2), f=0.14)
    b.play(arrow.animate(rate_func=there_and_back).shift(UR * 0.15), Indicate(bubble, color=TXT, scale_factor=1.04),
           f=0.14)
    b.finish(bubble)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


# ════════════════════════════════════════════════════════════════════════════
# ESCENAS: 7 bloques + vídeo completo
# ════════════════════════════════════════════════════════════════════════════
class _Block(SaqueoBase):
    BLOCK = 0

    def construct(self):
        self.setup_persistent(self.BLOCK)
        if self.BLOCK > 0:
            self.stamp_mob = None
        BLOCKS[self.BLOCK](self)
        self.report()


class Block0Hook(_Block):
    BLOCK = 0


class Block1Origenes(_Block):
    BLOCK = 1


class Block2ERE(_Block):
    BLOCK = 2


class Block3Regionales(_Block):
    BLOCK = 3


class Block4EraSanchez(_Block):
    BLOCK = 4


class Block5Total(_Block):
    BLOCK = 5


class Block6Cierre(_Block):
    BLOCK = 6


class FullVideo(SaqueoBase):
    """Los 7 bloques en una toma continua: 5400 fotogramas = 180.0 s exactos."""

    def construct(self):
        self.setup_persistent(0)
        for blk in BLOCKS:
            blk(self)
        self.report()
