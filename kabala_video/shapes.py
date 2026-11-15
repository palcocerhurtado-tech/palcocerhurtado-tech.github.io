"""
shapes.py — Iconografía generada 100 % por código (sin assets externos).

Ojo de la providencia, carro de fuego (Merkavá), siete palacios (hekhalot),
silueta del Adam Kadmón, kamea, cáscaras (qlifot), Gólem, Templo de Salomón,
escuadra y compás, fichas de archivo y burbuja de comentario.
"""
from __future__ import annotations

import numpy as np
from manim import (
    BOLD, DOWN, LEFT, NORMAL, ORIGIN, PI, RIGHT, TAU, UP,
    Arc, ArcBetweenPoints, Circle, Ellipse, Dot, Line, Polygon, Rectangle, RoundedRectangle,
    Square, Text, Triangle, VGroup, VMobject,
)

from utils import (
    BG, BONE, CLAY, CYAN, FONT_MONO, FONT_SANS, GOLD, HEBREW, RED, RED_GLOW, T, px,
)


# ── Ojo de la providencia ────────────────────────────────────────────────────
def providence_eye(h: float = 3.4) -> VGroup:
    tri = Triangle(color=GOLD, stroke_width=6).scale_to_fit_height(h)
    tri.set_fill(GOLD, 0.05)
    s = h / 3.4
    c = tri.get_center() + DOWN * 0.12 * s
    L, R = c + LEFT * 0.78 * s, c + RIGHT * 0.78 * s
    upper = ArcBetweenPoints(L, R, angle=-1.25, color=BONE, stroke_width=5)
    lower = ArcBetweenPoints(L, R, angle=1.25, color=BONE, stroke_width=5)
    iris = Circle(radius=0.27 * s, color=GOLD, stroke_width=5).move_to(c).set_fill(GOLD, 0.25)
    pupil = Dot(c, radius=0.11 * s, color=BG)
    eye = VGroup(upper, lower, iris, pupil)
    rays = VGroup()
    for k in range(24):
        a = k * TAU / 24 + 0.07
        d = np.array([np.cos(a), np.sin(a), 0])
        rays.add(Line(c + d * 2.15 * s, c + d * (2.7 + 0.35 * (k % 2)) * s,
                      color=GOLD, stroke_width=3, stroke_opacity=0.75))
    g = VGroup(rays, tri, eye)
    g.rays, g.tri, g.eye = rays, tri, eye
    return g


# ── Merkavá: carro de fuego ──────────────────────────────────────────────────
def _wheel(r: float) -> VGroup:
    rim = Circle(radius=r, color=GOLD, stroke_width=6)
    inner = Circle(radius=r * 0.8, color=GOLD, stroke_width=2.5, stroke_opacity=0.7)
    ell = Circle(radius=r * 0.8, color=BONE, stroke_width=3, stroke_opacity=0.8).stretch(0.32, 0)
    spokes = VGroup(*[Line(ORIGIN, r * 0.8 * np.array([np.cos(a), np.sin(a), 0]),
                           color=GOLD, stroke_width=2.5)
                      for a in np.linspace(0, TAU, 8, endpoint=False)])
    hub = Dot(radius=r * 0.09, color=GOLD)
    return VGroup(rim, inner, ell, spokes, hub)


def _flame(w: float, h: float, color) -> VMobject:
    f = VMobject(stroke_width=0)
    pts = [np.array([0, h, 0]), np.array([w * 0.35, h * 0.55, 0]), np.array([w * 0.5, h * 0.15, 0]),
           np.array([0, 0, 0]), np.array([-w * 0.5, h * 0.15, 0]),
           np.array([-w * 0.35, h * 0.55, 0]), np.array([0, h, 0])]
    f.set_points_smoothly(pts)
    f.set_fill(color, 0.75)
    return f


def merkava() -> VGroup:
    w1, w2 = _wheel(0.95).move_to([-1.55, -1.25, 0]), _wheel(0.95).move_to([1.55, -1.25, 0])
    axle = Line([-1.55, -1.25, 0], [1.55, -1.25, 0], color=GOLD, stroke_width=4)
    platform = Polygon([-2.4, -0.35, 0], [2.4, -0.35, 0], [2.0, -0.75, 0], [-2.0, -0.75, 0],
                       color=GOLD, stroke_width=4).set_fill(GOLD, 0.12)
    seat = Rectangle(width=1.6, height=0.35, color=GOLD, stroke_width=4).set_fill(GOLD, 0.25)
    seat.move_to([0, -0.15, 0])
    back = Polygon([-0.8, 0.05, 0], [0.8, 0.05, 0], [0.8, 1.6, 0], [0, 2.15, 0], [-0.8, 1.6, 0],
                   color=GOLD, stroke_width=4).set_fill(GOLD, 0.10)
    halo = Circle(radius=0.38, color=BONE, stroke_width=3).move_to([0, 1.15, 0])
    throne = VGroup(back, seat, halo)
    flames = VGroup()
    rng = np.random.default_rng(3)
    for i, x in enumerate(np.linspace(-2.6, 2.6, 9)):
        col = [RED, RED_GLOW, GOLD][i % 3]
        fl = _flame(0.55, rng.uniform(0.9, 1.6), col).move_to([x, 0.2, 0], aligned_edge=DOWN)
        fl.phase = rng.uniform(0, TAU)
        fl.cur = 1.0
        flames.add(fl)
    flames.set_z_index(-1)
    g = VGroup(flames, axle, w1, w2, platform, throne)
    g.wheels, g.flames, g.throne = VGroup(w1, w2), flames, throne
    return g


def flame_updater(m, dt):
    for fl in m:
        fl.t_ = getattr(fl, "t_", 0.0) + dt
        tgt = 1 + 0.12 * np.sin(fl.t_ * 9 + fl.phase)
        fl.stretch(tgt / fl.cur, 1, about_edge=DOWN)
        fl.cur = tgt


# ── Siete palacios (hekhalot) ────────────────────────────────────────────────
def arch(w: float, h: float, color=BONE, sw: float = 4) -> VGroup:
    r = w / 2
    left = Line([-r, 0, 0], [-r, h - r, 0], color=color, stroke_width=sw)
    right = Line([r, 0, 0], [r, h - r, 0], color=color, stroke_width=sw)
    top = Arc(radius=r, start_angle=0, angle=PI, color=color, stroke_width=sw).shift(UP * (h - r))
    return VGroup(left, top, right)


def palaces(n: int = 7) -> VGroup:
    gates = VGroup()
    guards = VGroup()
    for k in range(n):
        s = 0.84 ** k
        col = BONE if k < n - 1 else GOLD
        g = arch(4.2 * s, 5.0 * s, color=col, sw=5 - 0.4 * k)
        g.set_stroke(opacity=0.35 + 0.09 * k)
        g.move_to([0, -2.1 + 0.36 * (1 - s) * 4.2, 0], aligned_edge=DOWN)
        gates.add(g)
        if k < n - 1:                            # guardianes hostiles en cada umbral
            y = g.get_bottom()[1] + 5.0 * s * 0.55
            pair = VGroup(*[VGroup(Dot([sx * 2.1 * s, y, 0], radius=0.05, color=RED_GLOW),
                                   Dot([sx * 2.1 * s + 0.16 * s, y, 0], radius=0.05, color=RED_GLOW))
                            for sx in (-1, 1)])
            pair.set_opacity(0.25)
            guards.add(pair)
    ground = Line([-3.6, -2.1, 0], [3.6, -2.1, 0], color=BONE, stroke_width=2, stroke_opacity=0.4)
    out = VGroup(ground, gates, guards)
    out.gates, out.guards = gates, guards
    return out


def throne_icon(h: float = 0.9) -> VGroup:
    back = Polygon([-0.5, 0, 0], [0.5, 0, 0], [0.5, 1.0, 0], [0, 1.35, 0], [-0.5, 1.0, 0],
                   color=GOLD, stroke_width=4).set_fill(GOLD, 0.45)
    seat = Rectangle(width=1.2, height=0.25, color=GOLD, stroke_width=4).set_fill(GOLD, 0.6)
    seat.move_to([0, -0.05, 0])
    g = VGroup(back, seat)
    return g.scale_to_fit_height(h)


# ── Adam Kadmón ──────────────────────────────────────────────────────────────
def adam_kadmon(tree) -> VGroup:
    """Silueta humana ajustada a las posiciones del árbol: Kéter en lo alto de
    la cabeza (corona), Jojmá y Biná en los hemisferios, Maljut a los pies."""
    p, s = tree.pos, tree.s
    k = p[1]
    hy = p[2][1] - 0.25 * s
    head = Ellipse(width=2.95 * s, height=2.1 * s, color=BONE, stroke_width=3.5,
                   stroke_opacity=0.75).move_to([k[0], hy, 0]).set_fill(BONE, 0.05)
    neck = hy - 1.02 * s
    sh, hip, feet = neck - 0.35 * s, p[7][1] + 0.2 * s, p[10][1] - 0.4 * s
    x0, xs = k[0], 1.95 * s
    pts = [(-0.4, neck), (0.4, neck), (xs, sh), (xs + 0.45 * s, sh - 1.5 * s),
           (xs + 0.3 * s, sh - 2.5 * s), (xs - 0.15 * s, sh - 2.5 * s),
           (xs - 0.3 * s, sh - 1.0 * s), (1.45 * s, hip), (1.3 * s, feet + 0.2 * s),
           (1.0 * s, feet), (0.22 * s, feet), (0.12 * s, hip - 0.5 * s),
           (-0.12 * s, hip - 0.5 * s), (-0.22 * s, feet), (-1.0 * s, feet),
           (-1.3 * s, feet + 0.2 * s), (-1.45 * s, hip), (-(xs - 0.3 * s), sh - 1.0 * s),
           (-(xs - 0.15 * s), sh - 2.5 * s), (-(xs + 0.3 * s), sh - 2.5 * s),
           (-(xs + 0.45 * s), sh - 1.5 * s), (-xs, sh)]
    pts = [(x if abs(x) > 0.41 or (y != neck) else x * s, y) for x, y in pts]
    body = Polygon(*[np.array([x0 + x, y, 0]) for x, y in pts], color=BONE,
                   stroke_width=3.5, stroke_opacity=0.75).set_fill(BONE, 0.05)
    crown = VGroup(*[Line(k + np.array([dx, 0.36 * s, 0]), k + np.array([dx * 1.5, 0.75 * s, 0]),
                          color=GOLD, stroke_width=4) for dx in (-0.28 * s, 0, 0.28 * s)])
    g = VGroup(body, head, crown)
    g.set_z_index(-2)
    return g


# ── Kamea (amuleto) ──────────────────────────────────────────────────────────
def kamea(r: float = 2.35, name: str = "אדני") -> VGroup:
    outer = Circle(radius=r, color=GOLD, stroke_width=6)
    outer2 = Circle(radius=r * 0.8, color=GOLD, stroke_width=3)
    ring = VGroup()
    for i, ch in enumerate(HEBREW):
        a = PI / 2 - i * TAU / 22
        t = T(ch, font=FONT_SANS, font_size=px(50), color=BONE)
        t.move_to(r * 0.9 * np.array([np.cos(a), np.sin(a), 0]))
        t.rotate(a - PI / 2)
        ring.add(t)
    sq1 = Square(side_length=r * 1.05, color=GOLD, stroke_width=3)
    sq2 = sq1.copy().rotate(PI / 4)
    seal = VGroup(sq1, sq2).set_fill(GOLD, 0.04)
    ticks = VGroup(*[Dot(r * 0.8 * np.array([np.cos(a), np.sin(a), 0]), radius=0.04, color=GOLD)
                     for a in np.linspace(0, TAU, 8, endpoint=False)])
    center = T(name, font=FONT_SANS, font_size=px(110), weight=BOLD, color=GOLD)
    g = VGroup(outer, outer2, seal, ticks, ring, center)
    g.ring, g.center_name, g.seal = ring, center, seal
    return g


# ── Qlifot: cáscaras ─────────────────────────────────────────────────────────
def shell(r: float, color=RED_GLOW, seed: int = 0) -> VGroup:
    """Una esfera rota: tres fragmentos de arco con huecos (vacía por dentro)."""
    rng = np.random.default_rng(seed)
    start = rng.uniform(0, TAU)
    frags = VGroup()
    for k in range(3):
        a0 = start + k * TAU / 3 + rng.uniform(0.15, 0.35)
        frags.add(Arc(radius=r * rng.uniform(1.0, 1.25), start_angle=a0,
                      angle=TAU / 3 - rng.uniform(0.5, 0.9), color=color, stroke_width=4))
    return frags


# ── Gólem ────────────────────────────────────────────────────────────────────
def golem() -> VGroup:
    def block(w, h, x, y, cr=0.18):
        b = RoundedRectangle(width=w, height=h, corner_radius=cr, stroke_width=3, color="#3A2414")
        return b.set_fill(CLAY, 1).move_to([x, y, 0])

    legs = VGroup(block(0.75, 1.7, -0.5, -1.25), block(0.75, 1.7, 0.5, -1.25))
    torso = block(2.0, 2.0, 0, 0.55, 0.3)
    arms = VGroup(block(0.62, 2.0, -1.4, 0.3), block(0.62, 2.0, 1.4, 0.3))
    head = block(1.15, 1.05, 0, 2.2, 0.35)
    eyes = VGroup(Dot([-0.24, 2.3, 0], radius=0.09, color=BG), Dot([0.24, 2.3, 0], radius=0.09, color=BG))
    cracks = VGroup(*[Line(a, b, color="#2A1A0E", stroke_width=2) for a, b in
                      [([-0.6, 1.0, 0], [-0.3, 0.6, 0]), ([0.4, 0.2, 0], [0.7, -0.1, 0]),
                       ([-0.2, 2.5, 0], [0.05, 2.62, 0])]])
    g = VGroup(legs, arms, torso, head, cracks, eyes)
    g.parts = [legs, arms, torso, head]
    g.eyes, g.head = eyes, head
    return g


# ── Templo de Salomón ────────────────────────────────────────────────────────
def temple() -> VGroup:
    steps = VGroup(*[Rectangle(width=5.6 - 0.5 * i, height=0.22, color=BONE, stroke_width=3)
                     .move_to([0, -2.0 + 0.22 * i, 0]) for i in range(3)])
    hall = Rectangle(width=3.6, height=2.9, color=BONE, stroke_width=3).move_to([0, -0.22, 0])
    hall.set_fill(BONE, 0.03)
    roof = Polygon([-2.3, 1.25, 0], [2.3, 1.25, 0], [0, 2.35, 0], color=GOLD, stroke_width=4)
    roof.set_fill(GOLD, 0.08)
    door = arch(1.1, 1.8, color=GOLD, sw=4).move_to([0, -1.67, 0], aligned_edge=DOWN)
    pillars = VGroup()
    for x in (-2.35, 2.35):
        shaft = Rectangle(width=0.42, height=3.0, color=GOLD, stroke_width=4).set_fill(GOLD, 0.12)
        shaft.move_to([x, -0.17, 0])
        cap = Circle(radius=0.32, color=GOLD, stroke_width=4).set_fill(GOLD, 0.2).move_to([x, 1.58, 0])
        base = Rectangle(width=0.7, height=0.18, color=GOLD, stroke_width=3).move_to([x, -1.6, 0])
        pillars.add(VGroup(base, shaft, cap))
    g = VGroup(steps, hall, roof, door, pillars)
    return g


def square_compass(h: float = 4.0) -> VGroup:
    s = h / 4.0
    hinge = np.array([0, 1.9 * s, 0])
    leg_l = Line(hinge, [-1.7 * s, -1.6 * s, 0], color=GOLD, stroke_width=12)
    leg_r = Line(hinge, [1.7 * s, -1.6 * s, 0], color=GOLD, stroke_width=12)
    knob = Circle(radius=0.2 * s, color=GOLD, stroke_width=6).set_fill(BG, 1).move_to(hinge)
    top = Line(hinge, hinge + UP * 0.35 * s, color=GOLD, stroke_width=8)
    compass = VGroup(leg_l, leg_r, top, knob)
    vtx = np.array([0, -1.9 * s, 0])
    sq_l = Line(vtx, [-1.95 * s, 0.05 * s, 0], color=BONE, stroke_width=14)
    sq_r = Line(vtx, [1.95 * s, 0.05 * s, 0], color=BONE, stroke_width=14)
    square = VGroup(sq_l, sq_r)
    g = VGroup(square, compass)
    g.square, g.compass = square, compass
    return g


# ── Fichas de archivo y burbuja de comentario ────────────────────────────────
def dossier_card(name: str, w: float = 7.2, h: float = 1.25) -> VGroup:
    frame = Rectangle(width=w, height=h, color=GOLD, stroke_width=3).set_fill("#0E0C08", 0.95)
    tab = Rectangle(width=1.5, height=0.32, color=GOLD, stroke_width=2).set_fill(GOLD, 0.25)
    tab.next_to(frame, UP, buff=0, aligned_edge=LEFT)
    label = T(name, font=FONT_MONO, font_size=px(52), weight=BOLD, color=BONE)
    if label.width > w - 0.6:
        label.scale_to_fit_width(w - 0.6)
    label.move_to(frame)
    g = VGroup(frame, tab, label)
    g.label = label
    return g


def comment_icon(size: float = 1.0) -> VGroup:
    bub = RoundedRectangle(width=1.25 * size, height=0.95 * size, corner_radius=0.25 * size,
                           color=BONE, stroke_width=4).set_fill(BG, 0.8)
    tail = Polygon([-0.25 * size, -0.47 * size, 0], [0.05 * size, -0.47 * size, 0],
                   [-0.32 * size, -0.78 * size, 0], color=BONE, stroke_width=4).set_fill(BG, 0.8)
    dots = VGroup(*[Dot([x * size, 0, 0], radius=0.07 * size, color=CYAN) for x in (-0.3, 0, 0.3)])
    return VGroup(tail, bub, dots)
