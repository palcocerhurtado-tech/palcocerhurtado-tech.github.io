"""
main.py — «11-M: LA OPERACIÓN OCULTA»
Vídeo vertical 9:16 · 1080x1920 · 30 fps · 180.0 s exactos · Manim CE 0.18+

Render completo:   manim -qh main.py FullVideo
Bloques sueltos:   manim -qh main.py Block3Villarejo   (etc.)
Vista previa:      PREVIEW=1 manim main.py FullVideo  (540x960, 15 fps)

Sincronía: timeline.json (lo genera narration.py) fija el arranque de cada plano;
si no existe se usa una escaleta nominal. Estética poligonal; todo por código.
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
ALERT_HI = "#D2232A"
PANEL = "#141419"
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

SAFE = (-4.0, 4.0, -4.80, 6.08)  # x ∈ [60,1020] px · y ∈ [230,1536] px
MAX_W = 7.6
Y_STAMP = 5.55
HEAD_TOP = 4.85
Y_VIS = 0.35
Y_CAP = -2.55
Y_TL_LBL = -3.62
Y_TL = -4.22
CORNER_TR = np.array([3.75, 5.85, 0])
HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.environ.get("IMG_DIR", os.path.join(HERE, "img"))

# ── Fotos reales (opcionales): plano -> nombre de archivo en img/ (.jpg/.jpeg/.png/.webp)
# Si el archivo no existe, el plano se queda solo con los gráficos poligonales.
PHOTOS = {
    "b0_hook": "00_portada",
    "b0_date": "01_tren_atocha",
    "b0_toll": "02_homenaje",
    "b0_files": "03_sumario",
    "b1_perejil": "04_perejil_islote",
    "b1_theory": "05_perejil_soldados",
    "b2_prague": "06_cumbre_praga",
    "b2_iraq": "07_azores",
    "b3_villarejo": "08_villarejo",
    "b3_rejected": "09_audiencia_nacional",
    "b4_tedax": "10_tedax_el_pozo",
    "b4_found": "11_mochila_vallecas",
    "b4_xray": "12_radiografia",
    "b5_carrete": "13_policia_cientifica",
    "b5_leganes": "14_leganes",
    "b5_sentence": "15_juicio_2007",
}
PHOTO_W, PHOTO_H, PHOTO_Y = 7.8, 4.6, 0.2


def _find_img(stem: str):
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG"):
        p = os.path.join(IMG_DIR, stem + ext)
        if os.path.exists(p):
            return p
    return None


def archive_photo(stem: str, w=PHOTO_W, h=PHOTO_H, dim=0.55):
    """Foto de archivo: recorte al formato, duotono oscuro/hueso, brillo reducido y marco.
    Devuelve un Group (imagen + marco) o None si no hay archivo."""
    src = _find_img(stem)
    if src is None:
        return None
    from PIL import Image, ImageEnhance, ImageOps
    out_dir = os.path.join(IMG_DIR, "_proc")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"{stem}.png")
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB")
        tw, th = int(w * 120), int(h * 120)
        im = ImageOps.fit(im, (tw, th), method=Image.LANCZOS, centering=(0.5, 0.4))
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
        im = ImageOps.colorize(g, black="#0A0A0A", white="#E8E6E3", mid="#6E6458")
        im = ImageEnhance.Brightness(im).enhance(dim)
        im.save(dst)
    img = ImageMobject(dst)
    img.stretch_to_fit_width(w).stretch_to_fit_height(h)
    frame = Rectangle(width=w, height=h, color=GOLD, stroke_width=3, stroke_opacity=0.8)
    grp = Group(img, frame).move_to([0, PHOTO_Y, 0])
    grp.set_z_index(-5)
    return grp

# hitos de la línea de tiempo poligonal
MILESTONES = [("2002", -3.3), ("2002", -1.2), ("2004", 0.9), ("2019", 3.1)]  # Perejil, Praga, 11-M, Villarejo

# ════════════════════════════════════════════════════════════════════════════
# ESCALETA (sobrescrita por timeline.json)
# ════════════════════════════════════════════════════════════════════════════
DEFAULT_BEATS = [
    ("b0_hook", 0), ("b0_date", 3), ("b0_toll", 6), ("b0_names", 8), ("b0_files", 10), ("b0_cta", 12),
    ("b1_perejil", 15), ("b1_theory", 25), ("b1_link", 35),
    ("b2_prague", 45), ("b2_iraq", 55), ("b2_interp", 60),
    ("b3_villarejo", 75), ("b3_claim", 80), ("b3_rejected", 88), ("b3_audio", 95),
    ("b4_tedax", 105), ("b4_found", 112), ("b4_xray", 120),
    ("b5_carrete", 135), ("b5_leganes", 145), ("b5_sentence", 152),
    ("b6_recap", 165), ("b6_cta", 172),
]
BLOCK_START = ["b0_hook", "b1_perejil", "b2_prague", "b3_villarejo", "b4_tedax", "b5_carrete", "b6_recap"]


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
# RELOJ POR FOTOGRAMAS
# ════════════════════════════════════════════════════════════════════════════
class Beat:
    """Plano con fin absoluto. run_time=(n−0,5)/fps ⇒ Manim genera exactamente n fotogramas."""

    def __init__(self, scene: "OcultaBase", key: str):
        self.s = scene
        self.end_frame = int(round(TL[key][1] * FPS))
        self.span = max(2, self.end_frame - scene.frame_no)
        # capa de fotos reales: entra la del plano y sale la anterior en el primer play
        self.pending = []
        old = getattr(scene, "cur_photo", None)
        new = archive_photo(PHOTOS[key]) if key in PHOTOS else None
        if old is not None:
            self.pending.append(FadeOut(old))
        if new is not None:
            new.add_updater(lambda m, dt: m.scale(1 + 0.012 * dt))
            self.pending.append(FadeIn(new, scale=1.04))
        scene.photo_out, scene.cur_photo = old, new

    def left(self):
        return self.end_frame - self.s.frame_no

    def play(self, *anims, f=0.1, **kw):
        n = max(2, int(round(f * self.span)))
        if self.left() >= 2:
            n = min(n, self.left())
        anims = list(self.pending) + list(anims)
        self.pending = []
        self.s.play(*anims, run_time=(n - 0.5) / FPS, **kw)
        self.s.photo_out = None
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
    """Texto partido en palabras (submobjects) con ajuste al ancho seguro; nunca < 48.
    Los signos sueltos (· → –) se centran en la altura de las mayúsculas."""
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
    """Write para ≤4 palabras; cascada palabra a palabra para el resto."""
    if getattr(m, "nwords", 1) <= 4:
        return Write(m)
    return LaggedStart(*[FadeIn(w, shift=0.25 * UP, scale=1.12) for row in m for w in row], lag_ratio=0.12)


def assert_safe(m: Mobject, what=""):
    x0, x1, y0, y1 = SAFE
    e = 0.02
    ok = (m.get_left()[0] >= x0 - e and m.get_right()[0] <= x1 + e and
          m.get_bottom()[1] >= y0 - e and m.get_top()[1] <= y1 + e)
    assert ok, f"fuera de safe-zone: {what!r}"
    return m


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICOS POLIGONALES
# ════════════════════════════════════════════════════════════════════════════
def stamp(text="CLASIFICADO", color=ALERT_HI, fs=54, angle=4) -> VGroup:
    t = Text(text, font=MONO, font_size=fs, color=color, weight=BOLD)
    if t.width > 6.8:
        t.scale_to_fit_width(6.8)
    box = SurroundingRectangle(t, buff=0.16, color=color, stroke_width=6, corner_radius=0.06)
    return VGroup(box, t).rotate(angle * DEGREES)


STAMP_COL = {"CLASIFICADO": ALERT_HI, "DESCLASIFICADO": DATA}


def poly(points, color=TXT, fill=0.85, sw=2):
    return Polygon(*[[x, y, 0] for x, y in points], color=color, fill_color=color, fill_opacity=fill,
                   stroke_width=sw)


def bust(h=2.6, color=TXT, accent=DIM) -> VGroup:
    """Silueta poligonal genérica (sin rasgos)."""
    s = h / 2.6
    head = RegularPolygon(7, color=color, fill_opacity=0.92, stroke_width=0).scale(0.45 * s).move_to([0, 0.78 * s, 0])
    body = poly([(-1.0 * s, -1.2 * s), (-0.85 * s, -0.1 * s), (-0.35 * s, 0.25 * s), (0.35 * s, 0.25 * s),
                 (0.85 * s, -0.1 * s), (1.0 * s, -1.2 * s)], color, 0.92, 0)
    lapel = poly([(-0.3 * s, 0.2 * s), (0, -0.45 * s), (0.3 * s, 0.2 * s)], accent, 1, 0)
    return VGroup(body, lapel, head)


def soldier(h=2.4, color=TXT) -> VGroup:
    s = h / 2.4
    helmet = poly([(-0.42 * s, 0.85 * s), (-0.3 * s, 1.15 * s), (0.3 * s, 1.15 * s), (0.42 * s, 0.85 * s)], color, 0.95, 0)
    head = RegularPolygon(6, color=color, fill_opacity=0.9, stroke_width=0).scale(0.3 * s).move_to([0, 0.72 * s, 0])
    body = poly([(-0.6 * s, 0.38 * s), (0.6 * s, 0.38 * s), (0.5 * s, -0.5 * s), (0.3 * s, -1.2 * s),
                 (-0.3 * s, -1.2 * s), (-0.5 * s, -0.5 * s)], color, 0.9, 0)
    rifle = Line([0.5 * s, 0.2 * s, 0], [0.95 * s, 1.0 * s, 0], color=color, stroke_width=7)
    return VGroup(body, rifle, head, helmet)


def tedax_suit(h=2.8, color=TXT) -> VGroup:
    s = h / 2.8
    helmet = RegularPolygon(8, color=color, fill_opacity=0.95, stroke_width=0).scale(0.55 * s).move_to([0, 0.95 * s, 0])
    visor = poly([(-0.35 * s, 0.95 * s), (0.35 * s, 0.95 * s), (0.28 * s, 0.75 * s), (-0.28 * s, 0.75 * s)], DATA, 1, 0)
    body = poly([(-1.0 * s, 0.4 * s), (1.0 * s, 0.4 * s), (1.1 * s, -0.6 * s), (0.75 * s, -1.4 * s),
                 (-0.75 * s, -1.4 * s), (-1.1 * s, -0.6 * s)], color, 0.9, 0)
    plates = VGroup(*[Line([-0.7 * s, y * s, 0], [0.7 * s, y * s, 0], color=BG, stroke_width=4) for y in (0, -0.45, -0.9)])
    return VGroup(body, plates, helmet, visor)


def train_car(w=2.6, color=DATA) -> VGroup:
    body = poly([(-w / 2, -0.35), (-w / 2, 0.3), (-w / 2 + 0.2, 0.42), (w / 2 - 0.2, 0.42), (w / 2, 0.3),
                 (w / 2, -0.35)], color, 0.15, 4)
    win = VGroup(*[Rectangle(width=0.32, height=0.24, color=color, stroke_width=3).move_to([x, 0.08, 0])
                   for x in np.linspace(-w / 2 + 0.4, w / 2 - 0.4, 5)])
    wheels = VGroup(*[RegularPolygon(6, color=color, stroke_width=3).scale(0.12).move_to([x, -0.45, 0])
                      for x in (-w / 2 + 0.4, -w / 2 + 0.7, w / 2 - 0.7, w / 2 - 0.4)])
    return VGroup(body, win, wheels)


def backpack(color=TXT) -> VGroup:
    body = poly([(-0.75, -0.95), (-0.85, 0.35), (-0.45, 0.85), (0.45, 0.85), (0.85, 0.35), (0.75, -0.95)],
                color, 0.12, 5)
    pocket = poly([(-0.5, -0.8), (-0.55, -0.15), (0.55, -0.15), (0.5, -0.8)], color, 0.08, 3)
    strap = Arc(radius=0.3, start_angle=0, angle=PI, color=color, stroke_width=5).move_to([0, 1.0, 0])
    return VGroup(body, pocket, strap)


def phone(color=GOLD) -> VGroup:
    b = RoundedRectangle(width=0.55, height=1.0, corner_radius=0.08, color=color, stroke_width=4,
                         fill_color=PANEL, fill_opacity=1)
    scr = Rectangle(width=0.4, height=0.42, color=color, stroke_width=2).shift(UP * 0.18)
    keys = VGroup(*[Dot([x, y, 0], radius=0.025, color=color) for x in (-0.12, 0, 0.12) for y in (-0.15, -0.28, -0.41)])
    return VGroup(b, scr, keys)


def islet(color=GOLD) -> VGroup:
    sea = VGroup(*[Line([-4, y, 0], [4, y, 0], color=DATA, stroke_width=1.5, stroke_opacity=0.2)
                   for y in np.arange(-1.9, 2.4, 0.32)])
    coast = poly([(-4, -1.9), (-4, -0.9), (-2.6, -1.1), (-1.6, -0.7), (-0.4, -1.2), (1.0, -0.8), (2.4, -1.3),
                  (4, -1.0), (4, -1.9)], DIM, 0.6, 2)
    rock = poly([(0.3, 0.9), (0.9, 1.25), (1.5, 1.05), (1.7, 0.6), (1.2, 0.35), (0.55, 0.45)], color, 0.35, 4)
    return VGroup(sea, coast, rock)


def chain_link(color=GOLD) -> VGroup:
    a = RoundedRectangle(width=1.6, height=0.8, corner_radius=0.38, color=color, stroke_width=9).shift(LEFT * 0.55)
    b = RoundedRectangle(width=1.6, height=0.8, corner_radius=0.38, color=color, stroke_width=9).shift(RIGHT * 0.55)
    return VGroup(a, b)


def court_seal(color=GOLD) -> VGroup:
    ring = RegularPolygon(12, color=color, stroke_width=5).scale(1.3)
    roof = poly([(-0.9, 0.45), (0, 0.95), (0.9, 0.45)], color, 0.9, 0)
    cols = VGroup(*[Rectangle(width=0.16, height=0.85, color=color, fill_opacity=0.9, stroke_width=0)
                    .move_to([x, -0.05, 0]) for x in np.linspace(-0.6, 0.6, 5)])
    base = Rectangle(width=1.9, height=0.16, color=color, fill_opacity=0.9, stroke_width=0).move_to([0, -0.55, 0])
    return VGroup(ring, roof, cols, base)


def doc_sheet(w=3.2, h=4.0, color=TXT, lines=9, seed=1) -> VGroup:
    rnd = random.Random(seed)
    sheet = poly([(-w / 2, -h / 2), (-w / 2, h / 2), (w / 2 - 0.5, h / 2), (w / 2, h / 2 - 0.5), (w / 2, -h / 2)],
                 color, 0.9, 0)
    ls = VGroup(*[Line([-w / 2 + 0.3, h / 2 - 0.6 - k * (h - 1.0) / lines, 0],
                       [-w / 2 + 0.3 + rnd.uniform(0.5, 0.85) * (w - 0.6), h / 2 - 0.6 - k * (h - 1.0) / lines, 0],
                       color=DIM, stroke_width=6) for k in range(lines)])
    return VGroup(sheet, ls)


def waveform(color=DATA, seed=3, w=6.4) -> VGroup:
    rnd = random.Random(seed)
    xs = np.linspace(-w / 2, w / 2, 48)
    return VGroup(*[Line([x, -h, 0], [x, h, 0], color=color, stroke_width=6)
                    for x, h in zip(xs, [rnd.uniform(0.1, 1.0) for _ in xs])])


def film_roll(color=GOLD) -> VGroup:
    can = RegularPolygon(10, color=color, stroke_width=6, fill_color=PANEL, fill_opacity=1).scale(0.9)
    hub = RegularPolygon(6, color=color, stroke_width=4).scale(0.25)
    holes = VGroup(*[Dot(0.55 * np.array([np.cos(a), np.sin(a), 0]), radius=0.08, color=color)
                     for a in np.linspace(0, TAU, 6, endpoint=False)])
    strip = VGroup(Rectangle(width=2.6, height=0.7, color=color, stroke_width=4).move_to([1.9, -0.55, 0]),
                   *[Rectangle(width=0.5, height=0.42, color=color, stroke_width=2).move_to([1.0 + k * 0.62, -0.55, 0])
                     for k in range(4)])
    return VGroup(strip, can, hub, holes)


def building(color=TXT, w=3.0, h=2.4) -> VGroup:
    b = poly([(-w / 2, -h / 2), (-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h / 2)], color, 0.1, 4)
    wins = VGroup(*[Rectangle(width=0.36, height=0.36, color=color, stroke_width=3).move_to([x, y, 0])
                    for x in np.linspace(-w / 2 + 0.5, w / 2 - 0.5, 4) for y in np.linspace(-h / 2 + 0.6, h / 2 - 0.45, 3)])
    return VGroup(b, wins)


def burst(color=ALERT_HI, r=0.35) -> Polygon:
    pts = []
    for k in range(16):
        rr = r if k % 2 == 0 else r * 0.45
        a = k * TAU / 16
        pts.append([rr * np.cos(a), rr * np.sin(a), 0])
    return Polygon(*pts, color=color, fill_color=color, fill_opacity=0.9, stroke_width=0)


def puzzle(color=GOLD, s=0.9) -> VGroup:
    sq = Square(side_length=s, color=color, fill_opacity=0.85, stroke_width=0)
    k1 = RegularPolygon(6, color=color, fill_opacity=0.85, stroke_width=0).scale(s * 0.2).move_to(sq.get_top())
    k2 = RegularPolygon(6, color=color, fill_opacity=0.85, stroke_width=0).scale(s * 0.2).move_to(sq.get_right())
    return VGroup(sq, k1, k2)


def grain_field(n=110, seed=5) -> VGroup:
    rnd = random.Random(seed)
    return VGroup(*[Dot([rnd.uniform(-4.6, 4.6), rnd.uniform(-8.4, 8.4), 0], radius=rnd.uniform(0.008, 0.022),
                        color=TXT, fill_opacity=rnd.uniform(0.08, 0.3)) for _ in range(n)])


def poly_mesh(seed=9) -> VGroup:
    """Malla poligonal de fondo muy tenue."""
    rnd = random.Random(seed)
    pts = [np.array([rnd.uniform(-4.6, 4.6), rnd.uniform(-8.2, 8.2), 0]) for _ in range(46)]
    g = VGroup()
    for i, p in enumerate(pts):
        near = sorted(pts, key=lambda q: np.linalg.norm(q - p))[1:3]
        for q in near:
            g.add(Line(p, q, color=DATA, stroke_width=1, stroke_opacity=0.06))
    return g


# ════════════════════════════════════════════════════════════════════════════
# ESCENA BASE
# ════════════════════════════════════════════════════════════════════════════
class OcultaBase(Scene):
    LIT_AT_BLOCK = [[], [2], [2, 0], [2, 0, 1], [2, 0, 1, 3], [2, 0, 1, 3], [2, 0, 1, 3]]

    def setup_persistent(self, block: int):
        self.frame_no = int(round(TL[BLOCK_START[block]][0] * FPS))
        self.texts: list[tuple[Mobject, int]] = []
        self.violations: list[str] = []
        self.peak = (0, 0.0, [])
        self.grain = grain_field()
        self.mesh = poly_mesh()
        self.add(self.mesh, self.grain)
        self.stamp_mob = None
        self.cta_overlay = None
        # línea de tiempo poligonal
        pts = [np.array([-3.85, Y_TL, 0])]
        for k, (_, x) in enumerate(MILESTONES):
            pts.append(np.array([x - 0.55, Y_TL + (0.16 if k % 2 == 0 else -0.16), 0]))
            pts.append(np.array([x, Y_TL, 0]))
        pts.append(np.array([3.85, Y_TL + 0.12, 0]))
        self.tl_segs = VGroup(*[Line(pts[i], pts[i + 1], color=DATA, stroke_width=5) for i in range(len(pts) - 1)])
        self.tl_nodes = VGroup(*[RegularPolygon(6, color=DATA, stroke_width=4, fill_color=BG, fill_opacity=1)
                                 .scale(0.17).move_to([x, Y_TL, 0]) for _, x in MILESTONES])
        self.tl_lbls = VGroup(*[Text(t, font=MONO, font_size=48, color=DIM, weight=BOLD).move_to([x, Y_TL_LBL, 0])
                                for t, x in MILESTONES])
        self.tl = VGroup(self.tl_segs, self.tl_nodes, self.tl_lbls)
        if block > 0:
            for i in self.LIT_AT_BLOCK[block]:
                self._light_static(i)
            self.add(self.tl)

    def _light_static(self, i, color=None):
        col = color or (ALERT_HI if i == 2 else GOLD)
        self.tl_nodes[i].set_fill(col, 1).set_stroke(col)
        self.tl_lbls[i].set_color(col)

    def light(self, i, color=None) -> list[Animation]:
        col = color or (ALERT_HI if i == 2 else GOLD)
        return [self.tl_nodes[i].animate.set_fill(col, 1).set_stroke(col).scale(1.0),
                self.tl_lbls[i].animate.set_color(col),
                Flash(self.tl_nodes[i].get_center(), color=col, line_length=0.3, num_lines=10)]

    # ── utilidades ───────────────────────────────────────────────────────
    def reg(self, m, n=None):
        self.texts.append((m, n if n is not None else getattr(m, "nwords", 1)))
        assert_safe(m, getattr(m, "text", ""))
        return m

    def head(self, text, color=TXT, fs=76, top=HEAD_TOP):
        m = kinetic_text(text, fs=fs, color=color)
        m.move_to(ORIGIN).shift(UP * (top - m.get_top()[1]))
        return self.reg(m)

    def cap(self, text, color=DATA, fs=48, y=Y_CAP, max_w=MAX_W):
        m = kinetic_text(text, fs=fs, color=color, font=MONO, max_w=max_w, max_lines=2)
        return self.reg(m.move_to([0, y, 0]))

    def big(self, text, color=TXT, fs=96, y=Y_VIS, font=None):
        m = kinetic_text(text, fs=fs, color=color, font=font or SANS, max_lines=3)
        return self.reg(m.move_to([0, y, 0]))

    def name(self, text, at, color=TXT, fs=48, max_w=3.8):
        t = Text(text, font=MONO, font_size=fs, color=color, weight=BOLD)
        if t.width > max_w:
            t.scale_to_fit_width(max_w)
        t.move_to(at)
        t.nwords, t.text = len(text.split()), text
        return self.reg(t)

    def counter(self, tracker, fmt, color=ALERT_HI, fs=150, y=Y_VIS):
        def mk():
            t = Text(fmt(tracker.get_value()), font=MONO, font_size=fs, color=color, weight=BOLD)
            if t.width > MAX_W:
                t.scale_to_fit_width(MAX_W)
            return t.move_to([0, y, 0])
        m = always_redraw(mk)
        self.texts.append((m, 1))
        return m

    def check_words(self):
        """Palabras de contenido visibles (sello y fechas de la línea = interfaz fija)."""
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
        k = [self.grain, self.mesh, self.tl]
        for m in (getattr(self, "cur_photo", None), getattr(self, "photo_out", None)):
            if m is not None:
                k.append(m)
        for m in (self.stamp_mob, self.cta_overlay):
            if m is not None:
                k.append(m)
        return k

    def clear(self, extra_keep=(), **kw) -> list[Animation]:
        ids = set()
        for m in list(self.keep()) + list(extra_keep):
            ids.update(id(x) for x in m.get_family())
        return [FadeOut(m, **kw) for m in self.mobjects if not any(id(x) in ids for x in m.get_family())]

    def slam(self, text="CLASIFICADO") -> list[Animation]:
        new = stamp(text, STAMP_COL[text])
        new.move_to([0, Y_STAMP, 0]).align_to([SAFE[0] + 0.05, 0, 0], LEFT)
        anims = [FadeIn(new, scale=1.8, rate_func=rush_into)]
        if self.stamp_mob is not None:
            anims.append(FadeOut(self.stamp_mob, scale=0.7))
        self.stamp_mob = new
        return anims

    def seq(self, b: Beat, texts, f_each, **kw):
        """Titulares sucesivos en la misma posición (uno sustituye al anterior)."""
        prev = None
        out = None
        for t in texts:
            out = self.head(t, **kw)
            anims = [reveal(out)]
            if prev is not None:
                anims.append(FadeOut(prev, shift=UP * 0.3))
            b.play(*anims, f=f_each)
            prev = out
        return out

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
def block0(s: OcultaBase):
    b = Beat(s, "b0_hook")
    t1 = s.big("¿Y si el 11-M", fs=100, y=1.6)
    b.play(Create(s.tl_segs, lag_ratio=0.2), FadeIn(s.tl_nodes), FadeIn(s.tl_lbls), *s.slam("CLASIFICADO"), f=0.3)
    s.add(s.tl)
    b.play(reveal(t1), f=0.3)
    t2 = s.big("esconde algo más?", color=GOLD, fs=92, y=-0.4)
    b.play(reveal(t2), f=0.3)
    b.finish(t2)

    b = Beat(s, "b0_date")
    d = s.big("11·03·2004", color=ALERT_HI, fs=120, y=3.4, font=MONO)
    c = s.cap("10 BOMBAS · 4 TRENES", color=TXT, y=1.9)
    b.play(FadeOut(VGroup(t1, t2), shift=UP * 0.4), reveal(d), FadeIn(c), *s.light(2), f=0.25)
    rows = VGroup()
    for k, st in enumerate(["ATOCHA", "EL POZO", "SANTA EUGENIA", "TÉLLEZ"]):
        y = 0.75 - 0.85 * k
        car = train_car(2.2).scale(0.55).move_to([-2.75, y, 0])
        bz = burst().move_to(car.get_center())
        lbl = s.name(st, [0.85, y, 0], color=TXT, fs=52, max_w=4.4)
        lbl.align_to([-1.6, 0, 0], LEFT)
        rows.add(VGroup(car, bz, lbl))
    b.play(LaggedStart(*[AnimationGroup(FadeIn(r[0], shift=RIGHT * 0.4), FadeIn(r[2])) for r in rows],
                       lag_ratio=0.25), FadeOut(c, shift=UP * 0.2), f=0.35)
    b.play(LaggedStart(*[GrowFromCenter(r[1]) for r in rows], lag_ratio=0.2), f=0.25)
    b.finish(rows)

    b = Beat(s, "b0_toll")
    tr = ValueTracker(0)
    cnt = s.counter(tr, lambda v: f"{int(v)}", color=ALERT_HI, fs=200, y=1.6)
    m1 = s.cap("MUERTOS", color=TXT, fs=60, y=0.0)
    gone = s.clear()
    s.add(cnt)
    b.play(*gone, tr.animate.set_value(193), FadeIn(m1), f=0.35)
    cnt.clear_updaters()
    m2 = s.cap("CASI 2.000 HERIDOS", color=TXT, fs=56, y=-0.8)
    b.play(FadeIn(m2, shift=UP * 0.2), f=0.2)
    urn = VGroup(poly([(-0.8, -0.7), (-0.8, 0.5), (0.8, 0.5), (0.8, -0.7)], DATA, 0.12, 5),
                 Line([-0.35, 0.5, 0], [0.35, 0.5, 0], color=BG, stroke_width=10),
                 poly([(-0.3, 0.45), (-0.3, 1.0), (0.35, 1.0), (0.35, 0.45)], TXT, 0.9, 0)).move_to([0, -1.3, 0])
    m3 = s.cap("3 DÍAS DESPUÉS: ELECCIONES", color=DATA, y=Y_CAP - 0.25)
    b.play(FadeOut(m2), FadeIn(urn, shift=UP * 0.3), FadeIn(m3), cnt.animate.scale(0.8).shift(UP * 0.5),
           m1.animate.shift(UP * 0.3), f=0.3)
    b.finish(urn)

    b = Beat(s, "b0_names")
    mar = VGroup(RegularPolygon(5, color=ALERT_HI, stroke_width=5).scale(1.0), )
    fra = VGroup(RegularPolygon(6, color=DATA, stroke_width=5).scale(1.0))
    mar.move_to([-1.9, 1.3, 0])
    fra.move_to([1.9, 1.3, 0])
    nm = s.name("MARRUECOS", [-1.9, -0.05, 0], color=ALERT_HI, fs=52)
    nf = s.name("FRANCIA", [1.9, -0.05, 0], color=DATA, fs=52)
    b.play(*s.clear(), DrawBorderThenFill(mar), DrawBorderThenFill(fra), FadeIn(nm), FadeIn(nf), f=0.25)
    ex = bust(1.6, TXT).move_to([0, -1.25, 0])
    links = VGroup(Line(ex.get_top(), mar.get_bottom(), color=GOLD, stroke_width=3),
                   Line(ex.get_top(), fra.get_bottom(), color=GOLD, stroke_width=3))
    c = s.cap("UN EXCOMISARIO SEÑALA", color=GOLD, y=Y_CAP - 0.2)
    b.play(FadeIn(ex, shift=UP * 0.3), Create(links), FadeIn(c), f=0.3)
    q = s.big("?", color=GOLD, fs=160, y=3.6)
    b.play(FadeIn(q, scale=2), Indicate(links, color=ALERT_HI), f=0.25)
    b.finish(ex)

    b = Beat(s, "b0_files")
    folders = VGroup()
    for k in range(4):
        f_ = VGroup(poly([(-1.6, -0.9), (-1.6, 0.8), (-0.6, 0.8), (-0.4, 1.0), (1.6, 1.0), (1.6, -0.9)], GOLD, 0.15, 4))
        f_.shift(UP * (0.25 * k) + RIGHT * (0.15 * k) + DOWN * 0.6)
        folders.add(f_)
    h = s.head("Esto es lo que dicen los archivos.", fs=76)
    b.play(*s.clear(), LaggedStart(*[FadeIn(f_, shift=UP * 0.3) for f_ in folders], lag_ratio=0.15), reveal(h), f=0.7)
    b.finish(folders)

    b = Beat(s, "b0_cta")
    c1 = kinetic_text("Quédate: la última pieza", fs=60, color=BG, max_w=7.2)
    s.reg(c1.move_to([0, Y_CAP + 0.1, 0]))
    bar = Rectangle(width=8.0, height=c1.height + 0.5, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(c1)
    arrow = Arrow(bar.get_top() + RIGHT * 2.7, CORNER_TR, color=GOLD, stroke_width=8, buff=0.1,
                  max_tip_length_to_length_ratio=0.1)
    s.cta_overlay = VGroup(bar, c1, arrow)
    b.play(FadeOut(h, shift=UP * 0.3), FadeIn(VGroup(bar, c1), shift=UP * 0.5), GrowArrow(arrow), f=0.6)
    b.finish(folders)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 — PEREJIL
# ════════════════════════════════════════════════════════════════════════════
def block1(s: OcultaBase):
    b = Beat(s, "b1_perejil")
    cta = s.cta_overlay
    if cta is None:
        c1 = kinetic_text("Quédate: la última pieza", fs=60, color=BG, max_w=7.2).move_to([0, Y_CAP + 0.1, 0])
        bar = Rectangle(width=8.0, height=c1.height + 0.5, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(c1)
        cta = VGroup(bar, c1, Arrow(bar.get_top() + RIGHT * 2.7, CORNER_TR, color=GOLD, stroke_width=8))
        s.add(cta)
    s.cta_overlay = None
    c2 = s.reg(kinetic_text("aparece al final.", fs=60, color=BG, max_w=7.2).move_to(cta[1]))
    b.play(*s.clear(extra_keep=[cta]), FadeTransform(cta[1], c2), *s.slam("DESCLASIFICADO"), f=0.12)
    isl = islet().move_to([0, 0.6, 0])
    lab = s.name("PEREJIL", isl[2].get_center() + UP * 1.25 + LEFT * 1.6, color=GOLD, fs=52)
    h = s.head("Julio de 2002.", color=GOLD, fs=84)
    b.play(FadeOut(VGroup(cta[0], c2, cta[2]), shift=DOWN * 0.3), reveal(h), FadeIn(isl), FadeIn(lab), *s.light(0), f=0.18)
    sold = VGroup(*[soldier(0.55, ALERT_HI) for _ in range(3)]).arrange(RIGHT, buff=0.05).move_to(isl[2].get_center())
    h2 = s.head("Marruecos ocupa Perejil.", color=ALERT_HI, fs=80)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in sold]), f=0.2)
    sp = VGroup(*[soldier(0.55, DATA) for _ in range(3)]).arrange(RIGHT, buff=0.05).move_to(isl[2].get_center())
    heli = poly([(-0.9, 0), (0.5, 0), (0.9, 0.2), (0.5, 0.4), (-0.6, 0.4)], DATA, 0.8, 0).move_to([-3.0, 2.2, 0])
    h3 = s.head("España lo recupera.", color=DATA, fs=80)
    c = s.cap("OPERACIÓN ROMEO-SIERRA", color=DATA)
    b.play(FadeOut(h2, shift=UP * 0.3), reveal(h3), heli.animate.move_to(isl[2].get_center() + UP * 1.0),
           FadeOut(sold, shift=DOWN * 0.2), FadeIn(sp, shift=DOWN * 0.3), FadeIn(c), f=0.25)
    b.finish(isl)

    b = Beat(s, "b1_theory")
    h = s.head("La teoría: el 11-M como venganza.", color=ALERT_HI, fs=72)
    arc_ = CurvedArrow(s.tl_nodes[0].get_top() + UP * 0.1, s.tl_nodes[2].get_top() + UP * 0.1, angle=-1.2,
                       color=ALERT_HI, stroke_width=6)
    sol = soldier(2.6, ALERT_HI).move_to([0, 0.4, 0])
    b.play(*s.clear(), reveal(h), FadeIn(sol, shift=UP * 0.3), f=0.4)
    b.play(Create(arc_), Indicate(s.tl_nodes[2], color=ALERT_HI, scale_factor=1.6), f=0.4)
    b.finish(sol)

    b = Beat(s, "b1_link")
    h = s.head("Ninguna prueba lo confirma.", color=TXT, fs=78)
    link = chain_link().move_to([0, 0.5, 0])
    b.play(*s.clear(), reveal(h), f=0.35)
    h2 = s.head("Primer eslabón.", color=GOLD, fs=92)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), Create(link), f=0.35)
    b.finish(link)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 — PRAGA, IRAK, INTÉRPRETES
# ════════════════════════════════════════════════════════════════════════════
def block2(s: OcultaBase):
    b = Beat(s, "b2_prague")
    star = VGroup(*[poly([(0, 0), (0.22, 0.22 if k % 2 else 0.12), (0, 1.3 if k % 2 == 0 else 0.8)], DATA, 0.85, 0)
                    .rotate(k * PI / 4, about_point=ORIGIN) for k in range(8)]).scale(0.72).move_to([0, 1.05, 0])
    leaders = VGroup(*[bust(1.0, TXT if k != 2 else GOLD) for k in range(5)]).arrange(RIGHT, buff=0.12).move_to([0, -0.95, 0])
    h = s.head("Noviembre de 2002.", color=DATA, fs=84)
    b.play(*s.clear(), *s.slam("CLASIFICADO"), reveal(h), GrowFromCenter(star), *s.light(1), f=0.2)
    h2 = s.head("Cumbre de la OTAN en Praga.", color=TXT, fs=76)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), LaggedStart(*[FadeIn(x, shift=UP * 0.3) for x in leaders],
                                                               lag_ratio=0.12), f=0.25)
    c = s.cap("MARZO 2003 · AZORES", color=GOLD)
    h3 = s.head("España apoya la invasión de Irak.", color=GOLD, fs=72)
    b.play(FadeOut(h2, shift=UP * 0.3), reveal(h3), FadeIn(c), Indicate(leaders[2], color=GOLD), f=0.3)
    b.finish(leaders)

    b = Beat(s, "b2_iraq")
    sp = RegularPolygon(6, color=GOLD, fill_color=GOLD, fill_opacity=0.9).scale(0.5).move_to([0, -0.6, 0])
    ma = RegularPolygon(5, color=ALERT_HI, stroke_width=5).scale(0.7).move_to([-2.4, 1.4, 0])
    iq = RegularPolygon(5, color=ALERT_HI, stroke_width=5).scale(0.7).move_to([2.4, 1.4, 0])
    n1 = s.name("MARRUECOS", [-2.1, 0.35, 0], color=ALERT_HI, fs=48, max_w=3.4)
    n2 = s.name("IRAK", [2.4, 0.35, 0], color=ALERT_HI, fs=48)
    n3 = s.name("ESPAÑA", [0, -1.55, 0], color=GOLD, fs=52)
    h = s.head("Dos frentes abiertos.", color=TXT, fs=84)
    b.play(*s.clear(), reveal(h), DrawBorderThenFill(ma), DrawBorderThenFill(iq), FadeIn(n1), FadeIn(n2), f=0.4)
    lines = VGroup(Line(ma.get_center(), sp.get_center(), color=ALERT_HI, stroke_width=4),
                   Line(iq.get_center(), sp.get_center(), color=ALERT_HI, stroke_width=4))
    b.play(Create(lines), GrowFromCenter(sp), FadeIn(n3), f=0.4)
    b.finish(sp)

    b = Beat(s, "b2_interp")
    ints = VGroup()
    for k in range(4):
        bs = bust(1.15, TXT)
        bub = VGroup(RoundedRectangle(width=0.9, height=0.5, corner_radius=0.15, color=DATA, stroke_width=3),
                     *[Dot([x, 0, 0], radius=0.05, color=DATA) for x in (-0.22, 0, 0.22)])
        bub.next_to(bs, UP, buff=0.08)
        ints.add(VGroup(bs, bub))
    ints.arrange(RIGHT, buff=0.18).move_to([0, 0.4, 0])
    h = s.head("¿Sin intérpretes de árabe?", color=DATA, fs=80)
    b.play(*s.clear(), reveal(h), LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in ints], lag_ratio=0.12), f=0.35)
    qs = VGroup(*[Text("?", font=SANS, font_size=110, color=GOLD, weight=BOLD).move_to(x[0].get_center()) for x in ints])
    c = s.cap("NINGÚN DOCUMENTO LO PRUEBA", color=GOLD)
    b.play(*[x[0].animate.set_opacity(0.25) for x in ints], FadeIn(qs, scale=1.5), FadeIn(c), f=0.35)
    b.finish(ints)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — VILLAREJO
# ════════════════════════════════════════════════════════════════════════════
def block3(s: OcultaBase):
    b = Beat(s, "b3_villarejo")
    v = bust(3.0, TXT, accent=GOLD).move_to([0, 0.35, 0])
    shadow = VGroup(*[Line([-4, y, 0], [4, y, 0], color=DIM, stroke_width=2, stroke_opacity=0.5)
                      for y in np.arange(-1.6, 2.4, 0.22)])
    h = s.head("El excomisario Villarejo.", color=GOLD, fs=80)
    b.play(*s.clear(), *s.slam("DESCLASIFICADO"), FadeIn(shadow), reveal(h), FadeIn(v, shift=UP * 0.3), f=0.4)
    c = s.cap("LAS CLOACAS DEL ESTADO", color=TXT)
    b.play(FadeIn(c, shift=UP * 0.2), shadow.animate.set_stroke(opacity=0.25), f=0.3)
    b.finish(v)

    b = Beat(s, "b3_claim")
    doc = doc_sheet(2.0, 2.4, TXT).move_to([-1.1, 2.35, 0]).rotate(4 * DEGREES)
    pg = s.name("15 PÁGINAS", [1.75, 2.35, 0], color=TXT, fs=52)
    yr = s.cap("2019 · AUDIENCIA NACIONAL", color=DATA)
    b.play(*s.clear(), FadeIn(doc, shift=UP * 0.4), FadeIn(pg), FadeIn(yr), *s.light(3), f=0.2)
    q1 = s.big("«Organizado y ejecutado»", color=GOLD, fs=68, y=0.0)
    b.play(reveal(q1), FadeOut(yr, shift=DOWN * 0.2), f=0.25)
    q2 = s.big("Francia y Marruecos.", color=ALERT_HI, fs=72, y=-1.95)
    b.play(reveal(q2), Indicate(doc, color=GOLD, scale_factor=1.03), f=0.25)
    b.finish(doc)

    b = Beat(s, "b3_rejected")
    seal = court_seal().move_to([0, 0.6, 0])
    h = s.head("Conjeturas sin base documental.", color=TXT, fs=76)
    b.play(*s.clear(), reveal(h), DrawBorderThenFill(seal), f=0.35)
    st = stamp("RECHAZADO", ALERT_HI, fs=72, angle=-12).move_to([0, 0.5, 0])
    s.reg(st[1], 1)
    c = s.cap("GARCÍA-CASTELLÓN · FISCALÍA", color=GOLD)
    b.play(FadeIn(st, scale=2.2, rate_func=rush_into), FadeIn(c), f=0.3)
    b.finish(seal)

    b = Beat(s, "b3_audio")
    wave = waveform().move_to([0, 0.5, 0])
    h = s.head("Una grabación de 2009.", color=DATA, fs=80)
    b.play(*s.clear(), reveal(h), LaggedStart(*[GrowFromCenter(l) for l in wave], lag_ratio=0.02), f=0.4)
    c = s.cap("MANDOS POLICIALES: ESA HIPÓTESIS", color=GOLD)
    b.play(FadeIn(c), *[l.animate.stretch(0.4 + (k % 5) * 0.3, 1) for k, l in enumerate(wave)], f=0.3)
    b.finish(wave)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — TEDAX Y LA MOCHILA
# ════════════════════════════════════════════════════════════════════════════
def block4(s: OcultaBase):
    b = Beat(s, "b4_tedax")
    h = s.head("La mochila de Vallecas.", color=GOLD, fs=80)
    car = train_car(6.0).move_to([0, 1.3, 0])
    td = tedax_suit(2.4).move_to([0, -0.85, 0])
    b.play(*s.clear(), *s.slam("CLASIFICADO"), reveal(h), FadeIn(car, shift=LEFT * 0.6), FadeIn(td, shift=UP * 0.3), f=0.25)
    scan = Line([-3.1, 0.75, 0], [-3.1, 1.85, 0], color=DATA, stroke_width=8)
    h2 = s.head("Dos revisiones. Nadie la vio.", color=TXT, fs=74)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), FadeIn(scan), scan.animate.shift(RIGHT * 6.2), f=0.25)
    b.play(scan.animate.shift(LEFT * 6.2), f=0.2)
    b.play(FadeOut(scan), Indicate(car, color=DATA, scale_factor=1.02), f=0.1)
    b.finish(td)

    b = Beat(s, "b4_found")
    st = building(TXT, 3.4, 2.4).move_to([-1.6, 0.9, 0])
    nm = s.cap("PUENTE DE VALLECAS", color=TXT, y=-0.6)
    bp = backpack(GOLD).scale(0.8).move_to([2.2, 0.75, 0])
    h = s.head("Apareció de madrugada.", color=GOLD, fs=80)
    b.play(*s.clear(), reveal(h), FadeIn(st), FadeIn(nm), FadeIn(bp, shift=DOWN * 0.3), f=0.25)
    boom = poly([(-0.3, -0.15), (0.3, -0.15), (0.3, 0.15), (-0.3, 0.15)], ALERT_HI, 0.9, 0).move_to(bp.get_center())
    ph = phone().move_to(bp.get_center() + RIGHT * 0.05 + DOWN * 0.1)
    c = s.cap("EXPLOSIVO · TELÉFONO MÓVIL", color=ALERT_HI)
    b.play(bp.animate.shift(UP * 0.5), FadeIn(boom), FadeIn(ph), FadeIn(c), FadeOut(nm), f=0.25)
    z = bust(1.5, ALERT_HI).move_to([2.2, -1.2, 0])
    zn = s.name("JAMAL ZOUGAM", [-1.2, -1.8, 0], color=ALERT_HI, fs=52)
    ln = DashedLine(ph.get_bottom(), z.get_top(), color=GOLD, stroke_width=4)
    b.play(FadeOut(c), ph.animate.scale(1.2), Create(ln), FadeIn(z, shift=UP * 0.2), FadeIn(zn), f=0.3)
    b.finish(z)

    b = Beat(s, "b4_xray")
    panel = RoundedRectangle(width=6.6, height=4.2, corner_radius=0.2, color=DATA, stroke_width=4,
                             fill_color="#08202C", fill_opacity=1).move_to([0, 0.4, 0])
    ghost = backpack(DATA).scale(1.1).move_to(panel)
    wires = VGroup(Line([-0.5, 0.2, 0], [0.4, 0.5, 0], color=DATA, stroke_width=4),
                   Line([0.4, 0.5, 0], [0.6, -0.3, 0], color=DATA, stroke_width=4)).shift(UP * 0.4)
    loose = Line([-0.5, -0.4, 0], [-0.1, -0.15, 0], color=ALERT_HI, stroke_width=7).shift(UP * 0.4)
    h = s.head("La radiografía: un cable suelto.", color=DATA, fs=72)
    b.play(*s.clear(), reveal(h), FadeIn(panel), FadeIn(ghost), Create(wires), f=0.25)
    b.play(Create(loose), Flash(loose.get_end(), color=ALERT_HI, line_length=0.3), f=0.15)
    h2 = s.head("Más de 3 meses sin llegar al juez.", color=GOLD, fs=70)
    cross = VGroup(Line(panel.get_corner(UL), panel.get_corner(DR), color=ALERT_HI, stroke_width=10),
                   Line(panel.get_corner(UR), panel.get_corner(DL), color=ALERT_HI, stroke_width=10))
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), Create(cross), f=0.25)
    c = s.cap("EXPLICACIÓN OFICIAL: UN ERROR", color=TXT)
    b.play(FadeIn(c, shift=UP * 0.2), f=0.15)
    b.finish(panel)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — EL CARRETE, LEGANÉS, LA SENTENCIA
# ════════════════════════════════════════════════════════════════════════════
def block5(s: OcultaBase):
    b = Beat(s, "b5_carrete")
    roll = film_roll().move_to([-0.6, 0.5, 0])
    h = s.head("El carrete de fotos.", color=GOLD, fs=84)
    b.play(*s.clear(), *s.slam("DESCLASIFICADO"), reveal(h), FadeIn(roll, scale=0.6), f=0.2)
    td = tedax_suit(1.6).move_to([2.6, -1.0, 0])
    h2 = s.head("Entregado a los TEDAX.", color=TXT, fs=80)
    c = s.cap("REVELADO URGENTE", color=DATA)
    b.play(FadeOut(h, shift=UP * 0.3), reveal(h2), FadeIn(td), roll.animate.scale(0.7).move_to([1.6, 0.2, 0]),
           FadeIn(c), f=0.25)
    rnd = random.Random(4)
    parts = VGroup(*[Square(side_length=0.12, color=GOLD, fill_opacity=0.9, stroke_width=0)
                     .move_to(roll.get_center() + np.array([rnd.uniform(-0.7, 0.7), rnd.uniform(-0.7, 0.7), 0]))
                     for _ in range(40)])
    h3 = s.head("Y se perdió.", color=ALERT_HI, fs=96)
    b.play(FadeOut(h2, shift=UP * 0.3), reveal(h3), FadeOut(roll, scale=0.3), FadeIn(parts), f=0.2)
    b.play(*[p.animate.shift(np.array([rnd.uniform(-2.5, 2.5), rnd.uniform(-1.5, 2.5), 0])).set_opacity(0)
             for p in parts], f=0.25)
    b.finish(td)

    b = Beat(s, "b5_leganes")
    bld = building(TXT, 3.6, 3.0).move_to([0, 0.6, 0])
    h = s.head("Leganés.", color=TXT, fs=100)
    b.play(*s.clear(), reveal(h), FadeIn(bld, shift=UP * 0.3), f=0.3)
    bz = burst(ALERT_HI, 1.0).move_to(bld.get_center() + UP * 0.4)
    c = s.cap("SIETE SUICIDAS · UN GEO MUERTO", color=ALERT_HI)
    b.play(GrowFromCenter(bz), FadeIn(c), bld.animate.set_color(DIM), f=0.35)
    b.finish(bld)

    b = Beat(s, "b5_sentence")
    seal = court_seal(GOLD).move_to([0, 1.0, 0])
    h = s.head("2007: 21 condenados.", color=GOLD, fs=84)
    c = s.cap("CÉLULA YIHADISTA", color=TXT, y=-0.95)
    b.play(*s.clear(), reveal(h), DrawBorderThenFill(seal), FadeIn(c), f=0.25)
    pz = VGroup(puzzle(GOLD), puzzle(DATA).rotate(PI / 2), puzzle(ALERT_HI).rotate(PI)).arrange(RIGHT, buff=0.6)
    pz.move_to([0, 0.6, 0])
    h2 = s.head("Piezas que no encajan.", color=TXT, fs=80)
    b.play(FadeOut(h, shift=UP * 0.3), FadeOut(seal), FadeOut(c), reveal(h2), FadeIn(pz, scale=0.6), f=0.25)
    # la línea de tiempo se fragmenta
    rnd = random.Random(8)
    b.play(*[seg.animate.shift(np.array([rnd.uniform(-0.3, 0.3), rnd.uniform(0.2, 0.9), 0]))
             .rotate(rnd.uniform(-0.8, 0.8)).set_color(ALERT_HI) for seg in s.tl_segs],
           *[n.animate.shift(UP * rnd.uniform(0.1, 0.5)) for n in s.tl_nodes],
           s.tl_lbls.animate.set_opacity(0.3),
           *[p.animate.shift(np.array([rnd.uniform(-0.4, 0.4), rnd.uniform(-0.3, 0.3), 0])).rotate(rnd.uniform(-0.5, 0.5))
             for p in pz], f=0.3)
    b.finish(pz)


# ════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 — CIERRE + CTA
# ════════════════════════════════════════════════════════════════════════════
def block6(s: OcultaBase):
    b = Beat(s, "b6_recap")
    big_stamp = stamp("¿OPERACIÓN OCULTA?", ALERT_HI, fs=96, angle=-6).move_to([0, 1.9, 0])
    big_stamp.scale_to_fit_width(7.6)
    s.reg(big_stamp[1], 2)
    frags = VGroup(s.tl_segs, s.tl_nodes)
    b.play(*s.clear(), FadeOut(s.stamp_mob), ReplacementTransform(frags, big_stamp), FadeOut(s.tl_lbls), f=0.2)
    s.stamp_mob = None
    s.tl = VGroup()
    prev = None
    for w, col in [("Perejil.", GOLD), ("Praga.", DATA), ("Villarejo.", GOLD), ("La mochila.", TXT), ("El carrete.", ALERT_HI)]:
        m = s.big(w, color=col, fs=96, y=-0.4)
        anims = [FadeIn(m, scale=1.3)]
        if prev is not None:
            anims.append(FadeOut(prev, scale=0.8))
        b.play(*anims, f=0.09)
        prev = m
    q = s.big("¿Se ha contado toda la verdad?", color=TXT, fs=76, y=-0.4)
    b.play(FadeOut(prev, scale=0.8), reveal(q), f=0.25)
    b.finish(big_stamp)

    b = Beat(s, "b6_cta")
    ban = Rectangle(width=8.0, height=1.1, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to([0, -1.9, 0])
    c1 = s.reg(kinetic_text("Si quieres que analice", fs=62, color=BG, max_w=7.2).move_to(ban))
    b.play(FadeOut(q, shift=UP * 0.3), big_stamp.animate.scale(0.75).move_to([0, 4.3, 0]), FadeIn(ban, shift=UP * 0.4),
           reveal(c1), f=0.14)
    c2 = s.reg(kinetic_text("los archivos completos,", fs=62, color=BG, max_w=7.2).move_to(ban))
    b.play(FadeOut(c1, shift=UP * 0.3), FadeIn(c2, shift=UP * 0.3), f=0.12)
    c3 = s.reg(kinetic_text("sígueme.", fs=90, color=BG, max_w=7.2).move_to(ban))
    arrow = Arrow(ban.get_top() + RIGHT * 2.6, CORNER_TR, color=GOLD, stroke_width=9, buff=0.1,
                  max_tip_length_to_length_ratio=0.08)
    b.play(FadeOut(c2, shift=UP * 0.3), FadeIn(c3, scale=1.4), GrowArrow(arrow), f=0.14)
    qq = kinetic_text("¿Crees que fue una operación de Estado?", fs=56, color=BG, max_w=6.4)
    box = RoundedRectangle(width=qq.width + 0.6, height=qq.height + 0.5, corner_radius=0.3, color=TXT,
                           fill_color=TXT, fill_opacity=1).move_to([0, 1.0, 0])
    tail = Polygon(box.get_corner(DL) + RIGHT * 0.6, box.get_corner(DL) + RIGHT * 1.3,
                   box.get_corner(DL) + RIGHT * 0.3 + DOWN * 0.45, color=TXT, fill_color=TXT, fill_opacity=1)
    qq.move_to(box)
    s.reg(qq)
    bubble = VGroup(tail, box, qq)
    follow = VGroup(Circle(radius=0.2, color=BG, fill_opacity=1).move_to([-0.25, 0.2, 0]),
                    RoundedRectangle(width=0.7, height=0.4, corner_radius=0.18, color=BG, fill_opacity=1).move_to([-0.25, -0.25, 0]),
                    Line([0.35, 0, 0], [0.85, 0, 0], color=BG, stroke_width=8),
                    Line([0.6, -0.25, 0], [0.6, 0.25, 0], color=BG, stroke_width=8)).move_to(ban)
    b.play(FadeIn(bubble, shift=UP * 0.4, scale=0.85), FadeOut(c3, scale=0.6), FadeIn(follow, scale=1.6),
           FadeOut(big_stamp), f=0.16)
    b.play(arrow.animate(rate_func=there_and_back).shift(UR * 0.15), Indicate(follow, color=PANEL, scale_factor=1.2), f=0.14)
    b.play(arrow.animate(rate_func=there_and_back).shift(UR * 0.15), Indicate(bubble, color=TXT, scale_factor=1.04), f=0.14)
    b.finish(bubble)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


# ════════════════════════════════════════════════════════════════════════════
# ESCENAS: 7 bloques + vídeo completo
# ════════════════════════════════════════════════════════════════════════════
class _Block(OcultaBase):
    BLOCK = 0

    def construct(self):
        self.setup_persistent(self.BLOCK)
        BLOCKS[self.BLOCK](self)
        self.report()


class Block0Hook(_Block):
    BLOCK = 0


class Block1Perejil(_Block):
    BLOCK = 1


class Block2Praga(_Block):
    BLOCK = 2


class Block3Villarejo(_Block):
    BLOCK = 3


class Block4Tedax(_Block):
    BLOCK = 4


class Block5Pruebas(_Block):
    BLOCK = 5


class Block6Cierre(_Block):
    BLOCK = 6


class FullVideo(OcultaBase):
    """Los 7 bloques en una toma continua: 5400 fotogramas = 180.0 s exactos."""

    def construct(self):
        self.setup_persistent(0)
        for blk in BLOCKS:
            blk(self)
        self.report()
