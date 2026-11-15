"""
utils.py — Núcleo técnico de «Cábala: el código oculto del universo».

Contiene:
  * Configuración global 1080×1920 @ 30 fps (frame Manim de 9 × 16 unidades).
  * Paleta, tipografías y zonas seguras.
  * kinetic_text(): texto cinético palabra por palabra (sin Write).
  * TreeOfLife: el Árbol de la Vida recurrente (10 sefirot + 22 senderos).
  * KabalaScene: escena base con reloj en frames enteros, fondo de archivo,
    polvo flotante, HUD del árbol, ganchos, subtítulos, fuentes y transiciones.
"""
from __future__ import annotations

import os

import numpy as np
from manim import (
    BOLD, DOWN, LEFT, NORMAL, ORIGIN, OUT, PI, RIGHT, UP,
    AnimationGroup, Circle, Dot, FadeIn, FadeOut, ImageMobject, LaggedStart,
    Line, Rectangle, Scene, Text, UpdateFromAlphaFunc, VGroup, VMobject,
    ManimColor, config, interpolate_color,
)

# ─────────────────────────────────────────────────────────────────────────────
# §2 · ESPECIFICACIONES TÉCNICAS
# ─────────────────────────────────────────────────────────────────────────────
FPS = 30
PIXEL_W, PIXEL_H = 1080, 1920
FRAME_W, FRAME_H = 9.0, 16.0          # 1 unidad Manim = 120 px
UNIT_PX = PIXEL_H / FRAME_H

config.pixel_width = PIXEL_W
config.pixel_height = PIXEL_H
if os.environ.get("KABALA_PREVIEW"):          # revisión rápida a 540×960 (mismo encuadre)
    config.pixel_width, config.pixel_height = PIXEL_W // 2, PIXEL_H // 2
config.frame_rate = FPS
config.frame_width = FRAME_W
config.frame_height = FRAME_H
config.background_color = "#0A0A0A"

# ─────────────────────────────────────────────────────────────────────────────
# §3 · IDENTIDAD VISUAL
# ─────────────────────────────────────────────────────────────────────────────
BG = "#0A0A0A"      # fondo
BONE = "#E8E6E3"    # texto
CYAN = "#5AC8FA"    # datos
GOLD = "#C9A227"    # énfasis / revelación
RED = "#8B0000"     # alerta / misterio
BG_IN, BG_OUT = "#0B0F14", "#05070A"   # gradiente radial
PARCHMENT = "#16120A"                  # pergamino oscuro (derivado de BG+GOLD)
CLAY = "#5E3B22"                       # barro del Gólem (derivado de GOLD+RED)
RED_GLOW = "#B3261E"                   # rojo luminoso para contornos sobre negro

FONT_SANS = "DejaVu Sans"        # datos (bold)
FONT_SERIF = "DejaVu Serif"      # narrativa
FONT_MONO = "DejaVu Sans Mono"   # términos hebreos / archivo
HEBREW = "אבגדהוזחטיכלמנסעפצקרשת"  # las 22 letras


LRM = "\u200e"


def is_hebrew(s: str) -> bool:
    return any("\u0590" <= ch <= "\u05FF" for ch in s)


def T(text: str, **kw) -> Text:
    """Text() seguro para hebreo: Pango no dibuja nada si el párrafo empieza
    con un carácter RTL, así que se antepone una marca LRM invisible (la frase
    hebrea se sigue mostrando de derecha a izquierda)."""
    if is_hebrew(text):
        text = LRM + text
        kw.pop("disable_ligatures", None)
    return Text(text, **kw)


def px(size_px: float) -> float:
    """Convierte un tamaño de letra en píxeles reales (em a 1920 px de alto)
    al `font_size` de Manim con este frame (medido: font_size 48 → em de 80 px)."""
    return size_px * 0.6


def P(x_px: float, y_px: float) -> np.ndarray:
    """Coordenada de píxel (origen arriba-izquierda) → punto Manim."""
    return np.array([(x_px - PIXEL_W / 2) / UNIT_PX, (PIXEL_H / 2 - y_px) / UNIT_PX, 0.0])


# Safe zones: x ∈ [60, 1020] px, y ∈ [230, 1536] px
SAFE_LEFT, SAFE_RIGHT = P(60, 0)[0], P(1020, 0)[0]      # -4.0 … 4.0
SAFE_TOP, SAFE_BOTTOM = P(0, 230)[1], P(0, 1536)[1]     # 6.083 … -4.8
MAX_W = SAFE_RIGHT - SAFE_LEFT - 0.2                    # 7.8 u de ancho útil

# Zonas de composición (coordenadas Manim)
Y_HOOK_TOP = 4.55       # borde superior de los ganchos
Y_VIS = 0.30            # centro del visual principal
Y_CAP = -3.15           # centro del subtítulo
Y_SRC_TOP = -4.00       # borde superior de la fuente
HUD_POS = np.array([-3.22, 5.28, 0.0])  # mini-árbol (safe-zone superior-izquierda)

# Tamaños tipográficos (px reales)
SIZE_BODY = 56
SIZE_SRC = 48
SIZE_HOOK = 66
SIZE_HERO = 96


# ─────────────────────────────────────────────────────────────────────────────
# Texto cinético
# ─────────────────────────────────────────────────────────────────────────────
def _clean(word: str) -> str:
    return word.strip(".,:;!¡?¿«»“”\"'‘’()·…").lower()


def kinetic_text(text: str, size: float = SIZE_BODY, color=BONE, font: str = FONT_SERIF,
                 weight=BOLD, max_width: float = MAX_W, accents: dict | None = None,
                 line_buff: float = 0.16) -> VGroup:
    """Devuelve un VGroup cuyas submobjects son PALABRAS (cada una un VGroup de
    glifos), ya maquetadas en líneas centradas que nunca superan `max_width`.

    * Máximo 8 palabras por pantalla (se valida).
    * Cada palabra puede colorearse con `accents={"palabra": COLOR}` o por dígitos.
    * El reveal se hace con reveal_words() — nunca con Write.
    """
    words = text.split()
    if len(words) > 8:
        raise ValueError(f"Más de 8 palabras en pantalla: {text!r}")
    fs = px(size)
    accents = {k.lower(): v for k, v in (accents or {}).items()}

    def make(s: str) -> Text:
        return Text(s, font=font, font_size=fs, weight=weight, color=color,
                    disable_ligatures=True)

    # Ajuste de líneas por anchura medida
    lines: list[list[str]] = []
    cur: list[str] = []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and make(trial).width > max_width:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)

    line_mobs, word_groups = [], []
    for ln in lines:
        s = " ".join(ln)
        t = make(s)
        if len(t.submobjects) == len(s):          # 1 glifo por carácter (espacios vacíos)
            idx, groups = 0, []
            for w in ln:
                groups.append(VGroup(*t.submobjects[idx:idx + len(w)]))
                idx += len(w) + 1
        else:                                     # respaldo: una Text por palabra
            groups = [make(w) for w in ln]
            VGroup(*groups).arrange(RIGHT, buff=fs * 0.012, aligned_edge=DOWN)
            t = VGroup(*groups)
        for w, g in zip(ln, groups):
            key = _clean(w)
            if key in accents:
                g.set_color(accents[key])
            elif any(ch.isdigit() for ch in w):
                g.set_color(CYAN)
        line_mobs.append(t)
        word_groups.extend(groups)
    VGroup(*line_mobs).arrange(DOWN, buff=line_buff)
    out = VGroup(*word_groups)
    if out.width > max_width:                     # seguridad (no debería ocurrir)
        out.scale_to_fit_width(max_width)
    return out


def reveal_words(words: VGroup, run_time: float = 1.2, shift: float = 0.18):
    """Aparición palabra por palabra (fade + desplazamiento + micro-escala)."""
    return LaggedStart(*[FadeIn(w, shift=UP * shift, scale=1.08) for w in words],
                       lag_ratio=0.32, run_time=run_time)


# ─────────────────────────────────────────────────────────────────────────────
# Fondo de archivo y partículas
# ─────────────────────────────────────────────────────────────────────────────
def hex_rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def make_background(seed: int = 11) -> ImageMobject:
    """Gradiente radial #0B0F14 → #05070A + «ruido de archivo» (grano, rayas,
    manchas) generado con numpy."""
    h, w = 960, 540
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    r = np.sqrt(((xx - w / 2) / (w * 0.95)) ** 2 + ((yy - h * 0.44) / (h * 0.62)) ** 2)
    r = np.clip(r, 0, 1)[..., None]
    img = hex_rgb(BG_IN) * (1 - r) + hex_rgb(BG_OUT) * r
    rng = np.random.default_rng(seed)
    img += rng.normal(0, 1.9, (h, w, 1))                         # grano
    blot = rng.normal(0, 1, (h // 40 + 2, w // 40 + 2))          # manchas suaves
    blot = np.kron(blot, np.ones((40, 40)))[:h, :w, None]
    img += blot * 1.1
    for x in rng.integers(0, w, 7):                              # rayas verticales
        img[:, x:x + 1, :] += rng.uniform(1.5, 3.5)
    for y in rng.integers(0, h, 4):                              # rayas horizontales
        img[y:y + 1, :, :] += rng.uniform(1.0, 2.5)
    img = np.clip(img, 0, 255).astype(np.uint8)
    im = ImageMobject(img)
    im.stretch_to_fit_height(FRAME_H + 0.05).stretch_to_fit_width(FRAME_W + 0.05)
    im.set_z_index(-100)
    return im


class Dust(VGroup):
    """Motas de luz que derivan hacia arriba de forma continua (vida ambiental)."""

    def __init__(self, n: int = 54, seed: int = 5, **kw):
        super().__init__(**kw)
        rng = np.random.default_rng(seed)
        for _ in range(n):
            col = GOLD if rng.random() < 0.35 else BONE
            d = Dot(radius=rng.uniform(0.010, 0.032), color=col,
                    fill_opacity=rng.uniform(0.12, 0.42))
            d.move_to([rng.uniform(-4.6, 4.6), rng.uniform(-8.2, 8.2), 0])
            d.vel = np.array([rng.uniform(-0.05, 0.05), rng.uniform(0.05, 0.22), 0])
            self.add(d)
        self.set_z_index(-50)
        self.add_updater(Dust._drift)

    @staticmethod
    def _drift(m, dt):
        for d in m:
            d.shift(d.vel * dt)
            if d.get_y() > 8.3:
                d.set_y(-8.3)
            x = d.get_x()
            if x > 4.7 or x < -4.7:
                d.set_x(-np.sign(x) * 4.6)


# ─────────────────────────────────────────────────────────────────────────────
# Árbol de la Vida (recurso recurrente obligatorio)
# ─────────────────────────────────────────────────────────────────────────────
# Índices: 1 Kéter, 2 Jojmá, 3 Biná, 4 Jésed, 5 Guevurá, 6 Tiféret,
#          7 Nétsaj, 8 Hod, 9 Yesod, 10 Maljut  (diagrama clásico de 3 pilares)
SEF_POS = {1: (0, 0.0), 2: (1, -0.55), 3: (-1, -0.55), 4: (1, -1.7), 5: (-1, -1.7),
           6: (0, -2.25), 7: (1, -3.4), 8: (-1, -3.4), 9: (0, -4.0), 10: (0, -5.0)}
PATHS = [(1, 2), (1, 3), (1, 6), (2, 3), (2, 6), (2, 4), (3, 6), (3, 5), (4, 5), (4, 6),
         (4, 7), (5, 6), (5, 8), (6, 7), (6, 9), (6, 8), (7, 8), (7, 9), (7, 10),
         (8, 9), (8, 10), (9, 10)]                      # 22 senderos
assert len(PATHS) == 22 and len(SEF_POS) == 10
X_SPREAD = 1.3


class TreeOfLife(VGroup):
    """10 sefirot (nodos + halos) unidas por 22 senderos.

    Estructura de submobjects: [paths, glows, nodes] — accesibles por atributo.
    Empieza como «contorno» (trazo fino, sin relleno) y se ilumina con light().
    """

    def __init__(self, scale: float = 1.0, color=GOLD, node_r: float = 0.30,
                 stroke: float = 3.0, center=ORIGIN, **kw):
        super().__init__(**kw)
        self.s = scale
        self.base_color = color
        self.r = node_r * scale
        sw = max(stroke * (0.55 + 0.45 * scale), 1.0)
        mid_y = -2.5 * scale
        self.pos = {i: np.array([x * X_SPREAD * scale, y * scale - mid_y, 0.0])
                    for i, (x, y) in SEF_POS.items()}
        self.paths = VGroup(*[
            Line(self.pos[a], self.pos[b], buff=self.r, stroke_width=sw * 0.8,
                 color=color, stroke_opacity=0.55) for a, b in PATHS])
        self.glows = VGroup()
        self.nodes = VGroup()
        for i in range(1, 11):
            g = VGroup(*[Circle(radius=self.r * k, stroke_width=0)
                         .set_fill(color, 0).move_to(self.pos[i])
                         for k in (2.6, 2.0, 1.55, 1.2)])
            g.target_ops = (0.05, 0.08, 0.13, 0.22)
            self.glows.add(g)
            self.nodes.add(Circle(radius=self.r, stroke_width=sw, color=color)
                           .set_fill(color, 0).move_to(self.pos[i]))
        self.add(self.paths, self.glows, self.nodes)
        self.move_to(center)

    def node(self, i: int):
        return self.nodes[i - 1]

    def light(self, i: int, color=None, fill: float = 0.85):
        """Animaciones para iluminar la sefirá i (relleno + halo)."""
        c = color or self.base_color
        anims = [self.nodes[i - 1].animate.set_fill(c, fill).set_stroke(c, opacity=1)]
        for circ, op in zip(self.glows[i - 1], self.glows[i - 1].target_ops):
            anims.append(circ.animate.set_fill(c, op))
        return AnimationGroup(*anims)

    def light_now(self, idxs, color=None, fill: float = 0.85):
        c = color or self.base_color
        for i in idxs:
            self.nodes[i - 1].set_fill(c, fill).set_stroke(c, opacity=1)
            for circ, op in zip(self.glows[i - 1], self.glows[i - 1].target_ops):
                circ.set_fill(c, op)
        return self

    def light_all(self, color=None, lag: float = 0.12, run_time: float = 2.0):
        c = color or self.base_color
        return AnimationGroup(
            LaggedStart(*[self.light(i, c) for i in range(1, 11)], lag_ratio=lag),
            self.paths.animate.set_stroke(c, opacity=0.95),
            run_time=run_time)


def tint(mob, color, k: float = 1.0):
    """Recolorea conservando (y escalando) las opacidades de cada pieza."""
    for sm in mob.family_members_with_points():
        fo, so = sm.get_fill_opacity(), sm.get_stroke_opacity()
        sm.set_fill(color, fo * k)
        sm.set_stroke(color, opacity=so * k)
    return mob


def flip_recolor(mob, color, run_time_axis=RIGHT, angle: float = PI):
    """Volteo 3D (eje horizontal) + virado de color: el árbol se INVIERTE."""
    color = ManimColor(color)
    start = mob.copy()
    center = mob.get_center()
    src = [(sm.get_fill_color(), sm.get_stroke_color())
           for sm in start.family_members_with_points()]

    def f(m, a):
        m.become(start)
        for sm, (fc, sc) in zip(m.family_members_with_points(), src):
            sm.set_fill(interpolate_color(fc, color, a), sm.get_fill_opacity())
            sm.set_stroke(interpolate_color(sc, color, a), opacity=sm.get_stroke_opacity())
        m.rotate(angle * a, axis=run_time_axis, about_point=center)

    return UpdateFromAlphaFunc(mob, f)


def breathe(mob, cycles: int = 1, amp: float = 0.018):
    """Respiración sutil (escala oscilante que vuelve a 1). No pausa updaters."""
    st = {"s": 1.0}

    def f(m, a):
        s = 1 + amp * np.sin(2 * PI * cycles * a)
        m.scale(s / st["s"])
        st["s"] = s

    return UpdateFromAlphaFunc(mob, f, suspend_mobject_updating=False)


def spin_updater(rate: float):
    def u(m, dt):
        m.rotate(rate * dt)
    return u


def blink_updater(speed: float = 5.0, lo: float = 0.25):
    def u(m, dt):
        m.t_ = getattr(m, "t_", 0.0) + dt
        m.set_opacity(lo + (1 - lo) * (0.5 + 0.5 * np.sign(np.sin(m.t_ * speed))))
    return u


# ─────────────────────────────────────────────────────────────────────────────
# Escena base con línea de tiempo exacta
# ─────────────────────────────────────────────────────────────────────────────
BLOCK_STARTS = [0, 15, 45, 75, 105, 135, 165]
BLOCK_ENDS = [15, 45, 75, 105, 135, 165, 180]
TOTAL_SECONDS = 180


class KabalaScene(Scene):
    """Escena base: el reloj se cuenta en frames ENTEROS.

    Manim genera len(np.arange(0, run_time, 1/fps)) frames por play(); pasando
    run_time = (n - 0.5)/fps se obtienen exactamente n frames, sin deriva.
    """

    def k_setup(self, block_index: int = 0):
        self.frames = BLOCK_STARTS[block_index] * FPS
        self.rng = np.random.default_rng(1234 + block_index)
        self.bg = make_background()
        self.dust = Dust()
        self.add(self.bg, self.dust)
        self.hud = TreeOfLife(scale=0.24, color=GOLD, stroke=2.2, center=HUD_POS)
        self.hud.set_z_index(60)
        self.hud_lit = 0
        if block_index > 0:                        # estado del HUD al empezar
            self.hud.light_now(range(1, block_index + 1))
            self.hud.paths.set_stroke(GOLD, opacity=0.7)
            self.hud_lit = block_index
            self.add(self.hud)
        self.hook_mob = self.cap_mob = self.src_mob = None
        self.focus = Dot(radius=0.001).set_opacity(0)

    # ── reloj ──
    @property
    def now(self) -> float:
        return self.frames / FPS

    def run(self, *anims, rt: float = 1.0):
        anims = [a for a in anims if a is not None]
        n = max(1, int(round(rt * FPS)))
        self.play(*anims, run_time=(n - 0.5) / FPS)
        self.frames += n

    def until(self, t: float, focus=None):
        """Rellena hasta el segundo absoluto t con movimiento (nunca un wait
        estático): respiración del foco + polvo + updaters activos."""
        n = int(round(t * FPS)) - self.frames
        if n <= 0:
            return
        target = focus if focus is not None else self.focus
        cycles = max(1, int(round(n / FPS / 3.0)))
        self.play(breathe(target, cycles=cycles), run_time=(n - 0.5) / FPS)
        self.frames += n

    # ── capas de texto ──
    def hook(self, text: str, rt: float = 1.2, accents=None, size: float = SIZE_HOOK,
             color=BONE):
        anims = []
        if self.hook_mob is not None:
            self.run(FadeOut(self.hook_mob, shift=UP * 0.2), rt=0.25)
        h = kinetic_text(text, size=size, font=FONT_SERIF, color=color,
                         accents=accents or {}, max_width=7.9)
        h.move_to([0, 0, 0]).align_to([0, Y_HOOK_TOP, 0], UP)
        self.hook_mob = h
        anims.append(reveal_words(h, run_time=rt))
        return AnimationGroup(*anims)

    def drop_hook(self):
        if self.hook_mob is None:
            return None
        m, self.hook_mob = self.hook_mob, None
        return FadeOut(m, shift=UP * 0.2)

    def caption(self, text: str, rt: float = 1.2, font: str = FONT_SERIF, accents=None,
                size: float = SIZE_BODY, color=BONE, y: float = Y_CAP):
        if self.cap_mob is not None:
            self.run(FadeOut(self.cap_mob, shift=UP * 0.15), rt=0.25)
        c = kinetic_text(text, size=size, font=font, color=color, accents=accents or {})
        c.move_to([0, y, 0])
        self.cap_mob = c
        return reveal_words(c, run_time=rt)

    def drop_caption(self):
        if self.cap_mob is None:
            return None
        m, self.cap_mob = self.cap_mob, None
        return FadeOut(m, shift=UP * 0.15)

    def source(self, text: str):
        """Fuente en pantalla (cian, 48 px). Sustituye a la anterior."""
        anims = []
        if self.src_mob is not None:
            anims.append(FadeOut(self.src_mob))
        s = kinetic_text(text, size=SIZE_SRC, font=FONT_SANS, weight=NORMAL,
                         color=CYAN, max_width=7.9, line_buff=0.08)
        top = Y_SRC_TOP
        if self.cap_mob is not None:
            top = min(top, self.cap_mob.get_bottom()[1] - 0.22)
        s.move_to([0, 0, 0]).align_to([0, top, 0], UP)
        if s.get_bottom()[1] < SAFE_BOTTOM + 0.05:
            s.shift(UP * (SAFE_BOTTOM + 0.05 - s.get_bottom()[1]))
        self.src_mob = s
        anims.append(FadeIn(s, shift=LEFT * 0.3))
        return AnimationGroup(*anims)

    def drop_source(self):
        if self.src_mob is None:
            return None
        m, self.src_mob = self.src_mob, None
        return FadeOut(m)

    # ── HUD (el Árbol que progresa bloque a bloque) ──
    def hud_light(self, i: int):
        if self.hud not in self.mobjects:
            self.add(self.hud)
        self.hud_lit = max(self.hud_lit, i)
        return AnimationGroup(self.hud.light(i),
                              self.hud.paths.animate.set_stroke(GOLD, opacity=0.7))

    # ── transiciones ──
    def stage(self):
        """Mobjects de contenido (todo menos fondo, polvo y HUD)."""
        keep = {id(self.bg), id(self.dust), id(self.hud)}
        return [m for m in self.mobjects if id(m) not in keep]

    def glitch(self, rt: float = 0.2, strength: float = 0.14):
        """Glitch de 0.2 s: aberración cromática roja/cian + franjas de señal."""
        content = [m for m in self.stage() if isinstance(m, VMobject)]
        ghosts = VGroup()
        for col in (RED_GLOW, CYAN):
            g = VGroup(*[m.copy() for m in content])
            for sm in g.get_family():
                sm.clear_updaters()
            tint(g, col, 0.6)
            ghosts.add(g)
        bars = VGroup(*[Rectangle(width=FRAME_W + 0.4, height=0.1, stroke_width=0)
                        .set_fill(BONE, 0.10) for _ in range(9)])
        layer = VGroup(ghosts, bars).set_z_index(80)
        base = [g.get_center() for g in ghosts]
        rng = self.rng

        def f(m, a):
            for g, b in zip(ghosts, base):
                g.move_to(b + np.array([rng.uniform(-1, 1) * strength,
                                        rng.uniform(-0.3, 0.3) * strength, 0]))
            for bar in bars:
                bar.stretch_to_fit_height(rng.uniform(0.03, 0.42))
                bar.move_to([rng.uniform(-0.4, 0.4), rng.uniform(-8, 8), 0])
                bar.set_fill(CYAN if rng.random() < 0.3 else BONE, rng.uniform(0.04, 0.16))

        self.add(layer)
        self.run(UpdateFromAlphaFunc(layer, f), rt=rt)
        self.remove(layer)

    def parchment_wipe(self, extra_out=()):
        """Wipe de «pergamino»: un lienzo oscuro con canto dorado barre la
        pantalla, se limpia el escenario detrás y el lienzo sale por la derecha."""
        sheet = Rectangle(width=FRAME_W + 0.6, height=FRAME_H + 0.6, stroke_width=0)
        sheet.set_fill(PARCHMENT, 1)
        edge = Line(UP * 8.4, DOWN * 8.4, color=GOLD, stroke_width=6)
        edge.next_to(sheet, RIGHT, buff=0)
        lines = VGroup(*[Line(LEFT * 4.4, RIGHT * 4.4, stroke_width=1, color=GOLD,
                              stroke_opacity=0.12).shift(UP * y)
                         for y in np.arange(-7.5, 7.6, 0.75)])
        wipe = VGroup(sheet, lines, edge).set_z_index(50)
        wipe.move_to([-(FRAME_W + 0.6), 0, 0])
        self.add(wipe)
        self.run(wipe.animate.move_to(ORIGIN), *extra_out, rt=0.3)
        for m in self.stage():
            if m is not wipe:
                for sm in m.get_family():
                    sm.clear_updaters()
                self.remove(m)
        self.hook_mob = self.cap_mob = self.src_mob = None
        return wipe

    def transition(self, hud_index: int | None = None):
        """Cambio de bloque (0.8 s): glitch 0.2 s + wipe de pergamino 0.6 s."""
        self.glitch(0.2)
        wipe = self.parchment_wipe()
        anims = [wipe.animate.move_to([FRAME_W + 0.6, 0, 0])]
        if hud_index is not None:
            anims.append(self.hud_light(hud_index))
        self.run(*anims, rt=0.3)
        self.remove(wipe)
