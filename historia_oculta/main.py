"""
main.py — "LA VERDADERA HISTORIA OCULTA: DE LIRA A QANON"
Vídeo vertical 9:16 · 1080x1920 · 30 fps · 180.0 s exactos · Manim CE 0.18+

Render completo:   manim -qh main.py FullVideo
Bloques sueltos:   manim -qh main.py Block3Anunnaki   (etc.)
Vista previa:      PREVIEW=1 manim main.py FullVideo  (540x960, 15 fps)

Sincronía: si existe timeline.json (lo genera narration.py) los planos arrancan
exactamente cuando la voz dice su frase. Si no existe, se usa la escaleta de §4.
Todo el material gráfico se genera por código (sin assets externos).
"""

from __future__ import annotations

import json
import os
import random

import numpy as np
from manim import *  # noqa: F401,F403

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN 9:16
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

# Paleta §3
BG = "#0A0A0A"
TXT = "#E8E6E3"
DATA = "#5AC8FA"
GOLD = "#C9A227"
ALERT = "#8B0000"
ALERT_HI = "#D2232A"   # rojo alerta legible sobre negro (derivado de ALERT)
LIRA_BLUE = "#3D7BFF"  # mutación "lirana"
REPT_GREEN = "#3DDC84"  # mutación "reptiliana"
DIM = "#3A3A3A"

SANS = "DejaVu Sans"
MONO = "DejaVu Sans Mono"
MIN_FS = 48

# Zonas seguras (unidades de escena; 120 px = 1 u)
# x ∈ [60,1020] px  -> [-4.0, 4.0] u ;  y ∈ [230,1536] px -> [6.08, -4.8] u
SAFE_L, SAFE_R, SAFE_T, SAFE_B = -4.0, 4.0, 6.08, -4.8
MAX_W = 7.8
Y_STAMP = 5.55
Y_TAG = 4.72
Y_HEAD = 3.35
Y_VIS = -0.15
Y_CAP = -3.05
Y_HELIX = -4.25
CORNER_TR = np.array([3.75, 5.85, 0])

# ════════════════════════════════════════════════════════════════════════════
# ESCALETA (§4) — se sobreescribe con timeline.json si existe
# ════════════════════════════════════════════════════════════════════════════
DEFAULT_BEATS = [
    ("b0_helix", 0), ("b0_mutate", 3), ("b0_map", 8), ("b0_cta", 12),
    ("b1_alliance", 15), ("b1_draco", 22), ("b1_war", 30), ("b1_genocide", 38),
    ("b2_continents", 45), ("b2_extinction", 55), ("b2_treaty", 65),
    ("b3_anunnaki", 75), ("b3_sapiens", 85), ("b3_gold", 95), ("b3_enoc", 100),
    ("b4_weishaupt", 105), ("b4_obelisks", 113), ("b4_nobility", 120), ("b4_papa", 128),
    ("b5_orsic", 135), ("b5_haunebu", 142), ("b5_thule", 149), ("b5_base", 155),
    ("b6_dumbs", 165), ("b6_awaken", 168), ("b6_recap", 170), ("b6_cta", 172),
]


def load_timeline() -> dict[str, tuple[float, float]]:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timeline.json")
    beats = list(DEFAULT_BEATS)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        got = {b["key"]: float(b["start"]) for b in data["beats"]}
        if all(k in got for k, _ in DEFAULT_BEATS):
            beats = [(k, got[k]) for k, _ in DEFAULT_BEATS]
    out = {}
    for i, (k, s) in enumerate(beats):
        e = beats[i + 1][1] if i + 1 < len(beats) else TOTAL
        out[k] = (s, e)
    return out


TL = load_timeline()


# ════════════════════════════════════════════════════════════════════════════
# RELOJ POR FOTOGRAMAS — garantiza 180.0 s exactos
# ════════════════════════════════════════════════════════════════════════════
class Beat:
    """Un plano con inicio/fin absolutos. Cada play consume fotogramas enteros.

    `f` = fracción del tiempo restante del plano en el momento de abrirlo.
    Manim genera ceil(run_time*fps) fotogramas, así que run_time=(n-0.5)/fps
    produce exactamente n fotogramas.
    """

    def __init__(self, scene: "HiddenHistoryBase", key: str):
        self.s = scene
        self.key = key
        start, end = TL[key]
        self.end_frame = int(round(end * FPS))
        self.span = max(2, self.end_frame - scene.frame_no)

    def frames_left(self) -> int:
        return self.end_frame - self.s.frame_no

    def play(self, *anims, f: float = 0.1, min_frames: int = 2, **kw):
        n = max(min_frames, int(round(f * self.span)))
        left = self.frames_left()
        if left >= 2:
            n = min(n, left)
        else:
            n = 2  # plano comprimido: mínimo imprescindible
        self.s.play(*anims, run_time=(n - 0.5) / FPS, **kw)
        self.s.frame_no += n

    def hold(self, f: float = 0.1, mob: Mobject | None = None):
        """Pausa activa: deriva del fondo estelar + leve push-in (nunca wait)."""
        n = max(2, int(round(f * self.span)))
        n = min(n, max(2, self.frames_left()))
        if self.frames_left() < 2:
            return
        self._drift(n, mob)

    def finish(self, mob: Mobject | None = None):
        left = self.frames_left()
        if left >= 2:
            self._drift(left, mob)
        elif left == 1:
            self._drift(2, mob)

    def _drift(self, n: int, mob: Mobject | None):
        rt = (n - 0.5) / FPS
        anims = [self.s.stars.animate(rate_func=linear).shift(DOWN * 0.06 * rt)]
        if mob is not None:
            anims.append(mob.animate(rate_func=linear).scale(1 + 0.012 * rt))
        self.s.play(*anims, run_time=rt)
        self.s.frame_no += n


# ════════════════════════════════════════════════════════════════════════════
# TEXTO CINÉTICO
# ════════════════════════════════════════════════════════════════════════════
def _word(w: str, fs: float, color, font: str, weight) -> Text:
    return Text(w, font=font, font_size=fs, color=color, weight=weight)


def kinetic_text(text: str, fs: float = 64, color=TXT, font: str = SANS,
                 weight=BOLD, max_w: float = MAX_W, max_lines: int = 3) -> VGroup:
    """Texto partido en palabras (para animación palabra a palabra),
    con ajuste automático de líneas al ancho seguro. Nunca baja de MIN_FS."""
    words = text.split()
    fs = max(fs, MIN_FS)
    while True:
        probe = [_word(w, fs, color, font, weight) for w in words]
        space = _word("n", fs, color, font, weight).width * 0.62
        lines, cur, cur_w = [], [], 0.0
        for m in probe:
            add = m.width + (space if cur else 0)
            if cur and cur_w + add > max_w:
                lines.append(cur)
                cur, cur_w = [m], m.width
            else:
                cur.append(m)
                cur_w += add
        if cur:
            lines.append(cur)
        widest = max(sum(m.width for m in ln) + space * (len(ln) - 1) for ln in lines)
        if (len(lines) <= max_lines and widest <= max_w) or fs <= MIN_FS:
            break
        fs = max(MIN_FS, fs - 4)
    rows = VGroup()
    for ln in lines:
        row = VGroup(*ln)
        row.arrange(RIGHT, buff=space, aligned_edge=DOWN)
        rows.add(row)
    rows.arrange(DOWN, buff=fs / 48 * 0.22)
    if rows.width > max_w:  # palabra suelta más ancha que el área segura
        rows.scale_to_fit_width(max_w)
    rows.word_count = len(words)
    return rows


def reveal(mob: VGroup, lag: float = 0.12) -> Animation:
    """Write para <=4 palabras; cascada de palabras para el resto (§2)."""
    n = getattr(mob, "word_count", 1)
    if n <= 4:
        return Write(mob)
    words = [w for row in mob for w in row]
    return LaggedStart(*[FadeIn(w, shift=UP * 0.25, scale=1.15) for w in words],
                       lag_ratio=lag)


HEAD_TOP = 4.30  # bajo la etiqueta "RELATO ESPECULATIVO"


def head(text: str, color=TXT, fs: float = 66, y: float = Y_HEAD) -> VGroup:
    m = kinetic_text(text, fs=fs, color=color).move_to([0, y, 0])
    if m.get_top()[1] > HEAD_TOP:
        m.shift(DOWN * (m.get_top()[1] - HEAD_TOP))
    return m


def cap(text: str, color=DATA, fs: float = 50, y: float = Y_CAP) -> VGroup:
    return kinetic_text(text, fs=fs, color=color, font=MONO, weight=BOLD).move_to([0, y, 0])


def label(text: str, color=TXT, fs: float = MIN_FS, font: str = MONO) -> Text:
    return Text(text, font=font, font_size=fs, color=color, weight=BOLD)


# ════════════════════════════════════════════════════════════════════════════
# RECURSOS GRÁFICOS
# ════════════════════════════════════════════════════════════════════════════
class Helix(VGroup):
    """Doble hélice proyectada en 2D. 8 tramos; cada tramo = 2 trozos por hebra + 4 peldaños."""

    N_TRAMOS = 8

    def __init__(self, width=7.8, amp=0.34, turns=4.0, color=DATA, **kw):
        super().__init__(**kw)
        self.tramos = VGroup()
        x0 = -width / 2
        k = turns * TAU / width
        per = width / self.N_TRAMOS
        for i in range(self.N_TRAMOS):
            a, b = x0 + i * per, x0 + (i + 1) * per
            s1 = ParametricFunction(lambda t: np.array([t, amp * np.sin(k * t), 0]),
                                    t_range=[a, b, per / 24], stroke_width=6, color=color)
            s2 = ParametricFunction(lambda t: np.array([t, -amp * np.sin(k * t), 0]),
                                    t_range=[a, b, per / 24], stroke_width=6, color=color)
            rungs = VGroup()
            for j in range(4):
                x = a + (j + 0.5) * per / 4
                y = amp * np.sin(k * x)
                if abs(y) > 0.04:
                    rungs.add(Line([x, y, 0], [x, -y, 0], stroke_width=3.5,
                                   color=color, stroke_opacity=0.7))
            tramo = VGroup(s1, s2, rungs)
            self.tramos.add(tramo)
        self.add(self.tramos)

    def tramo(self, *idx) -> VGroup:
        return VGroup(*[self.tramos[i] for i in idx])


def stamp(text="CLASIFICADO", color=ALERT_HI) -> VGroup:
    t = Text(text, font=MONO, font_size=54, color=color, weight=BOLD)
    box = SurroundingRectangle(t, buff=0.16, color=color, stroke_width=6,
                               corner_radius=0.08)
    g = VGroup(box, t).rotate(4 * DEGREES)
    g.move_to([0, Y_STAMP, 0]).align_to([SAFE_L + 0.05, 0, 0], LEFT)
    return g


def starfield(n=150, seed=7) -> VGroup:
    rnd = random.Random(seed)
    dots = VGroup()
    for _ in range(n):
        dots.add(Dot([rnd.uniform(-4.6, 4.6), rnd.uniform(-8.4, 8.4), 0],
                     radius=rnd.uniform(0.008, 0.028), color=TXT,
                     fill_opacity=rnd.uniform(0.15, 0.55)))
    return dots


def blob(r=1.5, seed=1, jitter=0.25, n=14, color=DATA, fill=0.15) -> VMobject:
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = TAU * i / n
        rr = r * (1 + rnd.uniform(-jitter, jitter))
        pts.append([rr * np.cos(a), rr * np.sin(a) * 0.8, 0])
    m = VMobject(stroke_color=color, stroke_width=4, fill_color=color, fill_opacity=fill)
    m.set_points_smoothly(pts + [pts[0]])
    return m


def humanoid(h=2.6, color=DATA, fill=0.9) -> VGroup:
    s = h / 2.6
    head_ = Circle(radius=0.28 * s, color=color, fill_opacity=fill).move_to([0, 1.0 * s, 0])
    body = Polygon([-0.55 * s, 0.62 * s, 0], [0.55 * s, 0.62 * s, 0], [0.32 * s, -0.55 * s, 0],
                   [0.22 * s, -1.3 * s, 0], [-0.22 * s, -1.3 * s, 0], [-0.32 * s, -0.55 * s, 0],
                   color=color, fill_opacity=fill)
    return VGroup(head_, body)


def draco_head(scale=1.0, color=REPT_GREEN) -> VGroup:
    pts = [(-1.7, 0.0), (-0.7, 0.42), (0.1, 0.8), (0.55, 1.45), (0.75, 0.95), (1.15, 1.5),
           (1.3, 0.85), (1.75, 1.05), (1.55, 0.35), (1.65, -0.6), (1.1, -1.5),
           (0.35, -0.75), (-0.6, -0.42), (-1.7, -0.18)]
    shell = Polygon(*[[x, y, 0] for x, y in pts], color=color, stroke_width=4,
                    fill_color=color, fill_opacity=0.18)
    c = np.array([0.4, 0.15, 0])
    mesh = VGroup(*[Line(c, [x, y, 0], stroke_width=1.5, color=color, stroke_opacity=0.45)
                    for x, y in pts])
    eye = Ellipse(width=0.42, height=0.22, color=GOLD, fill_opacity=1).move_to([0.05, 0.32, 0])
    slit = Ellipse(width=0.06, height=0.2, color=BG, fill_opacity=1).move_to(eye)
    return VGroup(shell, mesh, eye, slit).scale(scale)


def anunnaki(h=4.0, color=GOLD) -> VGroup:
    s = h / 4.0
    crown = VGroup(*[Polygon([-0.32 * s + i * 0.02, (1.55 + i * 0.16) * s, 0],
                             [0.32 * s - i * 0.02, (1.55 + i * 0.16) * s, 0],
                             [0.28 * s - i * 0.02, (1.69 + i * 0.16) * s, 0],
                             [-0.28 * s + i * 0.02, (1.69 + i * 0.16) * s, 0],
                             color=color, fill_opacity=0.9, stroke_width=2)
                     for i in range(4)])
    head_ = Circle(radius=0.3 * s, color=color, fill_opacity=0.9).move_to([0, 1.25 * s, 0])
    robe = Polygon([-0.6 * s, 0.9 * s, 0], [0.6 * s, 0.9 * s, 0], [0.9 * s, -1.9 * s, 0],
                   [-0.9 * s, -1.9 * s, 0], color=color, fill_opacity=0.85)
    wing_l = Polygon([-0.55 * s, 0.8 * s, 0], [-2.0 * s, 1.4 * s, 0], [-1.8 * s, 0.6 * s, 0],
                     [-1.5 * s, -0.3 * s, 0], [-0.6 * s, 0.0, 0], color=color,
                     fill_opacity=0.35, stroke_width=3)
    wing_r = wing_l.copy().flip(UP).shift(RIGHT * 0.0)
    wing_r.move_to([-wing_l.get_center()[0], wing_l.get_center()[1], 0])
    return VGroup(wing_l, wing_r, robe, head_, crown)


def hominid(upright: bool, color=TXT) -> VGroup:
    """Mismo número de piezas en ambas versiones -> Transform limpio."""
    if upright:
        head_ = Circle(radius=0.3, color=color, fill_opacity=0.9).move_to([0, 1.55, 0])
        torso = Polygon([-0.5, 1.15, 0], [0.5, 1.15, 0], [0.3, -0.2, 0], [-0.3, -0.2, 0],
                        color=color, fill_opacity=0.9)
        leg1 = Line([-0.15, -0.2, 0], [-0.3, -1.9, 0], stroke_width=16, color=color)
        leg2 = Line([0.15, -0.2, 0], [0.3, -1.9, 0], stroke_width=16, color=color)
        arm = Line([0.45, 1.05, 0], [0.6, -0.3, 0], stroke_width=12, color=color)
    else:
        head_ = Circle(radius=0.3, color=color, fill_opacity=0.9).move_to([0.95, 0.85, 0])
        torso = Polygon([0.65, 0.75, 0], [0.9, 0.3, 0], [-0.1, -0.45, 0], [-0.45, -0.1, 0],
                        color=color, fill_opacity=0.9)
        leg1 = Line([-0.3, -0.3, 0], [-0.45, -1.9, 0], stroke_width=16, color=color)
        leg2 = Line([-0.05, -0.4, 0], [0.25, -1.9, 0], stroke_width=16, color=color)
        arm = Line([0.6, 0.45, 0], [0.9, -0.9, 0], stroke_width=12, color=color)
    return VGroup(head_, torso, leg1, leg2, arm)


def dinosaur(color=TXT) -> Polygon:
    pts = [(-2.6, 0.1), (-1.6, 0.25), (-0.8, 0.75), (0.2, 0.85), (0.9, 0.6), (1.4, 1.6),
           (1.7, 2.1), (2.1, 2.1), (2.1, 1.9), (1.75, 1.75), (1.45, 0.4), (1.1, 0.0),
           (1.0, -0.9), (0.75, -0.9), (0.7, -0.2), (-0.3, -0.2), (-0.4, -0.9), (-0.65, -0.9),
           (-0.7, -0.1), (-1.6, 0.0)]
    return Polygon(*[[x, y, 0] for x, y in pts], color=color, fill_opacity=0.85, stroke_width=3)


def bust_profile(color=TXT) -> VGroup:
    pts = [(0.0, 1.9), (0.5, 1.85), (0.75, 1.5), (0.8, 1.1), (1.0, 0.85), (0.8, 0.75),
           (0.85, 0.5), (0.7, 0.3), (0.65, 0.05), (0.3, -0.05), (0.3, -0.35), (1.6, -0.7),
           (1.8, -1.6), (-1.8, -1.6), (-1.6, -0.7), (-0.5, -0.35), (-0.55, 0.3), (-0.75, 0.9),
           (-0.6, 1.6)]
    face = Polygon(*[[x, y, 0] for x, y in pts], color=color, fill_opacity=0.85, stroke_width=3)
    queue = Polygon([-0.6, 1.0, 0], [-1.05, 0.55, 0], [-0.95, 0.35, 0], [-0.55, 0.65, 0],
                    color=color, fill_opacity=0.85)
    return VGroup(face, queue)


def illuminati_eye(size=1.6, color=GOLD) -> VGroup:
    tri = Triangle(color=color, stroke_width=5).scale(size)
    eye = Ellipse(width=size * 0.8, height=size * 0.36, color=color, stroke_width=4)
    pupil = Dot(radius=size * 0.09, color=color)
    rays = VGroup(*[Line(ORIGIN, size * 1.5 * np.array([np.cos(a), np.sin(a), 0]),
                         stroke_width=2, color=color, stroke_opacity=0.5)
                    for a in np.linspace(0.25, PI - 0.25, 7)])
    g = VGroup(rays, tri, VGroup(eye, pupil).shift(DOWN * size * 0.12))
    return g


def obelisk(h=3.0, color=TXT) -> VGroup:
    w0, w1 = 0.42, 0.28
    shaft = Polygon([-w0, 0, 0], [w0, 0, 0], [w1, h, 0], [-w1, h, 0], color=color,
                    fill_opacity=0.85, stroke_width=2)
    tip = Polygon([-w1, h, 0], [w1, h, 0], [0, h + 0.4, 0], color=GOLD, fill_opacity=1)
    base = Rectangle(width=1.2, height=0.18, color=color, fill_opacity=0.85).move_to([0, -0.09, 0])
    return VGroup(base, shaft, tip)


def woman_silhouette(color=TXT) -> VGroup:
    head_ = Circle(radius=0.36, color=color, fill_opacity=0.9).move_to([0, 1.7, 0])
    hair = Polygon([-0.42, 1.95, 0], [0.42, 1.95, 0], [0.55, 1.3, 0], [0.7, -0.3, 0],
                   [-0.7, -0.3, 0], [-0.55, 1.3, 0], color=color, fill_opacity=0.55,
                   stroke_width=2)
    body = Polygon([-0.6, 1.2, 0], [0.6, 1.2, 0], [0.9, -1.6, 0], [-0.9, -1.6, 0],
                   color=color, fill_opacity=0.85)
    return VGroup(hair, body, head_)


def disc_ship(color=DATA) -> VGroup:
    body = Ellipse(width=5.0, height=0.9, color=color, stroke_width=5)
    dome = Arc(radius=1.05, start_angle=0, angle=PI, color=color, stroke_width=5)
    dome.stretch(0.6, 1).move_to([0, 0.62, 0])
    bell = Polygon([-1.2, -0.38, 0], [1.2, -0.38, 0], [0.8, -0.95, 0], [-0.8, -0.95, 0],
                   color=color, stroke_width=4)
    ports = VGroup(*[Circle(radius=0.09, color=color, stroke_width=3).move_to([x, 0.05, 0])
                     for x in np.linspace(-1.8, 1.8, 7)])
    guns = VGroup(*[Line([x, -0.95, 0], [x, -1.25, 0], color=color, stroke_width=4)
                    for x in (-0.5, 0, 0.5)])
    return VGroup(body, dome, bell, ports, guns)


def blueprint_grid(w=8.0, h=4.6, step=0.5, color=DATA) -> VGroup:
    g = VGroup()
    for x in np.arange(-w / 2, w / 2 + 0.01, step):
        g.add(Line([x, -h / 2, 0], [x, h / 2, 0], stroke_width=1, color=color, stroke_opacity=0.18))
    for y in np.arange(-h / 2, h / 2 + 0.01, step):
        g.add(Line([-w / 2, y, 0], [w / 2, y, 0], stroke_width=1, color=color, stroke_opacity=0.18))
    return g


def trefoil(r=1.0, color=ALERT_HI) -> VGroup:
    blades = VGroup(*[AnnularSector(inner_radius=0.32 * r, outer_radius=r, angle=PI / 3,
                                    start_angle=PI / 3 + i * 2 * PI / 3, color=color,
                                    fill_opacity=0.9) for i in range(3)])
    return VGroup(blades, Dot(radius=0.2 * r, color=color),
                  Circle(radius=1.12 * r, color=color, stroke_width=4))


def cuneiform(seed=0, color=DATA, s=0.55) -> VGroup:
    """Signo pseudo-cuneiforme hecho de cuñas (sin fuentes externas)."""
    rnd = random.Random(seed)
    g = VGroup()
    for _ in range(rnd.randint(3, 5)):
        ang = rnd.choice([0, PI / 2, PI / 4, -PI / 4])
        wedge = VGroup(Triangle(color=color, fill_opacity=1).scale(0.1 * s / 0.55),
                       Line(ORIGIN, RIGHT * 0.45 * s, color=color, stroke_width=4))
        wedge[0].rotate(-PI / 2).move_to(ORIGIN)
        wedge[1].next_to(wedge[0], RIGHT, buff=0)
        wedge.rotate(ang).shift([rnd.uniform(-0.3, 0.3) * s, rnd.uniform(-0.3, 0.3) * s, 0])
        g.add(wedge)
    return g


def vimana(color=GOLD) -> VGroup:
    hull = Polygon([-2.0, 0, 0], [2.0, 0, 0], [1.4, -0.5, 0], [-1.4, -0.5, 0],
                   color=color, fill_opacity=0.3, stroke_width=4)
    tiers = VGroup(*[Polygon([-1.4 + i * 0.35, i * 0.35, 0], [1.4 - i * 0.35, i * 0.35, 0],
                             [1.2 - i * 0.35, (i + 1) * 0.35, 0],
                             [-1.2 + i * 0.35, (i + 1) * 0.35, 0],
                             color=color, fill_opacity=0.25, stroke_width=3) for i in range(3)])
    spire = Polygon([-0.25, 1.05, 0], [0.25, 1.05, 0], [0, 1.6, 0], color=color, fill_opacity=0.9)
    wings = VGroup(Polygon([-2.0, 0, 0], [-2.9, 0.5, 0], [-2.4, -0.25, 0], color=color,
                           fill_opacity=0.4),
                   Polygon([2.0, 0, 0], [2.9, 0.5, 0], [2.4, -0.25, 0], color=color,
                           fill_opacity=0.4))
    return VGroup(hull, tiers, spire, wings)


def puzzle_piece(color=DATA, s=0.8) -> VGroup:
    sq = Square(side_length=s, color=color, fill_opacity=0.85)
    k1 = Circle(radius=s * 0.2, color=color, fill_opacity=0.85).move_to(sq.get_top())
    k2 = Circle(radius=s * 0.2, color=color, fill_opacity=0.85).move_to(sq.get_right())
    return VGroup(sq, k1, k2)


def honeycomb(color=GOLD, r=0.32) -> VGroup:
    cells = VGroup()
    for q, rr in [(0, 0), (1, 0), (-1, 0), (0.5, 0.866), (-0.5, 0.866), (0.5, -0.866), (-0.5, -0.866)]:
        cells.add(RegularPolygon(6, color=color, stroke_width=3).scale(r)
                  .rotate(PI / 6).move_to([q * r * 1.75, rr * r * 1.75, 0]))
    return cells


def clock_icon(color=TXT, r=0.6) -> VGroup:
    c = Circle(radius=r, color=color, stroke_width=4)
    ticks = VGroup(*[Line(r * 0.82 * np.array([np.cos(a), np.sin(a), 0]),
                          r * np.array([np.cos(a), np.sin(a), 0]), color=color, stroke_width=3)
                     for a in np.linspace(0, TAU, 12, endpoint=False)])
    hh = Line(ORIGIN, [0, r * 0.55, 0], color=color, stroke_width=5)
    mm = Line(ORIGIN, [r * 0.7, 0, 0], color=color, stroke_width=4)
    return VGroup(c, ticks, hh, mm)


def comment_bubble(text: str) -> VGroup:
    t = kinetic_text(text, fs=52, color=BG, max_w=6.6)
    box = RoundedRectangle(width=t.width + 0.6, height=t.height + 0.5, corner_radius=0.3,
                           color=TXT, fill_color=TXT, fill_opacity=1)
    tail = Polygon(box.get_corner(DL) + RIGHT * 0.6, box.get_corner(DL) + RIGHT * 1.3,
                   box.get_corner(DL) + RIGHT * 0.3 + DOWN * 0.45, color=TXT,
                   fill_color=TXT, fill_opacity=1)
    t.move_to(box)
    return VGroup(tail, box, t)


def banner(text: str, color=GOLD, y=Y_CAP) -> VGroup:
    t = kinetic_text(text, fs=52, color=BG, max_w=7.3)
    bar = Rectangle(width=8.0, height=t.height + 0.5, color=color, fill_color=color,
                    fill_opacity=1, stroke_width=0)
    g = VGroup(bar, t.move_to(bar))
    g.word_count = t.word_count
    return g.move_to([0, y, 0])


def explode(mob: Mobject, color=ALERT_HI, n=26, seed=3, radius=1.6) -> tuple[VGroup, list]:
    rnd = random.Random(seed)
    c = mob.get_center()
    parts = VGroup(*[Dot(c, radius=rnd.uniform(0.03, 0.08), color=color) for _ in range(n)])
    anims = []
    for p in parts:
        a = rnd.uniform(0, TAU)
        d = rnd.uniform(0.4, 1.0) * radius
        anims.append(p.animate.shift(d * np.array([np.cos(a), np.sin(a), 0])).set_opacity(0))
    return parts, anims


# ════════════════════════════════════════════════════════════════════════════
# ESCENA BASE
# ════════════════════════════════════════════════════════════════════════════
BLOCK_START_KEY = ["b0_helix", "b1_alliance", "b2_continents", "b3_anunnaki",
                   "b4_weishaupt", "b5_orsic", "b6_dumbs"]


class HiddenHistoryBase(Scene):
    """Elementos persistentes: estrellas, sello, etiqueta, hélice."""

    def setup_persistent(self, block: int):
        self.frame_no = int(round(TL[BLOCK_START_KEY[block]][0] * FPS))
        self.stars = starfield()
        self.add(self.stars)
        self.tag = label("RELATO ESPECULATIVO", color=TXT, fs=MIN_FS).set_opacity(0.45)
        self.tag.move_to([0, Y_TAG, 0]).align_to([SAFE_L + 0.05, 0, 0], LEFT)
        self.helix = Helix().move_to([0, Y_HELIX, 0])
        self.helix.set_stroke(DATA, opacity=0.35)
        self.stamp_mob = None
        self.cta_overlay = None
        if block > 0:
            # estado de la hélice acumulado de bloques anteriores (escenas sueltas)
            if block > 1:
                self.helix.tramo(0, 1).set_stroke(LIRA_BLUE, opacity=1)
            if block > 2:
                self.helix.tramo(2).set_stroke(LIRA_BLUE, opacity=1)
                self.helix.tramo(3).set_stroke(REPT_GREEN, opacity=1)
            if block > 3:
                self.helix.tramo(4, 5).set_stroke(GOLD, opacity=1)
            if block > 4:
                self.helix.tramo(6).set_stroke(ALERT, opacity=1)
            if block > 5:
                self.helix.tramo(7).set_stroke(ALERT_HI, opacity=1)
            self.add(self.helix, self.tag)

    def persistent(self) -> list[Mobject]:
        keep = [self.stars, self.helix, self.tag]
        if self.stamp_mob is not None:
            keep.append(self.stamp_mob)
        if self.cta_overlay is not None:
            keep.append(self.cta_overlay)
        return keep

    def transient(self, extra_keep=()) -> list[Mobject]:
        """Objetos del bloque actual (nunca algo que comparta piezas con lo persistente)."""
        keep = set()
        for m in list(self.persistent()) + list(extra_keep):
            keep.update(id(x) for x in m.get_family())
        return [m for m in self.mobjects
                if not any(id(x) in keep for x in m.get_family())]

    def clear_anims(self, **kw) -> list[Animation]:
        out = []
        for m in self.transient():
            out.append(FadeOut(m, **kw))
        return out

    def slam_stamp(self, text: str, color=ALERT_HI) -> list[Animation]:
        new = stamp(text, color)
        anims = [FadeIn(new, scale=1.8, rate_func=rush_into)]
        if self.stamp_mob is not None:
            anims.append(FadeOut(self.stamp_mob, scale=0.7))
        self.stamp_mob = new
        return anims

    # ------------------------------------------------------------------
    def run_blocks(self, blocks):
        for b in blocks:
            BLOCKS[b](self)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 0 — GANCHO + CTA (0:00–0:15)
# ════════════════════════════════════════════════════════════════════════════
def block0(s: HiddenHistoryBase):
    # --- 0:00 hélice cian + "Tu ADN no es solo humano."
    b = Beat(s, "b0_helix")
    hx = s.helix
    hx.save_state()                      # pose final (banda inferior)
    hx.set_stroke(DATA, opacity=1)
    hx.rotate(PI / 2).scale(1.05).move_to([0, -0.9, 0])
    t1 = head("Tu ADN no es solo humano.", fs=70, y=Y_HEAD + 0.3)
    b.play(Create(hx, lag_ratio=0.15), *s.slam_stamp("CLASIFICADO"), f=0.55)
    b.play(reveal(t1), FadeIn(s.tag), f=0.3)
    b.finish(hx)

    # --- 0:03 mutación a rojo + "Liranos. Dracos. Anunnaki." / "Una guerra..."
    b = Beat(s, "b0_mutate")
    t2 = head("Liranos. Dracos. Anunnaki.", color=TXT, fs=66, y=Y_HEAD + 0.3)
    t3 = head("Una guerra de millones de años.", color=ALERT_HI, fs=66, y=Y_HEAD + 0.3)
    b.play(FadeOut(t1, shift=UP * 0.4), reveal(t2),
           hx.animate.set_stroke(ALERT_HI, opacity=1), f=0.35)
    b.play(Wiggle(hx, scale_value=1.05, rotation_angle=0.02 * TAU), f=0.15)
    b.play(FadeOut(t2, shift=UP * 0.4), reveal(t3), f=0.3)
    b.finish(hx)

    # --- 0:08 mapa estelar Lira — Draco + hélice a la banda inferior
    b = Beat(s, "b0_map")
    lira_c = VGroup(*[Dot(p, radius=0.07, color=DATA) for p in
                      [[-3.0, 1.9, 0], [-2.5, 1.5, 0], [-2.7, 0.9, 0], [-2.1, 1.0, 0], [-2.3, 0.4, 0]]])
    lira_l = VMobject(color=DATA, stroke_width=2).set_points_as_corners(
        [lira_c[i].get_center() for i in (0, 1, 2, 4, 3, 1)])
    draco_pts = [[3.2, -0.2, 0], [2.6, -0.6, 0], [2.9, -1.2, 0], [2.3, -1.6, 0],
                 [1.6, -1.4, 0], [1.2, -1.9, 0], [1.7, -2.4, 0]]
    draco_c = VGroup(*[Dot(p, radius=0.07, color=ALERT_HI) for p in draco_pts])
    draco_l = VMobject(color=ALERT_HI, stroke_width=2).set_points_as_corners(draco_pts)
    lbl_l = label("LIRA", DATA).next_to(lira_c, RIGHT, buff=0.3)
    lbl_d = label("DRACO", ALERT_HI).next_to(draco_c, LEFT, buff=0.3).shift(UP * 0.6)
    war = Line(lira_c[4].get_center(), draco_c[4].get_center(), color=ALERT_HI, stroke_width=5)
    t4 = head("Esto es lo que los archivos ocultan.", fs=64, y=Y_HEAD + 0.3)
    starmap = VGroup(lira_l, lira_c, draco_l, draco_c, lbl_l, lbl_d, war)
    b.play(Restore(hx), FadeOut(t3, shift=UP * 0.4), FadeIn(lira_c), FadeIn(draco_c),
           Create(lira_l), Create(draco_l), f=0.4)
    b.play(Create(war), FadeIn(lbl_l), FadeIn(lbl_d), reveal(t4), f=0.45)
    b.finish(starmap)

    # --- 0:12 CTA de apertura (cintillo + flecha a la esquina superior derecha)
    b = Beat(s, "b0_cta")
    c1 = banner("Quédate: el nombre de la sociedad")
    arrow = Arrow(c1.get_top() + RIGHT * 2.6, CORNER_TR, color=GOLD, stroke_width=8,
                  max_tip_length_to_length_ratio=0.12, buff=0.1)
    s.cta_overlay = VGroup(c1, arrow)
    b.play(FadeIn(c1, shift=UP * 0.5), GrowArrow(arrow), f=0.45)
    b.play(Indicate(war, color=GOLD), f=0.3)
    b.finish(starmap)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 — LIRA Y DRACO (0:15–0:45)
# ════════════════════════════════════════════════════════════════════════════
def block1(s: HiddenHistoryBase):
    # --- Alianza lira-vegana
    b = Beat(s, "b1_alliance")
    keep_cta = s.cta_overlay
    if keep_cta is None:  # escena suelta: recrea el cintillo de apertura
        c1 = banner("Quédate: el nombre de la sociedad")
        keep_cta = VGroup(c1, Arrow(c1.get_top() + RIGHT * 2.6, CORNER_TR, color=GOLD,
                                    stroke_width=8, max_tip_length_to_length_ratio=0.12))
        s.add(keep_cta)
    s.cta_overlay = None
    clear = [FadeOut(m) for m in s.transient(extra_keep=[keep_cta])]
    c2 = banner("que creó a los Illuminati aparece al final.")
    c2_arrow = keep_cta[1]
    b.play(*clear, *s.slam_stamp("DESCLASIFICADO"),
           FadeTransform(keep_cta[0], c2), f=0.08)
    g1 = head("Hace 22 millones de años,", fs=64)
    b.play(reveal(g1), f=0.12)
    stars_pos = {"LIRA": [-3.3, 1.9, 0], "VEGA": [-1.6, 1.1, 0], "SIRIO": [-3.1, 0.25, 0],
                 "ALTAIR": [-1.4, -0.6, 0], "ALFA CENTAURI": [-3.3, -1.45, 0],
                 "ORIÓN": [-1.6, -2.3, 0]}
    dots = VGroup()
    lbls = VGroup()
    for name, p in stars_pos.items():
        col = LIRA_BLUE if name == "LIRA" else DATA
        d = Dot(p, radius=0.13 if name == "LIRA" else 0.09, color=col)
        dots.add(d)
        lbls.add(label(name, col).next_to(d, RIGHT, buff=0.25))
    rays = VGroup(*[Line(dots[0].get_center(), d.get_center(), color=LIRA_BLUE,
                         stroke_width=3, stroke_opacity=0.8) for d in dots[1:]])
    lirano = humanoid(2.2, LIRA_BLUE, 0.85).move_to([2.9, -0.4, 0])
    g2 = head("los humanoides de Lira dominaban la galaxia.", fs=60)
    b.play(FadeOut(g1, shift=UP * 0.4), reveal(g2), FadeIn(dots[0], scale=3),
           FadeIn(lbls[0]), FadeOut(c2, shift=DOWN * 0.4), FadeOut(c2_arrow), f=0.2)
    b.play(LaggedStart(*[AnimationGroup(Create(r), FadeIn(d), FadeIn(l))
                         for r, d, l in zip(rays, dots[1:], lbls[1:])], lag_ratio=0.3),
           FadeIn(lirano, shift=UP * 0.3), f=0.3)
    g3 = head("Alianza lira-vegana.", color=DATA, fs=72)
    b.play(FadeOut(g2, shift=UP * 0.4), reveal(g3), Indicate(dots[1], scale_factor=2), f=0.15)
    b.finish(VGroup(dots, lbls, rays))

    # --- Imperio Draco
    b = Beat(s, "b1_draco")
    thuban = Dot([2.6, 1.4, 0], radius=0.16, color=ALERT_HI)
    glow = Circle(radius=0.5, color=ALERT_HI, stroke_width=3).move_to(thuban)
    thl = cap("ALPHA DRACONIS", color=ALERT_HI, fs=48, y=-2.45)
    dist = cap("THUBAN · 270 AÑOS LUZ", fs=48, y=Y_CAP)
    b.play(*s.clear_anims(shift=LEFT * 0.5),
           FadeIn(thuban, scale=4), Create(glow), FadeIn(thl), f=0.12)
    dh = draco_head(1.1).move_to([0, -0.1, 0])
    h1 = head("Imperio Alfa Draconiano.", color=REPT_GREEN, fs=64)
    b.play(GrowFromPoint(dh, thuban.get_center()), reveal(h1), FadeIn(dist), f=0.22)
    species = VGroup(*[Dot(radius=0.1, color=REPT_GREEN) for _ in range(7)])
    for i, d in enumerate(species):
        a = PI / 2 + i * TAU / 7
        d.move_to(dh.get_center() + 2.25 * np.array([np.cos(a), np.sin(a) * 0.85, 0]))
    h2 = head("Siete especies.", color=REPT_GREEN, fs=72)
    b.play(FadeOut(h1, shift=UP * 0.4), reveal(h2),
           LaggedStart(*[FadeIn(d, scale=3) for d in species], lag_ratio=0.15), f=0.2)
    h3 = head("Casta Royal White.", color=TXT, fs=72)
    d2 = cap("LLEGARON DESDE OTRA GALAXIA", fs=48)
    b.play(FadeOut(h2, shift=UP * 0.4), reveal(h3),
           dh[0].animate.set_fill(TXT, opacity=0.35).set_stroke(TXT),
           FadeOut(dist), FadeIn(d2), f=0.22)
    b.finish(dh)

    # --- Guerras de Lira: 3 de 14 planetas
    b = Beat(s, "b1_war")
    w1 = head("Guerras de Lira.", color=ALERT_HI, fs=72)
    planets = VGroup()
    for i in range(14):
        a = PI * 0.95 - i * PI * 0.9 / 13
        planets.add(Circle(radius=0.17, color=DATA, fill_opacity=0.6, stroke_width=2)
                    .move_to([3.3 * np.cos(a), 0.6 + 1.6 * np.sin(a) - 0.9, 0]))
    targets = [planets[4], planets[7], planets[10]]
    names = ["BILA", "TEKA", "MERCK"]
    big = VGroup(*[Circle(radius=0.55, color=DATA, fill_opacity=0.7).move_to(
        [x, -1.4, 0]) for x in (-2.6, 0, 2.6)])
    nl = VGroup(*[label(n, DATA).next_to(c, DOWN, buff=0.25) for n, c in zip(names, big)])
    b.play(*s.clear_anims(),
           reveal(w1), LaggedStart(*[FadeIn(p, scale=2) for p in planets], lag_ratio=0.05),
           f=0.18)
    w2 = head("3 de 14 planetas destruidos.", fs=62)
    b.play(*[TransformFromCopy(t, bg) for t, bg in zip(targets, big)], FadeIn(nl),
           FadeOut(w1, shift=UP * 0.4), reveal(w2), f=0.2)
    bursts = []
    parts_all = VGroup()
    for i, c in enumerate(big):
        parts, anims = explode(c, seed=10 + i, radius=1.8)
        parts_all.add(parts)
        bursts.append(AnimationGroup(*anims, FadeOut(c, scale=1.6)))
    s.add(parts_all)
    b.play(LaggedStart(*bursts, lag_ratio=0.35),
           *[t.animate.set_color(ALERT_HI) for t in targets],
           nl.animate.set_color(ALERT_HI), Flash(big[1].get_center(), color=ALERT_HI,
                                                  line_length=0.8, num_lines=16), f=0.35)
    b.finish(planets)

    # --- 50.000.000 + hélice azul + genocidio
    b = Beat(s, "b1_genocide")
    tracker = ValueTracker(0)

    def counter_mob():
        v = int(tracker.get_value())
        txt = f"{v:,}".replace(",", ".")
        return Text(txt, font=MONO, font_size=96, color=ALERT_HI, weight=BOLD).move_to([0, 0.3, 0])

    counter = always_redraw(counter_mob)
    sub = cap("DE LIRANOS MUERTOS", color=TXT, fs=54, y=-1.0)
    b.play(*s.clear_anims(),
           FadeIn(counter), f=0.06)
    b.play(tracker.animate(rate_func=rush_from).set_value(50_000_000), FadeIn(sub), f=0.38)
    counter.clear_updaters()
    g = head("El primer genocidio galáctico.", fs=64)
    b.play(reveal(g), s.helix.tramo(0, 1).animate.set_stroke(LIRA_BLUE, opacity=1),
           Indicate(s.helix.tramo(0, 1), color=LIRA_BLUE, scale_factor=1.1), f=0.35)
    b.finish(counter)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 — LEMURIA, ATLÁNTIDA Y LA HIBRIDACIÓN (0:45–1:15)
# ════════════════════════════════════════════════════════════════════════════
def block2(s: HiddenHistoryBase):
    b = Beat(s, "b2_continents")
    g = head("La Tierra fue el campo de batalla.", fs=62)
    b.play(*s.clear_anims(), *s.slam_stamp("CLASIFICADO"), reveal(g), f=0.14)
    ocean = VGroup(*[Line([-4, y, 0], [4, y, 0], color=DATA, stroke_width=1.2,
                          stroke_opacity=0.15) for y in np.arange(-2.4, 2.2, 0.3)])
    lem = blob(1.45, seed=4, color=REPT_GREEN).move_to([-1.95, 0.1, 0])
    atl = blob(1.45, seed=9, color=LIRA_BLUE).move_to([1.95, 0.1, 0])
    o1 = label("PACÍFICO", DATA).set_opacity(0.7).next_to(lem, DOWN, buff=0.35)
    o2 = label("ATLÁNTICO", DATA).set_opacity(0.7).next_to(atl, DOWN, buff=0.35)
    n1 = label("LEMURIA", REPT_GREEN).move_to(lem)
    n2 = label("ATLÁNTIDA", LIRA_BLUE).move_to(atl)
    b.play(FadeIn(ocean), DrawBorderThenFill(lem), DrawBorderThenFill(atl), f=0.2)
    g2 = head("Lemuria reptiliana.", color=REPT_GREEN, fs=70)
    b.play(FadeOut(g, shift=UP * 0.4), reveal(g2), FadeIn(n1), FadeIn(o1),
           Indicate(lem, color=REPT_GREEN), f=0.18)
    g3 = head("Atlántida de los Atlans.", color=LIRA_BLUE, fs=68)
    c = cap("REFUGIADOS LIRANOS DE LAS PLÉYADES", fs=48)
    b.play(FadeOut(g2, shift=UP * 0.4), reveal(g3), FadeIn(n2), FadeIn(o2), FadeIn(c),
           Indicate(atl, color=LIRA_BLUE), f=0.2)
    b.finish(VGroup(lem, atl))

    # --- Maldek y la extinción
    b = Beat(s, "b2_extinction")
    earth = Arc(radius=7, start_angle=PI * 0.36, angle=PI * 0.28, color=DATA, stroke_width=6)
    earth.move_to([0, -2.0, 0])
    dino = dinosaur().scale(0.75).move_to([0.3, -0.75, 0])
    m1 = head("Maldekianos:", color=ALERT_HI, fs=72)
    b.play(*s.clear_anims(), Create(earth), FadeIn(dino, shift=UP * 0.3), reveal(m1), f=0.18)
    rock = Dot([-3.6, 2.4, 0], radius=0.16, color=ALERT_HI)
    trail = TracedPath(rock.get_center, stroke_color=ALERT_HI, stroke_width=6,
                       dissipating_time=0.5)
    s.add(trail, rock)
    m2 = head("la extinción hace 65 millones de años.", fs=60)
    b.play(rock.animate(rate_func=rate_functions.ease_in_quad).move_to([1.0, -1.15, 0]),
           FadeOut(m1, shift=UP * 0.4), reveal(m2), f=0.25)
    flash = Circle(radius=0.2, color=ALERT_HI, fill_opacity=0.9).move_to([1.0, -1.15, 0])
    parts, anims = explode(dino, color=TXT, n=34, seed=5, radius=2.6)
    s.add(parts)
    b.play(flash.animate.scale(14).set_opacity(0), FadeOut(rock), FadeOut(dino, scale=1.2),
           *anims, earth.animate.set_color(ALERT_HI), f=0.22)
    s.remove(trail)
    c = cap("SUPERVIVIENTES DE MALDEK: ASIA", fs=48)
    b.play(FadeIn(c, shift=UP * 0.3), f=0.1)
    b.finish(earth)

    # --- Tratado de Andrómeda
    b = Beat(s, "b2_treaty")
    t1 = head("Tratado de Andrómeda:", color=GOLD, fs=66)
    ring = VGroup()
    for i in range(12):
        a = PI / 2 + i * TAU / 12
        ring.add(Dot([2.1 * np.cos(a), 0.1 + 2.1 * np.sin(a), 0], radius=0.14, color=LIRA_BLUE))
    rept = Dot([0, 0.1, 0], radius=0.2, color=REPT_GREEN)
    b.play(*s.clear_anims(), reveal(t1),
           LaggedStart(*[FadeIn(d, scale=2) for d in ring], lag_ratio=0.08), f=0.18)
    t2 = head("12 razas humanoides + 1 reptiliana.", fs=60)
    n12 = label("×12", LIRA_BLUE, fs=56).next_to(ring, RIGHT, buff=-0.2).shift(UP * 1.7)
    n1 = label("×1", REPT_GREEN, fs=56).next_to(rept, DOWN, buff=0.3)
    b.play(FadeOut(t1, shift=UP * 0.4), reveal(t2), FadeIn(rept, scale=3),
           FadeIn(n12), FadeIn(n1), f=0.18)
    mix_target = s.helix.tramo(2, 3)
    b.play(*[d.animate.move_to(mix_target.get_center() + RIGHT * (i - 6) * 0.1).scale(0.3)
             for i, d in enumerate(ring)],
           rept.animate.move_to(mix_target.get_center()).scale(0.3),
           FadeOut(n12), FadeOut(n1), f=0.2)
    b.play(FadeOut(ring), FadeOut(rept), s.helix.tramo(2).animate.set_stroke(LIRA_BLUE, opacity=1),
           s.helix.tramo(3).animate.set_stroke(REPT_GREEN, opacity=1),
           Indicate(mix_target, scale_factor=1.12, color=REPT_GREEN), f=0.14)
    c = cap("SABOTAJE DRACO: CONTROL TELEPÁTICO", color=ALERT_HI, fs=48)
    eye = draco_head(0.8).move_to([0, 0, 0])
    b.play(FadeIn(c), FadeIn(eye, scale=0.6), f=0.12)
    b.finish(eye)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — ANUNNAKI Y EL HOMO SAPIENS (1:15–1:45)
# ════════════════════════════════════════════════════════════════════════════
def block3(s: HiddenHistoryBase):
    b = Beat(s, "b3_anunnaki")
    h1 = head("Hace 300.000 años, los dioses volvieron.", fs=60)
    nib = Circle(radius=0.9, color=ALERT_HI, fill_color=ALERT, fill_opacity=0.8).move_to([2.3, 1.0, 0])
    halo = Circle(radius=1.25, color=GOLD, stroke_width=3).move_to(nib)
    orbit = Ellipse(width=7.6, height=2.4, color=GOLD, stroke_width=2,
                    stroke_opacity=0.5).rotate(-12 * DEGREES).move_to([0, 0.2, 0])
    an = anunnaki(3.6).move_to([-1.3, -0.4, 0])
    b.play(*s.clear_anims(), *s.slam_stamp("DESCLASIFICADO", GOLD), reveal(h1), f=0.2)
    nl = label("NIBIRU", GOLD).next_to(nib, DOWN, buff=0.45)
    b.play(Create(orbit), GrowFromCenter(nib), Create(halo), FadeIn(nl), f=0.2)
    h2 = head("Anunnaki de Nibiru.", color=GOLD, fs=70)
    b.play(FadeOut(h1, shift=UP * 0.4), reveal(h2), FadeIn(an, shift=UP * 0.5), f=0.2)
    h3 = head("En busca de oro.", color=GOLD, fs=72)
    ore = VGroup(*[Square(side_length=0.22, color=GOLD, fill_opacity=1).rotate(PI / 4)
                   .move_to([x, -2.5, 0]) for x in np.linspace(-2.5, 2.5, 9)])
    b.play(FadeOut(h2, shift=UP * 0.4), reveal(h3),
           LaggedStart(*[FadeIn(o, shift=UP * 0.4) for o in ore], lag_ratio=0.1), f=0.2)
    b.finish(an)

    b = Beat(s, "b3_sapiens")
    c1 = cap("PROTOTIPOS REPTILIANOS · ÁFRICA", color=REPT_GREEN, fs=48)
    er = hominid(False, REPT_GREEN).scale(1.05).move_to([0, -0.1, 0])
    lbl = label("HOMO ERECTUS", REPT_GREEN).move_to([0, 2.15, 0])
    i1 = head("Ingeniería genética:", color=DATA, fs=68)
    b.play(*s.clear_anims(), FadeIn(er, shift=RIGHT * 0.4), FadeIn(lbl), FadeIn(c1),
           reveal(i1), f=0.22)
    sap = hominid(True, GOLD).scale(1.05).move_to([0, -0.1, 0])
    lbl2 = label("HOMO SAPIENS", GOLD).move_to(lbl)
    scan = Line([-3, 2, 0], [3, 2, 0], color=DATA, stroke_width=5)
    s.add(scan)
    b.play(scan.animate.move_to([0, -2.2, 0]), Transform(er, sap), Transform(lbl, lbl2), f=0.3)
    s.remove(scan)
    i2 = head("el esclavo perfecto.", color=GOLD, fs=70)
    b.play(FadeOut(i1, shift=UP * 0.4), reveal(i2), FadeOut(c1), f=0.2)
    b.finish(er)

    b = Beat(s, "b3_gold")
    gtxt = head("Todos llevamos su huella.", color=GOLD, fs=66)
    ground = Line([-4, -0.6, 0], [4, -0.6, 0], color=TXT, stroke_width=4)
    people = VGroup(*[humanoid(1.2, GOLD, 0.85).move_to([x, 0.1, 0]) for x in (-2.4, -0.8, 0.8, 2.4)])
    under = VGroup(*[draco_head(0.35).move_to([x, -1.8, 0]) for x in (-2.0, 0, 2.0)])
    hell = Rectangle(width=8, height=1.7, fill_color=ALERT, fill_opacity=0.35,
                     stroke_width=0).move_to([0, -1.5, 0])
    c = cap("HACE ~200.000 AÑOS: LA BATALLA FINAL", color=TXT, fs=48)
    b.play(*s.clear_anims(), reveal(gtxt), s.helix.animate.set_stroke(GOLD, opacity=1),
           f=0.22)
    b.play(Create(ground), FadeIn(people, shift=UP * 0.3), FadeIn(hell),
           FadeIn(under, shift=DOWN * 0.3), FadeIn(c), f=0.3)
    b.play(s.helix.animate.set_stroke(DATA, opacity=0.35),
           s.helix.tramo(0, 1, 2).animate.set_stroke(LIRA_BLUE, opacity=1),
           s.helix.tramo(3).animate.set_stroke(REPT_GREEN, opacity=1),
           s.helix.tramo(4, 5).animate.set_stroke(GOLD, opacity=1), f=0.2)
    b.finish(people)

    # --- Enoc, Vimanas, Mohenjo-Daro
    b = Beat(s, "b3_enoc")
    e1 = head("Libro de Enoc: 200 Vigilantes.", color=TXT, fs=62)
    fall = VGroup(*[Dot([random.Random(i).uniform(-3.6, 3.6), 2.2, 0], radius=0.05, color=GOLD)
                    for i in range(40)])
    b.play(*s.clear_anims(), reveal(e1), FadeIn(fall), f=0.12)
    nef = cap("HIJAS DE LOS HOMBRES → NEFILIM", color=GOLD, fs=48)
    b.play(*[d.animate.shift(DOWN * random.Random(i + 99).uniform(2.4, 4.0))
             for i, d in enumerate(fall)], FadeIn(nef), f=0.2)
    vm = vimana().scale(0.85).move_to([0, 0.0, 0])
    e2 = head("Vimanas: carros voladores.", color=GOLD, fs=64)
    c2 = cap("RAMAYANA · MAHABHARATA", fs=48)
    b.play(FadeOut(fall), FadeOut(e1, shift=UP * 0.4), reveal(e2),
           FadeIn(vm, shift=LEFT * 1.5), FadeTransform(nef, c2), f=0.2)
    tre = trefoil(0.95).move_to([0, 0, 0])
    e3 = head("Mohenjo-Daro: radiación 50 veces superior.", color=ALERT_HI, fs=58)
    c3 = cap("PIEDRAS FUNDIDAS Y CRISTALIZADAS", color=TXT, fs=48)
    b.play(FadeOut(vm, shift=RIGHT * 1.5), FadeOut(e2, shift=UP * 0.4), reveal(e3),
           SpinInFromNothing(tre), FadeTransform(c2, c3), f=0.22)
    b.play(Rotate(tre[0], angle=PI / 3, about_point=tre.get_center()), f=0.12)
    b.finish(tre)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — SOCIEDADES SECRETAS Y NOBLEZA NEGRA (1:45–2:15)
# ════════════════════════════════════════════════════════════════════════════
def block4(s: HiddenHistoryBase):
    b = Beat(s, "b4_weishaupt")
    k1 = head("Los híbridos se organizaron.", fs=64)
    b.play(*s.clear_anims(), *s.slam_stamp("CLASIFICADO"), reveal(k1), f=0.1)
    k2 = head("Y juraron venganza.", color=ALERT_HI, fs=70)
    bust = bust_profile().scale(0.9).move_to([-1.4, -0.3, 0])
    eye = illuminati_eye(0.85).move_to([2.2, 0.9, 0])
    b.play(FadeOut(k1, shift=UP * 0.4), reveal(k2), FadeIn(bust, shift=RIGHT * 0.4), f=0.14)
    k3 = head("1776: Illuminati de Baviera.", color=GOLD, fs=64)
    n = cap("ADAM WEISHAUPT", color=TXT, fs=54)
    b.play(FadeOut(k2, shift=UP * 0.4), reveal(k3), FadeIn(n), DrawBorderThenFill(eye), f=0.18)
    k4 = head("1782: Congreso de Wilhelmsbad.", color=DATA, fs=62)
    n2 = cap("SE INFILTRAN EN LA MASONERÍA", fs=48)
    sq = VGroup(Line([-0.7, -0.6, 0], [0, 0.6, 0], color=DATA, stroke_width=6),
                Line([0.7, -0.6, 0], [0, 0.6, 0], color=DATA, stroke_width=6),
                Line([-0.8, -0.1, 0], [0.8, -0.1, 0], color=DATA, stroke_width=6)
                ).move_to([2.2, -1.4, 0])
    b.play(FadeOut(k3, shift=UP * 0.4), reveal(k4), FadeTransform(n, n2), Create(sq), f=0.22)
    b.play(Indicate(eye, color=GOLD), f=0.12)
    b.finish(bust)

    b = Beat(s, "b4_obelisks")
    o1 = head("El triunvirato oculto:", color=GOLD, fs=66)
    pos = {"VATICANO": [0, 0.1], "LONDRES": [-2.1, -1.5], "WASHINGTON": [2.0, -1.5]}
    obs = VGroup()
    labs = VGroup()
    for name, (x, y) in pos.items():
        ob = obelisk(1.6).move_to([x, y + 0.9, 0])
        obs.add(ob)
        labs.add(label(name, TXT).next_to(ob, DOWN, buff=0.15))
    b.play(*s.clear_anims(), reveal(o1),
           LaggedStart(*[GrowFromEdge(o, DOWN) for o in obs], lag_ratio=0.25), f=0.25)
    tri = Polygon(*[o.get_center() for o in obs], color=ALERT_HI, stroke_width=4)
    o2 = head("City, Washington, Vaticano.", fs=56)
    b.play(FadeOut(o1, shift=UP * 0.4), reveal(o2), FadeIn(labs), Create(tri), f=0.25)
    c = cap("UN OBELISCO EGIPCIO EN SU CENTRO", color=GOLD, fs=48, y=-3.4)
    b.play(FadeIn(c), *[Indicate(o[2], color=GOLD, scale_factor=1.6) for o in obs], f=0.2)
    b.finish(obs)

    b = Beat(s, "b4_nobility")
    nb = head("La nobleza negra:", color=TXT, fs=70)
    ringd = VGroup()
    for i in range(13):
        a = PI / 2 + i * TAU / 13
        ringd.add(RegularPolygon(5, color=ALERT_HI, fill_opacity=0.6).scale(0.2)
                  .move_to([1.9 * np.cos(a), -0.1 + 1.9 * np.sin(a), 0]))
    n13 = Text("13", font=SANS, font_size=120, color=ALERT_HI, weight=BOLD).move_to([0, -0.1, 0])
    b.play(*s.clear_anims(), reveal(nb),
           LaggedStart(*[FadeIn(d, scale=2) for d in ringd], lag_ratio=0.06), FadeIn(n13), f=0.25)
    nb2 = head("13 familias, sangre reptiliana.", color=ALERT_HI, fs=62)
    fams = ["ORSINI", "BREAKSPEAR", "ALDOBRANDINI", "FARNESE", "SOMAGLIA"]
    fam = cap(fams[0], color=TXT, fs=54)
    b.play(FadeOut(nb, shift=UP * 0.4), reveal(nb2), FadeIn(fam),
           s.helix.tramo(6).animate.set_stroke(ALERT, opacity=1),
           Indicate(s.helix.tramo(6), color=ALERT_HI), f=0.15)
    for name in fams[1:]:
        nxt = cap(name, color=TXT, fs=54)
        b.play(FadeOut(fam, shift=UP * 0.3), FadeIn(nxt, shift=UP * 0.3), f=0.09)
        fam = nxt
    b.finish(ringd)

    b = Beat(s, "b4_papa")
    p1 = head("Pepe Orsini: el Papa Gris.", color=TXT, fs=64)
    tiers = VGroup(
        VGroup(Rectangle(width=3.6, height=1.0, color="#9A9A9A", fill_opacity=0.9),
               label("PAPA GRIS", BG, fs=54)),
        VGroup(Rectangle(width=5.4, height=1.0, color=TXT, fill_opacity=0.25),
               label("PAPA BLANCO", TXT, fs=54)),
        VGroup(Rectangle(width=7.2, height=1.0, color=TXT, fill_opacity=0.08),
               label("PAPA NEGRO", TXT, fs=54)),
    ).arrange(DOWN, buff=0.2).move_to([0, -0.2, 0])
    b.play(*s.clear_anims(), reveal(p1),
           LaggedStart(*[FadeIn(t, shift=UP * 0.3) for t in reversed(tiers)], lag_ratio=0.3),
           f=0.35)
    c = cap("VATICANO · BANCA · POLÍTICA", color=ALERT_HI, fs=48)
    b.play(Indicate(tiers[0], color=GOLD, scale_factor=1.08), FadeIn(c), f=0.25)
    b.finish(tiers)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — NAZIS, VRIL Y BASE 211 (2:15–2:45)
# ════════════════════════════════════════════════════════════════════════════
def block5(s: HiddenHistoryBase):
    b = Beat(s, "b5_orsic")
    a1 = head("En 1919, una médium contactó con Aldebarán.", fs=58)
    b.play(*s.clear_anims(), *s.slam_stamp("DESCLASIFICADO", DATA), reveal(a1), f=0.12)
    wm = woman_silhouette(TXT).scale(0.95).move_to([-2.2, -0.5, 0])
    ald = Dot([2.6, 1.6, 0], radius=0.18, color=ALERT_HI)
    aldl = label("ALDEBARÁN", ALERT_HI).next_to(ald, DOWN, buff=0.3).align_to([SAFE_R, 0, 0], RIGHT)
    name = cap("MARIA ORSIC · 1919–1922", color=TXT, fs=48)
    b.play(FadeIn(wm, shift=UP * 0.3), FadeIn(ald, scale=4), FadeIn(aldl), FadeIn(name), f=0.15)
    waves = VGroup(*[Arc(radius=0.5 + i * 0.55, start_angle=PI * 1.02, angle=PI * 0.42,
                         color=DATA, stroke_width=4).move_arc_center_to(ald.get_center())
                     for i in range(6)])
    a2 = head("Transmisiones en sumerio y aldebarán.", color=DATA, fs=60)
    b.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=0.25),
           FadeOut(a1, shift=UP * 0.4), reveal(a2), f=0.28)
    glyphs = VGroup(*[cuneiform(seed=i) for i in range(6)])
    glyphs.arrange_in_grid(2, 3, buff=0.35).move_to([1.5, -0.6, 0])
    if glyphs.width > 4.6:
        glyphs.scale_to_fit_width(4.6)
    b.play(LaggedStart(*[FadeIn(g, shift=LEFT * 0.4) for g in glyphs], lag_ratio=0.15),
           *[w.animate.set_stroke(opacity=0.25) for w in waves], f=0.22)
    b.finish(wm)

    b = Beat(s, "b5_haunebu")
    grid = blueprint_grid()
    disc = disc_ship().move_to([0, -0.1, 0])
    h1 = head("1922: primer prototipo.", color=DATA, fs=66)
    b.play(*s.clear_anims(), FadeIn(grid), reveal(h1), f=0.14)
    b.play(Create(disc, lag_ratio=0.2), f=0.3)
    dims = VGroup(DashedLine([-2.5, 1.3, 0], [2.5, 1.3, 0], color=DATA, stroke_width=2),
                  label("HAUNEBU", DATA).move_to([-2.3, -1.9, 0]),
                  label("VRIL", DATA).move_to([2.6, -1.9, 0]))
    h2 = head("1934: primer vuelo.", color=GOLD, fs=70)
    c = cap("RFZ-1 · ANTIGRAVEDAD", color=GOLD, fs=48)
    b.play(FadeOut(h1, shift=UP * 0.4), reveal(h2), FadeIn(dims), FadeIn(c), f=0.22)
    b.play(disc.animate.shift(UP * 0.6).rotate(4 * DEGREES), f=0.2)
    b.finish(disc)

    b = Beat(s, "b5_thule")
    t1 = head("Sociedad Thule. Sociedad Vril.", fs=64)
    b.play(*s.clear_anims(), reveal(t1), f=0.15)
    card = RoundedRectangle(width=7.6, height=3.6, corner_radius=0.2, color=GOLD,
                            stroke_width=4).move_to([0, -0.3, 0])
    ct = kinetic_text("El misterio de Belicena Villca", fs=56, color=GOLD, max_w=7.0)
    ct.move_to(card.get_top() + DOWN * 0.85)
    au = label("NIMROD DE ROSARIO", TXT, fs=48).next_to(ct, DOWN, buff=0.3)
    b.play(Create(card), reveal(ct), FadeIn(au), f=0.25)
    ag = label("AGHARTA", DATA, fs=54).move_to(card.get_bottom() + UP * 0.6 + LEFT * 2.0)
    vs = label("vs", TXT, fs=48).move_to(card.get_bottom() + UP * 0.6)
    fb = label("GOLEMS", ALERT_HI, fs=54).move_to(card.get_bottom() + UP * 0.6 + RIGHT * 2.0)
    c = cap("FRATERNIDAD BLANCA: SIDDHAS TRAIDORES", color=ALERT_HI, fs=48)
    b.play(FadeIn(ag, shift=RIGHT * 0.4), FadeIn(vs), FadeIn(fb, shift=LEFT * 0.4),
           FadeIn(c), f=0.25)
    b.finish(card)

    b = Beat(s, "b5_base")
    ant = blob(2.1, seed=21, jitter=0.18, n=18, color=TXT, fill=0.12).move_to([0, -0.4, 0])
    bs = Dot([0.7, -0.1, 0], radius=0.14, color=ALERT_HI)
    bl = label("BASE 211", ALERT_HI, fs=54).next_to(bs, DOWN, buff=0.3)
    h1 = head("Base 211: Antártida.", color=TXT, fs=70)
    b.play(*s.clear_anims(), *s.slam_stamp("CLASIFICADO"), DrawBorderThenFill(ant),
           reveal(h1), f=0.18)
    pulses = VGroup(*[Circle(radius=0.2, color=ALERT_HI, stroke_width=3).move_to(bs)
                      for _ in range(3)])
    b.play(FadeIn(bs, scale=3), FadeIn(bl),
           LaggedStart(*[p.animate.scale(6).set_stroke(opacity=0) for p in pulses],
                       lag_ratio=0.3), f=0.2)
    ships = VGroup(*[Triangle(color=DATA, fill_opacity=1).scale(0.16).rotate(-PI / 4)
                     .move_to([-3.5 + i * 0.5, -2.4 - i * 0.2, 0]) for i in range(3)])
    h2 = head("Operación Highjump: 1947, almirante Byrd.", color=DATA, fs=58)
    c = cap("ALMIRANTE RICHARD BYRD", color=TXT, fs=48)
    b.play(FadeOut(h1, shift=UP * 0.4), reveal(h2), FadeIn(ships), FadeIn(c), f=0.2)
    b.play(*[sh.animate.move_to(bs.get_center() + [-(0.7 + i * 0.35), -0.6 - i * 0.2, 0])
             for i, sh in enumerate(ships)], f=0.25)
    b.finish(ant)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 — QANON, DUMBS Y EL GRAN DESPERTAR (2:45–3:00)
# ════════════════════════════════════════════════════════════════════════════
def block6(s: HiddenHistoryBase):
    b = Beat(s, "b6_dumbs")
    s.helix.tramo(7).set_stroke(ALERT_HI, opacity=1)
    # fragmentación de la hélice -> sellos CLASIFICADO apilados
    pieces = VGroup(*[sm for tramo in s.helix.tramos for sm in (tramo[0], tramo[1])])
    rnd = random.Random(42)
    b.play(*s.clear_anims(),
           *[p.animate.shift([rnd.uniform(-0.6, 0.6), rnd.uniform(0.3, 1.6), 0])
             .rotate(rnd.uniform(-1, 1)) for p in pieces],
           *[t[2].animate.set_opacity(0) for t in s.helix.tramos], f=0.12)
    stack = VGroup(*[stamp("CLASIFICADO", c) for c in (ALERT, ALERT_HI, ALERT_HI)])
    for i, st in enumerate(stack):
        st.shift(UP * 0.1 * i + RIGHT * 0.16 * i).rotate((i - 1) * 3 * DEGREES)
    old = s.stamp_mob
    s.stamp_mob = stack
    s.remove(s.helix)
    b.play(ReplacementTransform(pieces, stack), FadeOut(old), f=0.16)
    s.helix = VGroup()
    q1 = head("DUMBs: ciudades subterráneas.", color=TXT, fs=64)
    surface = Line([-4, 1.2, 0], [4, 1.2, 0], color=TXT, stroke_width=5)
    city = VGroup(*[Rectangle(width=0.4, height=h, color=TXT, fill_opacity=0.6)
                    .move_to([x, 1.2 + h / 2, 0]) for x, h in
                    zip(np.linspace(-3.2, 3.2, 9), [0.6, 1.0, 0.5, 1.3, 0.8, 1.1, 0.6, 0.9, 0.5])])
    tunnels = VGroup(Line([-3.6, -0.3, 0], [3.6, -0.3, 0]), Line([-3.0, -1.6, 0], [3.0, -1.6, 0]),
                     Line([-2.2, 1.2, 0], [-2.2, -1.6, 0]), Line([1.4, 1.2, 0], [1.4, -2.4, 0]),
                     Line([1.4, -2.4, 0], [3.4, -2.4, 0])).set_stroke(ALERT_HI, 6)
    nodes = VGroup(*[Square(side_length=0.36, color=ALERT_HI, fill_opacity=0.8).move_to(p)
                     for p in [[-2.2, -0.3, 0], [1.4, -0.3, 0], [-2.2, -1.6, 0],
                               [1.4, -1.6, 0], [3.4, -2.4, 0]]])
    b.play(reveal(q1), Create(surface), FadeIn(city, shift=UP * 0.2), f=0.15)
    c = cap("DEEP UNDERGROUND MILITARY BASES", color=DATA, fs=48)
    b.play(Create(tunnels, lag_ratio=0.3), FadeIn(nodes), FadeIn(c), f=0.2)
    q2 = head("Adrenocromo.", color=ALERT_HI, fs=80)
    b.play(FadeOut(q1, shift=UP * 0.4), reveal(q2),
           *[Indicate(n, color=ALERT_HI) for n in nodes], f=0.15)
    b.finish(tunnels)

    b = Beat(s, "b6_awaken")
    w1 = head("El Gran Despertar.", color=GOLD, fs=72)
    icons = VGroup(puzzle_piece(DATA, 0.9), honeycomb(GOLD, 0.32), clock_icon(TXT, 0.62))
    icons.arrange(RIGHT, buff=1.0).move_to([0, 0.1, 0])
    il = VGroup(*[label(t, c, fs=48).next_to(i, DOWN, buff=0.45)
                  for t, c, i in zip(["PIEZA", "PANAL", "RELOJ"], [DATA, GOLD, TXT], icons)])
    b.play(*s.clear_anims(), reveal(w1),
           LaggedStart(*[FadeIn(i, scale=0.5) for i in icons], lag_ratio=0.25), f=0.3)
    w2 = head("La Tormenta.", color=TXT, fs=72)
    bolt = Polygon([0.2, 0.9, 0], [-0.4, -0.1, 0], [0.05, -0.1, 0], [-0.25, -1.0, 0],
                   [0.5, 0.15, 0], [0.05, 0.15, 0], color=GOLD, fill_opacity=1).move_to([0, -1.9, 0])
    b.play(FadeIn(il), FadeOut(w1, shift=UP * 0.4), reveal(w2), FadeIn(bolt, scale=1.6), f=0.3)
    b.play(Rotate(icons[2][3], angle=-PI, about_point=icons[2][0].get_center()), f=0.2)
    b.finish(icons)

    b = Beat(s, "b6_recap")
    r = [head("22 millones de años.", color=DATA, fs=74, y=0.6),
         head("Siete especies.", color=REPT_GREEN, fs=78, y=0.6),
         head("Una guerra.", color=ALERT_HI, fs=86, y=0.6)]
    b.play(*s.clear_anims(), FadeIn(r[0], scale=1.3), f=0.3)
    b.play(FadeOut(r[0], scale=0.7), FadeIn(r[1], scale=1.3), f=0.3)
    b.play(FadeOut(r[1], scale=0.7), FadeIn(r[2], scale=1.3), f=0.3)
    b.finish(r[2])

    # --- CTA de cierre
    b = Beat(s, "b6_cta")
    bubble = comment_bubble("¿Crees que somos híbridos? Dímelo.").move_to([0, 1.6, 0])
    b.play(*s.clear_anims(), FadeIn(bubble, shift=UP * 0.5, scale=0.8), f=0.18)
    c1 = banner("Si quieres que analice los archivos completos,", y=-1.6)
    arrow = Arrow([2.6, -0.9, 0], CORNER_TR + DOWN * 0.1, color=GOLD, stroke_width=8,
                  max_tip_length_to_length_ratio=0.1, buff=0.1)
    b.play(FadeIn(c1, shift=UP * 0.5), f=0.15)
    b.hold(0.12, bubble)
    c2 = banner("sígueme.", y=-1.6)
    b.play(FadeOut(c1[1], shift=UP * 0.3), Transform(c1[0], c2[0]),
           FadeIn(c2[1], scale=1.4), GrowArrow(arrow), f=0.18)
    b.play(Indicate(c2[1], color=BG, scale_factor=1.25), Wiggle(arrow), f=0.15)
    b.play(Indicate(bubble, color=TXT, scale_factor=1.06), f=0.15)
    b.finish(bubble)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


# ════════════════════════════════════════════════════════════════════════════
# ESCENAS (7 bloques + vídeo completo)
# ════════════════════════════════════════════════════════════════════════════
class _BlockScene(HiddenHistoryBase):
    BLOCK = 0

    def construct(self):
        self.setup_persistent(self.BLOCK)
        BLOCKS[self.BLOCK](self)


class Block0Hook(_BlockScene):
    BLOCK = 0


class Block1LiraDraco(_BlockScene):
    BLOCK = 1


class Block2Hibridacion(_BlockScene):
    BLOCK = 2


class Block3Anunnaki(_BlockScene):
    BLOCK = 3


class Block4Sociedades(_BlockScene):
    BLOCK = 4


class Block5Vril(_BlockScene):
    BLOCK = 5


class Block6QAnon(_BlockScene):
    BLOCK = 6


class FullVideo(HiddenHistoryBase):
    """Los 7 bloques en una sola toma continua: 180.0 s exactos."""

    def construct(self):
        self.setup_persistent(0)
        self.run_blocks(range(7))
        expected = int(round(TOTAL * FPS))
        if self.frame_no != expected:
            print(f"[AVISO] fotogramas={self.frame_no} esperados={expected}")
