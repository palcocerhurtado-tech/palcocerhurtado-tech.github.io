"""
main.py — «HERMES TRISMEGISTO: EL CÓDIGO DEL 3 Y EL 33»
Vertical 9:16 · 1080×1920 · 30 fps · 180 s exactos · Manim CE · geometría sagrada.

    manim -qh --disable_caching main.py FullVideo        # o: python main.py
    KABALA_PREVIEW=1 manim --disable_caching main.py Block4     # vista previa 540×960

Motor compartido: ../kabala_video/utils.py (reloj por frames, texto cinético, glitch,
wipe) y ../thule_video/poly.py (mallas facetadas).
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
    AnimationGroup, Arc, Arrow, Circle, Create, Dot, FadeIn, FadeOut, Flash, GrowFromCenter,
    LaggedStart, Line, Polygon, RoundedRectangle, Text, Transform, UpdateFromAlphaFunc,
    VGroup, VMobject, config, smooth,
)
from poly import low_poly, ngon, resample, shade, stamp  # noqa: E402
from utils import (  # noqa: E402
    FONT_MONO, FONT_SANS, FONT_SERIF, FPS, KabalaScene, blink_updater, kinetic_text, px,
    reveal_words,
)

INK, BONE, GOLD, CYAN, RED = "#0A0A0A", "#E8E6E3", "#C9A227", "#5AC8FA", "#8B0000"
RED_T = "#C0262D"          # rojo legible para texto
EMERALD = "#1F8A5B"
config.background_color = INK
K.BG_IN, K.BG_OUT, K.PARCHMENT = "#11100C", "#070706", "#14110A"
Y_VIS = 0.35
STARTS = [0, 15, 45, 75, 105, 135, 165]
ENDS = [15, 45, 75, 105, 135, 165, 180]
HUD_C = np.array([-3.25, 5.3, 0.0])


def mono(t, size=48, color=BONE):
    return Text(t, font=FONT_MONO, font_size=px(size), weight=BOLD, color=color,
                disable_ligatures=True)


def sans(t, size=48, color=BONE):
    return Text(t, font=FONT_SANS, font_size=px(size), weight=BOLD, color=color,
                disable_ligatures=True)


def serif(t, size=56, color=GOLD):
    return Text(t, font=FONT_SERIF, font_size=px(size), weight=BOLD, color=color,
                disable_ligatures=True)


def tri(r=1.0, center=ORIGIN, inverted=False, color=GOLD, sw=6):
    a0 = -PI / 2 if inverted else PI / 2
    pts = [np.array(center) + r * np.array([np.cos(a0 + k * TAU / 3), np.sin(a0 + k * TAU / 3), 0])
           for k in range(3)]
    return Polygon(*pts, color=color, stroke_width=sw)


def glow(mob, color=GOLD, widths=(18, 10), ops=(0.12, 0.22)):
    g = VGroup(*[mob.copy().set_stroke(color, width=w, opacity=o).set_fill(opacity=0)
                 for w, o in zip(widths, ops)])
    return VGroup(g, mob)


def stylized_33(height=3.2, color=GOLD):
    t = Text("33", font=FONT_SERIF, font_size=px(400), weight=BOLD, color=color)
    t.set(height=height)
    halo = t.copy().set_fill(opacity=0).set_stroke(color, width=14, opacity=0.25)
    return VGroup(halo, t)


# ─────────────────────────────────────────────────────────────────────────────
# El sello recurrente (triángulo → círculo → cuerdas → cuentas → estrella)
# ─────────────────────────────────────────────────────────────────────────────
def seal_layers(r=0.62, center=HUD_C, sw=3):
    c = np.array(center)
    t = tri(r, c, sw=sw)
    circ = Circle(radius=r * 1.12, color=GOLD, stroke_width=sw * 0.8).move_to(c)
    xs = (-0.28, 0.0, 0.28)
    strings = VGroup(*[Line(c + np.array([x * r, -0.5 * r, 0]),
                            c + np.array([x * r, (0.95 - 1.6 * abs(x)) * r, 0]),
                            color=CYAN, stroke_width=sw * 0.6) for x in xs])
    beads = VGroup(*[Dot(c + r * 1.3 * np.array([np.cos(a), np.sin(a), 0]), radius=r * 0.045,
                         color=GOLD) for a in np.linspace(0, TAU, 33, endpoint=False)])
    star = tri(r, c, inverted=True, sw=sw)
    return {"tri": t, "circle": circ, "strings": strings, "beads": beads, "star": star}


class HermesScene(KabalaScene):
    LAYERS = ["tri", "circle", "strings", "beads", "star"]

    def k_setup(self, block_index: int = 0):
        self.frames = STARTS[block_index] * FPS
        self.rng = np.random.default_rng(33 + block_index)
        self.bg = K.make_background(seed=3)
        self.dust = K.Dust(n=50, seed=12)
        self.add(self.bg, self.dust)
        self.hook_mob = self.cap_mob = self.src_mob = None
        self.focus = Dot(radius=0.001).set_opacity(0)
        self.seal = seal_layers()
        self.hud = VGroup().set_z_index(60)
        self.hud_layers = []
        # capas ya ganadas al empezar cada bloque
        have = [[], ["tri"], ["tri", "circle"], ["tri", "circle", "strings"],
                ["tri", "circle", "strings"], ["tri", "circle", "strings", "beads", "star"],
                ["tri", "circle", "strings", "beads", "star"]][block_index]
        for k in have:
            self.hud.add(self.seal[k])
            self.hud_layers.append(k)
        if have:
            self.add(self.hud)
        self.pending, self.hud_angle = [], 0.0

        def spin(m, dt):
            m.rotate(0.12 * dt, about_point=HUD_C)
            self.hud_angle += 0.12 * dt
        self.hud.add_updater(spin)

    def stage(self):
        keep = {id(self.bg), id(self.dust), id(self.hud)}
        return [m for m in self.mobjects if id(m) not in keep]

    def hud_add(self, key):
        """Nueva capa del sello: vuela desde el centro y se incrusta en el HUD."""
        if key in self.hud_layers:
            return None
        if self.hud not in self.mobjects:
            self.add(self.hud)
        layer = self.seal[key]
        layer.rotate(self.hud_angle, about_point=HUD_C)
        tmp = layer.copy().scale(3.2, about_point=HUD_C).move_to([0, Y_VIS, 0]).set_opacity(0.0)
        self.hud_layers.append(key)
        self.pending.append((tmp, layer))
        return Transform(tmp, layer.copy())

    def run(self, *anims, rt=1.0):
        super().run(*anims, rt=rt)
        while self.pending:
            tmp, layer = self.pending.pop()
            self.remove(tmp)
            layer.rotate(0)
            self.hud.add(layer)

    def swap(self, old, new_anims, rt=0.7):
        self.run(*[FadeOut(o, scale=0.85) for o in old if o is not None], *new_anims, rt=rt)

    def label(self, text, pos, color=CYAN, size=44):
        return mono(text, size, color).move_to(pos)


# ═════════════════════════════════════════════════════════════════════════════
def block0(s):
    t = tri(2.1, [0, Y_VIS, 0], sw=8)
    halo = glow(t)[0]
    s.run(Create(t), FadeIn(halo), s.caption("Hay un número que lo contiene todo.",
                                             size=62, accents={"todo.": GOLD}, rt=1.4), rt=2.2)
    s.focus = t
    s.until(3.0)
    t2 = tri(2.1, [0, Y_VIS, 0], inverted=True, sw=8).set_color(CYAN)
    ghost = t.copy()
    star = VGroup(halo, t, t2)
    s.run(Transform(ghost, t2), s.caption("El 3. La tríada. La perfección.", size=66,
                                          font=FONT_SANS, accents={"3.": GOLD, "perfección.": GOLD}),
          rt=2.0)
    s.remove(ghost)
    s.add(t2)
    s.run(Flash([0, Y_VIS, 0], color=GOLD, flash_radius=2.6, num_lines=24), Rotate_(star, PI / 6),
          rt=1.2)
    s.until(8.0, focus=star)
    n33 = stylized_33(3.4).move_to([0, Y_VIS, 0])
    s.run(Transform(star, n33), s.caption("Y su eco en el 33. La maestría.", size=62,
                                          accents={"33.": GOLD, "maestría.": GOLD}), rt=1.6)
    s.focus = star
    s.until(12.0)
    ribbon = RoundedRectangle(width=8.3, height=1.5, corner_radius=0.2, stroke_width=3,
                              color=GOLD).set_fill(INK, 0.95).move_to([0, -3.15, 0])
    a1 = kinetic_text("Quédate: el secreto de Hermes Trismegisto", size=54, font=FONT_SANS,
                      accents={"quédate:": GOLD, "hermes": GOLD}).move_to(ribbon)
    arrow = Arrow([2.4, 3.3, 0], [3.7, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    arrow.add_updater(blink_updater(7))
    s.run(s.drop_caption(), FadeIn(ribbon, shift=UP * 0.4), reveal_words(a1, 0.7),
          s.hud_add("tri"), rt=0.9)
    s.add(arrow)
    s.until(13.6, focus=star)
    a2 = kinetic_text("aparece al final.", size=64, font=FONT_SANS,
                      accents={"final.": GOLD}).move_to(ribbon)
    s.run(FadeOut(a1, shift=UP * 0.2), rt=0.2)
    s.run(reveal_words(a2, 0.6), rt=0.6)
    s.until(15.0, focus=star)


def Rotate_(mob, angle):
    st = {"a": 0.0}
    c = mob.get_center()

    def f(m, a):
        m.rotate(angle * a - st["a"], about_point=c)
        st["a"] = angle * a
    return UpdateFromAlphaFunc(mob, f, rate_func=smooth)


# ═════════════════════════════════════════════════════════════════════════════
THOTH = [(-0.35, 1.45), (0.05, 1.7), (0.35, 1.5), (0.45, 1.25), (1.6, 0.55), (1.65, 0.45),
         (0.45, 1.0), (0.35, 0.75), (0.5, 0.2), (1.05, -0.05), (1.15, -2.0), (-1.15, -2.0),
         (-1.05, -0.05), (-0.55, 0.25), (-0.6, 0.95)]
HERMES = [(0.0, 1.55), (0.42, 1.45), (0.55, 1.1), (0.45, 0.65), (0.3, 0.45), (1.0, 0.1),
          (1.1, -2.0), (-1.1, -2.0), (-1.0, 0.1), (-0.3, 0.45), (-0.45, 0.65), (-0.55, 1.1),
          (-0.42, 1.45)]


def deity(pts, color, scale=1.0, seed=0):
    return low_poly(resample([(x * scale, y * scale) for x, y in pts], 0.4 * scale), color,
                    seed=seed, rings=2, dome=0.7)


def petasos(scale=1.0):
    s = scale
    brim = Polygon([-0.75 * s, 1.45 * s, 0], [0.75 * s, 1.45 * s, 0], [0.5 * s, 1.62 * s, 0],
                   [-0.5 * s, 1.62 * s, 0], stroke_width=0).set_fill(shade(GOLD, 0.8), 1)
    wing = lambda sx: Polygon([sx * 0.55 * s, 1.55 * s, 0], [sx * 1.25 * s, 2.0 * s, 0],
                              [sx * 1.05 * s, 1.75 * s, 0], [sx * 1.2 * s, 1.68 * s, 0],
                              stroke_width=0).set_fill(shade(BONE, 0.9), 1)
    return VGroup(brim, wing(1), wing(-1))


def caduceus(h=3.2, center=ORIGIN):
    c = np.array(center)
    staff = Line(c + DOWN * h / 2, c + UP * h / 2, color=GOLD, stroke_width=6)
    snakes = VGroup()
    for ph in (0, PI):
        ys = np.linspace(-h / 2 + 0.2, h / 2 - 0.5, 60)
        pts = [c + np.array([0.35 * np.sin(2.2 * (y + h / 2) + ph), y, 0]) for y in ys]
        snakes.add(VMobject(stroke_color=EMERALD if ph == 0 else CYAN, stroke_width=5)
                   .set_points_smoothly(pts))
    wings = VGroup(*[Polygon(c + [0, h / 2 - 0.3, 0], c + [sx * 0.9, h / 2 + 0.05, 0],
                             c + [sx * 0.7, h / 2 - 0.25, 0], c + [sx * 0.85, h / 2 - 0.4, 0],
                             stroke_width=0).set_fill(BONE, 0.9) for sx in (1, -1)])
    knob = Dot(c + UP * h / 2, radius=0.12, color=GOLD)
    return VGroup(staff, snakes, wings, knob)


def book(w=2.6, h=3.0, open_=0.0):
    left = Polygon([-w, h / 2, 0], [0, h / 2 - 0.1, 0], [0, -h / 2 - 0.1, 0], [-w, -h / 2, 0],
                   color=GOLD, stroke_width=3).set_fill("#2A2215", 1)
    right = left.copy().flip(UP, about_point=ORIGIN)
    lines = VGroup()
    for side in (-1, 1):
        for i in range(9):
            y = h / 2 - 0.45 - i * 0.28
            lines.add(Line([side * 0.25, y, 0], [side * (w - 0.3), y, 0], color=BONE,
                           stroke_width=2, stroke_opacity=0.5))
    return VGroup(left, right, lines)


def block1(s):
    s.transition(None)
    th = deity(THOTH, "#3C5A7A", 1.0, seed=1).move_to([-1.9, Y_VIS - 0.3, 0])
    he = VGroup(deity(HERMES, "#6E5A3A", 1.0, seed=2), petasos()).move_to([1.9, Y_VIS - 0.2, 0])
    cad = caduceus(2.6, [3.2, Y_VIS - 0.4, 0])
    lt = mono("THOT", 52, CYAN).next_to(th, DOWN, buff=0.2)
    lh = mono("HERMES", 52, GOLD).next_to(he, DOWN, buff=0.2)
    s.run(s.hook("El hombre que sabía tres veces.", accents={"tres": GOLD}),
          FadeIn(th, shift=RIGHT * 0.6), FadeIn(he, shift=LEFT * 0.6), rt=1.6)
    s.run(Create(cad, lag_ratio=0.2), FadeIn(lt), FadeIn(lh),
          s.caption("Thot + Hermes = Hermes Trismegisto.", font=FONT_SANS,
                    accents={"thot": CYAN, "trismegisto.": GOLD}), rt=1.4)
    s.until(20.5, focus=VGroup(th, he))
    fused = VGroup(deity(HERMES, "#4E5A5A", 1.25, seed=3), petasos(1.25)).move_to([0, Y_VIS, 0])
    name = mono("HERMES TRISMEGISTO", 54, GOLD).next_to(fused, DOWN, buff=0.25)
    s.run(th.animate.move_to(fused).set_opacity(0), he.animate.move_to(fused).set_opacity(0),
          FadeOut(VGroup(lt, lh)), cad.animate.move_to([2.6, Y_VIS, 0]), FadeIn(fused, scale=1.2),
          rt=1.4)
    s.run(Flash(fused.get_center(), color=GOLD, flash_radius=2.2, num_lines=20), FadeIn(name), rt=0.8)
    aa = VGroup(mono("aa aa", 56, CYAN), mono("→ «grande, grande»", 44, BONE)).arrange(RIGHT, buff=0.3)
    aa.move_to([0, 2.95, 0])
    s.run(s.drop_hook(), FadeIn(aa, shift=DOWN * 0.2),
          s.caption("Trismegisto: «tres veces grande».", accents={"veces": GOLD}), rt=1.2)
    s.until(25.0, focus=fused)
    # Las tres partes de la sabiduría
    big = tri(2.3, [0, Y_VIS - 0.1, 0], sw=7)
    words = VGroup(*[mono(w, 50, c) for w, c in
                     (("ALQUIMIA", GOLD), ("ASTROLOGÍA", CYAN), ("TEÚRGIA", RED_T))])
    vs = big.get_vertices()
    words[0].next_to(vs[0], UP, buff=0.2)
    words[1].next_to(vs[1], DOWN, buff=0.25).shift(RIGHT * 0.3)
    words[2].next_to(vs[2], DOWN, buff=0.25).shift(LEFT * 0.3)
    s.swap([fused, name, cad, aa], [Create(big)], rt=1.0)
    s.run(LaggedStart(*[FadeIn(w, scale=1.4) for w in words], lag_ratio=0.4),
          *[Flash(v, color=GOLD, flash_radius=0.5) for v in vs],
          s.caption("Las tres partes de la sabiduría.", accents={"tres": GOLD}), rt=2.0)
    hud = s.hud_add("circle")
    circ = Circle(radius=2.3 * 1.12, color=GOLD, stroke_width=4).move_to(big.get_center())
    s.run(Create(circ), hud, rt=1.2)
    s.until(35.0, focus=VGroup(big, words))
    # El Corpus Hermeticum
    bk = book().scale(0.9).move_to([0, Y_VIS, 0])
    left, right = bk[0], bk[1]
    right_closed = left.copy()
    s.swap([big, words, circ], [FadeIn(left), FadeIn(right_closed)], rt=0.7)
    s.run(Transform(right_closed, right), LaggedStart(*[Create(l) for l in bk[2]], lag_ratio=0.05),
          s.caption("El Corpus Hermeticum: la base de todo.", accents={"corpus": GOLD,
                                                                       "hermeticum:": GOLD}),
          rt=2.0)
    tags = VGroup(mono("GRIEGO · SIGLOS I–III d.C.", 46, CYAN),
                  mono("DIOS · COSMOS · HOMBRE", 46, GOLD)).arrange(DOWN, buff=0.18)
    tags.move_to([0, 3.15, 0])
    s.run(FadeIn(tags, shift=DOWN * 0.2), rt=0.6)
    s.until(45.0, focus=bk)


# ═════════════════════════════════════════════════════════════════════════════
def nine_triangles(r=2.4, center=(0, Y_VIS)):
    """Triángulo dividido en 9: 3×3 = 9."""
    big = tri(r, [*center, 0], sw=5)
    A, B, C = big.get_vertices()
    pts = {}
    for i in range(4):
        for j in range(4 - i):
            pts[(i, j)] = A + (B - A) * i / 3 + (C - A) * j / 3
    small = VGroup()
    for i in range(3):
        for j in range(3 - i):
            small.add(Polygon(pts[(i, j)], pts[(i + 1, j)], pts[(i, j + 1)], color=GOLD,
                              stroke_width=3).set_fill(GOLD, 0.15 + 0.05 * ((i + j) % 2)))
            if i + j < 2:
                small.add(Polygon(pts[(i + 1, j)], pts[(i + 1, j + 1)], pts[(i, j + 1)],
                                  color=GOLD, stroke_width=3).set_fill(GOLD, 0.35))
    return big, small


def lyre(h=2.4, center=ORIGIN):
    c = np.array(center)
    arms = VGroup(*[VMobject(stroke_color=GOLD, stroke_width=6).set_points_smoothly(
        [c + [sx * 0.3, -h / 2, 0], c + [sx * 0.9, -0.1, 0], c + [sx * 0.7, h / 2 - 0.3, 0],
         c + [sx * 1.0, h / 2, 0]]) for sx in (1, -1)])
    bar = Line(c + [-0.8, h / 2 - 0.2, 0], c + [0.8, h / 2 - 0.2, 0], color=GOLD, stroke_width=6)
    base = Line(c + [-0.45, -h / 2, 0], c + [0.45, -h / 2, 0], color=GOLD, stroke_width=6)
    strings = VGroup(*[Line(c + [x, -h / 2, 0], c + [x, h / 2 - 0.2, 0], color=CYAN, stroke_width=3)
                       for x in (-0.22, 0, 0.22)])
    return VGroup(arms, bar, base, strings)


def zodiac_sphere(r=1.2, center=ORIGIN):
    c = np.array(center)
    sph = Circle(radius=r, color=BONE, stroke_width=3).move_to(c)
    band = Circle(radius=r, color=GOLD, stroke_width=3).stretch(0.32, 1).rotate(0.4).move_to(c)
    ticks = VGroup()
    for k in range(12):
        a = TAU * k / 12
        p = c + np.array([r * 1.18 * np.cos(a), r * 1.18 * np.sin(a), 0])
        ticks.add(Dot(p, radius=0.08, color=(GOLD, CYAN, RED_T)[k % 3]))
    return VGroup(sph, band, ticks)


def vitruvian(scale=1.0, center=ORIGIN):
    c, s = np.array(center), scale
    head = Circle(radius=0.28 * s, color=BONE, stroke_width=4).move_to(c + [0, 1.25 * s, 0])
    body = Line(c + [0, 0.97 * s, 0], c + [0, -0.3 * s, 0], color=BONE, stroke_width=4)
    arms = VGroup(Line(c + [-1.35 * s, 0.85 * s, 0], c + [1.35 * s, 0.85 * s, 0], color=BONE, stroke_width=4),
                  Line(c + [0, 0.75 * s, 0], c + [-1.2 * s, 1.35 * s, 0], color=BONE, stroke_width=2, stroke_opacity=0.6),
                  Line(c + [0, 0.75 * s, 0], c + [1.2 * s, 1.35 * s, 0], color=BONE, stroke_width=2, stroke_opacity=0.6))
    legs = VGroup(Line(c + [0, -0.3 * s, 0], c + [-0.45 * s, -1.55 * s, 0], color=BONE, stroke_width=4),
                  Line(c + [0, -0.3 * s, 0], c + [0.45 * s, -1.55 * s, 0], color=BONE, stroke_width=4),
                  Line(c + [0, -0.3 * s, 0], c + [-1.0 * s, -1.3 * s, 0], color=BONE, stroke_width=2, stroke_opacity=0.6),
                  Line(c + [0, -0.3 * s, 0], c + [1.0 * s, -1.3 * s, 0], color=BONE, stroke_width=2, stroke_opacity=0.6))
    return VGroup(head, body, arms, legs)


def block2(s):
    s.transition(None)
    big, small = nine_triangles()
    s.run(s.hook("El 3 no es un número.", accents={"3": GOLD}), Create(big), rt=1.2)
    s.run(s.hook("Es una ley matemática y cósmica.", accents={"ley": GOLD}),
          LaggedStart(*[GrowFromCenter(t) for t in small], lag_ratio=0.15), rt=1.6)
    eq = VGroup(sans("3 × 3 = 9", 76, GOLD), sans("3 + 3 = 6", 56, BONE)).arrange(RIGHT, buff=0.6)
    eq.move_to([0, -1.85, 0])
    s.run(FadeIn(eq, shift=UP * 0.3), s.caption("El primer número perfecto para los pitagóricos.",
                                                accents={"perfecto": GOLD}), rt=1.3)
    s.focus = VGroup(big, small)
    s.until(52.0)
    medio = mono("«medio y analogía»: tres términos", 44, CYAN).move_to([0, -2.05, 0])
    s.run(FadeOut(eq), FadeIn(medio), rt=0.6)
    s.until(55.0, focus=VGroup(big, small))
    # geometría · música · astrología
    t = tri(0.9, [-2.6, Y_VIS + 0.2, 0], sw=6)
    ly = lyre(2.2, [0, Y_VIS + 0.2, 0])
    zs = zodiac_sphere(1.0, [2.6, Y_VIS + 0.2, 0])
    labs = VGroup(*[mono(w, 44, c).move_to([x, Y_VIS - 1.75, 0]) for w, c, x in
                    (("GEOMETRÍA", GOLD, -2.6), ("MÚSICA", CYAN, 0), ("ASTROLOGÍA", BONE, 2.6))])
    s.swap([big, small, medio], [s.drop_hook(), Create(t)], rt=0.8)
    s.run(Create(ly, lag_ratio=0.2), Create(zs, lag_ratio=0.1), FadeIn(labs),
          s.caption("La base de la geometría,", accents={"geometría,": GOLD}), rt=1.6)
    s.run(*[Indicate_(st) for st in ly[3]], s.caption("la música y la astrología.",
                                                     accents={"música": CYAN}), rt=1.2)
    note = VGroup(mono("3 sinfonías", 44, CYAN), mono("3 quaterniones", 44, GOLD)).arrange(RIGHT, buff=0.6)
    note.move_to([0, 3.15, 0])
    hud = s.hud_add("strings")
    s.run(FadeIn(note), hud, rt=1.0)
    s.until(65.0, focus=VGroup(t, ly, zs))
    # El hombre, vínculo de los tres mundos
    man = vitruvian(1.0, [0, Y_VIS, 0])
    rings = VGroup(*[Circle(radius=r, color=c, stroke_width=4).move_to([0, Y_VIS, 0])
                     for r, c in ((1.9, BONE), (2.5, CYAN), (3.1, GOLD))])
    rl = VGroup(*[mono(w, 40, c) for w, c in (("SUBLUNAR · elementos", BONE),
                                              ("CELESTE · cosmos", CYAN),
                                              ("INTELIGIBLE · Dios", GOLD))])
    for lab, r in zip(rl, (1.9, 2.5, 3.1)):
        lab.move_to([0, Y_VIS + r + 0.05, 0]).set_z_index(5)
        lab.add_background_rectangle(color=INK, opacity=0.85)
    s.swap([t, ly, zs, labs, note], [Create(man)], rt=1.0)
    s.run(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.3),
          LaggedStart(*[FadeIn(l) for l in rl], lag_ratio=0.3),
          s.caption("El hombre: el vínculo entre los tres mundos.", accents={"vínculo": GOLD}),
          rt=2.2)
    rings.add_updater(lambda m, dt: m.rotate(0.1 * dt, about_point=[0, Y_VIS, 0]))
    s.until(75.0, focus=man)
    rings.clear_updaters()


def Indicate_(mob):
    return UpdateFromAlphaFunc(mob, lambda m, a: m.set_stroke(width=3 + 6 * np.sin(PI * a)))


# ═════════════════════════════════════════════════════════════════════════════
def tablet(w=4.4, h=5.4):
    pts = [(-w / 2, h / 2 - 0.4), (-w / 2 + 0.4, h / 2), (w / 2 - 0.4, h / 2), (w / 2, h / 2 - 0.4),
           (w / 2, -h / 2), (-w / 2, -h / 2)]
    tb = low_poly(resample(pts, 0.55), EMERALD, seed=8, rings=2, jitter=0.06, dome=0.6)
    lines = VGroup(*[Line([-w / 2 + 0.5, y, 0], [w / 2 - 0.5, y, 0], color=GOLD, stroke_width=2,
                          stroke_opacity=0.45) for y in np.linspace(h / 2 - 0.8, -h / 2 + 0.6, 11)])
    return VGroup(tb, lines)


def block3(s):
    s.transition(None)
    tb = tablet().move_to([0, Y_VIS - 0.1, 0])
    s.run(s.hook("Lo que está arriba…", accents={"arriba…": GOLD}),
          LaggedStart(*[FadeIn(f, scale=0.3) for f in tb[0].family_members_with_points()],
                      lag_ratio=0.004), rt=1.6)
    s.run(s.hook("…es como lo que está abajo.", accents={"abajo.": GOLD}), Create(tb[1]), rt=1.2)
    s.run(s.caption("La Tabla Esmeralda.", size=72, accents={"esmeralda.": "#3FC98A"}), rt=0.8)
    orig = mono("ÁRABE · SIGLO VII · BREVÍSIMO Y CRÍPTICO", 40, CYAN).move_to([0, -2.35, 0])
    if orig.width > 7.8:
        orig.set(width=7.8)
    s.run(FadeIn(orig), Flash(tb.get_center(), color="#3FC98A", flash_radius=2.6, num_lines=20),
          rt=0.8)
    s.until(85.0, focus=tb)
    # El axioma: arriba / abajo en espejo
    up = serif("Como es arriba,", 80).move_to([0, 2.3, 0])
    down = serif("es abajo.", 80).move_to([0, -1.55, 0])
    mirror = Line([-3.8, 1.25, 0], [3.8, 1.25, 0], color=CYAN, stroke_width=3)
    reflect = up.copy().flip(RIGHT).set_opacity(0.18).move_to([0, 0.2, 0])
    s.swap([tb, orig], [s.drop_hook(), Create(mirror)], rt=0.8)
    s.run(AddLetters(up), rt=1.6)
    s.run(FadeIn(reflect), AddLetters(down), s.caption("El axioma hermético.", size=66,
                                                       font=FONT_SANS, accents={"hermético.": GOLD}),
          rt=1.6)
    upt, dnt = tri(0.45, [0, 3.45, 0], sw=4), tri(0.32, [0, -2.25, 0], inverted=True, sw=4)
    s.run(Create(upt), Create(dnt), rt=0.8)
    s.until(95.0, focus=VGroup(up, down))
    # La tabla se divide en tres
    tb2 = tablet().move_to([0, Y_VIS - 0.1, 0])
    s.swap([up, down, mirror, reflect, upt, dnt], [FadeIn(tb2)], rt=0.8)
    xs = tb2.get_left()[0], tb2.get_right()[0]
    thirds = [VGroup(*[f for f in tb2.family_members_with_points()
                       if xs[0] + (xs[1] - xs[0]) * k / 3 <= f.get_center()[0]
                       < xs[0] + (xs[1] - xs[0]) * (k + 1) / 3 + (1e-3 if k == 2 else 0)])
              for k in range(3)]
    s.run(thirds[0].animate.shift(LEFT * 0.7).rotate(0.06), thirds[2].animate.shift(RIGHT * 0.7)
          .rotate(-0.06), rt=1.2)
    tl = VGroup(*[mono(w, 42, c) for w, c in (("ALQUIMIA", GOLD), ("ASTROLOGÍA", CYAN),
                                              ("TEÚRGIA", RED_T))])
    for lab, x in zip(tl, (-2.75, 0, 2.75)):
        lab.move_to([x, 3.3, 0])
    s.run(LaggedStart(*[FadeIn(l, shift=UP * 0.3) for l in tl], lag_ratio=0.3),
          s.caption("Tres partes: alquimia, astrología, teúrgia.", font=FONT_SANS,
                    accents={"tres": GOLD}), rt=1.6)
    s.until(105.0, focus=tb2)


def AddLetters(text):
    return LaggedStart(*[FadeIn(ch, shift=UP * 0.2, scale=1.3) for ch in text], lag_ratio=0.08)


# ═════════════════════════════════════════════════════════════════════════════
def misbaha(r=2.2, center=(0, Y_VIS)):
    c = np.array([*center, 0])
    beads = VGroup()
    for k, a in enumerate(np.linspace(PI / 2 + 0.25, PI / 2 + TAU - 0.25, 33)):
        p = c + r * np.array([np.cos(a), np.sin(a) * 1.05, 0])
        b = Circle(radius=0.13, stroke_width=2, color=shade(GOLD, 1.2)).set_fill(GOLD, 0.85).move_to(p)
        beads.add(b)
    top = c + np.array([0, r * 1.05, 0])
    imam = Polygon(top + [0, 0.2, 0], top + [0.14, 0, 0], top + [0, -0.25, 0], top + [-0.14, 0, 0],
                   stroke_width=0).set_fill(CYAN, 1)
    tassel = VGroup(*[Line(top + [0, 0.2, 0], top + [dx, 0.85, 0], color=CYAN, stroke_width=3)
                      for dx in np.linspace(-0.2, 0.2, 5)])
    return VGroup(beads, imam, tassel)


def bridge(n=33, w=7.6, center=(0, Y_VIS)):
    c = np.array([*center, 0])
    aw = w / n
    deck = Line(c + [-w / 2, 0.35, 0], c + [w / 2, 0.35, 0], color=GOLD, stroke_width=5)
    arches = VGroup(*[Arc(radius=aw * 0.42, start_angle=0, angle=PI, color=GOLD, stroke_width=3)
                      .move_to(c + [-w / 2 + aw * (i + 0.5), 0.05, 0]) for i in range(n)])
    water = VGroup(*[Line(c + [-w / 2, -0.35 - 0.18 * i, 0], c + [w / 2, -0.35 - 0.18 * i, 0],
                          color=CYAN, stroke_width=2, stroke_opacity=0.3) for i in range(3)])
    return VGroup(deck, arches, water)


def risen(scale=1.0, center=ORIGIN):
    robe = [(0, 1.5), (0.35, 1.35), (0.42, 0.95), (1.5, 0.75), (1.55, 0.6), (0.7, 0.45),
            (0.9, -2.0), (-0.9, -2.0), (-0.7, 0.45), (-1.55, 0.6), (-1.5, 0.75), (-0.42, 0.95),
            (-0.35, 1.35)]
    body = low_poly(resample([(x * scale, y * scale) for x, y in robe], 0.4), BONE, seed=17,
                    rings=2, dome=0.6)
    halo = VGroup(*[Circle(radius=0.55 * scale * k, color=GOLD, stroke_width=3, stroke_opacity=o)
                    .move_to([0, 1.25 * scale, 0]) for k, o in ((1, 0.9), (1.4, 0.4), (1.9, 0.2))])
    rays = VGroup(*[Line([0, 1.25 * scale, 0], [3.2 * np.cos(a), 1.25 * scale + 3.2 * np.sin(a), 0],
                         color=GOLD, stroke_width=2, stroke_opacity=0.3)
                    for a in np.linspace(0, TAU, 33, endpoint=False)])
    g = VGroup(rays, halo, body).move_to(center)
    return g


def block4(s):
    s.transition(None)
    mb = misbaha()
    s.run(s.hook("Y entonces, el 3 se convierte en 33.", accents={"33.": GOLD}),
          LaggedStart(*[GrowFromCenter(b) for b in mb[0]], lag_ratio=0.06), rt=2.2)
    cnt = sans("33", 120, GOLD).move_to([0, Y_VIS, 0])
    s.run(FadeIn(mb[1:]), FadeIn(cnt, scale=1.6),
          s.caption("Islam: 33 cuentas en el dhikr.", font=FONT_SANS,
                    accents={"dhikr.": CYAN}), rt=1.2)
    dz = VGroup(*[mono(f"{w} ×33", 44, c) for w, c in (("TASBIH", GOLD), ("TAHMID", CYAN),
                                                       ("TAKBIR", BONE))]).arrange(DOWN, buff=0.12)
    dz.arrange(RIGHT, buff=0.35)
    if dz.width > 7.8:
        dz.set(width=7.8)
    dz.move_to([0, 3.95, 0])
    s.run(s.drop_hook(), LaggedStart(*[FadeIn(d, shift=DOWN * 0.2) for d in dz], lag_ratio=0.3),
          rt=1.0)
    hud = s.hud_add("beads")
    s.run(hud, rt=0.9)
    s.until(112.0, focus=mb)
    br = bridge()
    bl = mono("SI-O-SE-POL · ISFAHÁN", 50, CYAN).move_to([0, Y_VIS + 1.4, 0])
    s.swap([mb, cnt, dz], [Create(br[0]), FadeIn(bl)], rt=0.7)
    s.run(LaggedStart(*[Create(a) for a in br[1]], lag_ratio=0.08), FadeIn(br[2]),
          s.caption("Un puente de 33 arcos.", font=FONT_SANS, accents={"arcos.": GOLD}), rt=1.8)
    s.until(115.0, focus=br)
    # Gnosis cristiana: 33 años, 33 emanaciones
    rs = risen(1.0, [0, Y_VIS + 0.1, 0])
    n33 = sans("33", 110, GOLD).move_to([2.7, Y_VIS + 1.3, 0])
    s.swap([br, bl], [FadeIn(rs, shift=UP * 0.5)], rt=0.8)
    s.run(FadeIn(n33, scale=1.5), s.caption("Gnosis cristiana: los 33 años de Cristo.",
                                            accents={"cristo.": GOLD}), rt=1.2)
    s.until(119.6, focus=rs)
    dots = VGroup(*[Dot([3.4 * np.cos(a), Y_VIS + 3.0 * np.sin(a), 0], radius=0.07, color=CYAN)
                    for a in np.linspace(0, TAU, 33, endpoint=False)])
    one = Dot([0, Y_VIS + 1.35, 0], radius=0.16, color=GOLD)
    s.run(LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.03),
          s.caption("33 emanaciones: una sola Unidad.", font=FONT_SANS,
                    accents={"unidad.": GOLD}), rt=1.4)
    s.run(*[d.animate.move_to(one.get_center()).set_opacity(0) for d in dots], FadeIn(one, scale=3),
          rt=1.2)
    s.until(125.0, focus=rs)
    # Matemáticas: dos triángulos
    t1 = tri(1.6, [0, Y_VIS + 1.0, 0], sw=6)
    t2 = tri(1.6, [0, Y_VIS + 1.0, 0], inverted=True, sw=6).set_color(CYAN)
    s.swap([rs, n33, one], [Create(t1)], rt=0.7)
    hud = s.hud_add("star")
    s.run(Create(t2), hud, s.caption("Matemáticas: el 33,", font=FONT_SANS,
                                     accents={"33,": GOLD}), rt=1.2)
    facts = VGroup(sans("33 = 3 × 11", 66, GOLD),
                   mono("1 + 3 + 11 = 15 < 33 · defectivo", 40, BONE),
                   mono("semiprimo · libre de cuadrados", 40, BONE),
                   mono("repdigit · primo nº 33 = 137", 40, CYAN)).arrange(DOWN, buff=0.16)
    facts.move_to([0, -1.55, 0])
    for f in facts:
        if f.width > 7.8:
            f.set(width=7.8)
    s.run(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in facts], lag_ratio=0.3),
          s.caption("la unión de dos triángulos.", accents={"triángulos.": GOLD}, y=-3.65), rt=2.0)
    s.until(135.0, focus=VGroup(t1, t2))


# ═════════════════════════════════════════════════════════════════════════════
def scholar(color, seed, scale=0.9):
    pts = [(0, 1.7), (0.5, 1.6), (0.55, 1.35), (0.35, 1.25), (0.4, 0.9), (1.0, 0.6), (1.15, -2.0),
           (-1.15, -2.0), (-1.0, 0.6), (-0.4, 0.9), (-0.35, 1.25), (-0.55, 1.35), (-0.5, 1.6)]
    return low_poly(resample([(x * scale, y * scale) for x, y in pts], 0.4), color, seed=seed,
                    rings=2, dome=0.7)


def square_compass(h=2.0, center=ORIGIN):
    c, s = np.array(center), h / 4
    hinge = c + [0, 1.9 * s, 0]
    comp = VGroup(Line(hinge, c + [-1.7 * s, -1.6 * s, 0], color=GOLD, stroke_width=8),
                  Line(hinge, c + [1.7 * s, -1.6 * s, 0], color=GOLD, stroke_width=8),
                  Dot(hinge, radius=0.12 * s * 2, color=GOLD))
    sq = VGroup(Line(c + [0, -1.9 * s, 0], c + [-1.95 * s, 0.05 * s, 0], color=BONE, stroke_width=10),
                Line(c + [0, -1.9 * s, 0], c + [1.95 * s, 0.05 * s, 0], color=BONE, stroke_width=10))
    return VGroup(sq, comp)


def block5(s):
    s.transition(None)
    fi = scholar("#5A3A3A", 3).move_to([-1.7, Y_VIS - 0.1, 0])
    pi = scholar("#3A4A5A", 4).move_to([1.7, Y_VIS - 0.1, 0])
    names = VGroup(mono("FICINO", 50, GOLD).next_to(fi, DOWN, buff=0.2),
                   mono("PICO DELLA MIRANDOLA", 40, GOLD).next_to(pi, DOWN, buff=0.2))
    if names[1].get_right()[0] > 4.0:
        names[1].shift(LEFT * (names[1].get_right()[0] - 4.0))
    s.run(s.hook("Los sabios del Renacimiento lo sabían.", accents={"renacimiento": GOLD}),
          FadeIn(fi, shift=RIGHT * 0.5), FadeIn(pi, shift=LEFT * 0.5), rt=1.6)
    s.run(FadeIn(names), s.caption("Prisca Theologia: la revelación primordial.",
                                   accents={"prisca": GOLD, "theologia:": GOLD}), rt=1.2)
    s.focus = VGroup(fi, pi)
    s.until(145.0)
    # Escalera de 33 grados
    steps = VGroup()
    for i in range(33):
        x0, y0 = -3.6 + i * 0.21, -2.0 + i * 0.13
        steps.add(Polygon([x0, y0, 0], [x0 + 0.21, y0, 0], [x0 + 0.21, y0 + 0.13, 0],
                          [x0, y0 + 0.13, 0], stroke_width=1.5, stroke_color=GOLD)
                  .set_fill(shade(GOLD, 0.3 + 0.7 * i / 33), 1))
    sc = square_compass(1.6, [3.0, 3.0 - 0.35, 0])
    s.swap([fi, pi, names], [s.drop_hook()], rt=0.5)
    counter = {"n": 0}
    num = sans("1", 110, GOLD).move_to([-2.4, 2.9, 0])
    s.add(num)

    def upd(m, a):
        n = max(1, int(round(a * 33)))
        if n != counter["n"]:
            counter["n"] = n
            m.become(sans(str(n), 110, GOLD).move_to([-2.4, 2.9, 0]))
    s.run(LaggedStart(*[FadeIn(st, shift=UP * 0.1) for st in steps], lag_ratio=0.08),
          UpdateFromAlphaFunc(num, upd),
          s.caption("Masonería: 33 grados hacia la maestría.", font=FONT_SANS,
                    accents={"maestría.": GOLD}), rt=2.6)
    s.run(Create(sc, lag_ratio=0.3), rt=0.8)
    extra = VGroup(mono("REAA · GRADO 33", 46, GOLD), mono("Consejo Supremo: máx. 33", 42, CYAN),
                   mono("32 sendas + el gran círculo", 42, BONE)).arrange(DOWN, buff=0.14)
    if extra.width > 4.4:
        extra.set(width=4.4)
    extra.move_to([1.75, -1.9, 0])
    s.run(LaggedStart(*[FadeIn(e, shift=LEFT * 0.3) for e in extra], lag_ratio=0.35), rt=1.4)
    s.until(155.0, focus=steps)
    # La cadena de la sabiduría
    chain_names = ["HERMES", "ZOROASTRO", "ORFEO", "PITÁGORAS", "FICINO"]
    nodes = VGroup()
    for i, n in enumerate(chain_names):
        y = 3.0 - i * 1.15
        box = RoundedRectangle(width=4.2, height=0.8, corner_radius=0.15, stroke_width=3,
                               color=GOLD if i in (0, 4) else BONE).set_fill(INK, 0.9)
        nodes.add(VGroup(box, mono(n, 50, GOLD if i in (0, 4) else BONE)).move_to([0, y, 0]))
    links = VGroup(*[Arrow(nodes[i].get_bottom(), nodes[i + 1].get_top(), buff=0.05,
                           color=CYAN, stroke_width=5, max_tip_length_to_length_ratio=0.5)
                     for i in range(4)])
    s.swap([steps, sc, num, extra], [FadeIn(nodes[0], scale=1.3)], rt=0.6)
    s.run(LaggedStart(*[AnimationGroup(Create(l), FadeIn(n, shift=DOWN * 0.3))
                        for l, n in zip(links, nodes[1:])], lag_ratio=0.5),
          s.caption("La cadena de la sabiduría.", accents={"sabiduría.": GOLD}), rt=3.0)
    s.until(165.0, focus=nodes)


# ═════════════════════════════════════════════════════════════════════════════
def block6(s):
    s.transition(None)
    big = seal_layers(r=2.0, center=[0, Y_VIS + 0.3, 0], sw=7)
    seal = VGroup(*[big[k] for k in HermesScene.LAYERS])
    s.run(LaggedStart(*[Create(big[k]) for k in HermesScene.LAYERS], lag_ratio=0.25),
          s.caption("3. 33. Hermes.", size=80, font=FONT_SANS,
                    accents={"3.": GOLD, "33.": GOLD, "hermes.": GOLD}), rt=2.0)
    seal.add_updater(lambda m, dt: m.rotate(0.3 * dt, about_point=[0, Y_VIS + 0.3, 0]))
    s.until(168.6, focus=seal)
    seal.clear_updaters()
    n33 = stylized_33(3.6).move_to([0, Y_VIS + 0.3, 0])
    s.run(Transform(seal, n33), s.caption("Una pregunta.", size=80, accents={"pregunta.": GOLD}),
          rt=1.4)
    st = stamp("HERMES", RED, 120, angle=-0.08).move_to([0, Y_VIS - 2.0, 0]).set_z_index(20)
    s.run(FadeIn(st, scale=2.2), rt=0.4)
    s.run(Flash(st.get_center(), color=GOLD, flash_radius=2.8, num_lines=24), rt=0.6)
    s.until(172.0, focus=st)
    banner = RoundedRectangle(width=8.3, height=1.75, corner_radius=0.2, stroke_width=3,
                              color=GOLD).set_fill(INK, 0.95).move_to([0, -2.6, 0])
    cta = kinetic_text("Si quieres que analice el Corpus Hermeticum, sígueme.", size=52,
                       font=FONT_SANS, accents={"corpus": GOLD, "hermeticum,": GOLD,
                                                "sígueme.": GOLD}).move_to(banner)
    arrow = Arrow([2.6, 3.3, 0], [3.7, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    bub = RoundedRectangle(width=1.25, height=0.95, corner_radius=0.25, color=BONE,
                           stroke_width=4).set_fill(INK, 0.9).move_to([3.25, -4.15, 0])
    dots = VGroup(*[Dot([3.25 + x, -4.15, 0], radius=0.07, color=CYAN) for x in (-0.3, 0, 0.3)])
    ask = kinetic_text("¿Crees que el 33 es solo un número?", size=48, font=FONT_SERIF,
                       accents={"33": GOLD}, max_width=6.0)
    ask.next_to(bub, LEFT, buff=0.3)
    s.run(s.drop_caption(), VGroup(seal, st).animate.scale(0.72).shift(UP * 1.2), FadeIn(banner),
          reveal_words(cta, 1.2), rt=1.3)
    arrow.add_updater(blink_updater(7))
    s.add(arrow)
    s.run(FadeIn(VGroup(bub, dots), scale=0.6), reveal_words(ask, 1.1), rt=1.2)
    s.until(180.0, focus=VGroup(seal, st))


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


class _Block(HermesScene):
    INDEX = 0

    def construct(self):
        self.k_setup(self.INDEX)
        BLOCKS[self.INDEX](self)
        assert self.frames == ENDS[self.INDEX] * FPS, (self.INDEX, self.frames)


for _i in range(7):
    globals()[f"Block{_i}"] = type(f"Block{_i}", (_Block,), {"INDEX": _i})


class FullVideo(HermesScene):
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
