"""
main.py — «EL CÓDIGO GNÓSTICO: DE NAG HAMMADI A MATRIX»
Vertical 9:16 · 1080×1920 · 30 fps · 180 s exactos · Manim CE · estilo poligonal facetado.

    manim -qh --disable_caching main.py FullVideo
    KABALA_PREVIEW=1 manim --disable_caching main.py Block3     # vista previa 540×960

Motor compartido: ../kabala_video/utils.py (reloj por frames, texto cinético, glitch,
wipe) y ../thule_video/poly.py (mallas low-poly sombreadas).
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("kabala_video", "thule_video"):
    sys.path.insert(0, os.path.join(HERE, "..", d))
sys.path.insert(0, HERE)

import utils as K  # noqa: E402  (fija 1080×1920 @ 30 fps)
from manim import (  # noqa: E402
    BOLD, DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP,
    Arrow, Create, Dot, FadeIn, FadeOut, Flash, LaggedStart, Line, ManimColor, Polygon,
    RoundedRectangle, Text, UpdateFromAlphaFunc, VGroup, VMobject, config,
    interpolate_color, smooth,
)
from poly import low_poly, ngon, resample, shade, stamp  # noqa: E402
from utils import (  # noqa: E402
    FONT_MONO, FONT_SANS, FONT_SERIF, FPS, KabalaScene, blink_updater, kinetic_text, px,
    reveal_words,
)

INK, BONE, CYAN, GOLD, BLOOD, ILLUSION = "#050508", "#E8E6E3", "#5AC8FA", "#C9A227", "#8B0000", "#4A2C6D"
RED = "#C0262D"            # rojo legible para texto
CODE = "#3BD16F"           # verde del código de Matrix (solo en la lluvia binaria)
config.background_color = INK
K.BG_IN, K.BG_OUT, K.PARCHMENT = "#0C0A16", "#050508", "#0A0912"
Y_VIS = 0.35
STARTS = [0, 15, 45, 75, 105, 135, 165]
ENDS = [15, 45, 75, 105, 135, 165, 180]


def mono(t, size=48, color=BONE):
    return Text(t, font=FONT_MONO, font_size=px(size), weight=BOLD, color=color,
                disable_ligatures=True)


def lerp(c1, c2, a):
    return interpolate_color(ManimColor(c1), ManimColor(c2), a)


# ─────────────────────────────────────────────────────────────────────────────
# La «Matrix»: malla poligonal recurrente
# ─────────────────────────────────────────────────────────────────────────────
class MatrixMesh(VGroup):
    """Lámina triangulada que cubre la pantalla. Late, cambia de color, se agrieta,
    se fragmenta, se vuelve oro y acaba en partículas."""

    def __init__(self, cols=10, rows=18, seed=1, color=CYAN, base_op=0.30):
        super().__init__()
        rng = np.random.default_rng(seed)
        xs, ys = np.linspace(-5.0, 5.0, cols + 1), np.linspace(-8.5, 8.5, rows + 1)
        P = np.zeros((rows + 1, cols + 1, 3))
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                jit = 0 if i in (0, cols) or j in (0, rows) else 0.33
                P[j, i] = [x + rng.uniform(-jit, jit), y + rng.uniform(-jit, jit) * 1.2, 0]
        self.color_, self.base_op, self.amp, self.t_ = color, base_op, 0.35, 0.0
        for j in range(rows):
            for i in range(cols):
                a, b, c, d = P[j, i], P[j, i + 1], P[j + 1, i + 1], P[j + 1, i]
                for tri in ((a, b, c), (a, c, d)) if (i + j) % 2 else ((a, b, d), (b, c, d)):
                    g = np.mean(tri, axis=0)
                    k = 0.45 + 0.4 * rng.random() + 0.15 * (-g[0] + g[1]) / 9
                    p = Polygon(*tri, stroke_width=1.2)
                    p.k, p.ph, p.c0, p.op = k, rng.uniform(0, TAU), g, 1.0
                    self.add(p)
        self.paint(color)
        self.set_z_index(-30)
        self.add_updater(MatrixMesh._pulse)

    def paint(self, color, glow=0.0):
        self.color_ = color
        for p in self:
            p.set_fill(shade(color, p.k + glow))
            p.set_stroke(shade(color, 1.4), opacity=0.32 * p.op)
        return self

    @staticmethod
    def _pulse(m, dt):
        m.t_ += dt
        for p in m:
            p.set_fill(opacity=m.base_op * p.op * (1 + m.amp * np.sin(2.4 * m.t_ + p.ph)))

    def tint(self, color, glow=0.0, op=None):
        c0, op0 = self.color_, self.base_op

        def f(m, a):
            m.paint(lerp(c0, color, a), glow * a)
            if op is not None:
                m.base_op = op0 + (op - op0) * a
            if a >= 1:
                m.color_ = color
        return UpdateFromAlphaFunc(self, f, suspend_mobject_updating=False)

    def near(self, center, r):
        return [p for p in self if np.linalg.norm(p.c0[:2] - np.array(center)[:2]) < r]


def crack_lines(rng, n=5, center=(0, 0.3)):
    """Grietas doradas: caminos quebrados que salen de un punto."""
    g = VGroup()
    for k in range(n):
        a = TAU * k / n + rng.uniform(-0.3, 0.3)
        pts, p = [np.array([*center, 0.0])], np.array([*center, 0.0])
        for _ in range(7):
            a += rng.uniform(-0.6, 0.6)
            p = p + np.array([np.cos(a), np.sin(a), 0]) * rng.uniform(0.5, 1.0)
            pts.append(p.copy())
        v = VMobject(stroke_color=GOLD, stroke_width=5).set_points_as_corners(pts)
        glow = v.copy().set_stroke(GOLD, width=16, opacity=0.25)
        g.add(VGroup(glow, v))
    return g


def golden_core(r=3.0, center=(0, Y_VIS)):
    return VGroup(*[Polygon(*[np.array([*c, 0]) for c in ngon(14, r * s, rot=s, center=center)],
                            stroke_width=0).set_fill(GOLD, 0.06 + 0.07 * i)
                    for i, s in enumerate((1.0, 0.75, 0.52, 0.32, 0.16))]).set_z_index(-40)


# ─────────────────────────────────────────────────────────────────────────────
# Siluetas poligonales
# ─────────────────────────────────────────────────────────────────────────────
AGENT = [(0, 2.0), (0.3, 1.95), (0.42, 1.7), (0.4, 1.35), (0.25, 1.15), (0.28, 1.0), (0.95, 0.85),
         (1.15, 0.5), (1.2, -0.6), (0.95, -0.65), (0.9, 0.2), (0.75, -0.5), (0.6, -2.0), (0.15, -2.0),
         (0.05, -0.7), (-0.05, -0.7), (-0.15, -2.0), (-0.6, -2.0), (-0.75, -0.5), (-0.9, 0.2),
         (-0.95, -0.65), (-1.2, -0.6), (-1.15, 0.5), (-0.95, 0.85), (-0.28, 1.0), (-0.25, 1.15),
         (-0.4, 1.35), (-0.42, 1.7), (-0.3, 1.95)]
COAT = [(0, 2.0), (0.3, 1.95), (0.42, 1.7), (0.4, 1.35), (0.25, 1.15), (0.28, 1.0), (0.95, 0.85),
        (1.1, 0.4), (1.15, -0.6), (0.95, -0.6), (0.92, 0.0), (1.35, -2.0), (0.35, -2.0), (0.15, -1.0),
        (-0.15, -1.0), (-0.35, -2.0), (-1.35, -2.0), (-0.92, 0.0), (-0.95, -0.6), (-1.15, -0.6),
        (-1.1, 0.4), (-0.95, 0.85), (-0.28, 1.0), (-0.25, 1.15), (-0.4, 1.35), (-0.42, 1.7),
        (-0.3, 1.95)]
ROBE = [(0, 2.0), (0.45, 1.85), (0.6, 1.4), (0.55, 1.0), (0.9, 0.7), (1.0, -0.5), (1.25, -2.0),
        (-1.25, -2.0), (-1.0, -0.5), (-0.9, 0.7), (-0.55, 1.0), (-0.6, 1.4), (-0.45, 1.85)]
ARCHON = [(0, 2.2), (0.25, 1.6), (0.6, 2.0), (0.55, 1.3), (1.1, 0.5), (0.7, -0.6), (0.4, -2.0),
          (-0.4, -2.0), (-0.7, -0.6), (-1.1, 0.5), (-0.55, 1.3), (-0.6, 2.0), (-0.25, 1.6)]


def figure(pts, color, seed=0, scale=1.0):
    g = low_poly(resample([(x * scale, y * scale) for x, y in pts], 0.38 * scale), color,
                 seed=seed, rings=2, jitter=0.08, dome=0.7)
    return g


def agent(scale=1.0, seed=3, color="#2E3440"):
    body = figure(AGENT, color, seed, scale)
    s = scale
    shirt = Polygon([-0.2 * s, 1.0 * s, 0], [0.2 * s, 1.0 * s, 0], [0, 0.35 * s, 0],
                    stroke_width=0).set_fill(BONE, 0.9)
    tie = Polygon([-0.05 * s, 0.95 * s, 0], [0.05 * s, 0.95 * s, 0], [0, 0.4 * s, 0],
                  stroke_width=0).set_fill(INK, 1)
    glasses = VGroup(*[Polygon([x - 0.17 * s, 1.6 * s, 0], [x + 0.17 * s, 1.6 * s, 0],
                               [x + 0.12 * s, 1.47 * s, 0], [x - 0.13 * s, 1.47 * s, 0],
                               stroke_width=0).set_fill(INK, 1) for x in (-0.18 * s, 0.18 * s)])
    return VGroup(body, shirt, tie, glasses)


def coat(scale=1.0, seed=5, color="#1E2230", glasses=True):
    body = figure(COAT, color, seed, scale)
    out = VGroup(body)
    if glasses:
        s = scale
        out.add(VGroup(*[Polygon([x - 0.15 * s, 1.6 * s, 0], [x + 0.15 * s, 1.6 * s, 0],
                                 [x + 0.1 * s, 1.48 * s, 0], [x - 0.1 * s, 1.48 * s, 0],
                                 stroke_width=0).set_fill(INK, 1) for x in (-0.17 * s, 0.17 * s)]))
    return out


def pill(color, angle=0.4, size=0.42):
    pts = [(np.cos(a) * size * (1.0 if abs(np.cos(a)) > 0.3 else 1.0) * 1.0,
            np.sin(a) * size * 0.45) for a in np.linspace(0, TAU, 12, endpoint=False)]
    p = low_poly(pts, color, seed=7, rings=1, dome=1.2)
    return p.rotate(angle)


def demiurge(scale=1.0):
    """Serpiente con cabeza de león: cuerpo en S facetado + melena de picos."""
    s = scale
    ts = np.linspace(0, 1, 26)
    cx = 1.15 * np.sin(ts * TAU * 1.1) * s
    cy = (-0.4 - 3.1 * ts) * s
    w = (0.55 - 0.45 * ts) * s
    left = [(cx[i] - w[i], cy[i]) for i in range(len(ts))]
    right = [(cx[i] + w[i], cy[i]) for i in range(len(ts))][::-1]
    body = low_poly(left + right, "#3B5B2E", seed=11, rings=1, jitter=0.03, dome=0.5)
    mane = [(np.cos(a) * (1.25 if i % 2 == 0 else 0.85) * s,
             0.55 * s + np.sin(a) * (1.25 if i % 2 == 0 else 0.85) * s)
            for i, a in enumerate(np.linspace(0, TAU, 22, endpoint=False))]
    mane_m = low_poly(mane, "#B5651D", seed=12, rings=1, dome=0.8)
    face = low_poly(ngon(8, 0.62 * s, rot=PI / 8, center=(0, 0.5 * s)), "#D9A441", seed=13,
                    rings=1, dome=1.0)
    eyes = VGroup(*[Polygon([x - 0.14 * s, 0.7 * s, 0], [x + 0.14 * s, 0.75 * s, 0],
                            [x, 0.6 * s, 0], stroke_width=0).set_fill(RED, 1)
                    for x in (-0.22 * s, 0.22 * s)])
    return VGroup(body, mane_m, face, eyes)


def archon(scale=1.0, seed=0, color=ILLUSION):
    g = figure(ARCHON, color, seed, scale)
    eye = Polygon([-0.2 * scale, 0.75 * scale, 0], [0.2 * scale, 0.75 * scale, 0],
                  [0, 0.55 * scale, 0], stroke_width=0).set_fill(GOLD, 1)
    return VGroup(g, eye)


EGYPT = [(-1.8, 1.6), (1.2, 1.65), (1.5, 1.3), (1.9, 0.4), (2.2, -0.3), (2.0, -1.6), (-1.8, -1.6)]


def codex(seed=0):
    pts = [(-0.28, 0.38), (0.28, 0.38), (0.3, -0.38), (-0.26, -0.4)]
    c = low_poly(pts, "#8C6B3E", seed=seed, rings=1, dome=0.5)
    spine = Polygon([-0.28, 0.38, 0], [-0.2, 0.38, 0], [-0.18, -0.4, 0], [-0.26, -0.4, 0],
                    stroke_width=0).set_fill(shade("#8C6B3E", 0.4), 1)
    return VGroup(c, spine)


def binary_rain(cols=13, per=11, seed=2, color=CODE):
    rng = np.random.default_rng(seed)
    g = VGroup()
    for i in range(cols):
        x = -4.2 + i * 8.4 / (cols - 1)
        v = rng.uniform(1.2, 3.0)
        col = VGroup()
        y0 = rng.uniform(-2, 9)
        for j in range(per):
            t = Text(str(rng.integers(0, 2)), font=FONT_MONO, font_size=px(52), weight=BOLD,
                     color=color).move_to([x, y0 - j * 0.62, 0])
            t.set_opacity(max(0.15, 1 - j / per))
            col.add(t)
        col.v = v
        g.add(col)

    def fall(m, dt):
        for c in m:
            c.shift(DOWN * c.v * dt)
            if c[-1].get_y() < -9:
                c.shift(UP * 17)
    g.add_updater(fall)
    return g


# ─────────────────────────────────────────────────────────────────────────────
class GnosisScene(KabalaScene):
    def k_setup(self, block_index: int = 0):
        self.frames = STARTS[block_index] * FPS
        self.rng = np.random.default_rng(1945 + block_index)
        self.bg = K.make_background(seed=29)
        self.dust = K.Dust(n=50, seed=4)
        self.add(self.bg, self.dust)
        self.hook_mob = self.cap_mob = self.src_mob = None
        self.focus = Dot(radius=0.001).set_opacity(0)
        self.mesh = MatrixMesh()
        self.core = golden_core()
        self.hud = self.mesh
        # Estado de la malla al empezar cada bloque (para renders sueltos)
        self.mesh.base_op = 0.0 if block_index == 0 else 0.28
        if 1 <= block_index <= 4:
            self.mesh.paint(ILLUSION)
        if block_index == 5:
            self.mesh.paint(GOLD, 0.2)
            self.mesh.base_op = 0.32
        if block_index >= 3 and block_index <= 4:
            self.add(self.core.set_opacity(0.5))
        if block_index < 6:
            self.add(self.mesh)

    def stage(self):
        keep = {id(self.bg), id(self.dust), id(self.mesh), id(self.core)}
        return [m for m in self.mobjects if id(m) not in keep]

    def swap(self, old, new_anims, rt=0.7):
        self.run(*[FadeOut(o, scale=0.85) for o in old if o is not None], *new_anims, rt=rt)


# ═════════════════════════════════════════════════════════════════════════════
def block0(s):
    m = s.mesh
    s.run(UpdateFromAlphaFunc(m, lambda mm, a: setattr(mm, "base_op", 0.3 * a),
                              suspend_mobject_updating=False),
          LaggedStart(*[Create(p) for p in m], lag_ratio=0.002),
          s.caption("Tu película favorita está basada…", size=62, rt=1.0), rt=1.6)
    s.run(s.caption("…en la segunda venida de Cristo.", size=62, accents={"cristo.": GOLD}),
          rt=1.0)
    s.until(3.0)
    s.run(m.tint(ILLUSION, op=0.28), s.caption("Y no lo sabías.", size=80,
                                               accents={"sabías.": CYAN}), rt=1.4)
    s.until(5.2)
    s.run(s.caption("Matrix no es ciencia ficción. Es gnosis.", size=64, font=FONT_SANS,
                    accents={"matrix": CODE, "gnosis.": GOLD}), rt=1.3)
    s.until(8.0)
    arch = VGroup(*[archon(0.55, seed=i) for i in range(3)]).arrange(RIGHT, buff=0.5)
    arch.move_to([0, Y_VIS, 0])
    ags = VGroup(agent(0.5, seed=8).move_to([-2.6, Y_VIS - 0.4, 0]),
                 agent(0.5, seed=9).move_to([2.6, Y_VIS - 0.4, 0]))
    s.run(LaggedStart(*[FadeIn(a, shift=UP * 0.6) for a in [*arch, *ags]], lag_ratio=0.18),
          s.caption("Esto es lo que los textos prohibidos revelan.",
                    accents={"prohibidos": RED}), rt=1.8)
    s.focus = arch
    s.until(12.0)
    ribbon = RoundedRectangle(width=8.3, height=1.5, corner_radius=0.2, stroke_width=3,
                              color=GOLD).set_fill(INK, 0.95).move_to([0, -3.15, 0])
    a1 = kinetic_text("Quédate: la verdad sobre el Demiurgo", size=58, font=FONT_SANS,
                      accents={"quédate:": GOLD, "demiurgo": GOLD}).move_to(ribbon)
    arrow = Arrow([2.4, 3.3, 0], [3.7, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    arrow.add_updater(blink_updater(7))
    s.run(s.drop_caption(), FadeIn(ribbon, shift=UP * 0.4), reveal_words(a1, 0.7), rt=0.8)
    s.add(arrow)
    s.until(13.6, focus=arch)
    a2 = kinetic_text("aparece al final.", size=64, font=FONT_SANS,
                      accents={"final.": GOLD}).move_to(ribbon)
    s.run(FadeOut(a1, shift=UP * 0.2), rt=0.2)
    s.run(reveal_words(a2, 0.6), rt=0.6)
    s.until(15.0, focus=arch)


# ═════════════════════════════════════════════════════════════════════════════
def block1(s):
    s.transition(None)
    eg = low_poly(resample(EGYPT, 0.45), "#8A6B3A", seed=4, rings=2, dome=0.6)
    eg.scale(1.1).move_to([0, Y_VIS + 0.55, 0])
    c = eg.get_center()
    nile_pts = [c + np.array([x, y, 0]) * 1.3 for x, y in
                [(0.95, -1.6), (1.05, -0.9), (0.9, -0.3), (0.95, 0.4), (0.7, 1.0), (0.6, 1.62)]]
    nile_pts = [c + (p - c) * 1.1 / 1.3 for p in nile_pts]
    nile = VMobject(stroke_color=CYAN, stroke_width=6).set_points_smoothly(nile_pts)
    nh = c + np.array([1.0, -0.75, 0]) * 1.1
    pin = VGroup(Polygon(nh, nh + [-0.2, 0.62, 0], nh + [0, 0.78, 0], stroke_width=0)
                 .set_fill(shade(GOLD, 1.1), 1),
                 Polygon(nh, nh + [0.2, 0.62, 0], nh + [0, 0.78, 0], stroke_width=0)
                 .set_fill(shade(GOLD, 0.6), 1))
    lab = mono("NAG HAMMADI", 52, GOLD).next_to(pin, LEFT, buff=0.25).shift(UP * 0.35)
    s.run(s.hook("Antes de la Iglesia, hubo otra verdad.", accents={"verdad.": GOLD}),
          LaggedStart(*[FadeIn(f, scale=0.4) for f in eg.family_members_with_points()],
                      lag_ratio=0.004), rt=2.0)
    s.run(Create(nile), FadeIn(pin, shift=DOWN * 0.5), FadeIn(lab), rt=1.0)
    s.run(Flash(nh, color=GOLD, flash_radius=0.6, num_lines=14),
          s.caption("1945: 13 códices gnósticos.", font=FONT_SANS, size=64), rt=1.0)
    books = VGroup(*[codex(i) for i in range(13)])
    books.arrange_in_grid(rows=2, cols=7, buff=0.18).scale(0.8).move_to([0, -2.0, 0])
    s.run(LaggedStart(*[FadeIn(b, shift=UP * 0.4) for b in books], lag_ratio=0.12), rt=2.0)
    s.focus = eg
    s.until(25.0)
    # Los apóstoles: Tomás, Felipe, María Magdalena
    ap = VGroup(*[figure(ROBE, col, seed=i, scale=0.62)
                  for i, col in enumerate(("#6B5A44", "#4C5A6B", "#6B4456"))]).arrange(RIGHT, buff=0.9)
    ap.move_to([0, Y_VIS + 0.4, 0])
    names = VGroup(*[mono(n, 40, BONE).next_to(a, DOWN, buff=0.15)
                     for n, a in zip(("TOMÁS", "FELIPE", "MARÍA MAGDALENA"), ap)])
    names[1].shift(DOWN * 0.45)
    if names[2].get_right()[0] > 4.0:
        names[2].shift(LEFT * (names[2].get_right()[0] - 4.0))
    titles = VGroup(mono("La Hipóstasis de los Arcontes", 44, CYAN),
                    mono("Evangelio de Tomás", 44, CYAN)).arrange(DOWN, buff=0.12)
    titles.move_to([0, 3.15, 0])
    s.swap([eg, nile, pin, lab, books], [s.drop_hook(),
                                          LaggedStart(*[FadeIn(a, shift=UP * 0.5) for a in ap],
                                                      lag_ratio=0.25)], rt=1.4)
    s.run(FadeIn(names), FadeIn(titles, shift=DOWN * 0.2),
          s.caption("Conocimiento secreto. Perseguido por herejía.",
                    accents={"herejía.": RED}), rt=1.3)
    s.focus = ap
    s.until(35.0)
    # La malla se ilumina en oro: la chispa divina
    spark = low_poly([(np.cos(a) * (0.6 if i % 2 == 0 else 0.22), np.sin(a) * (0.6 if i % 2 == 0 else 0.22))
                      for i, a in enumerate(np.linspace(0, TAU, 16, endpoint=False))],
                     GOLD, seed=3, rings=1, dome=1.2).move_to([0, Y_VIS, 0])
    s.swap([ap, names, titles], [s.mesh.tint(GOLD, glow=0.15, op=0.3), FadeIn(spark, scale=0.2)],
           rt=1.6)
    s.run(Flash(spark.get_center(), color=GOLD, flash_radius=1.6, num_lines=20),
          s.caption("La Gnosis: despertar la chispa divina.", accents={"gnosis:": GOLD,
                                                                      "divina.": GOLD}), rt=1.2)
    s.until(42.5, focus=spark)
    s.run(s.mesh.tint(ILLUSION, op=0.28), spark.animate.scale(0.5), rt=1.4)
    s.until(45.0, focus=spark)


# ═════════════════════════════════════════════════════════════════════════════
def block2(s):
    s.transition(None)
    dm = demiurge(1.15).move_to([0, Y_VIS + 0.2, 0])
    s.run(s.hook("El mundo no fue creado por Dios.", accents={"dios.": GOLD}),
          LaggedStart(*[FadeIn(f, scale=0.4) for f in dm.family_members_with_points()],
                      lag_ratio=0.003), rt=2.0)
    s.until(47.8, focus=dm)
    s.run(s.hook("Fue creado por un carcelero.", accents={"carcelero.": RED}), rt=1.0)
    s.run(dm[3].animate.scale(1.5).set_fill(RED, 1),
          s.caption("El Demiurgo: el dios inferior.", font=FONT_SANS,
                    accents={"demiurgo:": RED}), rt=1.0)
    s.focus = dm
    s.until(55.0)
    # Arcontes en las esferas planetarias
    rings = VGroup(*[Polygon(*[[r * np.cos(a), Y_VIS + 0.42 * r * np.sin(a), 0]
                               for a in np.linspace(0, TAU, 18, endpoint=False)],
                             stroke_width=2, stroke_color=ILLUSION, stroke_opacity=0.8)
                     for r in (1.2, 1.9, 2.6, 3.3)])
    archs = VGroup()
    for i, r in enumerate((1.2, 1.9, 2.6, 3.3)):
        a = 0.6 + i * 1.7
        archs.add(archon(0.32, seed=20 + i).move_to([r * np.cos(a), Y_VIS + 0.42 * r * np.sin(a) + 0.5, 0]))
    core = low_poly(ngon(10, 0.45, center=(0, Y_VIS)), RED, seed=5, rings=1, dome=1)
    s.swap([dm], [s.drop_hook(), Create(rings, lag_ratio=0.2), FadeIn(core, scale=0.3)], rt=1.2)
    s.run(LaggedStart(*[FadeIn(a, shift=DOWN * 0.4) for a in archs], lag_ratio=0.2),
          s.caption("Arcontes: los guardianes de la prisión.", accents={"arcontes:": RED,
                                                                        "prisión.": RED}), rt=1.6)

    def orbit(m, dt):
        m.t_ = getattr(m, "t_", 0) + dt
        for i, (a, r) in enumerate(zip(m, (1.2, 1.9, 2.6, 3.3))):
            ang = 0.6 + i * 1.7 + m.t_ * (0.5 - 0.08 * i)
            a.move_to([r * np.cos(ang), Y_VIS + 0.42 * r * np.sin(ang) + 0.5, 0])
    archs.add_updater(orbit)
    s.until(65.0, focus=rings)
    archs.clear_updaters()
    # La malla se agrieta
    cracks = crack_lines(s.rng, n=6)
    s.swap([rings, archs, core], [s.mesh.tint(ILLUSION, op=0.34)], rt=0.8)
    s.add(s.core.set_opacity(0))
    s.run(LaggedStart(*[Create(c) for c in cracks], lag_ratio=0.15),
          s.core.animate.set_opacity(0.5),
          *[p.animate.set_fill(opacity=0.05) for p in s.mesh.near((0, Y_VIS), 1.2)],
          s.caption("El mundo material: una ilusión para atrapar almas.",
                    accents={"ilusión": ILLUSION, "almas.": GOLD}), rt=2.4)
    for p in s.mesh.near((0, Y_VIS), 1.2):
        p.op = 0.15
    s.glitch(0.2, strength=0.2)
    s.until(75.0, focus=cracks)


# ═════════════════════════════════════════════════════════════════════════════
def block3(s):
    s.transition(None)
    rain = binary_rain().set_z_index(-20)
    s.add(rain)
    s.run(s.hook("1999. Las Wachowski lo entendieron.", accents={"wachowski": CODE}),
          FadeIn(rain), s.mesh.tint("#1F5C3A", op=0.32), rt=1.6)
    s.run(s.caption("Matrix: el mundo ilusorio.", font=FONT_SANS, size=66,
                    accents={"matrix:": CODE, "ilusorio.": ILLUSION}), rt=1.0)
    s.until(85.0, focus=rain)
    # El Agente
    ag = agent(1.25, seed=31).move_to([0, Y_VIS - 0.1, 0])
    shades = ag[3]
    s.run(s.drop_hook(), FadeIn(ag, shift=UP * 0.6), rain.animate.set_opacity(0.35), rt=1.2)
    s.run(shades.animate.set_fill("#3BD16F", 1), Flash(shades.get_center(), color=CODE,
                                                       flash_radius=0.8),
          s.caption("Los Agentes: los Arcontes modernos.", accents={"agentes:": RED,
                                                                    "arcontes": RED}), rt=1.0)
    s.focus = ag
    s.glitch(0.2, strength=0.18)
    s.until(95.0)
    # Morpheus ofrece la pastilla
    mo = coat(1.15, seed=41, color="#2B2030").move_to([0, Y_VIS - 0.1, 0])
    red = pill("#D0312D", 0.5).move_to(mo.get_center() + np.array([-1.55, -0.45, 0]))
    blue = pill("#2D6BD0", -0.5).move_to(mo.get_center() + np.array([1.55, -0.45, 0]))
    hands = VGroup(*[low_poly(ngon(6, 0.28, center=(0, 0)), "#7A5A44", seed=50 + i, rings=1)
                     .move_to(p.get_center() + DOWN * 0.3) for i, p in enumerate((red, blue))])
    s.swap([ag], [FadeIn(mo, shift=LEFT * 0.6)], rt=0.8)
    s.run(FadeIn(hands), FadeIn(red, scale=0.3), FadeIn(blue, scale=0.3),
          s.caption("Morpheus: el Redentor Gnóstico.", accents={"morpheus:": GOLD,
                                                               "redentor": GOLD}), rt=1.2)
    s.run(red.animate.scale(1.5), blue.animate.set_opacity(0.3),
          Flash(red.get_center(), color=RED, flash_radius=0.7), rt=0.8)
    s.until(105.0, focus=red)
    rain.clear_updaters()


# ═════════════════════════════════════════════════════════════════════════════
def block4(s):
    s.transition(None)
    neo = coat(1.2, seed=61, color="#141821").move_to([0, Y_VIS - 0.2, 0])
    s.run(s.hook("Neo no es un hacker. Es un iniciado.", accents={"iniciado.": GOLD}),
          s.mesh.tint(ILLUSION, op=0.32), FadeIn(neo, shift=UP * 0.5), rt=1.6)
    # La malla se fragmenta alrededor de Neo
    near = s.mesh.near((0, Y_VIS), 3.0)
    rng = s.rng
    anims = []
    for p in near:
        d = p.c0 - np.array([0, Y_VIS, 0])
        d = d / (np.linalg.norm(d) + 1e-6)
        anims.append(p.animate.shift(d * rng.uniform(0.3, 0.9)).rotate(rng.uniform(-0.6, 0.6)))
    for p in near:
        p.op = 0.4
    s.run(LaggedStart(*anims, lag_ratio=0.01), s.core.animate.set_opacity(1.0).scale(1.15),
          s.caption("El despertar de la Gnosis.", accents={"gnosis.": GOLD}), rt=2.2)
    s.focus = neo
    s.until(115.0)
    # Neo detiene las balas
    bullets = VGroup()
    for i, y in enumerate((-0.6, -0.1, 0.4, 0.9, 1.4)):
        b = low_poly([(0.45, 0), (0.1, 0.11), (-0.35, 0.09), (-0.35, -0.09), (0.1, -0.11)],
                     GOLD, seed=70 + i, rings=1, dome=1.2).rotate(PI)
        b.move_to([4.8 + i * 0.5, Y_VIS + y, 0])
        bullets.add(b)
    stops = [1.2 + 0.12 * i for i in range(5)]
    ripples = VGroup(*[Polygon(*[[st + 0.18 * np.cos(a) * 0.4, Y_VIS + y + 0.5 * np.sin(a), 0]
                                 for a in np.linspace(0, TAU, 10, endpoint=False)],
                               stroke_width=3, stroke_color=CYAN, stroke_opacity=0.8)
                       for st, y in zip(stops, (-0.6, -0.1, 0.4, 0.9, 1.4))])
    s.run(neo.animate.shift(LEFT * 1.4), *[b.animate.move_to([st, b.get_y(), 0])
                                          for b, st in zip(bullets, stops)],
          s.caption("Transgredir las reglas del Demiurgo.", accents={"transgredir": GOLD}),
          rt=1.4)
    s.run(LaggedStart(*[FadeIn(r, scale=0.3) for r in ripples], lag_ratio=0.15),
          *[b.animate.rotate(rng.uniform(-0.3, 0.3)) for b in bullets], rt=1.2)
    s.run(*[b.animate.shift(DOWN * (Y_VIS + 2.3 + b.get_y() - Y_VIS)).rotate(1.2).set_opacity(0.6)
            for b in bullets], FadeOut(ripples), rt=1.4)
    s.until(125.0, focus=neo)
    # La malla se convierte en luz dorada
    s.run(s.mesh.tint(GOLD, glow=0.2, op=0.32), FadeOut(bullets),
          neo.animate.shift(RIGHT * 1.4), s.drop_hook(), rt=1.8)
    light = VGroup(*[Line([0, Y_VIS, 0], [6 * np.cos(a), Y_VIS + 6 * np.sin(a), 0],
                          stroke_width=4, color=GOLD, stroke_opacity=0.5)
                     for a in np.linspace(0, TAU, 20, endpoint=False)]).set_z_index(-25)
    s.run(Create(light, lag_ratio=0.05), s.caption("La chispa divina se libera.",
                                                   accents={"chispa": GOLD, "divina": GOLD}),
          rt=1.4)
    light.add_updater(lambda m, dt: m.rotate(0.15 * dt, about_point=[0, Y_VIS, 0]))
    s.until(135.0, focus=neo)


# ═════════════════════════════════════════════════════════════════════════════
def block5(s):
    s.transition(None)
    neo = coat(0.95, seed=61, color="#141821").move_to([-1.8, Y_VIS - 0.2, 0])
    sm = agent(0.95, seed=31).move_to([1.8, Y_VIS - 0.2, 0])
    s.run(s.hook("La gnosis no es solo conocimiento. Es poder.", accents={"poder.": GOLD}),
          FadeIn(neo, shift=RIGHT * 0.8), FadeIn(sm, shift=LEFT * 0.8), rt=1.6)
    vs = Text("VS", font=FONT_SANS, font_size=px(110), weight=BOLD, color=RED).move_to([0, Y_VIS + 0.3, 0])
    s.run(FadeIn(vs, scale=2), s.caption("El Redentor vs. el Arconte.", font=FONT_SANS,
                                         accents={"redentor": GOLD, "arconte.": RED}), rt=1.0)
    s.glitch(0.2, strength=0.2)
    s.focus = VGroup(neo, sm)
    s.until(145.0)
    # Neo se convierte en luz
    st = neo.copy()

    def to_light(m, a):
        m.become(st)
        for f in m.family_members_with_points():
            k = getattr(f, "k", 0.6)
            f.set_fill(lerp(f.get_fill_color(), "#FFFFFF", a), f.get_fill_opacity())
            f.set_stroke("#FFFFFF", opacity=0.6 * a)
        m.scale(1 + 0.15 * a)
    s.run(FadeOut(vs), UpdateFromAlphaFunc(neo, to_light, rate_func=smooth),
          sm.animate.set_opacity(0.4).shift(RIGHT * 0.5),
          s.caption("La ilusión se rompe.", accents={"rompe.": GOLD}), rt=2.0)
    s.run(Flash(neo.get_center(), color="#FFFFFF", flash_radius=2.2, num_lines=24), rt=0.6)
    s.until(155.0, focus=neo)
    # La malla se desintegra en partículas
    rng = s.rng
    s.mesh.clear_updaters()
    anims = []
    for p in s.mesh:
        d = p.c0[:2] - np.array([0, Y_VIS])
        d = np.array([*(d / (np.linalg.norm(d) + 1e-6)), 0])
        anims.append(p.animate.shift(d * rng.uniform(1, 4)).scale(rng.uniform(0.05, 0.3))
                     .set_opacity(0))
    s.run(LaggedStart(*anims, lag_ratio=0.003), FadeOut(sm, scale=0.5),
          s.drop_hook(), s.caption("El mundo material es una ilusión.",
                                   accents={"ilusión.": ILLUSION}), rt=3.0)
    s.remove(s.mesh)
    s.until(165.0, focus=neo)


# ═════════════════════════════════════════════════════════════════════════════
def block6(s):
    s.transition(None)
    s.remove(s.mesh)
    seal = stamp("GNOSIS", GOLD, 150, angle=-0.06).move_to([0, Y_VIS + 0.3, 0])
    glow = golden_core(3.2, center=(0, Y_VIS + 0.3)).set_z_index(-5)
    s.run(FadeIn(glow, scale=0.3), FadeIn(seal, scale=2.2), rt=0.8)
    s.run(Flash(seal.get_center(), color=GOLD, flash_radius=2.6, num_lines=24),
          s.caption("Nag Hammadi. El Demiurgo. Los Arcontes.", font=FONT_SANS,
                    accents={"demiurgo.": RED, "arcontes.": RED}, rt=1.3), rt=1.4)
    s.until(169.6, focus=seal)
    s.run(s.caption("Matrix. Una pregunta.", font=FONT_SANS, size=72,
                    accents={"matrix.": CODE, "pregunta.": GOLD}), rt=0.9)
    s.until(172.0, focus=seal)
    # CTA final: la luz se vuelve lluvia binaria que se disuelve
    rain = binary_rain(seed=9, color=GOLD).set_z_index(-20)
    rain.set_opacity(0)
    banner = RoundedRectangle(width=8.3, height=1.75, corner_radius=0.2, stroke_width=3,
                              color=GOLD).set_fill(INK, 0.95).move_to([0, -2.6, 0])
    cta = kinetic_text("Si quieres que analice los textos completos, sígueme.", size=52,
                       font=FONT_SANS, accents={"sígueme.": GOLD}).move_to(banner)
    arrow = Arrow([2.6, 3.3, 0], [3.7, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    bub = RoundedRectangle(width=1.25, height=0.95, corner_radius=0.25, color=BONE,
                           stroke_width=4).set_fill(INK, 0.9).move_to([3.25, -4.15, 0])
    dots = VGroup(*[Dot([3.25 + x, -4.15, 0], radius=0.07, color=CYAN) for x in (-0.3, 0, 0.3)])
    ask = kinetic_text("¿Crees que vivimos en una Matrix? Dímelo.", size=48, font=FONT_SERIF,
                       accents={"matrix?": CODE, "dímelo.": GOLD}, max_width=6.0)
    ask.next_to(bub, LEFT, buff=0.3)
    s.add(rain)
    s.run(s.drop_caption(), FadeOut(seal, scale=0.7), FadeOut(glow),
          UpdateFromAlphaFunc(rain, lambda m, a: [c.set_opacity(0.6 * a) for c in m],
                              suspend_mobject_updating=False),
          FadeIn(banner), reveal_words(cta, 1.2), rt=1.4)
    arrow.add_updater(blink_updater(7))
    s.add(arrow)
    s.run(FadeIn(VGroup(bub, dots), scale=0.6), reveal_words(ask, 1.1), rt=1.2)
    s.run(UpdateFromAlphaFunc(rain, lambda m, a: [c.set_opacity(0.6 * (1 - a)) for c in m],
                              suspend_mobject_updating=False), rt=180.0 - s.now)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


class _Block(GnosisScene):
    INDEX = 0

    def construct(self):
        self.k_setup(self.INDEX)
        BLOCKS[self.INDEX](self)
        assert self.frames == ENDS[self.INDEX] * FPS, (self.INDEX, self.frames)


for _i in range(7):
    globals()[f"Block{_i}"] = type(f"Block{_i}", (_Block,), {"INDEX": _i})


class FullVideo(GnosisScene):
    def construct(self):
        self.k_setup(0)
        for i, b in enumerate(BLOCKS):
            assert self.frames == STARTS[i] * FPS, (i, self.frames)
            b(self)
            assert self.frames == ENDS[i] * FPS, (i, self.frames)
        assert self.frames == 180 * FPS


if __name__ == "__main__":
    config.disable_caching = True
    FullVideo().render()
