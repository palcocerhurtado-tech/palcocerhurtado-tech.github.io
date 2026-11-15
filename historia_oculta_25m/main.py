"""
main.py — «25 MILLONES DE AÑOS DE GUERRA OCULTA»
Escena Manim CE `HistoriaOculta` · 1080x1920 · 30 fps · ~180 s

  python narration.py
  manim render main.py HistoriaOculta -r 1080,1920 --fps 30
  python narration.py --mux media/videos/main/1920p30/HistoriaOculta.mp4

Todo es geometría generada en código. Lee timings.json (si no existe usa las
duraciones nominales del guion). Cada bloque B0…B10 consume exactamente su
duración: el reloj trabaja en fotogramas enteros con fin de bloque absoluto.
"""

from __future__ import annotations

import json
import math
import os
import random
import subprocess

import numpy as np
from manim import *  # noqa: F401,F403

# ════════════════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════════════════
PREVIEW = os.environ.get("PREVIEW") == "1"
config.pixel_width = 540 if PREVIEW else 1080
config.pixel_height = 960 if PREVIEW else 1920
config.frame_rate = 15 if PREVIEW else 30
config.frame_height = 16.0
config.frame_width = 9.0
config.background_color = "#07060B"
FPS = config.frame_rate

FONDO = "#07060B"
NOCHE = "#14111F"
ORO = "#D4AF37"
ORO_CLARO = "#F5D77A"
CIAN = "#3FE0FF"
CARMESI = "#E0284B"
VIOLETA = "#8A5CFF"
VERDE = "#39D98A"
FOSFORO = "#3BFF6E"
HUESO = "#EDE6D6"
GRIS = "#6E6A78"

SAFE = (-4.0, 4.0, -4.80, 6.08)  # xmin, xmax, ymin, ymax
MAX_W = 7.6
MIN_FS = 48
HEAD_TOP = 5.75
VIS_C = np.array([0, 0.45, 0])
LBL_Y = -1.95
EYE_POS = np.array([0, 2.8, 0])  # ojo final == punto del primer frame (loop)

HERE = os.path.dirname(os.path.abspath(__file__))


def _pick_font(cands, fallback):
    try:
        out = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout
    except Exception:
        return fallback
    fams = {f.strip() for line in out.splitlines() for f in line.split(",")}
    for c in cands:
        if c in fams:
            return c
    return fallback


FONT = _pick_font(["Bebas Neue", "Oswald", "Montserrat", "DejaVu Sans"], "Sans")
MONO = _pick_font(["DejaVu Sans Mono"], "Monospace")

# ════════════════════════════════════════════════════════════════════════════
# TIMINGS
# ════════════════════════════════════════════════════════════════════════════
NOMINAL = {"B0": 6, "B1": 15, "B2": 15, "B3": 15, "B4": 17, "B5": 18,
           "B6": 15, "B7": 19, "B8": 18, "B9": 23, "B10": 19}
ORDER = [f"B{i}" for i in range(11)]


def load_timings():
    p = os.path.join(HERE, "timings.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        blocks = {b["id"]: (float(b["start"]), float(b["dur"])) for b in d["blocks"]}
        if all(k in blocks for k in ORDER):
            return blocks, float(d["total"])
    t, blocks = 0.0, {}
    for k in ORDER:
        blocks[k] = (t, float(NOMINAL[k]))
        t += NOMINAL[k]
    return blocks, t


TIMINGS, TOTAL = load_timings()


# ════════════════════════════════════════════════════════════════════════════
# UTILIDADES GRÁFICAS
# ════════════════════════════════════════════════════════════════════════════
def assert_safe(m: Mobject, what: str = "") -> Mobject:
    x0, x1, y0, y1 = SAFE
    eps = 0.02
    l, r = m.get_left()[0], m.get_right()[0]
    b, t = m.get_bottom()[1], m.get_top()[1]
    assert l >= x0 - eps and r <= x1 + eps and b >= y0 - eps and t <= y1 + eps, \
        f"fuera de safe-zone: {what!r} x=[{l:.2f},{r:.2f}] y=[{b:.2f},{t:.2f}]"
    return m


def glow(m: VMobject, color=None, width=None) -> VGroup:
    """Copia detrás con stroke x3 y opacidad 0,25."""
    back = m.copy()
    for sm in back.family_members_with_points():
        sw = sm.get_stroke_width() or 2
        sm.set_stroke(color or sm.get_color(), width=width or max(3 * sw, 6), opacity=0.25)
        sm.set_fill(opacity=0)
    return VGroup(back, m)


def n_words(text: str) -> int:
    return len(text.split())


def ktext(text: str, fs=92, color=HUESO, font=None, max_w=MAX_W, max_lines=3,
          min_fs=None) -> VGroup:
    """Texto en líneas de palabras (submobjects = palabras). Nunca < 48."""
    font = font or FONT
    floor = max(MIN_FS, min_fs or int(fs * 0.62))
    words = text.split()
    while True:
        mobs = [Text(w, font=font, font_size=fs, color=color, weight=BOLD) for w in words]
        sp = Text("n", font=font, font_size=fs, weight=BOLD).width * 0.55
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
        if (len(lines) <= max_lines and widest <= max_w) or fs <= floor:
            break
        fs = max(floor, fs - 6)
    rows = VGroup(*[VGroup(*ln).arrange(RIGHT, buff=sp, aligned_edge=DOWN) for ln in lines])
    for row, ln in zip(rows, lines):  # signos sueltos (· – → = + &) centrados en la altura de las mayúsculas
        refs = [m for m, w in zip(ln, [x for x in words]) if m.height > 0.5 * max(z.height for z in ln)]
        cy = np.mean([m.get_center()[1] for m in refs]) if refs else row.get_center()[1]
        for m in ln:
            if m.height < 0.45 * max(z.height for z in ln):
                m.set_y(cy)
    rows.arrange(DOWN, buff=0.18 * fs / 48)
    if rows.width > max_w:
        rows.scale_to_fit_width(max_w)
    rows.nwords = len(words)
    rows.text = text
    return rows


def reveal(m: VGroup):
    n = getattr(m, "nwords", 1)
    if n <= 4:
        return Write(m)
    words = [w for row in m for w in row]
    return LaggedStart(*[FadeIn(p, shift=0.25 * UP) for p in words], lag_ratio=0.12)


# ── glifos de nivel ────────────────────────────────────────────────────────
def g_star(s, c):
    return Star(5, outer_radius=s * 0.55, inner_radius=s * 0.24, color=c, fill_opacity=1, stroke_width=1)


def g_wave(s, c):
    return ParametricFunction(lambda t: np.array([t, 0.25 * s * np.sin(t * 2 * PI / (s * 0.55)), 0]),
                              t_range=[-s * 0.6, s * 0.6, s / 40], color=c, stroke_width=3)


def g_wedge(s, c):
    return VGroup(Triangle(color=c, fill_opacity=1, stroke_width=1).scale(s * 0.2).rotate(-PI / 2)
                  .shift(LEFT * s * 0.3),
                  Line(LEFT * s * 0.15, RIGHT * s * 0.55, color=c, stroke_width=3))


def g_hex(s, c):
    return RegularPolygon(6, color=c, stroke_width=3).scale(s * 0.5)


def g_delta(s, c):
    return VGroup(Triangle(color=c, stroke_width=3).scale(s * 0.55),
                  Dot(radius=s * 0.08, color=c).shift(DOWN * s * 0.08))


def g_bars(s, c):
    return VGroup(*[Rectangle(width=s * 0.16, height=s * 0.8, color=c, fill_opacity=1, stroke_width=0)
                    .shift(RIGHT * (i - 1) * s * 0.32) for i in range(3)])


def g_spiral(s, c):
    return ParametricFunction(lambda t: s * 0.09 * t * np.array([np.cos(t), np.sin(t), 0]),
                              t_range=[0, 3 * TAU, 0.1], color=c, stroke_width=3).scale(0.35)


def g_arch(s, c):
    return VGroup(Arc(radius=s * 0.45, start_angle=0, angle=PI, color=c, stroke_width=3),
                  Line(LEFT * s * 0.45, RIGHT * s * 0.45, color=c, stroke_width=3))


def g_censor(s, c):
    return Rectangle(width=s * 1.2, height=s * 0.32, color=c, fill_color=FONDO, fill_opacity=1,
                     stroke_width=3)


def g_bolt(s, c):
    return Polygon([0.1, 0.5, 0], [-0.25, -0.05, 0], [0.02, -0.05, 0], [-0.15, -0.5, 0],
                   [0.28, 0.1, 0], [0.02, 0.1, 0], color=c, fill_opacity=1, stroke_width=1).scale(s)


GLYPHS = [g_star, g_wave, g_wedge, g_hex, g_delta, g_bars, g_spiral, g_arch, g_censor, g_bolt]
LEVEL_COL = [CIAN, VERDE, ORO, VIOLETA, ORO, CARMESI, VIOLETA, CARMESI, FOSFORO, ORO]


# ── pirámide ───────────────────────────────────────────────────────────────
P_BASE_Y, P_APEX_Y, P_W, P_H = -4.55, -2.35, 4.4, 2.2
P_CAP_H = 0.34
P_LVL_H = (P_H - P_CAP_H) / 10


def p_width(y):
    return P_W * (P_APEX_Y - y) / P_H


def level_poly(i, color):
    yb = P_BASE_Y + i * P_LVL_H + 0.012
    yt = yb + P_LVL_H - 0.024
    wb, wt = p_width(yb) / 2, p_width(yt) / 2
    return Polygon([-wb, yb, 0], [wb, yb, 0], [wt, yt, 0], [-wt, yt, 0],
                   color=color, stroke_width=2, fill_color=color, fill_opacity=0.75)


def closed_eye(w=0.34, c=ORO_CLARO):
    a = ArcBetweenPoints(LEFT * w / 2, RIGHT * w / 2, angle=0.7, color=c, stroke_width=3)
    b = ArcBetweenPoints(LEFT * w / 2, RIGHT * w / 2, angle=0.45, color=c, stroke_width=3)
    lashes = VGroup(*[Line(a.point_from_proportion(p), a.point_from_proportion(p) + DOWN * w * 0.15,
                           color=c, stroke_width=2) for p in (0.3, 0.5, 0.7)])
    return VGroup(a, b, lashes)


def open_eye(w=2.0, c=ORO_CLARO):
    up = ArcBetweenPoints(LEFT * w / 2, RIGHT * w / 2, angle=-1.6, color=c, stroke_width=6)
    lo = ArcBetweenPoints(LEFT * w / 2, RIGHT * w / 2, angle=1.6, color=c, stroke_width=6)
    return VGroup(up, lo)


def triangle_eye_symbol(s=1.0, c=ORO):
    tri = Triangle(color=c, stroke_width=5).scale(s)
    eye = VGroup(ArcBetweenPoints(LEFT * 0.5 * s, RIGHT * 0.5 * s, angle=-1.4, color=c, stroke_width=4),
                 ArcBetweenPoints(LEFT * 0.5 * s, RIGHT * 0.5 * s, angle=1.4, color=c, stroke_width=4),
                 Dot(radius=0.09 * s, color=ORO_CLARO)).shift(DOWN * 0.12 * s)
    return VGroup(tri, eye)


def obelisk(h=3.0, c=HUESO):
    w0, w1 = 0.36, 0.24
    shaft = Polygon([-w0, 0, 0], [w0, 0, 0], [w1, h, 0], [-w1, h, 0], color=c, fill_color=NOCHE,
                    fill_opacity=1, stroke_width=3)
    tip = Polygon([-w1, h, 0], [w1, h, 0], [0, h + 0.38, 0], color=ORO, fill_color=ORO, fill_opacity=1)
    return VGroup(shaft, tip)


def blob(r=1.0, seed=1, jitter=0.25, n=12, color=CIAN, fill=0.5):
    rnd = random.Random(seed)
    pts = [[r * (1 + rnd.uniform(-jitter, jitter)) * np.cos(TAU * i / n),
            r * (1 + rnd.uniform(-jitter, jitter)) * np.sin(TAU * i / n) * 0.8, 0] for i in range(n)]
    m = VMobject(stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=fill)
    m.set_points_smoothly(pts + [pts[0]])
    return m


def humanoid(h=2.4, c=ORO, fill=0.9):
    s = h / 2.4
    return VGroup(
        Circle(radius=0.26 * s, color=c, fill_opacity=fill).move_to([0, 0.95 * s, 0]),
        Polygon([-0.5 * s, 0.6 * s, 0], [0.5 * s, 0.6 * s, 0], [0.3 * s, -0.5 * s, 0],
                [0.2 * s, -1.2 * s, 0], [-0.2 * s, -1.2 * s, 0], [-0.3 * s, -0.5 * s, 0],
                color=c, fill_opacity=fill))


def book(w=2.6, h=1.8, c=ORO):
    left = Rectangle(width=w / 2, height=h, color=c, fill_color=NOCHE, fill_opacity=1,
                     stroke_width=4).next_to(ORIGIN, LEFT, buff=0)
    right = left.copy().next_to(ORIGIN, RIGHT, buff=0)
    cover = right.copy().set_fill(c, 0.9)
    lines_l = VGroup(*[Line([-w / 2 + 0.2, y, 0], [-0.2, y, 0], color=c, stroke_width=2, stroke_opacity=0.5)
                       for y in np.linspace(h / 2 - 0.3, -h / 2 + 0.3, 6)])
    lines_r = lines_l.copy().shift(RIGHT * w / 2)
    return VGroup(left, right, lines_l, lines_r, cover)


def lightning(p0, p1, seed=0, c=ORO_CLARO, segs=9):
    rnd = random.Random(seed)
    p0, p1 = np.array(p0, float), np.array(p1, float)
    pts = [p0]
    for i in range(1, segs):
        q = p0 + (p1 - p0) * i / segs
        pts.append(q + np.array([rnd.uniform(-0.35, 0.35), 0, 0]))
    pts.append(p1)
    return VMobject(color=c, stroke_width=7).set_points_as_corners(pts)


# ════════════════════════════════════════════════════════════════════════════
# RELOJ
# ════════════════════════════════════════════════════════════════════════════
class Timeline:
    """Reparte el bloque por pesos (segundos nominales del guion) en fotogramas enteros.

    Manim genera ceil(run_time·fps) fotogramas ⇒ run_time=(n−0,5)/fps da n exactos.
    El fin de cada sub-marca se calcula en absoluto: no hay deriva acumulada.
    """

    def __init__(self, scene: "HistoriaOculta", bid: str):
        self.s = scene
        self.bid = bid
        start, dur = TIMINGS[bid]
        self.f0 = int(round(start * FPS))
        self.f1 = int(round((start + dur) * FPS))
        err = scene.fc - self.f0
        scene.log.append(f"{bid}: inicio esperado {self.f0} fr, real {scene.fc} fr "
                         f"(error {err} fr) · renderer.time={scene.renderer.time:.3f}s")
        if err != 0:  # corrección: el bloque anterior se pasó/quedó corto
            self.f0 = scene.fc
        self.k = (self.f1 - self.f0) / NOMINAL[bid]  # fotogramas por segundo nominal
        self.w = 0.0

    def play(self, *anims, w: float = 1.0, **kw):
        self.w += w
        target = self.f0 + int(round(self.w * self.k))
        n = target - self.s.fc
        if n < 2:
            n = 2
        self.s._play_frames(n, *anims, **kw)

    def finish(self, focus: Mobject | None = None):
        n = self.f1 - self.s.fc
        if n >= 2:
            self.s.ambient(n, focus)
        elif n == 1:
            self.s.ambient(2, focus)


# ════════════════════════════════════════════════════════════════════════════
# ESCENA
# ════════════════════════════════════════════════════════════════════════════
class HistoriaOculta(Scene):
    def construct(self):
        self.fc = 0
        self.log: list[str] = []
        self.texts: list[tuple[Mobject, int]] = []
        self.word_peak = (0, 0.0, [])
        self.violations: list[str] = []
        self.setup_layers()
        for bid in ORDER:
            getattr(self, f"block_{bid}")(TIMINGS[bid][1])
        self.report()

    # ── capas persistentes ────────────────────────────────────────────────
    def setup_layers(self):
        rnd = random.Random(11)
        self.dust_k = ValueTracker(1.0)
        self.dust_t = 0.0
        dust = VGroup()
        for _ in range(220):
            d = Dot([rnd.uniform(-4.7, 4.7), rnd.uniform(-8.3, 8.3), 0],
                    radius=rnd.uniform(0.008, 0.03), color=rnd.choice([HUESO, HUESO, ORO_CLARO, CIAN]))
            d.base = rnd.uniform(0.15, 0.6)
            d.ph = rnd.uniform(0, TAU)
            d.sp = rnd.uniform(0.03, 0.12)
            d.set_opacity(d.base)
            dust.add(d)

        def drift(g, dt):
            self.dust_t += dt
            k = self.dust_k.get_value()
            for d in g:
                d.shift(DOWN * d.sp * k * dt)
                if d.get_y() < -8.4:
                    d.shift(UP * 16.8)
                d.set_opacity(d.base * (0.55 + 0.45 * math.sin(2.1 * self.dust_t + d.ph)))

        dust.add_updater(drift)
        self.dust = dust
        self.add(dust, self.dust_k)

        vig = VGroup()
        for i in range(8):
            op = 0.5 * (1 - i / 8) ** 1.6
            for rect in (Rectangle(width=9.2, height=0.18).move_to([0, 8 - 0.09 - i * 0.18, 0]),
                         Rectangle(width=9.2, height=0.18).move_to([0, -8 + 0.09 + i * 0.18, 0]),
                         Rectangle(width=0.12, height=16.2).move_to([-4.5 + 0.06 + i * 0.12, 0, 0]),
                         Rectangle(width=0.12, height=16.2).move_to([4.5 - 0.06 - i * 0.12, 0, 0])):
                rect.set_fill(FONDO, op).set_stroke(width=0)
                vig.add(rect)
        self.vig = vig
        self.add_foreground_mobjects(vig)

        # pirámide: contorno + piedra angular (niveles se añaden al encenderse)
        apex = np.array([0, P_APEX_Y, 0])
        bl, br = np.array([-P_W / 2, P_BASE_Y, 0]), np.array([P_W / 2, P_BASE_Y, 0])
        contour = DashedVMobject(Polygon(bl, br, apex, color=ORO, stroke_width=3), num_dashes=46)
        cb = P_APEX_Y - P_CAP_H
        cap = Polygon([-p_width(cb) / 2, cb, 0], [p_width(cb) / 2, cb, 0], apex,
                      color=ORO, stroke_width=3, fill_color=NOCHE, fill_opacity=1)
        eye = closed_eye().move_to([0, cb + 0.1, 0])
        self.p_contour, self.p_cap, self.p_eye = contour, cap, eye
        self.levels = VGroup()
        self.glyphs = VGroup()
        self.pyr = VGroup(contour, self.levels, self.glyphs, cap, eye)
        self.pyr_dimmed = False

    # ── utilidades de escena ──────────────────────────────────────────────
    def _play_frames(self, n: int, *anims, **kw):
        self.play(*anims, run_time=(n - 0.5) / FPS, **kw)
        self.fc += n
        self.check_words()

    def ambient(self, n: int, focus: Mobject | None = None):
        anims = [self.dust_k.animate.set_value(self.dust_k.get_value())]
        if focus is not None:
            anims.append(focus.animate(rate_func=there_and_back).scale(1.03))
        self._play_frames(n, *anims)

    def reg(self, m: Mobject, n: int | None = None) -> Mobject:
        self.texts.append((m, n if n is not None else getattr(m, "nwords", 1)))
        assert_safe(m, getattr(m, "text", ""))
        return m

    def T(self, text, fs=92, color=HUESO, pos=None, top=None, font=None, max_w=MAX_W,
          max_lines=3, glow_it=False, min_fs=None):
        m = ktext(text, fs=fs, color=color, font=font, max_w=max_w, max_lines=max_lines,
                  min_fs=min_fs)
        if top is not None:
            m.move_to([0 if pos is None else pos[0], 0, 0])
            m.shift(UP * (top - m.get_top()[1]))
        elif pos is not None:
            m.move_to(pos)
        self.reg(m)
        if glow_it:
            g = glow(m, color, width=5)
            g.nwords, g.text = m.nwords, m.text
            return g
        return m

    def head(self, text, color=HUESO, fs=94, glow_it=True):
        return self.T(text, fs=fs, color=color, top=HEAD_TOP, glow_it=glow_it)

    def label(self, text, color=HUESO, fs=54, y=LBL_Y, x=0.0, font=None, max_w=MAX_W):
        return self.T(text, fs=fs, color=color, pos=[x, y, 0], font=font, max_w=max_w,
                      max_lines=2, min_fs=MIN_FS)

    def counter(self, tracker, fs=150, color=CIAN, pos=VIS_C, prefix="", suffix="", font=None):
        font = font or FONT

        def mk():
            v = int(round(tracker.get_value()))
            t = Text(prefix + f"{v:,}".replace(",", ".") + suffix, font=font, font_size=fs,
                     color=color, weight=BOLD)
            if t.width > MAX_W:
                t.scale_to_fit_width(MAX_W)
            return t.move_to(pos)

        m = always_redraw(mk)
        self.texts.append((m, 1))
        return m

    def check_words(self):
        fam = {id(m) for m in self.get_mobject_family_members()}
        n, who = 0, []
        for m, k in self.texts:
            if id(m) in fam:
                ops = [sm.get_fill_opacity() for sm in m.family_members_with_points()]
                if ops and max(ops) > 0.1:
                    n += k
                    who.append(getattr(m, "text", "#"))
        if n > self.word_peak[0]:
            self.word_peak = (n, self.fc / FPS, who)
        if n > 8:
            self.violations.append(f"{self.fc / FPS:7.2f}s  {n} palabras: {who}")

    def keep(self) -> list[Mobject]:
        return [self.dust, self.dust_k, self.vig, self.pyr]

    def clear(self, **kw) -> list[Animation]:
        keep_ids = set()
        for m in self.keep():
            keep_ids.update(id(x) for x in m.get_family())
        return [FadeOut(m, **kw) for m in self.mobjects
                if not any(id(x) in keep_ids for x in m.get_family())]

    # ── pirámide ─────────────────────────────────────────────────────────
    def pyr_dim(self) -> Animation:
        self.pyr_dimmed = True
        base = np.array([0, P_BASE_Y, 0])
        return self.pyr.animate.scale(0.85, about_point=base).fade(0.75)

    def light_block(self, tl: Timeline, i: int, *anims, w=0.8):
        """Primer paso de cada bloque: el nivel i entra deslizándose y se enciende con su glifo."""
        pre = []
        if self.pyr_dimmed:
            pre.append(Restore(self.pyr))
            self.pyr_dimmed = False
        col = LEVEL_COL[i]
        lv = level_poly(i, col)
        gl = GLYPHS[i](0.15, FONDO).move_to(lv.get_center())
        if i == 8:
            gl.set_stroke(FONDO).set_fill(FONDO, 1)
        vis = VGroup(lv, gl)
        start = vis.copy().shift(LEFT * 2.6).set_opacity(0)
        tl.play(*pre, Transform(start, vis.copy(), remover=True), *anims, w=w)
        self.levels.add(lv)
        self.glyphs.add(gl)
        self.pyr.save_state()

    # ══════════════════════════════════════════════════════════════════════
    # B0 · GANCHO
    # ══════════════════════════════════════════════════════════════════════
    def block_B0(self, T):
        tl = Timeline(self, "B0")
        dot = Dot(EYE_POS, radius=0.09, color=ORO_CLARO)
        self.add(dot)
        ring = Circle(radius=0.09, color=ORO, stroke_width=6).move_to(EYE_POS)
        tl.play(ring.animate.scale(14).set_stroke(opacity=0), dot.animate.scale(0.2).set_opacity(0),
                w=0.3)
        self.remove(ring, dot)

        tr = ValueTracker(0)
        cnt = self.counter(tr, fs=150, color=CIAN, pos=[0, 1.3, 0])
        sub = self.T("AÑOS DE GUERRA OCULTA", fs=64, color=HUESO, pos=[0, -0.45, 0])
        cta = self.T("MÍRALO ENTERO", fs=52, color=ORO_CLARO, pos=[0, 5.55, 0])
        self.add(cnt)
        tl.play(tr.animate(rate_func=rate_functions.ease_out_cubic).set_value(25_000_000),
                Write(sub), FadeIn(cta, shift=DOWN * 0.2), w=1.9)
        cnt.clear_updaters()

        words = [("LIRA", g_star, CIAN), ("ATLÁNTIDA", g_wave, CIAN),
                 ("SATURNO", None, VIOLETA), ("ILLUMINATI", g_delta, ORO), ("EPSTEIN", g_censor, FOSFORO)]
        prev = VGroup(cnt, sub, cta)
        for w, gfn, col in words:
            word = self.T(w, fs=104, color=col, pos=[0, 0.2, 0], glow_it=True)
            if gfn is None:
                icon = VGroup(Circle(radius=0.32, color=col, fill_opacity=0.9),
                              Ellipse(width=1.3, height=0.32, color=ORO, stroke_width=4).rotate(0.25))
            else:
                icon = gfn(1.1, col)
            icon.move_to([0, 1.85, 0])
            tl.play(FadeOut(prev, scale=1.25), FadeIn(word, scale=0.7), FadeIn(icon, scale=0.4), w=0.48)
            prev = VGroup(word, icon)

        una = self.T("UNA SOLA GUERRA", fs=100, color=ORO, pos=[0, 0.6, 0], glow_it=True)
        tl.play(FadeOut(prev, scale=1.2), Write(una), Create(self.p_contour), FadeIn(self.p_cap),
                Create(self.p_eye), w=1.0)
        self.add(self.pyr)
        self.pyr.save_state()
        tl.finish(una)

    # ══════════════════════════════════════════════════════════════════════
    # B1 · LAS GUERRAS DE LIRA
    # ══════════════════════════════════════════════════════════════════════
    def block_B1(self, T):
        tl = Timeline(self, "B1")
        C = VIS_C + UP * 0.1
        vega = Dot(C + np.array([-0.9, 1.0, 0]), radius=0.16, color=CIAN)
        vg = glow(vega.copy().set_stroke(CIAN, 4), CIAN, width=18)
        para = [C + np.array(p) for p in ([-0.4, 0.3, 0], [0.5, 0.15, 0], [0.75, -1.1, 0], [-0.15, -0.95, 0])]
        stars = VGroup(*[Dot(p, radius=0.09, color=CIAN) for p in para])
        lines = VMobject(color=CIAN, stroke_width=3).set_points_as_corners(para + [para[0]])
        link = Line(vega.get_center(), para[0], color=CIAN, stroke_width=3)
        h1 = self.head("HACE 22 MILLONES DE AÑOS", color=HUESO)
        self.light_block(tl, 0, *self.clear(), self.dust_k.animate.set_value(6), FadeIn(vega), FadeIn(vg),
                         w=0.8)
        tl.play(reveal(h1), Create(lines), Create(link), LaggedStart(*[FadeIn(s, scale=2) for s in stars]),
                w=1.4)
        tl.play(self.dust_k.animate.set_value(1.5), self.pyr_dim(), Indicate(vega, scale_factor=1.6), w=0.8)

        # zoom: 14 planetas en órbitas concéntricas + serpiente Draco
        orbits = VGroup(*[Circle(radius=0.38 + 0.115 * i, color=CIAN, stroke_width=1.2, stroke_opacity=0.35)
                          .move_to(VIS_C) for i in range(14)])
        rnd = random.Random(3)
        planets = VGroup()
        for i in range(14):
            a = rnd.uniform(0, TAU)
            p = Dot(VIS_C + (0.38 + 0.115 * i) * np.array([np.cos(a), np.sin(a), 0]),
                    radius=0.075, color=CIAN)
            p.ang, p.rad, p.w = a, 0.38 + 0.115 * i, 0.9 / (1 + i * 0.25)
            planets.add(p)

        def orbit_upd(g, dt):
            for p in g:
                p.ang += p.w * dt
                p.move_to(VIS_C + p.rad * np.array([np.cos(p.ang), np.sin(p.ang), 0]))

        sun = Dot(VIS_C, radius=0.2, color=CIAN)
        h2 = self.head("IMPERIO DRACO · THUBAN", color=CARMESI)
        tl.play(FadeOut(VGroup(stars, lines, link), scale=2.5), FadeOut(vg),
                vega.animate.move_to(VIS_C).scale(1.3), FadeOut(h1, shift=UP * 0.3), w=0.9)
        self.remove(vega)
        self.add(sun)
        planets.add_updater(orbit_upd)
        snake = VGroup()
        for k in range(30):
            s = k / 29
            x = -3.6 + 3.2 * s
            y = 3.3 - 2.6 * s + 0.35 * np.sin(s * 3.3 * TAU)
            ang = math.atan2(-2.6 + 0.35 * 3.3 * TAU * np.cos(s * 3.3 * TAU), 3.2)
            snake.add(Triangle(color=CARMESI, fill_opacity=0.9, stroke_width=1)
                      .scale(0.15 - 0.07 * s).rotate(ang - PI / 2).move_to([x, y, 0]))
        tl.play(LaggedStart(*[Create(o) for o in orbits], lag_ratio=0.05),
                LaggedStart(*[FadeIn(p, scale=2) for p in planets], lag_ratio=0.05), w=1.0)
        tl.play(reveal(h2), LaggedStart(*[FadeIn(t, shift=RIGHT * 0.3) for t in snake], lag_ratio=0.08),
                w=1.1)

        # 3 planetas estallan
        planets.clear_updaters()
        victims = [planets[5], planets[9], planets[12]]
        lab = self.label("BILA · TEKA · MERCK", color=CARMESI)
        tl.play(*[v.animate.set_color(CARMESI).scale(1.8) for v in victims], FadeOut(h2, shift=UP * 0.3),
                FadeIn(lab), w=1.0)
        frags_anims, frags = [], VGroup()
        rr = random.Random(9)
        for v in victims:
            for _ in range(20):
                f = Dot(v.get_center(), radius=rr.uniform(0.02, 0.05), color=CARMESI)
                a = rr.uniform(0, TAU)
                frags.add(f)
                frags_anims.append(f.animate.shift(rr.uniform(0.4, 1.3) * np.array([np.cos(a), np.sin(a), 0]))
                                   .set_opacity(0))
        self.add(frags)
        tr = ValueTracker(0)
        cnt = self.counter(tr, fs=150, color=CARMESI, pos=[0, 4.75, 0])
        muertos = self.T("MUERTOS", fs=72, color=CARMESI, pos=[0, 3.55, 0])
        self.add(cnt)
        tl.play(*frags_anims, *[FadeOut(v, scale=2) for v in victims], Flash(VIS_C, color=CARMESI),
                tr.animate(rate_func=rate_functions.ease_out_cubic).set_value(50_000_000), w=1.8)
        cnt.clear_updaters()
        tl.play(Write(muertos), snake.animate.shift(DOWN * 0.3 + RIGHT * 0.3), w=1.2)
        self.remove(frags)

        # diáspora
        dests = {"PLÉYADES": [-3.0, -1.0, 0], "SIRIO": [0.0, 2.6, 0], "ORIÓN": [3.0, -1.0, 0]}
        dmarks = VGroup(*[Star(5, outer_radius=0.2, inner_radius=0.09, color=CIAN, fill_opacity=1).move_to(p)
                          for p in dests.values()])
        lab2 = self.label("PLÉYADES · SIRIO · ORIÓN", color=CIAN)
        arcs, travellers = VGroup(), VGroup()
        for p in dests.values():
            a = ArcBetweenPoints(VIS_C, np.array(p), angle=-0.9, color=CIAN, stroke_width=3)
            arcs.add(a)
            for j in range(5):
                travellers.add(Dot(VIS_C, radius=0.05, color=CIAN))
        tl.play(FadeOut(VGroup(cnt, muertos, lab, snake), shift=UP * 0.3),
                LaggedStart(*[FadeIn(m, scale=3) for m in dmarks], lag_ratio=0.2), FadeIn(lab2), w=1.4)
        moves = []
        for k, t in enumerate(travellers):
            moves.append(MoveAlongPath(t, arcs[k // 5], rate_func=rate_functions.ease_in_out_sine))
        tl.play(LaggedStart(*moves, lag_ratio=0.06), Create(arcs), w=2.4)
        tl.finish(dmarks)

    # ══════════════════════════════════════════════════════════════════════
    # B2 · LEMURIA, ATLÁNTIDA, MALDEK
    # ══════════════════════════════════════════════════════════════════════
    def block_B2(self, T):
        tl = Timeline(self, "B2")
        R = 1.7
        earth = Circle(radius=R, color=CIAN, stroke_width=3, fill_color=NOCHE, fill_opacity=1).move_to(VIS_C)
        lat = ValueTracker(0)

        def lats():
            g = VGroup()
            ph = lat.get_value()
            for k in range(6):
                f = abs(np.cos(ph + k * PI / 6))
                g.add(Ellipse(width=2 * R * max(f, 0.02), height=2 * R, color=CIAN, stroke_width=1.2,
                              stroke_opacity=0.35).move_to(VIS_C))
            return g

        meridians = always_redraw(lats)
        lem = blob(0.55, seed=4, color=VERDE, fill=0.8).move_to(VIS_C + np.array([-0.85, 0.2, 0]))
        atl = blob(0.55, seed=8, color=CIAN, fill=0.8).move_to(VIS_C + np.array([0.85, -0.2, 0]))
        h = self.head("LEMURIA VS ATLÁNTIDA", color=HUESO)
        self.light_block(tl, 1, *self.clear(), FadeIn(earth), FadeIn(meridians), w=0.8)
        tl.play(reveal(h), DrawBorderThenFill(lem), DrawBorderThenFill(atl), lat.animate.set_value(PI / 3),
                self.pyr_dim(), w=1.6)
        beams = VGroup(*[Line(lem.get_center(), atl.get_center() + UP * (k - 1) * 0.25,
                              color=[VERDE, CARMESI, CIAN][k], stroke_width=5) for k in range(3)])
        tl.play(LaggedStart(*[ShowPassingFlash(b.copy(), time_width=0.6) for b in beams], lag_ratio=0.3),
                lat.animate.set_value(PI), w=1.6)

        # Maldek
        mal = Circle(radius=0.8, color=CARMESI, fill_opacity=0.85).move_to(VIS_C)
        h2 = self.head("MALDEK → CINTURÓN DE ASTEROIDES", color=CARMESI, fs=86)
        tl.play(FadeOut(VGroup(earth, meridians, lem, atl, h), scale=0.6), GrowFromCenter(mal), w=1.0)
        rnd = random.Random(21)
        pts = VGroup(*[Dot(mal.get_center() + rnd.uniform(0, 0.7) * np.array(
            [np.cos(a := rnd.uniform(0, TAU)), np.sin(a), 0]), radius=rnd.uniform(0.02, 0.05), color=CARMESI)
            for _ in range(120)])
        self.add(pts)
        tl.play(FadeOut(mal, scale=1.6), *[p.animate.shift(rnd.uniform(0.5, 2.2) * normalize(
            p.get_center() - VIS_C + 1e-3 * RIGHT)) for p in pts], reveal(h2), w=1.4)
        belt = [VIS_C + np.array([3.3 * np.cos(a), -0.6 + 1.6 * np.sin(a), 0])
                for a in np.linspace(PI * 0.12, PI * 0.88, 120)]
        rr = random.Random(5)
        tl.play(*[p.animate.move_to(belt[i] + np.array([0, rr.uniform(-0.2, 0.2), 0])).set_color(GRIS)
                  for i, p in enumerate(pts)], w=1.6)

        # Andrómeda → ADN
        spiral = VGroup()
        for arm in (0, PI):
            for t in np.linspace(0.2, 3.2, 40):
                r = 0.32 * np.exp(0.42 * t)
                spiral.add(Dot(VIS_C + np.array([r * np.cos(t + arm), 0.55 * r * np.sin(t + arm), 0]),
                               radius=0.035, color=HUESO))
        h3 = self.head("12 LINAJES + 1 REPTILIANO", color=CIAN)
        tl.play(FadeOut(pts), FadeOut(h2, shift=UP * 0.3), LaggedStart(*[FadeIn(d) for d in spiral],
                                                                      lag_ratio=0.01), w=1.3)
        helix = VGroup()
        top, bot = VIS_C[1] + 2.0, VIS_C[1] - 2.0
        s1 = ParametricFunction(lambda t: np.array([0.7 * np.sin(t), top - (top - bot) * t / (3 * TAU), 0]),
                                t_range=[0, 3 * TAU, 0.05], color=CIAN, stroke_width=5)
        s2 = ParametricFunction(lambda t: np.array([-0.7 * np.sin(t), top - (top - bot) * t / (3 * TAU), 0]),
                                t_range=[0, 3 * TAU, 0.05], color=CIAN, stroke_width=5)
        rungs = VGroup()
        for k in range(13):
            t = (k + 0.5) * 3 * TAU / 13
            y = top - (top - bot) * t / (3 * TAU)
            x = 0.7 * np.sin(t)
            rungs.add(Line([x, y, 0], [-x, y, 0], color=VERDE if k == 6 else CIAN, stroke_width=6))
        helix.add(s1, s2, rungs)
        tl.play(ReplacementTransform(spiral, helix), w=1.5)
        tl.play(reveal(h3), Indicate(rungs[6], color=VERDE, scale_factor=1.5), w=2.2)

        man = humanoid(3.4, ORO).move_to(VIS_C)
        nos = self.head("NOSOTROS", color=ORO, fs=104)
        tl.play(FadeOut(h3, shift=UP * 0.3), ReplacementTransform(helix, man), Write(nos), w=1.2)
        tl.finish(man)

    # ══════════════════════════════════════════════════════════════════════
    # B3 · ANUNNAKI, DILUVIO, PIEDRA
    # ══════════════════════════════════════════════════════════════════════
    def block_B3(self, T):
        tl = Timeline(self, "B3")
        rnd = random.Random(33)
        wedges = VGroup()
        for _ in range(46):
            wd = g_wedge(rnd.uniform(0.35, 0.8), ORO).rotate(rnd.choice([0, PI / 2, -PI / 2, PI / 4]))
            wd.move_to([rnd.uniform(-3.6, 3.6), rnd.uniform(3.0, 5.0), 0]).set_opacity(rnd.uniform(0.4, 1))
            wedges.add(wd)
        h1 = self.head("HACE 300.000 AÑOS", color=HUESO)
        self.light_block(tl, 2, *self.clear(), FadeIn(wedges), w=0.6)
        tl.play(*[w.animate.shift(DOWN * rnd.uniform(3.5, 6.5)) for w in wedges], reveal(h1), self.pyr_dim(),
                w=1.4)
        h2 = self.head("ANUNNAKI", color=ORO, fs=110)
        tl.play(FadeOut(h1, shift=UP * 0.3), Write(h2), wedges.animate.set_opacity(0.15), w=1.0)

        # Enki vs Enlil
        div = Line([0, 2.6, 0], [0, -1.6, 0], color=HUESO, stroke_width=2, stroke_opacity=0.5)
        ek = VGroup(
            ParametricFunction(lambda t: np.array([-2.0 + 0.45 * np.sin(t), 2.2 - 0.17 * t, 0]),
                               t_range=[0, 22, 0.05], color=CIAN, stroke_width=5),
            ParametricFunction(lambda t: np.array([-2.0 - 0.45 * np.sin(t), 2.2 - 0.17 * t, 0]),
                               t_range=[0, 22, 0.05], color=CIAN, stroke_width=3, stroke_opacity=0.6),
            Triangle(color=CIAN, fill_opacity=1).scale(0.22).rotate(PI).move_to([-2.0, 2.45, 0]))
        crown_c = np.array([2.0, 0.6, 0])
        rays = VGroup(*[Line(crown_c + 0.45 * np.array([np.cos(a), np.sin(a), 0]),
                             crown_c + (1.1 + 0.35 * (k % 2)) * np.array([np.cos(a), np.sin(a), 0]),
                             color=CARMESI, stroke_width=5) for k, a in enumerate(np.linspace(0, TAU, 16, endpoint=False))])
        crown = VGroup(Circle(radius=0.42, color=CARMESI, fill_opacity=0.9).move_to(crown_c), rays)
        h3 = self.head("ENKI VS ENLIL", color=HUESO)
        tl.play(FadeOut(h2, shift=UP * 0.3), FadeOut(wedges), Create(div), Create(ek), w=1.6)
        tl.play(reveal(h3), GrowFromCenter(crown), w=1.2)
        tl.play(Rotate(rays, angle=PI / 4, about_point=crown_c), w=1.2)

        # diluvio
        atl = VGroup(Polygon([-2.4, -1.2, 0], [2.4, -1.2, 0], [1.4, 0.2, 0], [-1.4, 0.2, 0],
                             color=CIAN, fill_opacity=0.35),
                     Polygon([-0.9, 0.2, 0], [0.9, 0.2, 0], [0, 1.4, 0], color=CIAN, fill_opacity=0.5))
        waves = VGroup(*[ParametricFunction(lambda t, k=k: np.array([t, 0.12 * np.sin(2.4 * t + k), 0]),
                                            t_range=[-4, 4, 0.05], color=CIAN, stroke_width=4,
                                            stroke_opacity=0.9 - 0.08 * k).shift(DOWN * (2.0 + 0.25 * k))
                         for k in range(9)])
        h4 = self.head("DILUVIO · 10.500 A.C.", color=CIAN)
        tl.play(FadeOut(VGroup(div, ek, crown, h3)), FadeIn(atl), reveal(h4), w=1.0)
        tl.play(waves.animate.shift(UP * 3.3), w=2.0)

        # Göbekli Tepe
        C = VIS_C + DOWN * 0.3
        pillars = VGroup()
        for k in range(8):
            a = k * TAU / 8
            p = VGroup(Rectangle(width=0.5, height=0.16, color=HUESO, fill_opacity=0.9),
                       Rectangle(width=0.16, height=0.36, color=HUESO, fill_opacity=0.9).shift(DOWN * 0.24))
            pillars.add(p.rotate(a + PI / 2).move_to(C + 1.45 * np.array([np.cos(a), np.sin(a), 0])))
        star = Star(6, outer_radius=0.28, inner_radius=0.12, color=ORO_CLARO, fill_opacity=1).move_to([2.8, 2.3, 0])
        beam = Line(C, star.get_center(), color=ORO_CLARO, stroke_width=5)
        h5 = self.head("GÖBEKLI TEPE · 9.600 A.C.", color=ORO)
        tl.play(FadeOut(VGroup(atl, waves, h4)), LaggedStart(*[GrowFromCenter(p) for p in pillars],
                                                            lag_ratio=0.1), w=1.2)
        tl.play(reveal(h5), FadeIn(star, scale=3), Create(beam), w=1.4)
        scope = RoundedRectangle(width=6.4, height=2.6, corner_radius=0.2, color=ORO, stroke_width=3).move_to(VIS_C)
        grid = VGroup(*[Line([x, VIS_C[1] - 1.2, 0], [x, VIS_C[1] + 1.2, 0], color=ORO, stroke_width=1,
                             stroke_opacity=0.25) for x in np.linspace(-3, 3, 9)])
        ph = ValueTracker(0)
        wave = always_redraw(lambda: ParametricFunction(
            lambda t: np.array([t, VIS_C[1] + 0.85 * np.sin(5 * t - ph.get_value()), 0]),
            t_range=[-3.0, 3.0, 0.03], color=ORO_CLARO, stroke_width=5))
        hz = self.head("110 HZ", color=ORO_CLARO, fs=110)
        tl.play(FadeOut(VGroup(pillars, star, beam)), FadeOut(h5, shift=UP * 0.3), FadeIn(scope), FadeIn(grid),
                FadeIn(wave), Write(hz), ph.animate.set_value(6), w=1.2)
        tl.play(ph.animate.set_value(20), w=1.2)
        wave.clear_updaters()
        tl.finish(scope)

    # ══════════════════════════════════════════════════════════════════════
    # B4 · SATURNO Y EL ALMA
    # ══════════════════════════════════════════════════════════════════════
    def block_B4(self, T):
        tl = Timeline(self, "B4")
        sat = VGroup(Ellipse(width=5.6, height=1.25, color=ORO, stroke_width=5).rotate(-0.25),
                     Circle(radius=1.2, color=VIOLETA, fill_color=NOCHE, fill_opacity=1, stroke_width=4),
                     Ellipse(width=4.4, height=0.9, color=ORO_CLARO, stroke_width=3).rotate(-0.25)).move_to(VIS_C)
        front = ArcBetweenPoints(sat[0].point_from_proportion(0.5), sat[0].point_from_proportion(0.0), angle=0)
        front = sat[0].copy().set_stroke(ORO, 5)
        front.pointwise_become_partial(sat[0], 0.5, 1.0)
        h1 = self.head("SATURNO = CRONOS", color=ORO)
        lab = self.label("EL LIBRO DE LA SABIDURÍA", color=VIOLETA, fs=52)
        self.light_block(tl, 3, *self.clear(), GrowFromCenter(sat), w=0.8)
        tl.play(reveal(h1), FadeIn(lab), Create(front), self.pyr_dim(), w=1.6)
        tl.play(Rotate(VGroup(sat, front), angle=0.15, about_point=VIS_C), w=1.6)

        ang = ValueTracker(0.3)

        def cube():
            a = ang.get_value()
            vs = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
            ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
            b = 0.55
            rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
            p = (vs @ ry.T @ rx.T) * 1.15
            pts = [VIS_C + np.array([q[0], q[1], 0]) for q in p]
            edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if bin(i ^ j).count("1") == 1]
            hull = Polygon(*[pts[i] for i in (0, 1, 3, 7, 6, 4)], color=FONDO, fill_color=FONDO,
                           fill_opacity=1, stroke_width=0)
            g = VGroup(hull)
            for i, j in edges:
                g.add(Line(pts[i], pts[j], color=ORO, stroke_width=5))
            return g

        cube_m = always_redraw(cube)
        h2 = self.head("EL CUBO NEGRO", color=ORO)
        snap = cube()
        tl.play(ReplacementTransform(VGroup(sat, front), snap), FadeOut(VGroup(h1, lab), shift=UP * 0.3),
                reveal(h2), w=1.4)
        self.remove(snap)
        self.add(cube_m)
        tl.play(ang.animate.set_value(0.3 + PI / 2), w=1.6)
        cube_m.clear_updaters()

        hexa = RegularPolygon(6, color=ORO, stroke_width=7).scale(1.9).move_to(VIS_C)
        hexg = glow(hexa, ORO, width=22)
        vort = ParametricFunction(lambda t: VIS_C + 0.06 * t * np.array([np.cos(t), np.sin(t), 0]),
                                  t_range=[0, 6 * TAU, 0.05], color=VIOLETA, stroke_width=3)
        h3 = self.head("HEXÁGONO REAL", color=ORO)
        tl.play(FadeOut(cube_m, scale=3), FadeOut(h2, shift=UP * 0.3), GrowFromCenter(hexg), Create(vort),
                reveal(h3), w=1.3)
        h4 = self.head("14.500 KM POR LADO", color=ORO_CLARO)
        tl.play(Rotate(hexg, angle=PI / 3, about_point=VIS_C), Rotate(vort, angle=-PI, about_point=VIS_C),
                FadeOut(h3, shift=UP * 0.3), reveal(h4), w=1.4)
        tl.play(Rotate(hexg, angle=PI / 6, about_point=VIS_C), Rotate(vort, angle=-PI / 2, about_point=VIS_C),
                w=1.3)

        # espíritu vs alma
        div = Line([0, 2.4, 0], [0, -1.5, 0], color=HUESO, stroke_width=2, stroke_opacity=0.4)
        spark = VGroup(*[Line(ORIGIN, 0.55 * np.array([np.cos(a), np.sin(a), 0]), color=HUESO, stroke_width=4)
                         for a in np.linspace(0, TAU, 8, endpoint=False)], Dot(radius=0.14, color=HUESO))
        spark.move_to([-2.0, 1.55, 0])
        sg = glow(spark, VIOLETA, width=20)
        lt = self.T("ESPÍRITU: ETERNO", fs=54, color=HUESO, pos=[-2.0, 0.05, 0], max_w=3.7)
        batt = VGroup(RoundedRectangle(width=0.95, height=1.7, corner_radius=0.1, color=VIOLETA, stroke_width=4),
                      Rectangle(width=0.36, height=0.16, color=VIOLETA, fill_opacity=1).move_to([0, 0.93, 0]))
        batt.move_to([1.35, 1.55, 0])
        lvl = ValueTracker(0.1)
        fill = always_redraw(lambda: Rectangle(width=0.75, height=1.5 * lvl.get_value(), color=VIOLETA,
                                               fill_opacity=0.85, stroke_width=0)
                             .align_to(batt[0].get_bottom() + UP * 0.1, DOWN).set_x(batt.get_x()))
        dark = Triangle(color=GRIS, fill_color=FONDO, fill_opacity=1, stroke_width=3).scale(0.45).move_to([3.1, 1.55, 0])
        rt = self.T("ALMA: BATERÍA", fs=54, color=VIOLETA, pos=[2.0, 0.05, 0], max_w=3.7)
        nim = self.label("NIMROD DE ROSARIO", color=ORO, fs=52, y=-1.55)
        tl.play(FadeOut(VGroup(hexg, vort, h4), scale=0.5), Create(div), FadeIn(sg, scale=0.3), FadeIn(lt),
                w=1.4)
        tl.play(FadeIn(batt), FadeIn(fill), FadeIn(dark), FadeIn(rt), FadeIn(nim),
                lvl.animate.set_value(0.95), sg.animate.scale(1.25), w=1.6)
        flow = VGroup(*[Dot(batt.get_center(), radius=0.05, color=VIOLETA) for _ in range(8)])
        self.add(flow)
        tl.play(lvl.animate.set_value(0.05), sg.animate.scale(0.8),
                LaggedStart(*[d.animate.move_to(dark.get_center()).set_opacity(0) for d in flow], lag_ratio=0.12),
                dark.animate.set_stroke(VIOLETA), w=2.0)
        fill.clear_updaters()
        self.remove(flow)
        tl.finish(sg)

    # ══════════════════════════════════════════════════════════════════════
    # B5 · ILLUMINATI Y SOCIEDADES SECRETAS
    # ══════════════════════════════════════════════════════════════════════
    def block_B5(self, T):
        tl = Timeline(self, "B5")
        STEP = 4.4
        Y_ACT = 1.2
        spine = Line([-3.55, Y_ACT + 1.0, 0], [-3.55, Y_ACT - 5 * STEP - 1.0, 0], color=ORO, stroke_width=3,
                     stroke_opacity=0.6)
        track = VGroup(spine)

        def node(k):  # siempre en la posición activa; entra con el avance
            return Dot([-3.55, Y_ACT, 0], radius=0.14, color=ORO)

        # 1776
        n1 = node(0)
        ic1 = triangle_eye_symbol(1.0).move_to([0.3, Y_ACT + 0.5, 0])
        t1 = self.T("1776 · INGOLSTADT", fs=80, color=ORO, pos=[0.25, Y_ACT - 1.5, 0], max_w=7.0)
        track.add(n1)
        self.light_block(tl, 4, *self.clear(), Create(spine), FadeIn(n1, scale=3), w=0.7)
        tl.play(DrawBorderThenFill(ic1), reveal(t1), self.pyr_dim(), w=2.0)
        tl.play(Indicate(ic1, color=ORO_CLARO), w=1.3)

        def advance(new_node, prev_items):
            out = [track.animate.shift(UP * STEP), FadeIn(new_node, shift=UP * STEP, scale=3)]
            out += [FadeOut(m, shift=UP * STEP) for m in prev_items]
            return out

        # 1785
        n2 = node(1)
        seal = VGroup(Circle(radius=1.0, color=CARMESI, stroke_width=8),
                      Circle(radius=0.78, color=CARMESI, stroke_width=3),
                      Line([-0.6, -0.6, 0], [0.6, 0.6, 0], color=CARMESI, stroke_width=8))
        seal.move_to([0.3, Y_ACT + 0.5, 0]).rotate(-0.5).scale(1.6).set_opacity(0)
        t2 = self.T("1785 · PROHIBIDOS", fs=80, color=CARMESI, pos=[0.25, Y_ACT - 1.5, 0], max_w=7.0)
        tl.play(*advance(n2, [ic1, t1]), w=0.9)
        track.add(n2)
        tl.play(seal.animate.rotate(0.5).scale(1 / 1.6).set_opacity(1), reveal(t2), w=0.7)
        tl.play(Wiggle(seal), Flash(seal.get_center(), color=CARMESI, line_length=0.6), w=1.4)

        # libro negro
        n3 = node(2)
        bk = book(2.8, 1.8, ORO).move_to([0.3, Y_ACT + 0.5, 0])
        t3 = self.T("EL LIBRO NEGRO DE LOS ILLUMINATI", fs=66, color=HUESO, pos=[0.25, Y_ACT - 1.55, 0],
                    max_w=7.0)
        t3b = self.T("NO MURIERON: MUTARON", fs=80, color=ORO, pos=[0.25, Y_ACT - 1.55, 0], max_w=7.0)
        tl.play(*advance(n3, [seal, t2]), FadeIn(bk[:4]), FadeIn(bk[4]), w=0.8)
        track.add(n3)
        spine_x = bk[0].get_right()[0]
        tl.play(bk[4].animate.stretch(-1, 0, about_point=[spine_x, 0, 0]).set_fill(NOCHE, 1), reveal(t3), w=1.2)
        tl.play(FadeOut(t3, shift=UP * 0.3), reveal(t3b), w=1.0)

        # 1832 · 322
        n4 = node(3)
        big = self.T("322", fs=170, color=ORO, pos=[0.3, Y_ACT + 0.55, 0], glow_it=True)
        t4 = self.T("1832 · SKULL & BONES", fs=76, color=HUESO, pos=[0.25, Y_ACT - 1.55, 0], max_w=7.0)
        tl.play(*advance(n4, [bk, t3b]), w=0.8)
        track.add(n4)
        tl.play(FadeIn(big, scale=1.8), reveal(t4), w=1.2)
        tl.play(Indicate(big, color=ORO_CLARO), w=1.0)

        # búho
        n5 = node(4)
        oc = np.array([0.3, Y_ACT + 0.45, 0])
        owl = VGroup(Ellipse(width=1.9, height=2.3, color=HUESO, fill_color=NOCHE, fill_opacity=1, stroke_width=4),
                     Circle(radius=0.36, color=ORO, stroke_width=5).shift(LEFT * 0.45 + UP * 0.35),
                     Circle(radius=0.36, color=ORO, stroke_width=5).shift(RIGHT * 0.45 + UP * 0.35),
                     Dot(radius=0.12, color=ORO_CLARO).shift(LEFT * 0.45 + UP * 0.35),
                     Dot(radius=0.12, color=ORO_CLARO).shift(RIGHT * 0.45 + UP * 0.35),
                     Polygon([-0.8, 0.85, 0], [-0.4, 1.0, 0], [-0.75, 1.45, 0], color=HUESO, fill_opacity=1),
                     Polygon([0.8, 0.85, 0], [0.4, 1.0, 0], [0.75, 1.45, 0], color=HUESO, fill_opacity=1),
                     Polygon([-0.1, 0.05, 0], [0.1, 0.05, 0], [0, -0.25, 0], color=ORO, fill_opacity=1)
                     ).move_to(oc)
        t5 = self.T("BOHEMIAN GROVE · CADA JULIO", fs=68, color=HUESO, pos=[0.25, Y_ACT - 1.55, 0], max_w=7.0)
        tl.play(*advance(n5, [big, t4]), FadeIn(owl, shift=UP * 0.3), w=0.9)
        track.add(n5)
        tl.play(reveal(t5), Indicate(VGroup(owl[3], owl[4]), color=ORO_CLARO, scale_factor=1.5), w=1.1)

        # Bilderberg
        n6 = node(5)
        tc = np.array([0.3, Y_ACT + 0.45, 0])
        table = VGroup(Circle(radius=0.9, color=ORO, fill_color=NOCHE, fill_opacity=1, stroke_width=5).move_to(tc),
                       *[Square(side_length=0.26, color=HUESO, fill_opacity=0.9).move_to(
                           tc + 1.25 * np.array([np.cos(a), np.sin(a), 0])).rotate(a)
                         for a in np.linspace(0, TAU, 14, endpoint=False)])
        t6 = self.T("BILDERBERG · 1954", fs=80, color=ORO, pos=[0.25, Y_ACT - 1.55, 0], max_w=7.0)
        tl.play(*advance(n6, [owl, t5]), w=0.8)
        track.add(n6)
        tl.play(LaggedStart(*[FadeIn(m, scale=0.4) for m in table], lag_ratio=0.06), reveal(t6), w=1.2)
        tl.play(Rotate(table[1:], angle=PI / 7, about_point=tc), w=1.0)
        tl.finish(table)

    # ══════════════════════════════════════════════════════════════════════
    # B6 · TRES CIUDADES Y LA PIRÁMIDE
    # ══════════════════════════════════════════════════════════════════════
    def block_B6(self, T):
        tl = Timeline(self, "B6")
        xs = [-2.7, 0.0, 2.7]
        base_y = -1.15
        obs = VGroup(*[obelisk(2.9).move_to([x, base_y + 1.64, 0]) for x in xs])
        hdr = self.head("LONDRES · VATICANO · WASHINGTON", color=HUESO, fs=80)
        roles = [self.T(w, fs=48, color=c, pos=[x, base_y - 0.42, 0], max_w=2.45, min_fs=48)
                 for w, c, x in zip(["DINERO", "DOGMA", "ESPADA"], [ORO, HUESO, CARMESI], xs)]
        self.light_block(tl, 5, *self.clear(), w=0.7)
        tl.play(LaggedStart(*[GrowFromEdge(o, DOWN) for o in obs], lag_ratio=0.25), reveal(hdr),
                self.pyr_dim(), w=1.8)
        for r in roles:
            tl.play(FadeIn(r, shift=UP * 0.3), w=0.83)

        tips = [o[1].get_vertices()[2] for o in obs]
        tri = Polygon(*tips, color=ORO_CLARO, stroke_width=5)
        corp = self.label("1871 · CORPORACIÓN", color=CARMESI, fs=56)
        triG = glow(tri, ORO_CLARO, 16)
        tl.play(FadeOut(hdr, shift=UP * 0.3), Create(triG), FadeIn(corp), w=1.6)
        tl.play(Indicate(obs[2], color=CARMESI), w=1.4)

        # sello octogonal ORDO AB CHAO
        oc = VIS_C + UP * 0.6
        octa = VGroup(RegularPolygon(8, color=ORO, stroke_width=5).scale(2.1),
                      RegularPolygon(8, color=ORO, stroke_width=2).scale(1.55)).move_to(oc)
        motto = "ORDO · AB · CHAO ·"
        letters = VGroup()
        chars = [c for c in motto if c != " "]
        for k, ch in enumerate(chars):
            a = PI / 2 - k * TAU / len(chars)
            t = Text(ch, font=FONT, font_size=50, color=ORO_CLARO, weight=BOLD)
            t.rotate(a - PI / 2).move_to(oc + 1.82 * np.array([np.cos(a), np.sin(a), 0]))
            letters.add(t)
        seal = VGroup(octa, letters).set_z_index(-1)
        self.texts.append((letters, 3))
        letters.text = "ORDO AB CHAO"
        tl.play(FadeIn(seal, scale=0.6), *[r.animate.set_opacity(0) for r in roles], corp.animate.set_opacity(0),
                VGroup(obs, triG).animate.set_opacity(0.35), w=1.3)
        tl.play(Rotate(seal, angle=-PI / 4, about_point=oc), w=1.4)

        # pirámide de la jerarquía
        tl.play(FadeOut(VGroup(seal, obs, *roles, corp, triG)), Restore(self.pyr), w=0.7)
        self.pyr_dimmed = False
        self.pyr.save_state()
        tl.play(self.pyr.animate.scale(1.7).move_to([0, 0.3, 0]), w=1.0)
        ptop, pbot = self.pyr.get_top()[1], self.pyr.get_bottom()[1]
        tags = []
        for text, y, col in [("ENTIDADES", ptop + 0.45, ORO_CLARO), ("LINAJES", ptop - 1.25, VERDE),
                             ("SOCIEDADES SECRETAS", ptop - 2.5, HUESO), ("NOSOTROS", pbot - 0.42, ORO)]:
            tg = self.T(text, fs=50, color=col, pos=[0, y, 0], max_w=7.4)
            bg = BackgroundRectangle(tg, color=FONDO, fill_opacity=0.85, buff=0.08)
            tags.append(VGroup(bg, tg))
        tl.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.4) for t in tags], lag_ratio=0.35), w=1.5)
        tl.play(FadeOut(VGroup(*tags)), Restore(self.pyr), w=0.9)
        tl.finish()

    # ══════════════════════════════════════════════════════════════════════
    # B7 · LA GUERRA POR LA MENTE
    # ══════════════════════════════════════════════════════════════════════
    def block_B7(self, T):
        tl = Timeline(self, "B7")
        mc = VIS_C + LEFT * 1.6
        mega = VGroup(Polygon(mc + np.array([-0.5, 0.25, 0]), mc + np.array([0.9, 0.85, 0]),
                              mc + np.array([0.9, -0.85, 0]), mc + np.array([-0.5, -0.25, 0]),
                              color=VIOLETA, fill_color=NOCHE, fill_opacity=1, stroke_width=5),
                      Rectangle(width=0.4, height=0.5, color=VIOLETA, fill_opacity=1).move_to(mc + LEFT * 0.7),
                      Line(mc + np.array([-0.1, -0.25, 0]), mc + np.array([-0.2, -0.9, 0]), color=VIOLETA,
                           stroke_width=6))
        arcs = VGroup(*[Arc(radius=0.5 + 0.42 * k, start_angle=-0.6, angle=1.2, color=VIOLETA, stroke_width=5)
                        .move_arc_center_to(mc + RIGHT * 0.9) for k in range(6)])
        h1 = self.head("1914 · PROPAGANDA", color=VIOLETA)
        self.light_block(tl, 6, *self.clear(), FadeIn(mega, shift=RIGHT * 0.4), w=0.8)
        tl.play(reveal(h1), LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.2), self.pyr_dim(), w=1.6)
        tl.play(LaggedStart(*[a.animate.set_stroke(HUESO, opacity=0.3) for a in arcs], lag_ratio=0.15), w=1.6)

        # cerebro
        bc = VIS_C
        lobes = VGroup(*[blob(0.95, seed=s, jitter=0.12, n=10, color=VIOLETA, fill=0.15)
                         .move_to(bc + off) for s, off in [(1, [-0.65, 0.25, 0]), (2, [0.65, 0.25, 0]),
                                                          (3, [-0.4, -0.45, 0]), (4, [0.45, -0.45, 0])]])
        sulci = VGroup(*[ParametricFunction(lambda t, k=k: bc + np.array([t, 0.15 * np.sin(4 * t + k) + 0.35 * (k - 1.5), 0]),
                                            t_range=[-1.1, 1.1, 0.04], color=VIOLETA, stroke_width=2.5)
                         for k in range(4)])
        stem = Line(bc + DOWN * 0.9, bc + DOWN * 1.6, color=VIOLETA, stroke_width=8)
        h2 = self.head("TAVISTOCK · 1920 · 1947", color=HUESO, fs=86)
        lab = self.label("EL INSTITUTO TAVISTOCK", color=VIOLETA, fs=52)
        tl.play(FadeOut(VGroup(mega, arcs, h1)), Create(lobes, lag_ratio=0.3), w=1.4)
        tl.play(Create(sulci), Create(stem), reveal(h2), FadeIn(lab), w=1.6)
        tl.play(Indicate(lobes, color=ORO_CLARO, scale_factor=1.05), w=1.0)

        # TV estática -> espiral
        tv = RoundedRectangle(width=5.0, height=3.6, corner_radius=0.3, color=HUESO, stroke_width=6).move_to(VIS_C)
        rnd = np.random.default_rng(4)
        cells = VGroup(*[Square(side_length=0.29, stroke_width=0, fill_color=HUESO, fill_opacity=0.5)
                         .move_to(VIS_C + np.array([-2.25 + 0.3 * i + 0.15, -1.55 + 0.3 * j + 0.15, 0]))
                         for i in range(15) for j in range(11)])

        def static_upd(g):
            v = rnd.random(len(g))
            for c, o in zip(g, v):
                c.set_fill(opacity=float(o) * 0.85)

        cells.add_updater(static_upd)
        tl.play(FadeOut(VGroup(lobes, sulci, stem, h2, lab)), Create(tv), FadeIn(cells), w=1.4)
        tl.play(tv.animate.scale(1.02), w=0.9)
        cells.clear_updaters()
        hyp = VGroup(ParametricFunction(lambda t: VIS_C + 0.075 * t * np.array([np.cos(t), np.sin(t), 0]),
                                        t_range=[0, 7 * TAU, 0.05], color=VIOLETA, stroke_width=6),
                     ParametricFunction(lambda t: VIS_C + 0.075 * t * np.array([np.cos(t + PI), np.sin(t + PI), 0]),
                                        t_range=[0, 7 * TAU, 0.05], color=HUESO, stroke_width=6))
        tl.play(FadeOut(cells), FadeIn(hyp, scale=0.3), w=0.7)
        tl.play(Rotate(hyp, angle=-2 * PI, about_point=VIS_C, rate_func=linear), w=0.8)

        # documento MK-Ultra
        doc = Rectangle(width=5.4, height=3.9, color=HUESO, fill_color=HUESO, fill_opacity=0.92,
                        stroke_width=0).move_to(VIS_C)
        rr = random.Random(7)
        lines_ = VGroup()
        bars = VGroup()
        for k in range(9):
            y = VIS_C[1] + 1.55 - k * 0.38
            wdt = rr.uniform(3.0, 4.6)
            x0 = VIS_C[0] - 2.3
            lines_.add(Line([x0, y, 0], [x0 + wdt, y, 0], color=GRIS, stroke_width=7))
            if k in (1, 2, 4, 6, 7):
                bars.add(Rectangle(width=wdt, height=0.24, fill_color=FONDO, fill_opacity=1, stroke_width=0)
                         .move_to([x0 + wdt / 2, y, 0]))
        tl.play(FadeOut(VGroup(hyp, tv), scale=0.6), FadeIn(doc), LaggedStart(*[Create(l) for l in lines_],
                                                                            lag_ratio=0.08), w=1.2)
        bars_start = [b.copy().stretch(0.01, 0).align_to(doc, LEFT) for b in bars]
        for b, s in zip(bars, bars_start):
            b.save_state()
            b.become(s)
        self.add(bars)
        tl.play(LaggedStart(*[Restore(b) for b in bars], lag_ratio=0.15), w=1.2)
        stamp = VGroup(RoundedRectangle(width=4.2, height=1.15, corner_radius=0.12, color=CARMESI, stroke_width=8),
                       Text("MK-ULTRA", font=FONT, font_size=84, color=CARMESI, weight=BOLD))
        stamp[1].scale_to_fit_width(3.7)
        stamp.rotate(0.12).move_to(VIS_C + UP * 0.3)
        self.reg(stamp[1], 1)
        date = self.T("13·04·1953", fs=60, color=CARMESI, pos=VIS_C + DOWN * 1.15, font=MONO)
        tl.play(FadeIn(stamp, scale=2.2, rate_func=rate_functions.rush_into), w=0.6)
        tl.play(FadeIn(date, shift=UP * 0.2), Flash(stamp.get_center(), color=CARMESI, line_length=0.7), w=1.0)
        decl = self.head("DESCLASIFICADO", color=FOSFORO, fs=96)
        tr = ValueTracker(0)
        cnt = self.counter(tr, fs=96, color=VIOLETA, pos=[0, -1.3, 0], prefix="+")
        inst = self.T("INSTITUCIONES", fs=50, color=HUESO, pos=[0, -2.12, 0])
        tl.play(reveal(decl), *[b.animate.set_fill(opacity=0.15) for b in bars], w=1.0)
        doc_g = VGroup(doc, lines_, bars, stamp, date)
        self.add(cnt)
        tl.play(doc_g.animate.scale(0.8).shift(UP * 0.45), tr.animate.set_value(80), w=1.2)
        cnt.clear_updaters()
        tl.play(FadeIn(inst, shift=UP * 0.2), Indicate(cnt, color=ORO_CLARO), w=0.8)
        tl.finish(stamp)

    # ══════════════════════════════════════════════════════════════════════
    # B8 · BAJO TUS PIES
    # ══════════════════════════════════════════════════════════════════════
    def block_B8(self, T):
        tl = Timeline(self, "B8")
        SY = 2.0
        surface = Line([-4, SY, 0], [4, SY, 0], color=HUESO, stroke_width=5)
        rr = random.Random(8)
        sky = VGroup(*[Rectangle(width=0.42, height=h, color=HUESO, fill_color=NOCHE, fill_opacity=1, stroke_width=2)
                       .move_to([x, SY + h / 2, 0]) for x, h in zip(np.linspace(-3.4, 3.4, 11),
                                                                    [0.5, 0.9, 0.4, 1.1, 0.7, 0.3, 0.8, 1.0, 0.45, 0.75, 0.55])])
        strata = VGroup(*[Rectangle(width=8, height=0.9, fill_color=c, fill_opacity=1, stroke_width=0)
                          .move_to([0, SY - 0.45 - 0.9 * k, 0])
                          for k, c in enumerate(["#1B1726", "#17131F", "#120F1A", "#0E0C15"])])
        h1 = self.head("BAJO TUS PIES", color=CARMESI, fs=104)
        self.light_block(tl, 7, *self.clear(), FadeIn(strata), Create(surface), w=0.8)
        tl.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in sky], lag_ratio=0.08), reveal(h1),
                self.pyr_dim(), w=1.8)
        tl.play(Indicate(h1, color=ORO_CLARO, scale_factor=1.04), w=1.4)

        nodes_p = [[-3.2, 1.2], [-1.6, 0.6], [0.2, 1.1], [1.9, 0.5], [3.3, 1.0], [-2.6, -0.4], [-0.6, -0.2],
                   [1.2, -0.6], [2.8, -0.3], [-1.4, -1.3], [0.6, -1.4], [2.2, -1.2]]
        nodes = VGroup(*[Square(side_length=0.26, color=CARMESI, fill_color=FONDO, fill_opacity=1, stroke_width=3)
                         .move_to([x, y, 0]) for x, y in nodes_p])
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (1, 6), (2, 6), (3, 7), (4, 8), (5, 6), (6, 7), (7, 8),
                 (5, 9), (6, 10), (7, 10), (8, 11), (9, 10), (10, 11), (2, 2)]
        tunnels = VGroup(*[Line(nodes[a].get_center(), nodes[b].get_center(), color=CARMESI, stroke_width=4,
                                stroke_opacity=0.8) for a, b in edges if a != b])
        c1 = self.label("130 BASES · EE.UU.", color=HUESO, fs=60)
        c2 = self.label("1.400 EN EL MUNDO", color=CARMESI, fs=60)
        tl.play(FadeOut(h1, shift=UP * 0.3), Create(tunnels, lag_ratio=0.15), FadeIn(nodes), w=1.6)
        tl.play(LaggedStart(*[n.animate.set_fill(CARMESI, 0.9) for n in nodes], lag_ratio=0.08), FadeIn(c1),
                w=1.6)
        tl.play(FadeOut(c1, shift=UP * 0.3), FadeIn(c2, shift=UP * 0.3), w=1.8)

        deep = nodes[10]
        h3 = self.head("DULCE · 1979", color=CARMESI, fs=104)
        tl.play(FadeOut(c2), reveal(h3), Flash(deep.get_center(), color=CARMESI, line_length=0.5), w=1.2)
        tl.play(Flash(deep.get_center(), color=ORO_CLARO, line_length=0.7, num_lines=16),
                deep.animate.scale(1.6), w=1.0)
        tl.play(Flash(deep.get_center(), color=CARMESI, line_length=0.9), w=0.8)

        G = VIS_C
        globe = VGroup(Circle(radius=1.75, color=CIAN, stroke_width=4).move_to(G),
                       *[Ellipse(width=3.5 * f, height=3.5, color=CIAN, stroke_width=1.5, stroke_opacity=0.4).move_to(G)
                         for f in (0.25, 0.6, 0.9)],
                       *[Line(G + np.array([-1.75 * np.sqrt(1 - y * y), 1.75 * y, 0]),
                              G + np.array([1.75 * np.sqrt(1 - y * y), 1.75 * y, 0]),
                              color=CIAN, stroke_width=1.5, stroke_opacity=0.4) for y in (-0.5, 0, 0.5)])
        pA, pB = G + np.array([1.0, 0.8, 0]), G + np.array([-1.1, -0.2, 0])
        arr = CurvedArrow(pA, pB, angle=1.1, color=ORO, stroke_width=6)
        h4 = self.head("PAPERCLIP · 1945", color=ORO, fs=96)
        tl.play(FadeOut(VGroup(sky, strata, surface, tunnels, nodes, h3)), Create(globe), w=1.2)
        dA, dB = Dot(pA, color=ORO_CLARO), Dot(pB, color=ORO_CLARO)
        tl.play(FadeIn(dA), Create(arr), reveal(h4), FadeIn(dB), w=1.8)

        ice = Polygon([-3.0, -1.4, 0], [-1.6, -0.6, 0], [-0.6, -0.95, 0], [0.5, -0.45, 0], [1.6, -0.85, 0],
                      [3.0, -1.3, 0], [2.2, -1.75, 0], [-2.2, -1.75, 0], color=HUESO, fill_color=HUESO,
                      fill_opacity=0.9, stroke_width=3)
        corona = VGroup(*[Line(ORIGIN, (0.95 + 0.25 * (k % 2)) * np.array([np.cos(a), np.sin(a), 0]),
                               color=ORO, stroke_width=4, stroke_opacity=0.8)
                          for k, a in enumerate(np.linspace(0, TAU, 28, endpoint=False))])
        eclipse = VGroup(corona, glow(Circle(radius=0.78, color=ORO, stroke_width=5), ORO, 24),
                         Circle(radius=0.74, color=FONDO, fill_color=FONDO, fill_opacity=1, stroke_width=0))
        eclipse.move_to([0, 2.6, 0])
        h5 = self.head("ANTÁRTIDA", color=HUESO, fs=104)
        tl.play(FadeOut(VGroup(dA, dB, globe, arr, h4)), FadeIn(ice, shift=UP * 0.4), FadeIn(eclipse, scale=0.5), reveal(h5), w=1.4)
        tl.play(eclipse.animate.move_to([0, 0.3, 0]), Rotate(corona, angle=PI / 6), w=1.6)
        tl.finish(eclipse)

    # ══════════════════════════════════════════════════════════════════════
    # B9 · EPSTEIN (terminal)
    # ══════════════════════════════════════════════════════════════════════
    def block_B9(self, T):
        tl = Timeline(self, "B9")
        frame = RoundedRectangle(width=7.9, height=6.6, corner_radius=0.15, color=FOSFORO, stroke_width=3,
                                 stroke_opacity=0.7).move_to([0, 2.45, 0])
        scan = VGroup(*[Line([-3.9, y, 0], [3.9, y, 0], color=FOSFORO, stroke_width=1, stroke_opacity=0.07)
                        for y in np.arange(-0.8, 5.7, 0.12)])
        title = Text("> ARCHIVO: EPSTEIN", font=MONO, font_size=60, color=FOSFORO, weight=BOLD)
        if title.width > 7.0:
            title.scale_to_fit_width(7.0)
        title.move_to([-0.25, 5.15, 0])
        title.nwords, title.text = 3, "> ARCHIVO: EPSTEIN"
        self.reg(title)
        cursor = Rectangle(width=0.3, height=0.55, fill_color=FOSFORO, fill_opacity=1, stroke_width=0)
        cursor.next_to(title, RIGHT, buff=0.1)
        if cursor.get_right()[0] > 3.95:
            cursor.next_to(title, DOWN, buff=0.1).align_to(title, LEFT)
        self.light_block(tl, 8, *self.clear(), FadeIn(frame), FadeIn(scan), w=0.4)
        tl.play(AddTextLetterByLetter(title), self.pyr_dim(), w=1.1)
        tl.play(cursor.animate(rate_func=there_and_back).set_opacity(0), w=0.5)

        cards_txt = ["2008 · FLORIDA · 13 MESES", "06·07·2019 · ARRESTO", "10·08·2019 · MUERTO EN SU CELDA",
                     "MAXWELL · 20 AÑOS"]
        cy = 2.45
        prev = None
        small = Rectangle(width=0.3, height=0.55, fill_color=FOSFORO, fill_opacity=1, stroke_width=0).move_to([-3.5, 5.15, 0])
        for k, txt in enumerate(cards_txt):
            t = self.T(txt, fs=68, color=FOSFORO, pos=[0, cy, 0], font=MONO, max_w=6.6)
            box = RoundedRectangle(width=7.2, height=t.height + 0.9, corner_radius=0.15, color=FOSFORO,
                                   stroke_width=4).move_to([0, cy, 0])
            card = VGroup(box, t).shift(RIGHT * 8)
            anims = [card.animate.shift(LEFT * 8)]
            if prev is not None:
                anims.append(prev.animate.shift(LEFT * 8).set_opacity(0))
            else:
                anims += [FadeOut(title), ReplacementTransform(cursor, small)]
            tl.play(*anims, w=0.75)
            tl.play(Indicate(t, color=HUESO, scale_factor=1.04), small.animate(rate_func=there_and_back).set_opacity(0.1),
                    w=1.0)
            prev = card
            self.remove(*[m for m in self.mobjects if m is not card and isinstance(m, VGroup) and m.get_x() < -6])

        # libro de cumpleaños
        bk = book(3.4, 2.3, FOSFORO).move_to([0, 2.5, 0])
        bt = self.T("238 PÁGINAS · 2025", fs=68, color=FOSFORO, pos=[0, 0.4, 0], font=MONO, max_w=7.2)
        sx = bk[0].get_right()[0]
        tl.play(prev.animate.shift(LEFT * 8).set_opacity(0), FadeIn(bk), w=0.7)
        pages = VGroup(*[bk[1].copy().set_fill(NOCHE, 1) for _ in range(6)])
        self.add(pages)
        tl.play(bk[4].animate.stretch(-1, 0, about_point=[sx, 0, 0]).set_fill(NOCHE, 1), reveal(bt), w=1.0)
        tl.play(LaggedStart(*[p.animate.stretch(-1, 0, about_point=[sx, 0, 0]) for p in pages], lag_ratio=0.25),
                w=2.3)

        # 427 – 1
        basey = 0.3
        b1 = Rectangle(width=1.6, height=0.01, fill_color=FOSFORO, fill_opacity=0.9, stroke_width=0)
        b1.move_to([-1.3, basey, 0], aligned_edge=DOWN)
        b2 = Rectangle(width=1.6, height=0.01, fill_color=CARMESI, fill_opacity=0.9, stroke_width=0)
        b2.move_to([1.3, basey, 0], aligned_edge=DOWN)
        axis = Line([-3.0, basey, 0], [3.0, basey, 0], color=FOSFORO, stroke_width=3)
        vt = self.T("427 – 1", fs=120, color=FOSFORO, pos=[0, -1.55, 0], font=MONO)
        tl.play(FadeOut(VGroup(bk, pages, bt)), Create(axis), FadeIn(b1), FadeIn(b2), w=0.8)
        tl.play(b1.animate.stretch_to_fit_height(4.2).align_to([0, basey, 0], DOWN),
                b2.animate.stretch_to_fit_height(0.06).align_to([0, basey, 0], DOWN), Write(vt), w=2.0)
        tl.play(Indicate(vt, color=HUESO), w=1.2)

        # 3.500.000 páginas
        stack = VGroup(*[Rectangle(width=3.0, height=0.13, color=FOSFORO, fill_color=NOCHE, fill_opacity=1,
                                   stroke_width=2).move_to([0, -0.6 + 0.16 * k, 0]) for k in range(22)])
        cens = VGroup(*[Rectangle(width=rr, height=0.07, fill_color=FONDO, fill_opacity=1, stroke_width=0)
                        .move_to(stack[k].get_center() + LEFT * 0.3) for k, rr in
                        zip(range(1, 22, 3), [1.6, 2.1, 1.2, 1.9, 1.4, 2.2, 1.0])])
        tr = ValueTracker(0)
        cnt = self.counter(tr, fs=130, color=FOSFORO, pos=[0.2, 4.25, 0], font=MONO)
        pg = self.T("PÁGINAS", fs=60, color=HUESO, pos=[0, 3.3, 0], font=MONO)
        self.add(cnt)
        tl.play(FadeOut(VGroup(b1, b2, axis, vt)), LaggedStart(*[FadeIn(s, shift=UP * 0.3) for s in stack],
                                                              lag_ratio=0.05), FadeIn(pg),
                tr.animate.set_value(3_500_000), w=2.4)
        cnt.clear_updaters()
        self.add(cens)
        tl.play(cens.animate(rate_func=there_and_back).set_opacity(0.1), w=0.8)
        tl.play(cens.animate(rate_func=there_and_back).set_opacity(0.1), w=0.8)

        # red de nodos
        rnd = random.Random(19)
        C = np.array([0, 1.8, 0])
        net = VGroup(*[Dot([rnd.uniform(-3.6, 3.6), rnd.uniform(-1.2, 4.6), 0], radius=0.1, color=GRIS)
                       for _ in range(26)])
        hub = Dot(C, radius=0.26, color=CARMESI)
        links = VGroup(*[Line(d.get_center(), C, color=GRIS, stroke_width=1.5, stroke_opacity=0.6) for d in net])
        gt = self.T("GERENTE DEL CHANTAJE", fs=74, color=CARMESI, pos=[0, -1.15, 0], font=MONO, max_w=7.4)
        tl.play(FadeOut(VGroup(stack, cens, cnt, pg)), FadeIn(net), Create(links), FadeIn(hub, scale=3), w=0.9)
        tl.play(*[d.animate.move_to(C + 0.35 * (d.get_center() - C)) for d in net],
                links.animate.set_stroke(opacity=0.15), reveal(gt), hub.animate.scale(1.4), w=1.1)
        tl.finish(hub)

    # ══════════════════════════════════════════════════════════════════════
    # B10 · CONVERGENCIA Y CIERRE
    # ══════════════════════════════════════════════════════════════════════
    def block_B10(self, T):
        tl = Timeline(self, "B10")
        q = Text("Q", font=FONT, font_size=420, color=HUESO, weight=BOLD).move_to(VIS_C + UP * 0.2)
        qr = q.copy().set_color(CARMESI).set_opacity(0.7)
        qc = q.copy().set_color(CIAN).set_opacity(0.7)
        jit = random.Random(2)

        def glitch(m, dt, sign=1):
            m.move_to(q.get_center() + sign * np.array([jit.uniform(0.02, 0.14), jit.uniform(-0.06, 0.06), 0]))

        qr.add_updater(lambda m, dt: glitch(m, dt, 1))
        qc.add_updater(lambda m, dt: glitch(m, dt, -1))
        self.reg(q, 1)
        oct_ = self.head("OCTUBRE 2017", color=HUESO, fs=96)
        self.light_block(tl, 9, *self.clear(), FadeIn(qr), FadeIn(qc), FadeIn(q), w=0.7)
        tl.play(Write(oct_), self.pyr_dim(), w=1.3)
        tl.play(q.animate.shift(RIGHT * 0.05), w=1.0)
        qr.clear_updaters()
        qc.clear_updaters()

        rnd = random.Random(10)
        cyan = VGroup(*[Dot([rnd.uniform(-3.9, -1.5), VIS_C[1] + rnd.uniform(-1.6, 1.6), 0], radius=0.06, color=CIAN)
                        for _ in range(60)])
        red = VGroup(*[Dot([rnd.uniform(1.5, 3.9), VIS_C[1] + rnd.uniform(-1.6, 1.6), 0], radius=0.06, color=CARMESI)
                       for _ in range(60)])
        h2 = self.head("ALIANZA VS CÁBALA", color=HUESO, fs=94)
        tl.play(FadeOut(VGroup(q, qr, qc, oct_)), FadeIn(cyan, shift=RIGHT * 0.5), FadeIn(red, shift=LEFT * 0.5),
                reveal(h2), w=1.2)
        tl.play(*[d.animate.shift(RIGHT * rnd.uniform(1.4, 2.3)) for d in cyan],
                *[d.animate.shift(LEFT * rnd.uniform(1.4, 2.3)) for d in red], w=1.2)
        bolt = lightning([0.4, 3.4, 0], [-0.2, -1.3, 0], seed=4)
        h3 = self.head("LA TORMENTA", color=ORO_CLARO, fs=104)
        tl.play(Create(glow(bolt, ORO_CLARO, 24)), Flash(VIS_C, color=ORO_CLARO, line_length=1.2, num_lines=20),
                FadeOut(h2, shift=UP * 0.3), Write(h3), *[d.animate.shift(rnd.uniform(-1.5, 1.5) * RIGHT +
                                                                       rnd.uniform(-1.5, 1.5) * UP).set_opacity(0)
                                                       for d in [*cyan, *red]], w=1.6)

        # glifos vuelan a su nivel
        self.remove(cyan, red)
        tl.play(*self.clear(), Restore(self.pyr), w=0.6)
        self.pyr_dimmed = False
        flights = []
        for i in range(9):
            g = GLYPHS[i](2.8, LEVEL_COL[i]).move_to(VIS_C + UP * 0.4)
            target = self.glyphs[i]
            flights.append(Succession(FadeIn(g, scale=0.5, run_time=0.3),
                                      g.animate(run_time=0.7).move_to(target.get_center()).scale(0.06).set_opacity(0)))
        tl.play(LaggedStart(*flights, lag_ratio=0.32), w=2.6)
        tl.play(*[lv.animate.set_fill(ORO, 0.85).set_stroke(ORO_CLARO) for lv in self.levels], w=0.7)
        tl.play(self.pyr.animate.stretch_to_fit_width(7.6).stretch_to_fit_height(8.2).move_to([0, -0.5, 0]),
                FadeOut(self.p_eye), w=1.1)

        # el ojo se abre
        eye_closed = closed_eye(1.8, ORO_CLARO).move_to(EYE_POS)
        eye_open = open_eye(1.9, ORO_CLARO).move_to(EYE_POS)
        iris_hex = RegularPolygon(6, color=ORO, stroke_width=5).scale(0.42).move_to(EYE_POS)
        iris_sp = ParametricFunction(lambda t: EYE_POS + 0.03 * t * np.array([np.cos(t), np.sin(t), 0]),
                                     t_range=[0, 4 * TAU, 0.08], color=VIOLETA, stroke_width=3)
        iris = VGroup(iris_hex, iris_sp)
        rays = VGroup(*[Line(EYE_POS + 1.15 * np.array([np.cos(a), np.sin(a), 0]),
                             EYE_POS + (1.6 + 0.35 * (k % 2)) * np.array([np.cos(a), np.sin(a), 0]),
                             color=ORO_CLARO, stroke_width=4, stroke_opacity=0.85)
                        for k, a in enumerate(np.linspace(0, TAU, 24, endpoint=False))])
        h4 = self.head("LA MISMA GUERRA", color=ORO, fs=96)
        tl.play(FadeIn(eye_closed), FadeOut(h3, shift=UP * 0.3), w=0.5)
        tl.play(ReplacementTransform(eye_closed, eye_open), GrowFromCenter(iris), reveal(h4), w=1.0)
        iris.add_updater(lambda m, dt: m.rotate(0.9 * dt, about_point=EYE_POS))
        h5 = self.head("EL BOTÍN: TU ESPÍRITU", color=ORO_CLARO, fs=96)
        tl.play(LaggedStart(*[GrowFromPoint(r, EYE_POS) for r in rays], lag_ratio=0.03), w=0.8)
        tl.play(FadeOut(h4, shift=UP * 0.3), reveal(h5), w=0.7)

        # CTA
        cta_t = self.T("SIGUE · LLEGA LA PARTE 2", fs=64, color=FONDO, pos=[0, -3.35, 0], max_w=7.0)
        bar = Rectangle(width=7.9, height=cta_t.height + 0.45, fill_color=ORO, fill_opacity=1,
                        stroke_width=0).move_to(cta_t)
        cta = VGroup(bar, cta_t)
        arrow = Arrow([2.4, -2.8, 0], [3.6, 5.6, 0], color=ORO_CLARO, stroke_width=9, buff=0,
                      max_tip_length_to_length_ratio=0.06)
        tl.play(FadeOut(h5, shift=UP * 0.3), FadeIn(cta, shift=UP * 0.4), GrowArrow(arrow),
                rays.animate.set_stroke(opacity=0.5), w=1.2)
        tl.play(arrow.animate(rate_func=there_and_back).shift(UR * 0.12).set_stroke(ORO),
                Indicate(cta_t, color=NOCHE, scale_factor=1.04), w=0.9)
        tl.play(arrow.animate(rate_func=there_and_back).shift(UR * 0.12), w=0.8)
        # últimos 0,5 s: el ojo colapsa en un punto dorado (== primer frame)
        n_end = int(round(0.5 * FPS))
        iris.clear_updaters()
        dot = Dot(EYE_POS, radius=0.09, color=ORO_CLARO)
        rest = tl.f1 - self.fc - n_end
        if rest >= 2:
            self.ambient(rest, eye_open)
        everything = [m for m in self.mobjects if m not in (self.dust, self.dust_k, self.vig)
                      and m not in (eye_open, iris)]
        self._play_frames(max(2, tl.f1 - self.fc),
                          *[FadeOut(m) for m in everything],
                          VGroup(eye_open, iris).animate.scale(0.02).set_opacity(0),
                          FadeIn(dot, scale=4))

    # ── informe ───────────────────────────────────────────────────────────
    def report(self):
        lines = list(self.log)
        expected = int(round(TOTAL * FPS))
        lines.append(f"FIN: fotogramas={self.fc} esperados≈{expected} · renderer.time={self.renderer.time:.3f}s")
        lines.append(f"pico de palabras visibles: {self.word_peak[0]} a {self.word_peak[1]:.2f}s {self.word_peak[2]}")
        lines.append(f"violaciones >8 palabras: {len(self.violations)}")
        lines += self.violations[:40]
        txt = "\n".join(lines)
        print(txt)
        try:
            with open(os.path.join(HERE, "render_report.txt"), "w", encoding="utf-8") as fh:
                fh.write(txt + "\n")
        except OSError:
            pass
