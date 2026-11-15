"""
main.py — «EL SOL NEGRO: THULE, VRIL Y LA BASE 211»
Vertical 9:16 · 1080×1920 · 30 fps · 180 s exactos · Manim CE · estilo low-poly 3D oscuro.

    manim -qh --disable_caching main.py FullVideo
    KABALA_PREVIEW=1 manim --disable_caching main.py Block2      # vista previa 540×960

Reutiliza el motor de ../kabala_video/utils.py (reloj exacto por frames, texto
cinético palabra a palabra, glitch, wipe). La geometría está en poly.py.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kabala_video"))
sys.path.insert(0, HERE)

import utils as K  # noqa: E402  (fija 1080×1920 @ 30 fps)
from manim import (  # noqa: E402
    BOLD, DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP,
    AnimationGroup, Arrow, Create, Dot, FadeIn, FadeOut, Flash, LaggedStart, Line,
    Polygon, RoundedRectangle, Text, Transform, UpdateFromAlphaFunc, ValueTracker, VGroup,
    always_redraw, config, smooth,
)
from poly import (  # noqa: E402
    ANTARCTICA, BLOOD, BONE, CYAN, GERMANY, GOLD, ICE, INK, MUNICH, MYSTIC, NEUSCHWABENLAND,
    STEEL, black_sun, hammer, haunebu, low_poly, medium, ngon, plane, recolor, resample,
    shade, ship, stamp, thule_island, victalen,
)
from utils import (  # noqa: E402
    FONT_MONO, FONT_SANS, FONT_SERIF, FPS, KabalaScene, blink_updater, kinetic_text, px,
    reveal_words,
)

# Identidad visual de este video sobre el motor compartido
config.background_color = INK
K.BG_IN, K.BG_OUT, K.PARCHMENT = "#100B1A", "#050508", "#0B0912"
RED = "#C0262D"            # rojo legible para texto (el #8B0000 se usa en superficies)
Y_VIS = 0.35
STARTS = [0, 15, 45, 75, 105, 135, 165]
ENDS = [15, 45, 75, 105, 135, 165, 180]


def mono(t, size=48, color=BONE):
    return Text(t, font=FONT_MONO, font_size=px(size), weight=BOLD, color=color,
                disable_ligatures=True)


def store_opacity(mob):
    for sm in mob.family_members_with_points():
        sm.fo0, sm.so0 = sm.get_fill_opacity(), sm.get_stroke_opacity()
    return mob


def set_alpha(mob, a):
    for sm in mob.family_members_with_points():
        sm.set_fill(opacity=getattr(sm, "fo0", 1) * a)
        sm.set_stroke(opacity=getattr(sm, "so0", 1) * a)
    return mob


def build_in(mob, rt_lag=0.02):
    """Aparición cara a cara de una malla low-poly."""
    faces = [sm for sm in mob.family_members_with_points()]
    return LaggedStart(*[FadeIn(f, scale=0.4) for f in faces], lag_ratio=rt_lag)


def shatter(mob, rng, dist=2.2):
    """Las caras salen despedidas y se apagan."""
    anims = []
    c = mob.get_center()
    for f in mob.family_members_with_points():
        d = f.get_center() - c
        d = d / (np.linalg.norm(d) + 1e-6) + rng.normal(0, 0.4, 3) * np.array([1, 1, 0])
        anims.append(f.animate.shift(d * dist * rng.uniform(0.5, 1.2))
                     .rotate(rng.uniform(-2, 2)).set_opacity(0))
    return LaggedStart(*anims, lag_ratio=0.002)


def starfield(n=90, seed=3):
    rng = np.random.default_rng(seed)
    g = VGroup()
    for _ in range(n):
        r = rng.uniform(0.012, 0.035)
        p = Polygon(*[[r * np.cos(a), r * np.sin(a), 0] for a in (0, 2.1, 4.2)], stroke_width=0)
        p.set_fill(BONE, rng.uniform(0.2, 0.8)).move_to([rng.uniform(-4.5, 4.5), rng.uniform(-8, 8), 0])
        g.add(p)
    g.set_z_index(-40)
    return g


class ThuleScene(KabalaScene):
    def k_setup(self, block_index: int = 0):
        self.frames = STARTS[block_index] * FPS
        self.rng = np.random.default_rng(211 + block_index)
        self.bg = K.make_background(seed=17)
        self.dust = K.Dust(n=60, seed=9)
        for d in self.dust:
            d.set_color(CYAN if np.random.random() < 0.3 else BONE)
        self.add(self.bg, self.dust)
        self.hook_mob = self.cap_mob = self.src_mob = None
        self.chip = None
        self.focus = Dot(radius=0.001).set_opacity(0)
        # Sol Negro recurrente (fondo): gira siempre, se enciende bloque a bloque
        self.bsun = black_sun(r0=0.9, r1=3.7, color=MYSTIC, seed=40).move_to([0, Y_VIS, 0])
        store_opacity(self.bsun)
        set_alpha(self.bsun, 0.22)
        self.bsun.set_z_index(-30)
        self.bsun.add_updater(lambda m, dt: m.rotate(0.06 * dt, about_point=[0, Y_VIS, 0]))
        self.lit = 0
        self.hud = self.bsun          # el motor protege self.hud de los wipes
        if block_index > 0:
            self.light_runes(2 * block_index, now=True)
            self.add(self.bsun)

    def stage(self):
        keep = {id(self.bg), id(self.dust), id(self.bsun)}
        return [m for m in self.mobjects if id(m) not in keep]

    def light_runes(self, upto, now=False):
        anims = []
        for k in range(self.lit, min(upto, 12)):
            r = self.bsun.runes[k]
            if now:
                recolor(r, BLOOD, 0.1)
                set_alpha(r, 0.32)
            else:
                anims.append(UpdateFromAlphaFunc(
                    r, lambda m, a: set_alpha(recolor(m, BLOOD, 0.1), 0.22 + 0.1 * a)))
        self.lit = max(self.lit, min(upto, 12))
        return anims

    def transition(self, block):
        super().transition(None)
        a = self.light_runes(2 * block)
        if a:
            self.run(*a, rt=0.5)

    def legend_chip(self):
        t = mono("SEGÚN LA LEYENDA", 40, INK)
        box = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.3, corner_radius=0.1,
                               stroke_width=0).set_fill(GOLD, 1)
        chip = VGroup(box, t.move_to(box)).move_to([0, 5.55, 0]).set_z_index(70)
        self.chip = chip
        return FadeIn(chip, shift=DOWN * 0.2)

    def swap(self, old, new_anims, rt=0.7):
        outs = [FadeOut(o, scale=0.85) for o in old if o is not None]
        self.run(*outs, *new_anims, rt=rt)


# ═════════════════════════════════════════════════════════════════════════════
def move_disc(h, delta):
    """Desplaza un disco que se reconstruye cada frame (mueve su centro 3D)."""
    parts = [h.body, *h.pods]
    c0 = [p.center_pt.copy() for p in parts]

    def f(m, a):
        for p, c in zip(parts, c0):
            p.center_pt = c + np.array(delta) * a
    return UpdateFromAlphaFunc(h, f, suspend_mobject_updating=False)


def block0(s):
    sun = black_sun(color=CYAN, seed=1).move_to([0, Y_VIS, 0])
    s.run(LaggedStart(*[FadeIn(r, scale=0.3, shift=r.dir * -0.6) for r in sun.runes],
                      lag_ratio=0.12), FadeIn(sun.disc), Create(sun.ring, lag_ratio=0.02),
          s.caption("El ocultismo no era un mito.", size=62, rt=1.2), rt=1.6)
    s.focus = sun
    s.run(s.caption("Era un arma.", size=80, accents={"arma.": RED}, rt=0.6), rt=0.8)
    s.until(3.0)
    st = sun.copy()

    def turn_red(m, a):
        m.become(st)
        recolor(m, interpolate(CYAN, BLOOD, a))
        m.rotate(a * PI / 3, about_point=[0, Y_VIS, 0])

    s.run(UpdateFromAlphaFunc(sun, turn_red, rate_func=smooth),
          s.caption("Thule. Vril. Sol Negro.", size=66, font=FONT_SANS,
                    accents={"thule.": GOLD, "vril.": GOLD, "negro.": RED}, rt=1.2), rt=2.4)
    s.until(5.6)
    s.run(s.caption("Una Alemania que buscaba dioses en el hielo.",
                    accents={"dioses": GOLD, "hielo.": CYAN}), rt=1.3)
    s.until(8.0)
    # El sol se hunde en el fondo; emergen las cinco médiums
    s.add(s.bsun)
    meds = VGroup(*[medium(seed=i, scale=0.42) for i in range(5)])
    meds.arrange(RIGHT, buff=0.15).move_to([0, Y_VIS - 0.2, 0])
    meds[2].scale(1.25).set_z_index(2)
    s.run(FadeOut(sun, scale=1.6), UpdateFromAlphaFunc(s.bsun, lambda m, a: set_alpha(m, 0.22 * a)),
          LaggedStart(*[FadeIn(m, shift=UP * 0.8) for m in meds], lag_ratio=0.15),
          s.caption("Esto es lo que los archivos desclasificados ocultan."), rt=1.6)
    s.run(*[m.eyes.animate.set_fill(GOLD, 1) for m in meds], rt=0.4)
    s.focus = meds
    s.until(12.0)
    # CTA de apertura
    ribbon = RoundedRectangle(width=8.3, height=1.5, corner_radius=0.2, stroke_width=3,
                              color=GOLD).set_fill(INK, 0.95).move_to([0, -3.15, 0])
    a1 = kinetic_text("Quédate: la base secreta", size=60, font=FONT_SANS,
                      accents={"quédate:": GOLD}).move_to(ribbon)
    arrow = Arrow([2.4, 3.2, 0], [3.7, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    arrow.add_updater(blink_updater(7))
    s.run(s.drop_caption(), FadeIn(ribbon, shift=UP * 0.4), reveal_words(a1, 0.6), rt=0.8)
    s.add(arrow)
    s.until(13.5, focus=meds)
    a2 = kinetic_text("en la Antártida aparece al final.", size=58, font=FONT_SANS,
                      accents={"antártida": CYAN, "final.": GOLD}).move_to(ribbon)
    s.run(FadeOut(a1, shift=UP * 0.2), rt=0.2)
    s.run(reveal_words(a2, 0.7), rt=0.7)
    s.until(15.0, focus=meds)


def interpolate(c1, c2, a):
    from manim import ManimColor, interpolate_color
    return interpolate_color(ManimColor(c1), ManimColor(c2), a)


# ═════════════════════════════════════════════════════════════════════════════
def block1(s):
    s.transition(1)
    hm = hammer().scale(0.9).move_to([0, Y_VIS + 0.2, 0])
    s.run(s.hook("1918. Múnich. Nace una sociedad secreta.", accents={"secreta.": GOLD}),
          build_in(hm, 0.004), rt=2.0)
    s.focus = hm
    vt = ValueTracker(0)
    num = always_redraw(lambda: Text(f"{int(vt.get_value()):,}".replace(",", "."),
                                     font=FONT_SANS, font_size=px(150), weight=BOLD,
                                     color=CYAN).move_to([0, -1.75, 0]))
    s.add(num)
    s.run(vt.animate.set_value(2000), s.caption("Sociedad Thule: 2.000 miembros.",
                                                font=FONT_SANS, accents={"thule:": GOLD}),
          rt=2.0)
    s.until(25.0)
    num.clear_updaters()
    # Mapa de Alemania + Múnich
    de = low_poly(resample(GERMANY, 0.35), "#2A3A52", seed=8, rings=2, dome=0.5)
    de.scale(1.35).move_to([0, Y_VIS, 0])
    mx, my = MUNICH
    c = de.get_center()
    pin_pt = c + np.array([mx, my, 0]) * 1.35 + np.array([0, 0.12, 0])
    pin = VGroup(Polygon(pin_pt + [0, 0, 0], pin_pt + [-0.22, 0.6, 0], pin_pt + [0, 0.75, 0],
                         stroke_width=0).set_fill(shade(GOLD, 1.1), 1),
                 Polygon(pin_pt + [0, 0, 0], pin_pt + [0.22, 0.6, 0], pin_pt + [0, 0.75, 0],
                         stroke_width=0).set_fill(shade(GOLD, 0.6), 1))
    lab = mono("MÚNICH · 1918", 50, GOLD).next_to(pin, DOWN, buff=0.25)
    if lab.get_right()[0] > 3.9:
        lab.shift(LEFT * (lab.get_right()[0] - 3.9))
    s.swap([hm, num], [build_in(de, 0.003)], rt=1.4)
    s.run(FadeIn(pin, shift=DOWN * 0.6), FadeIn(lab), s.drop_hook(),
          s.caption("Rudolf von Sebottendorf. Ocultismo y racismo.",
                    accents={"sebottendorf.": GOLD, "racismo.": RED}), rt=1.3)
    s.run(Flash(pin_pt, color=GOLD, flash_radius=0.6, num_lines=14), rt=0.6)
    s.focus = de
    s.until(35.0)
    # La isla de Thule emerge del mar
    sea = VGroup()
    for i in range(14):
        x0 = -4.6 + i * 0.68
        for j in range(3):
            y0 = -1.2 - j * 0.45
            sea.add(Polygon([x0, y0, 0], [x0 + 0.68, y0 + 0.05, 0], [x0 + 0.3, y0 - 0.45, 0],
                            stroke_width=1, stroke_color=CYAN, stroke_opacity=0.25)
                    .set_fill(shade("#123047", 0.5 + 0.15 * ((i + j) % 3)), 1))
    isl = low_poly(thule_island(), ICE, seed=5, rings=2, jitter=0.12, dome=1.0)
    isl.scale(0.95).move_to([0, Y_VIS + 0.4, 0])
    tl = mono("THULE", 64, GOLD).next_to(isl, UP, buff=0.25)
    s.swap([de, pin, lab], [FadeIn(sea, shift=UP * 0.3)], rt=0.8)
    s.run(FadeIn(isl, shift=UP * 1.2), FadeIn(tl),
          s.caption("Buscaban el origen de la raza aria.", accents={"aria.": GOLD}), rt=1.6)
    s.focus = isl
    s.until(40.5)
    atl = mono("¿ATLÁNTIDA?", 52, CYAN).next_to(isl, DOWN, buff=0.15).shift(RIGHT * 1.2)
    s.run(FadeIn(atl), s.caption("En Thule o en la Atlántida.",
                                 accents={"thule": GOLD, "atlántida.": CYAN}), rt=1.2)
    s.until(45.0, focus=isl)


# ═════════════════════════════════════════════════════════════════════════════
def cuneiform(rng, n=18):
    g = VGroup()
    for _ in range(n):
        w = rng.uniform(0.12, 0.3)
        t = Polygon([0, 0, 0], [w, 0.05, 0], [w * 0.2, -w * 0.9, 0], stroke_width=0)
        t.set_fill(shade(GOLD, rng.uniform(0.6, 1.2)), 1).rotate(rng.uniform(0, TAU))
        g.add(t)
    return g


def block2(s):
    s.transition(2)
    m = medium(seed=21, scale=1.15).move_to([0, Y_VIS - 0.3, 0])
    s.run(s.hook("1919. Una médium empieza a escribir en sumerio.",
                 accents={"sumerio.": GOLD}), s.legend_chip(), build_in(m, 0.004), rt=2.0)
    s.run(m.eyes.animate.set_fill(GOLD, 1).scale(1.4), rt=0.4)
    glyphs = cuneiform(s.rng).set_z_index(5)
    head = m.eyes.get_center()
    for gph in glyphs:
        gph.move_to(head)
    s.run(LaggedStart(*[g.animate.move_to([s.rng.uniform(-3.6, 3.6), s.rng.uniform(1.5, 3.2), 0])
                        for g in glyphs], lag_ratio=0.06),
          s.caption("Maria Orsic. Vril Society.", font=FONT_SANS,
                    accents={"orsic.": GOLD, "vril": MYSTIC}), rt=1.6)
    names = VGroup(mono("MARIA ORSIC", 56, GOLD),
                   mono("SIGRUN · TRAUTE · GUDRUN · HEIKE", 40, BONE)).arrange(DOWN, buff=0.15)
    names.move_to([0, -1.95, 0])
    s.run(s.drop_hook(), FadeIn(names, shift=UP * 0.2), rt=0.6)
    s.focus = m
    s.until(55.0)
    # La nave: primero alambre, luego sólida; Aldebarán al fondo
    star = low_poly([(0.5 * np.cos(a) * (1 if i % 2 == 0 else 0.42),
                      0.5 * np.sin(a) * (1 if i % 2 == 0 else 0.42))
                     for i, a in enumerate(np.linspace(0, TAU, 16, endpoint=False))],
                    "#E07B39", seed=2, rings=1).move_to([2.9, 3.0, 0])
    al = mono("ALDEBARÁN", 46, "#E07B39").next_to(star, DOWN, buff=0.15)
    wire = haunebu(0.95, center=[0, Y_VIS - 0.4, 0], wire=True)
    solid = haunebu(0.95, center=[0, Y_VIS - 0.4, 0])
    beam = VGroup(*[Dot([2.9 - 2.9 * t, 3.0 - (3.4) * t, 0], radius=0.035, color="#E07B39")
                    for t in np.linspace(0.05, 0.95, 14)])
    s.swap([m, glyphs, names], [build_in(star), FadeIn(al)], rt=0.8)
    s.run(LaggedStart(*[FadeIn(d, scale=2) for d in beam], lag_ratio=0.1),
          Create(wire, lag_ratio=0.01),
          s.caption("Transmisiones de Aldebarán: 64 años luz.", font=FONT_SANS,
                    accents={"aldebarán:": "#E07B39"}), rt=2.4)
    s.run(FadeOut(wire), FadeIn(solid), FadeOut(beam), rt=0.8)
    s.focus = solid
    s.until(65.0)
    # La nave gira: instrucciones para propulsión antigravitatoria
    for part in [solid.body, *solid.pods]:
        part.add_updater(part.spin_updater(0.9))
    rings = VGroup(*[Polygon(*[[r * np.cos(a), -1.6 + 0.25 * r * np.sin(a) + Y_VIS, 0]
                               for a in np.linspace(0, TAU, 12, endpoint=False)],
                             stroke_width=2, stroke_color=CYAN, stroke_opacity=0.5)
                     for r in (1.0, 1.6, 2.2)])
    s.run(Create(rings), s.caption("Instrucciones para una propulsión antigravitatoria.",
                                   accents={"antigravitatoria.": CYAN}), rt=1.4)
    tags = VGroup(mono("HAUNEBU", 52, GOLD), mono("·", 52, BONE), mono("VRIL", 52, MYSTIC))
    tags.arrange(RIGHT, buff=0.25).move_to([0, 3.1, 0])
    s.run(move_disc(solid, UP * 0.35), rings.animate.scale(1.15).set_stroke(opacity=0.2),
          FadeIn(tags), FadeOut(VGroup(star, al)), rt=1.2)
    s.until(75.0, focus=rings)
    for part in [solid.body, *solid.pods]:
        part.clear_updaters()


# ═════════════════════════════════════════════════════════════════════════════
def block3(s):
    s.transition(3)
    sun = black_sun(color=GOLD, seed=7).move_to([0, Y_VIS, 0])
    floor = VGroup()
    for i in range(-6, 7):
        for j in range(5):
            y = -2.4 - j * 0.42
            w = 0.7 + j * 0.12
            p = Polygon([i * w, y, 0], [(i + 1) * w, y, 0], [(i + 1) * (w + 0.12), y - 0.42, 0],
                        [i * (w + 0.12), y - 0.42, 0], stroke_width=1, stroke_color=GOLD,
                        stroke_opacity=0.2)
            floor.add(p.set_fill(shade("#3A3328", 0.4 + 0.2 * ((i + j) % 2)), 1))
    s.run(s.hook("Himmler lo hizo esculpir en el suelo.", accents={"suelo.": GOLD}),
          FadeIn(floor, shift=UP * 0.3), FadeIn(sun.ring), FadeIn(sun.disc, scale=0.3), rt=1.5)
    s.run(LaggedStart(*[build_in(r, 0.01) for r in sun.runes], lag_ratio=0.18),
          s.caption("Wewelsburg: el centro del culto SS.",
                    accents={"wewelsburg:": GOLD}), rt=3.5)
    s.focus = sun
    s.until(85.0)
    # Las 12 runas se encienden una a una
    cnt = VGroup()
    s.run(s.drop_hook(), s.caption("12 runas Sig. El sol de los arios.", font=FONT_SANS,
                                   accents={"sig.": GOLD}), rt=1.2)
    for k, r in enumerate(sun.runes):
        n = Text(f"{k + 1:02d}", font=FONT_MONO, font_size=px(110), weight=BOLD,
                 color=CYAN).move_to([0, 3.6, 0])
        anims = [UpdateFromAlphaFunc(r, lambda m, a: recolor(m, GOLD, 0.45 * a)),
                 Flash(r.get_center(), color=GOLD, flash_radius=0.5, num_lines=8)]
        anims.append(FadeOut(cnt) if len(cnt) else FadeIn(n))
        if len(cnt):
            anims.append(FadeIn(n))
        s.run(*anims, rt=0.55)
        cnt = n
    s.until(95.0, focus=sun)
    # El símbolo se fragmenta y las piezas flotan
    rng = s.rng
    drift = []
    for r in sun.runes:
        d = r.dir * rng.uniform(0.6, 1.3) + np.array([rng.normal(0, 0.2), rng.normal(0, 0.2), 0])
        drift.append(r.animate.shift(d).rotate(rng.uniform(-0.8, 0.8)))
    s.run(FadeOut(cnt), *drift, sun.ring.animate.scale(1.12).set_opacity(0.3),
          s.caption("Un símbolo de renacimiento. Y de muerte.", accents={"muerte.": RED}),
          UpdateFromAlphaFunc(sun.runes, lambda m, a: recolor(m, interpolate(GOLD, BLOOD, a))),
          rt=3.0)
    for r in sun.runes:
        r.add_updater(lambda m, dt, w=rng.uniform(-0.3, 0.3): m.rotate(w * dt))
    s.until(105.0, focus=sun.disc)


# ═════════════════════════════════════════════════════════════════════════════
def antarctica():
    a = low_poly(resample(ANTARCTICA, 0.3), ICE, seed=12, rings=3, jitter=0.1, dome=0.9)
    return a.scale(1.15).move_to([0.3, Y_VIS - 0.45, 0])


def block4(s):
    s.transition(4)
    ice = antarctica()
    s.run(s.hook("1945. Los nazis huyen al hielo.", accents={"hielo.": CYAN}), s.legend_chip(),
          build_in(ice, 0.002), rt=2.2)
    c = ice.get_center()
    p = c + np.array([*NEUSCHWABENLAND, 0]) * 1.15
    dome = haunebu(0.35, center=p + np.array([0, -0.1, 0]), wire=True)
    pin = Polygon(p + [0, 0.15, 0], p + [-0.2, 0.8, 0], p + [0.2, 0.8, 0], stroke_width=0)
    pin.set_fill(RED, 1)
    lab = mono("BASE 211", 60, RED).next_to(pin, RIGHT, buff=0.2).shift(UP * 0.3)
    s.run(FadeIn(pin, shift=DOWN * 0.5), Create(dome, lag_ratio=0.01), FadeIn(lab),
          s.caption("Base 211. Nueva Suabia.", font=FONT_SANS,
                    accents={"211.": RED, "suabia.": CYAN}), rt=1.6)
    pulse = VGroup(*[Polygon(*[p + np.array([r * np.cos(a), 0.35 * r * np.sin(a), 0])
                               for a in np.linspace(0, TAU, 10, endpoint=False)],
                             stroke_width=3, stroke_color=RED, stroke_opacity=0.6)
                     for r in (0.4, 0.8, 1.2)])
    s.run(LaggedStart(*[FadeIn(q, scale=0.3) for q in pulse], lag_ratio=0.3), rt=1.0)
    s.focus = ice
    s.until(115.0)
    # Operación Highjump: 13 barcos
    fleet = VGroup(*[ship().scale(0.2) for _ in range(13)])
    fleet.arrange_in_grid(rows=3, cols=5, buff=(0.25, 0.45)).move_to([0, Y_VIS + 0.6, 0])
    big = ship().scale(0.7).move_to([-6, -1.3, 0])
    yr = Text("1947", font=FONT_SANS, font_size=px(150), weight=BOLD, color=GOLD).move_to([0, 3.35, 0])
    s.swap([ice, dome, pin, lab, pulse], [FadeIn(yr, shift=DOWN * 0.3), s.drop_hook()], rt=0.6)
    s.run(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.8) for f in fleet], lag_ratio=0.12),
          big.animate.move_to([0, -1.3, 0]),
          s.caption("1947: Operación Highjump. 13 barcos, 4.000 hombres.", font=FONT_SANS,
                    accents={"highjump.": GOLD}), rt=2.6)
    s.focus = fleet
    s.until(125.0)
    # Byrd sobrevuela la Antártida
    ice2 = antarctica()
    pl = plane().scale(0.55).rotate(-0.6).move_to([-4.2, -2.4, 0])
    shadow = pl.copy().set_fill(INK, 0.45).set_stroke(width=0).shift(DOWN * 0.45 + RIGHT * 0.3)
    s.swap([fleet, big, yr], [FadeIn(ice2)], rt=0.6)
    s.run(pl.animate.move_to([3.8, 3.0, 0]), shadow.animate.move_to([4.1, 2.55, 0]),
          s.caption("Almirante Richard Byrd.", accents={"byrd.": GOLD}), rt=4.0)
    s.run(s.caption("¿Destruir la base o enfrentarse a ella?", accents={"destruir": RED}),
          rt=1.2)
    s.until(135.0, focus=ice2)


# ═════════════════════════════════════════════════════════════════════════════
def block5(s):
    s.transition(5)
    stars = starfield()
    ships = VGroup(haunebu(0.55, center=[-2.3, 2.3, 0], tilt=0.35),
                   haunebu(0.95, center=[0.6, Y_VIS - 0.1, 0], tilt=0.28),
                   haunebu(0.7, center=[2.2, -1.9, 0], tilt=0.4))
    s.add(stars)
    s.run(s.hook("Discos de 40 metros. 6.000 km/h."), s.legend_chip(),
          LaggedStart(*[FadeIn(h, shift=LEFT * 1.5) for h in ships], lag_ratio=0.3), rt=1.8)
    for i, h in enumerate(ships):
        for part in [h.body, *h.pods]:
            part.add_updater(part.spin_updater(0.6 + 0.3 * i))
    s.run(s.caption("Haunebu: de 25 a 40 metros.", font=FONT_SANS), rt=1.0)
    s.until(140.0, focus=stars)
    lines = VGroup(*[Line([x, y, 0], [x - 2.5, y, 0], stroke_width=3, color=CYAN,
                          stroke_opacity=0.6) for x, y in
                     [(-0.6, 0.4), (-0.4, -0.2), (-0.8, 0.8), (-0.5, 1.1), (-0.7, -0.5)]])
    s.run(s.drop_hook(), Create(lines, lag_ratio=0.1), move_disc(ships[1], RIGHT * 0.5),
          s.caption("Haunebu-II: 6.000 km/h.", font=FONT_SANS, size=66,
                    accents={"haunebu-ii:": GOLD}), rt=1.2)
    s.until(145.0, focus=stars)
    # Blindaje Victalen
    for h in ships:
        for part in [h.body, *h.pods]:
            part.clear_updaters()
    plate = victalen().move_to([0, Y_VIS, 0])

    def shimmer(m, dt):
        m.t_ = getattr(m, "t_", 0) + dt
        for t in m:
            t.set_fill(opacity=0.45 + 0.4 * (0.5 + 0.5 * np.sin(m.t_ * 2.2 + t.ph)))

    s.swap([ships, lines], [LaggedStart(*[FadeIn(t, scale=0.2) for t in plate], lag_ratio=0.002)],
           rt=1.6)
    plate.add_updater(shimmer)
    lab = mono("VICTALEN", 72, CYAN).move_to([0, 3.45, 0])
    s.run(FadeIn(lab), s.caption("Blindaje «Victalen»: humo congelado.",
                                 accents={"«victalen»:": CYAN}), rt=1.2)
    s.until(155.0, focus=stars)
    plate.clear_updaters()
    # Las naves se desintegran en partículas
    disc = haunebu(1.0, center=[0, Y_VIS, 0])
    s.swap([plate, lab], [FadeIn(disc, scale=0.7)], rt=0.8)
    s.run(shatter(disc, s.rng),
          s.caption("Tecnología de otro mundo. O de otro tiempo.",
                    accents={"mundo.": CYAN, "tiempo.": GOLD}), rt=3.0)
    s.until(165.0, focus=stars)


# ═════════════════════════════════════════════════════════════════════════════
def block6(s):
    s.transition(6)
    a = s.light_runes(12)
    s.run(*a, UpdateFromAlphaFunc(s.bsun, lambda m, t: set_alpha(m, 0.22 + 0.5 * t)), rt=1.0)
    s.run(s.caption("Thule. Vril. Sol Negro. Base 211. Una pregunta.", font=FONT_SANS,
                    accents={"211.": RED, "pregunta.": GOLD}, rt=1.8), rt=1.8)
    case = stamp("CASO CERRADO", BLOOD, 120).move_to([0, Y_VIS, 0]).set_z_index(30)
    s.run(FadeIn(case, scale=2.2), rt=0.4)
    s.glitch(0.2, strength=0.25)
    s.until(172.0, focus=case)
    # El Sol Negro se convierte en malla de alambre y se disuelve
    sun = s.bsun

    def to_wire(m, t):
        for sm in m.family_members_with_points():
            sm.set_fill(opacity=getattr(sm, "fo0", 1) * 0.72 * (1 - t))
            sm.set_stroke(CYAN, width=1.4, opacity=0.8 * t)

    banner = RoundedRectangle(width=8.3, height=1.75, corner_radius=0.2, stroke_width=3,
                              color=GOLD).set_fill(INK, 0.95).move_to([0, -2.6, 0])
    cta = kinetic_text("Si quieres que analice los archivos completos, sígueme.", size=52,
                       font=FONT_SANS, accents={"sígueme.": GOLD}).move_to(banner)
    arrow = Arrow([2.6, 3.3, 0], [3.7, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    bub = RoundedRectangle(width=1.25, height=0.95, corner_radius=0.25, color=BONE,
                           stroke_width=4).set_fill(INK, 0.9).move_to([3.25, -4.15, 0])
    dots = VGroup(*[Dot([3.25 + x, -4.15, 0], radius=0.07, color=CYAN) for x in (-0.3, 0, 0.3)])
    ask = kinetic_text("¿Crees que la base sigue ahí? Dímelo.", size=48, font=FONT_SERIF,
                       accents={"dímelo.": GOLD}, max_width=6.0)
    ask.next_to(bub, LEFT, buff=0.3)
    s.run(s.drop_caption(), FadeOut(case, scale=0.7), UpdateFromAlphaFunc(sun, to_wire),
          FadeIn(banner), reveal_words(cta, 1.2), rt=1.4)
    arrow.add_updater(blink_updater(7))
    s.add(arrow)
    s.run(FadeIn(VGroup(bub, dots), scale=0.6), reveal_words(ask, 1.1), rt=1.2)
    s.run(UpdateFromAlphaFunc(sun, lambda m, t: [sm.set_stroke(opacity=0.8 * (1 - t))
                                                for sm in m.family_members_with_points()]),
          rt=180.0 - s.now)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


class _Block(ThuleScene):
    INDEX = 0

    def construct(self):
        self.k_setup(self.INDEX)
        BLOCKS[self.INDEX](self)
        assert self.frames == ENDS[self.INDEX] * FPS, (self.INDEX, self.frames)


for _i in range(7):
    globals()[f"Block{_i}"] = type(f"Block{_i}", (_Block,), {"INDEX": _i})


class FullVideo(ThuleScene):
    def construct(self):
        self.k_setup(0)
        for i, b in enumerate(BLOCKS):
            assert self.frames == STARTS[i] * FPS, (i, self.frames)
            b(self)
            assert self.frames == ENDS[i] * FPS, (i, self.frames)
        assert self.frames == 180 * FPS
