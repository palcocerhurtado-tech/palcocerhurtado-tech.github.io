"""
poly.py — Motor «low-poly 3D oscuro» para Manim CE.

* low_poly(): triangula cualquier contorno en anillos concéntricos con ruido,
  sombrea cada cara según su orientación respecto a una luz arriba-izquierda y
  añade un velo blanco (opacidad 0.2) a las caras iluminadas.
* Revolve: sólido de revolución proyectado en 3D real (discos Haunebu, cúpulas,
  esferas), con caras ocultas descartadas, orden del pintor y rotación.
* Iconografía: Sol Negro (12 runas Sig extruidas), médiums, mapas, martillo,
  barco, avión, malla «Victalen», sello «CASO CERRADO».
"""
from __future__ import annotations

import numpy as np
from manim import (
    BOLD, DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP,
    ManimColor, Polygon, RoundedRectangle, Text, VGroup, interpolate_color,
)

INK = "#050508"
BONE = "#E8E6E3"
CYAN = "#5AC8FA"
GOLD = "#C9A227"
BLOOD = "#8B0000"
MYSTIC = "#4A2C6D"
ICE = "#9FC7DD"
STEEL = "#8A9099"
LIGHT = np.array([-0.55, 0.7, 0.45])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def shade(color, k: float):
    """k∈[0,1]: de casi negro al color; k>1 aclara hacia blanco."""
    c = ManimColor(color)
    if k <= 1:
        return interpolate_color(ManimColor(INK), c, 0.12 + 0.88 * max(k, 0))
    return interpolate_color(c, ManimColor("#FFFFFF"), min(k - 1, 0.6))


def _tri(a, b, c, color, k, mesh, mesh_op, sw):
    p = Polygon(a, b, c, stroke_width=sw, stroke_color=mesh, stroke_opacity=mesh_op)
    p.set_fill(shade(color, k), 1)
    p.k = k
    return p


# ─────────────────────────────────────────────────────────────────────────────
def low_poly(points, color, seed=0, rings=2, jitter=0.07, dome=0.6, mesh=None,
             mesh_op=0.35, sw=1.0, highlight=True, base_k=0.0):
    """Malla triangulada y sombreada de un contorno (lista de puntos 2D/3D)."""
    rng = np.random.default_rng(seed)
    P = np.array([[p[0], p[1], 0.0] for p in points])
    c = P.mean(axis=0)
    size = np.max(np.linalg.norm(P - c, axis=1))
    mesh = mesh or shade(color, 1.35)
    layers = [P]
    for j in range(1, rings + 1):
        s = 1 - j / (rings + 1)
        L = c + (P - c) * s
        L[:, :2] += rng.normal(0, jitter * size * 0.5, (len(P), 2))
        layers.append(L)
    faces = VGroup()
    hl = VGroup()

    def k_of(*vs):
        g = np.mean(vs, axis=0)
        d = (g - c) / (size + 1e-9)
        n = np.array([d[0] * dome, d[1] * dome, 1.0])
        n /= np.linalg.norm(n)
        return base_k + 0.42 + 0.62 * float(np.dot(n, LIGHT)) + rng.normal(0, 0.06)

    n = len(P)
    for j in range(rings):
        A, B = layers[j], layers[j + 1]
        for i in range(n):
            a, b = A[i], A[(i + 1) % n]
            cc, d = B[(i + 1) % n], B[i]
            for tri in ((a, b, cc), (a, cc, d)):
                k = k_of(*tri)
                faces.add(_tri(*tri, color, k, mesh, mesh_op, sw))
                if highlight and k > 0.95:
                    hl.add(Polygon(*tri, stroke_width=0).set_fill("#FFFFFF", 0.2))
    inner = layers[-1]
    for i in range(n):
        tri = (inner[i], inner[(i + 1) % n], c)
        k = k_of(*tri)
        faces.add(_tri(*tri, color, k, mesh, mesh_op, sw))
        if highlight and k > 0.95:
            hl.add(Polygon(*tri, stroke_width=0).set_fill("#FFFFFF", 0.2))
    g = VGroup(faces, hl)
    g.faces, g.hl = faces, hl
    return g


def resample(points, step):
    """Inserta vértices a lo largo del contorno (caras más pequeñas)."""
    P = [np.array([p[0], p[1], 0.0]) for p in points]
    out = []
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        m = max(1, int(np.linalg.norm(b - a) / step))
        for t in range(m):
            out.append(a + (b - a) * t / m)
    return out


def ngon(n, r, rot=0.0, center=(0, 0), wobble=0.0, seed=0):
    rng = np.random.default_rng(seed)
    return [(center[0] + r * (1 + rng.uniform(-wobble, wobble)) * np.cos(rot + TAU * i / n),
             center[1] + r * (1 + rng.uniform(-wobble, wobble)) * np.sin(rot + TAU * i / n))
            for i in range(n)]


# ─────────────────────────────────────────────────────────────────────────────
class Revolve(VGroup):
    """Sólido de revolución (perfil [(r, y)] de arriba a abajo) en 3D real."""

    def __init__(self, profile, color=STEEL, n=20, tilt=0.32, scale=1.0, center=ORIGIN,
                 mesh_op=0.45, wire=False, wire_color=CYAN, **kw):
        super().__init__(**kw)
        self.profile = [(r * scale, y * scale) for r, y in profile]
        self.color_, self.n, self.tilt = color, n, tilt
        self.center_pt = np.array(center, dtype=float)
        self.phase, self.op, self.mesh_op = 0.0, 1.0, mesh_op
        self.wire, self.wire_color = wire, wire_color
        self.rebuild()

    def _pt(self, r, y, th):
        x, z = r * np.cos(th), r * np.sin(th)
        ca, sa = np.cos(self.tilt), np.sin(self.tilt)
        return np.array([x, y * ca - z * sa, y * sa + z * ca])

    def rebuild(self):
        faces = []
        ymid = np.mean([y for _, y in self.profile])
        for k in range(self.n):
            t0 = self.phase + TAU * k / self.n
            t1 = self.phase + TAU * (k + 1) / self.n
            for j in range(len(self.profile) - 1):
                (r0, y0), (r1, y1) = self.profile[j], self.profile[j + 1]
                q = [self._pt(r0, y0, t0), self._pt(r0, y0, t1),
                     self._pt(r1, y1, t1), self._pt(r1, y1, t0)]
                if r0 < 1e-6:
                    q = [q[0], q[2], q[3]]
                elif r1 < 1e-6:
                    q = [q[0], q[1], q[2]]
                q = np.array(q)
                nrm = np.cross(q[1] - q[0], q[-1] - q[0])
                if np.linalg.norm(nrm) < 1e-9:
                    continue
                nrm /= np.linalg.norm(nrm)
                g = q.mean(axis=0)
                ref = g - self._pt(0, ymid, 0)
                if np.dot(nrm, ref) < 0:
                    nrm = -nrm
                if nrm[2] <= 0.0 and not self.wire:
                    continue
                kk = 0.38 + 0.75 * max(0.0, float(np.dot(nrm, LIGHT))) + 0.05 * ((k + j) % 2)
                pts = [np.array([p[0], p[1], 0]) + self.center_pt for p in q]
                poly = Polygon(*pts, stroke_width=1.0)
                if self.wire:
                    poly.set_fill(INK, 0).set_stroke(self.wire_color, 1.6, 0.7 * self.op)
                else:
                    poly.set_fill(shade(self.color_, kk), self.op)
                    poly.set_stroke(shade(self.color_, 1.4), 1.0, self.mesh_op * self.op)
                faces.append((g[2], poly, kk))
        faces.sort(key=lambda t: t[0])
        self.submobjects = []
        for _, p, kk in faces:
            self.add(p)
            if kk > 1.0 and not self.wire:
                self.add(p.copy().set_fill("#FFFFFF", 0.2 * self.op).set_stroke(width=0))
        return self

    def spin_updater(self, speed=0.6):
        def u(m, dt):
            m.phase += speed * dt
            m.rebuild()
        return u


HAUNEBU = [(0, 1.05), (0.32, 1.0), (0.52, 0.86), (0.6, 0.7), (0.62, 0.52), (0.95, 0.47),
           (1.0, 0.4), (1.0, 0.22), (1.55, 0.12), (2.3, -0.02), (2.26, -0.11), (1.45, -0.3),
           (0.9, -0.38), (0.0, -0.42)]


def sphere_profile(r=1.0, m=6):
    return [(r * np.sin(PI * i / m), r * np.cos(PI * i / m)) for i in range(m + 1)]


def haunebu(scale=1.0, center=ORIGIN, color=STEEL, n=22, tilt=0.3, wire=False):
    """Disco Haunebu: cuerpo de revolución + 3 cápsulas esféricas bajo el casco."""
    body = Revolve(HAUNEBU, color, n=n, tilt=tilt, scale=scale, center=center, wire=wire)
    pods = VGroup()
    for i, dx in enumerate((-0.95, 0.0, 0.95)):
        c = np.array(center) + np.array([dx * scale, -0.55 * scale - 0.05 * scale * (i == 1), 0])
        pods.add(Revolve(sphere_profile(0.3), color, n=10, tilt=tilt, scale=scale, center=c,
                         wire=wire))
    g = VGroup(pods, body)
    g.body, g.pods = body, pods
    return g


# ─────────────────────────────────────────────────────────────────────────────
SIG = [(0.08, 1.0), (0.27, 1.0), (0.06, 0.57), (0.25, 0.57), (-0.08, 0.0), (-0.27, 0.0),
       (-0.06, 0.43), (-0.25, 0.43)]


def black_sun(r0=0.55, r1=2.55, color=GOLD, seed=4):
    """Sol Negro: 12 runas Sig radiales, extruidas, con disco y anillo facetados."""
    runes = VGroup()
    L = r1 - r0
    for k in range(12):
        a = PI / 2 - k * TAU / 12
        u = np.array([np.cos(a), np.sin(a)])
        v = np.array([np.sin(a), -np.cos(a)])
        pts = [tuple(u * (r0 + y * L) + v * x * L * 0.62) for x, y in SIG]
        pts = resample(pts, 0.32)
        face = low_poly(pts, color, seed=seed + k, rings=1, jitter=0.05, dome=0.25)
        back = Polygon(*[np.array(p) + np.array([0.07, -0.07, 0]) for p in pts], stroke_width=0)
        back.set_fill(shade(color, 0.18), 1)
        rune = VGroup(back, face)
        rune.dir = np.array([u[0], u[1], 0])
        runes.add(rune)
    disc = low_poly(ngon(12, r0 * 0.82, rot=0.13), color, seed=seed, rings=1, dome=0.9)
    ring_pts = ngon(36, r1 + 0.18) + ngon(36, r1 + 0.02)[::-1]
    ring = VGroup()
    o, i_ = ngon(36, r1 + 0.22), ngon(36, r1 + 0.04)
    for j in range(36):
        a, b, c, d = o[j], o[(j + 1) % 36], i_[(j + 1) % 36], i_[j]
        pts = [np.array([*p, 0]) for p in (a, b, c, d)]
        g = np.mean(pts, axis=0)
        k = 0.45 + 0.6 * max(0, float(np.dot(g / np.linalg.norm(g), LIGHT[:3] / 1)))
        ring.add(Polygon(*pts, stroke_width=0.8, stroke_color=shade(color, 1.3),
                         stroke_opacity=0.5).set_fill(shade(color, k), 1))
    sun = VGroup(ring, runes, disc)
    sun.runes, sun.disc, sun.ring = runes, disc, ring
    return sun


def recolor(mob, color, k_shift=0.0):
    """Re-sombrea una malla low-poly a otro color conservando su relieve."""
    for sm in mob.family_members_with_points():
        k = getattr(sm, "k", None)
        if k is not None:
            sm.set_fill(shade(color, k + k_shift), sm.get_fill_opacity())
            sm.set_stroke(shade(color, 1.35))
    return mob


# ─────────────────────────────────────────────────────────────────────────────
MEDIUM = [(0.0, 2.0), (0.42, 1.92), (0.72, 1.6), (0.82, 1.15), (0.78, 0.7), (0.95, 0.2),
          (1.05, -0.6), (1.45, -0.95), (1.75, -1.6), (1.8, -2.1), (-1.8, -2.1), (-1.75, -1.6),
          (-1.35, -0.95), (-0.7, -0.75), (-0.52, -0.35), (-0.62, 0.35), (-0.75, 0.9),
          (-0.7, 1.5), (-0.42, 1.88)]


def medium(color=MYSTIC, seed=0, scale=1.0):
    pts = [(x * scale, y * scale) for x, y in MEDIUM]
    pts = resample(pts, 0.45 * scale)
    g = low_poly(pts, color, seed=seed, rings=2, jitter=0.1, dome=0.7)
    eye_y = 1.05 * scale
    eyes = VGroup(*[Polygon([x - 0.1 * scale, eye_y, 0], [x + 0.1 * scale, eye_y + 0.03 * scale, 0],
                            [x, eye_y - 0.06 * scale, 0], stroke_width=0).set_fill(CYAN, 0.9)
                    for x in (-0.22 * scale, 0.2 * scale)])
    out = VGroup(g, eyes)
    out.eyes = eyes
    return out


GERMANY = [(-0.55, 1.95), (0.05, 2.1), (0.55, 1.75), (1.05, 1.9), (1.25, 1.2), (1.4, 0.4),
           (0.85, 0.05), (1.15, -0.55), (1.0, -1.1), (1.2, -1.55), (0.55, -1.7), (-0.25, -1.65),
           (-0.95, -1.7), (-0.85, -1.05), (-1.25, -0.6), (-1.25, 0.2), (-1.1, 0.85),
           (-1.15, 1.4), (-0.75, 1.45)]
MUNICH = (0.55, -1.25)

ANTARCTICA = [(-0.3, 2.0), (0.2, 1.8), (0.75, 1.95), (1.35, 1.6), (1.95, 1.2), (2.2, 0.4),
              (2.35, -0.4), (1.95, -1.2), (1.3, -1.7), (0.4, -2.0), (-0.5, -1.9), (-1.2, -1.55),
              (-1.65, -0.85), (-1.55, -0.2), (-2.0, 0.2), (-2.55, 0.85), (-3.2, 1.6),
              (-2.6, 1.35), (-1.9, 1.15), (-1.2, 1.6)]
NEUSCHWABENLAND = (0.25, 1.45)


def thule_island(seed=7):
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(22):
        a = TAU * i / 22
        r = 1.6 * (1 + 0.28 * np.sin(3 * a + 1) + rng.uniform(-0.12, 0.12))
        pts.append((r * np.cos(a) * 1.25, r * np.sin(a) * 0.85))
    return pts


def hammer(color=STEEL):
    head = [(-1.6, 1.3), (1.6, 1.3), (1.75, 0.55), (1.2, 0.2), (-1.2, 0.2), (-1.75, 0.55)]
    handle = [(-0.24, 0.2), (0.24, 0.2), (0.2, -2.0), (-0.2, -2.0)]
    pommel = ngon(6, 0.36, rot=PI / 6, center=(0, -2.25))
    return VGroup(low_poly(resample(handle, 0.5), "#5E3B22", seed=2, rings=1),
                  low_poly(pommel, color, seed=3, rings=1),
                  low_poly(resample(head, 0.5), color, seed=1, rings=2, dome=0.8))


def ship(color=STEEL):
    hull = [(-3.2, 0.0), (3.4, 0.0), (2.8, -0.75), (-2.6, -0.75)]
    deck = [(-1.6, 0.0), (1.2, 0.0), (1.0, 0.55), (-0.2, 0.62), (-1.4, 0.5)]
    bridge = [(-0.7, 0.55), (0.3, 0.55), (0.2, 1.05), (-0.6, 1.05)]
    mast = [(-0.12, 1.05), (0.02, 1.05), (-0.03, 2.0)]
    return VGroup(low_poly(resample(hull, 0.6), color, seed=11, rings=1, dome=0.3),
                  low_poly(resample(deck, 0.5), color, seed=12, rings=1),
                  low_poly(bridge, color, seed=13, rings=1),
                  low_poly(mast, color, seed=14, rings=0))


def plane(color=STEEL):
    pts = [(0.0, 1.1), (0.16, 0.6), (1.9, 0.15), (1.9, -0.05), (0.16, 0.05), (0.12, -0.75),
           (0.6, -1.0), (0.6, -1.12), (0.0, -0.98), (-0.6, -1.12), (-0.6, -1.0), (-0.12, -0.75),
           (-0.16, 0.05), (-1.9, -0.05), (-1.9, 0.15), (-0.16, 0.6)]
    return low_poly(pts, color, seed=21, rings=1, dome=0.5)


def victalen(w=7.0, h=4.6, cell=0.42, color=STEEL, seed=31):
    """Placa de blindaje: malla de triángulos con vibración (humo congelado)."""
    rng = np.random.default_rng(seed)
    tris = VGroup()
    nx, ny = int(w / cell), int(h / (cell * 0.866))
    for j in range(ny):
        for i in range(nx):
            x0 = -w / 2 + i * cell + (j % 2) * cell / 2
            y0 = -h / 2 + j * cell * 0.866
            for up in (True, False):
                if up:
                    pts = [(x0, y0), (x0 + cell, y0), (x0 + cell / 2, y0 + cell * 0.866)]
                else:
                    pts = [(x0 + cell / 2, y0 + cell * 0.866), (x0 + cell * 1.5, y0 + cell * 0.866),
                           (x0 + cell, y0)]
                pts = [np.array([p[0] + rng.normal(0, 0.03), p[1] + rng.normal(0, 0.03), 0])
                       for p in pts]
                if max(abs(p[0]) for p in pts) > w / 2:
                    continue
                k = 0.35 + 0.55 * rng.random()
                t = Polygon(*pts, stroke_width=1, stroke_color=shade(color, 1.4),
                            stroke_opacity=0.45).set_fill(shade(color, k), 0.85)
                t.k, t.ph = k, rng.uniform(0, TAU)
                tris.add(t)
    return tris


def stamp(text, color=BLOOD, size=110, angle=-0.14, font="DejaVu Sans"):
    t = Text(text, font=font, font_size=size * 0.6, weight=BOLD, color=BONE)
    box = RoundedRectangle(width=t.width + 0.8, height=t.height + 0.6, corner_radius=0.12,
                           stroke_width=12, color=color).set_fill(color, 0.85)
    return VGroup(box, t).rotate(angle)
