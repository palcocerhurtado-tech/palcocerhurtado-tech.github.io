"""
main.py — «313 $: el bot que me hizo resolver 9 acertijos para venderme humo»
Video vertical 9:16 · 1080×1920 · 30 fps · 180 s exactos · Manim CE.

Reutiliza el motor de ../kabala_video/utils.py (reloj por frames, texto cinético,
glitch, wipe, fondo de archivo). Las pruebas son las capturas reales, procesadas
por prepare_assets.py (foto de perfil y contador de chats difuminados).

    python prepare_assets.py
    manim -qh --disable_caching main.py FullVideo
    KABALA_PREVIEW=1 manim --disable_caching main.py Block3      # vista previa 540×960
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kabala_video"))
sys.path.insert(0, HERE)

from manim import (  # noqa: E402
    BOLD, DOWN, LEFT, NORMAL, ORIGIN, PI, RIGHT, UP, UL,
    RESAMPLING_ALGORITHMS, AnimationGroup, Arrow, Circle, Create, Dot, FadeIn, FadeOut, Flash, Group,
    ImageMobject, LaggedStart, Line, Polygon, Rectangle, RoundedRectangle, Text,
    Transform, VGroup, config,
)
import utils as K  # noqa: E402  (motor del video de la Cábala; fija 1080×1920 @ 30 fps)
from utils import (  # noqa: E402
    BG, BONE, CYAN, FONT_MONO, FONT_SANS, FONT_SERIF, FPS, GOLD, RED, RED_GLOW,
    SAFE_BOTTOM, Dust, KabalaScene, blink_updater, kinetic_text, make_background, px,
    reveal_words,
)

PURPLE = "#7B5CFF"          # burbujas de mis mensajes en Telegram
ALERT = "#E5484D"           # rojo legible sobre negro (alertas)
ASSETS = os.path.join(HERE, "assets")
with open(os.path.join(ASSETS, "clips.json")) as fh:
    CLIPS = json.load(fh)

STARTS = [0, 12, 36, 76, 112, 136, 164]
ENDS = [12, 36, 76, 112, 136, 164, 180]
TOTAL = 180

Y_HUD, Y_CHIP, Y_HEAD = 5.45, 4.62, 3.98
Y_EVID, EVID_MAX_H, EVID_MAX_W = 0.62, 6.0, 7.6
Y_CAPTION = -3.2
STAGES = ["ATRACCIÓN", "COMPROMISO", "ESCALADA", "COSTE HUNDIDO", "CONVERSIÓN"]


def mono(text, size=44, color=BONE, weight=BOLD):
    return Text(text, font=FONT_MONO, font_size=px(size), weight=weight, color=color,
                disable_ligatures=True)


def sans(text, size=48, color=BONE, weight=BOLD):
    return Text(text, font=FONT_SANS, font_size=px(size), weight=weight, color=color,
                disable_ligatures=True)


# ─────────────────────────────────────────────────────────────────────────────
# Piezas gráficas
# ─────────────────────────────────────────────────────────────────────────────
def funnel_shape(h=4.0, w=5.6, n=5, color=GOLD, sw=4):
    """Embudo de n bandas (de ancho a estrecho) + caño."""
    bands = VGroup()
    top = h / 2
    band_h = h * 0.8 / n
    for i in range(n):
        y0 = top - i * band_h
        y1 = y0 - band_h
        w0 = w * (1 - 0.8 * i / n) / 2
        w1 = w * (1 - 0.8 * (i + 1) / n) / 2
        b = Polygon([-w0, y0, 0], [w0, y0, 0], [w1, y1, 0], [-w1, y1, 0],
                    color=color, stroke_width=sw).set_fill(color, 0)
        bands.add(b)
    wn = w * 0.2 / 2
    spout = Polygon([-wn, top - h * 0.8, 0], [wn, top - h * 0.8, 0], [wn * 0.6, -h / 2, 0],
                    [-wn * 0.6, -h / 2, 0], color=color, stroke_width=sw).set_fill(color, 0.15)
    g = VGroup(bands, spout)
    g.bands = bands
    return g


def stamp(word, color=PURPLE, size=96, angle=-0.12):
    t = sans(word, size, color=BONE)
    box = RoundedRectangle(width=t.width + 0.8, height=t.height + 0.55, corner_radius=0.18,
                           stroke_width=10, color=color).set_fill(color, 0.85)
    g = VGroup(box, t).rotate(angle)
    g.set_z_index(30)
    return g


class Evidence(Group):
    """Una captura real recortada, con borde y cajas de resaltado."""

    def __init__(self, name, max_w=EVID_MAX_W, max_h=EVID_MAX_H, center=(0, Y_EVID, 0)):
        super().__init__()
        self.name = name
        self.meta = CLIPS[name]
        img = ImageMobject(os.path.join(ASSETS, f"{name}.png"))
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])
        aspect = img.height / img.width
        w = min(max_w, max_h / aspect)
        img.set(width=w)
        img.move_to(center)
        frame = Rectangle(width=img.width + 0.08, height=img.height + 0.08, stroke_width=2,
                          color=BONE, stroke_opacity=0.5).move_to(img)
        self.img = img
        self.add(img, frame)

    def box(self, i, color=ALERT, buff=0.04):
        a, b, c, d = self.meta["highlights"][i]
        img = self.img
        ul = img.get_corner(UL)
        W, H = img.width, img.height
        r = Rectangle(width=(c - a) * W + 2 * buff, height=(d - b) * H + 2 * buff,
                      stroke_width=6, color=color)
        r.move_to(ul + np.array([(a + c) / 2 * W, -(b + d) / 2 * H, 0]))
        r.set_z_index(10)
        return r

    def loupe(self, i, width=8.0, center=(0, Y_EVID, 0)):
        """Ampliación («lupa») del resaltado i."""
        im = ImageMobject(os.path.join(ASSETS, f"{self.name}_h{i}.png"))
        im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])
        im.set(width=width)
        if im.height > 3.2:
            im.set(height=3.2)
        im.move_to(center)
        fr = RoundedRectangle(width=im.width + 0.25, height=im.height + 0.25, corner_radius=0.12,
                              stroke_width=6, color=GOLD).set_fill(BG, 1).move_to(im)
        g = Group(fr, im)
        g.set_z_index(40)
        return g


class Sun(Evidence):
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Escena base
# ─────────────────────────────────────────────────────────────────────────────
class FunnelScene(KabalaScene):
    def k_setup(self, block_index: int = 0):
        self.frames = STARTS[block_index] * FPS
        self.rng = np.random.default_rng(99 + block_index)
        self.bg = make_background(seed=23)
        self.dust = Dust(n=40, seed=8)
        self.add(self.bg, self.dust)
        self.hook_mob = self.cap_mob = self.src_mob = None
        self.chip = None
        self.focus = Dot(radius=0.001).set_opacity(0)
        # Estado inicial del HUD según el bloque
        keys = [0, 0, 0, 4, 8, 9, 9][block_index]
        clock = ["10:29", "10:29", "10:31", "11:03", "11:34", "11:36", "11:37"][block_index]
        stage = [0, 0, 1, 2, 3, 4, 5][block_index]
        self._build_hud(keys, clock, stage, visible=block_index > 0)

    # ── HUD: embudo · reloj · llaves ──
    def _build_hud(self, keys, clock, stage, visible=True):
        panel = RoundedRectangle(width=8.1, height=0.95, corner_radius=0.2, stroke_width=2,
                                 color=BONE, stroke_opacity=0.35).set_fill(BG, 0.85)
        panel.move_to([0, Y_HUD, 0])
        icon = funnel_shape(h=0.72, w=0.95, sw=2.2).move_to([-3.45, Y_HUD, 0])
        for i in range(stage):
            icon.bands[i].set_fill(GOLD, 0.85)
        self.hud_icon = icon
        self.hud_clock = mono(clock, 60, CYAN).move_to([-1.65, Y_HUD, 0])
        sq = VGroup(*[RoundedRectangle(width=0.27, height=0.42, corner_radius=0.05, stroke_width=2,
                                       color=PURPLE) for _ in range(9)])
        sq.arrange(RIGHT, buff=0.07).move_to([1.2, Y_HUD, 0])
        for i in range(keys):
            sq[i].set_fill(PURPLE, 0.95)
        self.hud_keys = sq
        self.hud_count = mono(f"{keys}/9", 52, BONE).next_to(sq, RIGHT, buff=0.18)
        self.keys = keys
        band = RoundedRectangle(width=8.4, height=2.25, corner_radius=0.25, stroke_width=0)
        band.set_fill(BG, 0.82).move_to([0, -3.62, 0])
        self.hud = Group(band, panel, icon, self.hud_clock, sq, self.hud_count)
        band.set_z_index(55)
        for m in (panel, icon, self.hud_clock, sq, self.hud_count):
            m.set_z_index(60)
        self.hud_band = band
        if visible:
            self.add(self.hud)

    def hud_show(self):
        self.add(self.hud)
        return FadeIn(self.hud, shift=DOWN * 0.3)

    def set_clock(self, hhmm):
        new = mono(hhmm, 60, CYAN).move_to(self.hud_clock).set_z_index(60)
        return Transform(self.hud_clock, new)

    def add_key(self):
        self.keys += 1
        i = self.keys - 1
        new = mono(f"{self.keys}/9", 52, BONE).move_to(self.hud_count).set_z_index(60)
        # lista (no AnimationGroup): un grupo nuevo con piezas del HUD lo desarmaría
        return [self.hud_keys[i].animate.set_fill(PURPLE, 0.95), Transform(self.hud_count, new)]

    def set_stage(self, i):
        return self.hud_icon.bands[i - 1].animate.set_fill(GOLD, 0.85)

    def stage(self):
        """Todo lo que no sea fondo, polvo o una pieza del HUD."""
        hud_ids = {id(m) for m in self.hud.get_family()}
        return [m for m in self.mobjects
                if id(m) not in hud_ids and m is not self.bg and m is not self.dust]

    def transition(self, hud_index=None):
        super().transition(None)
        if self.hud not in self.mobjects:      # por si alguna animación lo desarmó
            self.remove(*[m for m in self.mobjects if id(m) in {id(x) for x in self.hud}])
            self.add(self.hud)

    # ── capas de texto con z alto (por encima de la banda) ──
    def caption(self, text, rt=1.0, **kw):
        kw.setdefault("y", Y_CAPTION)
        a = super().caption(text, rt=rt, **kw)
        self.cap_mob.set_z_index(62)
        return a

    def source(self, text):
        a = super().source(text)
        self.src_mob.set_z_index(62)
        return a

    def hook(self, text, rt=1.0, **kw):
        a = super().hook(text, rt=rt, **kw)
        self.hook_mob.set_z_index(62)
        return a

    def stage_chip(self, i):
        """Etiqueta «EMBUDO i/5 · ETAPA» bajo el HUD + banda del icono."""
        anims = []
        if self.chip is not None:
            anims.append(FadeOut(self.chip))
        t = mono(f"EMBUDO {i}/5 · {STAGES[i - 1]}", 44, BG)
        box = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.3, corner_radius=0.12,
                               stroke_width=0).set_fill(GOLD, 1)
        chip = VGroup(box, t).move_to([0, Y_CHIP, 0])
        t.move_to(box)
        chip.set_z_index(62)
        self.chip = chip
        anims += [FadeIn(chip, shift=DOWN * 0.2), self.set_stage(i)]
        return anims

    def header(self, text, color=BONE):
        t = mono(text, 50, color).move_to([0, Y_HEAD, 0]).set_z_index(62)
        return t

    def zoom_highlight(self, ev, i, caption=None, hold_to=None, accents=None, cap_font=FONT_SERIF):
        """Marca la frase en la captura y la amplía en una «lupa»."""
        box = ev.box(i)
        self.run(Create(box), rt=0.45)
        lp = ev.loupe(i)
        veil = Rectangle(width=9.4, height=7.2, stroke_width=0).set_fill(BG, 0).move_to([0, Y_EVID, 0])
        veil.set_z_index(35)
        self.add(veil)
        anims = [FadeIn(lp, scale=0.6), veil.animate.set_fill(BG, 0.72)]
        if caption:
            anims.append(self.caption(caption, rt=0.9, accents=accents or {}, font=cap_font))
        self.run(*anims, rt=0.9)
        if hold_to is not None:
            self.until(hold_to, focus=lp)
        return box, lp, veil

    def clear_zoom(self, *mobs):
        self.run(*[FadeOut(m) for m in mobs], rt=0.3)

    def swap_evidence(self, old, new, rt=0.6):
        anims = [FadeIn(new, shift=LEFT * 0.6)]
        if old is not None:
            anims.append(FadeOut(old, shift=LEFT * 0.6))
        self.run(*anims, rt=rt)
        return new

    def solve(self, word, hhmm, color=PURPLE, extra=None):
        """Sello con la respuesta + reloj y llaves del HUD."""
        st = stamp(word, color).move_to([0, Y_EVID + 0.3, 0])
        anims = [FadeIn(st, scale=1.9), self.set_clock(hhmm), *self.add_key()]
        if extra:
            anims += extra
        self.run(*anims, rt=0.4)
        self.run(Flash(st.get_center(), color=color, flash_radius=1.6, line_length=0.45,
                       num_lines=18), rt=0.5)
        return st


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUES
# ─────────────────────────────────────────────────────────────────────────────
def block0(s):
    """0:00–0:12 · Gancho + CTA."""
    big = sans("313 $", 230, ALERT).move_to([0, 1.3, 0])
    s.run(FadeIn(big, scale=2.2), s.caption("Un bot de Telegram me pidió esto.", rt=1.2,
                                            accents={"telegram": CYAN}), rt=1.3)
    s.glitch(0.2, strength=0.3)
    s.focus = big
    s.until(3.2)
    stats = VGroup(*[VGroup(sans(n, 120, c), sans(t, 60, BONE)).arrange(RIGHT, buff=0.35,
                                                                        aligned_edge=DOWN)
                     for n, t, c in (("9", "acertijos", PURPLE), ("68", "minutos", CYAN),
                                     ("1", "bot", GOLD))])
    stats.arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([0, 1.0, 0])
    s.run(FadeOut(big, scale=0.6), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.6) for r in stats],
                                               lag_ratio=0.35),
          s.caption("Y casi pico.", rt=0.8, accents={"pico.": ALERT}), rt=1.6)
    s.focus = stats
    s.until(6.0)
    # El embudo: muchos entran, casi nadie sale… y ese es el plan
    fun = funnel_shape(h=4.4, w=6.0).move_to([0, 0.9, 0])
    rng = s.rng
    dots = VGroup(*[Dot(radius=0.06, color=BONE).move_to([rng.uniform(-3.2, 3.2),
                                                          rng.uniform(3.4, 4.2), 0])
                    for _ in range(40)])
    s.run(FadeOut(stats, shift=LEFT), Create(fun), FadeIn(dots), s.caption(
        "Así funciona el embudo por dentro.", rt=1.0, accents={"embudo": GOLD}), rt=1.2)
    tip = fun.get_bottom() + DOWN * 0.1

    def fall(k, d):
        if k < 3:   # los pocos que llegan al fondo
            return d.animate(run_time=1.4).move_to(tip).set_color(GOLD)
        y = rng.uniform(-0.5, 2.6)
        return d.animate(run_time=1.4).move_to([d.get_x() * 0.4, y, 0]).set_opacity(0)

    s.run(LaggedStart(*[fall(k, d) for k, d in enumerate(dots)], lag_ratio=0.03),
          LaggedStart(*[b.animate.set_fill(GOLD, 0.25) for b in fun.bands], lag_ratio=0.2),
          rt=1.6)
    # El embudo se repliega al HUD
    s.hud_icon.set_z_index(60)
    s.run(FadeOut(dots), Transform(fun, s.hud_icon.copy()), s.hud_show(), rt=0.9)
    s.remove(fun)
    # CTA de apertura (10–12 s)
    ribbon = RoundedRectangle(width=8.2, height=1.4, corner_radius=0.22, stroke_width=3,
                              color=GOLD).set_fill(BG, 0.95).move_to([0, 1.0, 0])
    msg = kinetic_text("Quédate: al final, las 5 señales.", size=58, font=FONT_SANS,
                       accents={"señales.": GOLD}).move_to(ribbon)
    arrow = Arrow([2.4, 2.6, 0], [3.5, 4.55, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.25)
    arrow.add_updater(blink_updater(7))
    s.add(arrow)
    s.run(s.drop_caption(), FadeIn(ribbon, shift=UP * 0.3), reveal_words(msg, 0.8), rt=0.9)
    s.until(12.0, focus=msg)


def block1(s):
    """0:12–0:36 · La entrada al bot (10:29)."""
    s.transition(None)
    s.run(*s.stage_chip(1), rt=0.5)
    head = s.header("DOMINGO · TELEGRAM · BOT «Sol13»", CYAN)
    ev = Evidence("start")
    s.run(FadeIn(head), FadeIn(ev, shift=UP * 0.4), s.caption("10:29. Escribo /start.",
                                                             accents={"/start.": PURPLE}),
          rt=1.0)
    s.run(s.source("Telegram · bot Sol13 · 10:29"), rt=0.4)
    s.focus = ev
    s.until(16.0)
    box, lp, veil = s.zoom_highlight(ev, 0, caption="Primera orden: «No hagas capturas».",
                                     accents={"capturas».": ALERT})
    s.until(19.0, focus=lp)
    st = stamp("HICE 47", ALERT, size=100, angle=0.1).move_to([0.6, Y_EVID - 2.05, 0])
    st.set_z_index(45)
    s.run(FadeIn(st, scale=2.0), rt=0.4)
    s.run(Flash(st.get_center(), color=ALERT, flash_radius=1.5, num_lines=16), rt=0.5)
    s.until(21.6, focus=st)
    s.clear_zoom(box, lp, veil, st)
    box, lp, veil = s.zoom_highlight(ev, 1, caption="«48 horas. Ya vas tarde.»",
                                     accents={"tarde.»": ALERT})
    s.until(26.4, focus=lp)
    s.clear_zoom(box, lp, veil)
    ev2 = Evidence("walkaway")
    s.swap_evidence(ev, ev2)
    s.run(s.source("Telegram · Sol13 · 10:29–10:30"), rt=0.3)
    b0 = ev2.box(0)
    s.run(Create(b0), s.caption("«Fuiste elegido para llegar aquí.»",
                                accents={"elegido": GOLD}), rt=1.0)
    s.until(30.4, focus=ev2)
    b1 = ev2.box(1, color=GOLD)
    s.run(Create(b1), s.caption("Dos botones: irte o cruzar.", font=FONT_SANS), rt=1.0)
    s.until(33.4, focus=ev2)
    s.run(s.caption("Crucé.", accents={"crucé.": PURPLE}, size=72), rt=0.7)
    s.until(36.0, focus=ev2)


TRIALS_A = [
    # (n, palabra, hora, evidencia, caption, quote_evid, quote_idx, quote_caption)
    (1, "CHOSEN", "10:40", "palimpsest", "Dos textos. Solo cambia una palabra.",
     "palimpsest", 1, "«Entenderás por qué estás aquí.»"),
    (2, "POWER", "10:45", "trial02", "Emerson con contraseña. Cuenta 8 palabras.",
     None, None, "«Estás entre la fracción que posee esta capacidad.»"),
    (3, "ALARIC", "10:47", "trial03", "Lógica: tres iniciados, tres símbolos.",
     "alaric", 0, "«Cada error quema tiempo que no tienes.»"),
    (4, "ASCEND", "11:03", "wordsearch", "Sopa de letras. Las iniciales: ASCEND.",
     "ascend", 0, "«La mayoría nunca ve esta sala.»"),
]
TRIALS_B = [
    (5, "DANCE", "11:05", "fifth", "Sigilos de facciones → iniciales.",
     "trial05", 0, "«El reloj nunca se detiene por ti.»"),
    (6, "1933", "11:17", "streetview", "Street View, Nueva York. Año en la piedra.",
     "y1933", 1, "«La vigilancia se estrecha sobre tu usuario.»"),
    (7, "MANIFEST", "11:22", "trial07", "Un vídeo: 4 fragmentos en milisegundos.",
     "trial07", 0, "«Captura cada fragmento antes de que arda.»"),
    (8, "CLARITY", "11:34", "sun", "Una palabra escondida en el Sol.",
     "trial08", 0, "«Menos de 1 de cada 1.000 llega aquí.»"),
]
QUOTE_SOURCES = {2: "TRAL_2_REWARD.pdf · premio del acertijo 2"}


def trial_beat(s, spec, t0, dur, prev_ev):
    n, word, hhmm, evname, cap, qev, qi, qcap = spec
    head = s.header(f"ACERTIJO {n}/9", PURPLE)
    if s.hook_mob is not None:
        s.run(FadeOut(s.hook_mob), rt=0.15)
    s.hook_mob = head
    ev = Evidence(evname, max_h=EVID_MAX_H - 0.4)
    old = [prev_ev] if prev_ev is not None else []
    s.run(FadeIn(head), *[FadeOut(o, shift=LEFT * 0.6) for o in old],
          FadeIn(ev, shift=LEFT * 0.6), s.caption(cap, font=FONT_SANS, rt=0.9), rt=1.0)
    s.focus = ev
    s.until(t0 + dur * 0.36)
    extra, extra_mobs = [], []
    if n == 6:
        mine = stamp("ESTE LO SAQUÉ YO", GOLD, size=52, angle=0.08).move_to([0, Y_EVID - 1.9, 0])
        extra, extra_mobs = [FadeIn(mine, shift=UP * 0.3)], [mine]
    if n == 8:
        gem = mono("metadatos: imagen generada con Gemini", 40, CYAN)
        gem.next_to(ev, DOWN, buff=0.12).set_z_index(30)
        extra, extra_mobs = [FadeIn(gem)], [gem]
    st = s.solve(word, hhmm, extra=extra)
    s.until(t0 + dur * 0.55, focus=st)
    # La frase del bot / del premio
    if qev is not None:
        qe = Evidence(qev, max_h=EVID_MAX_H - 0.4)
        s.run(FadeOut(st), FadeOut(ev), *[FadeOut(m) for m in extra_mobs], FadeIn(qe), rt=0.35)
        box, lp, veil = s.zoom_highlight(qe, qi, caption=qcap)
        s.until(t0 + dur - 0.35, focus=lp)
        s.run(FadeOut(box), FadeOut(lp), FadeOut(veil), rt=0.3)
        return qe
    card = RoundedRectangle(width=7.8, height=2.6, corner_radius=0.2, stroke_width=4,
                            color=GOLD).set_fill(BG, 0.95).move_to([0, Y_EVID, 0]).set_z_index(40)
    q = kinetic_text(qcap, size=60, font=FONT_SERIF, color=GOLD).move_to(card).set_z_index(41)
    srcq = mono(QUOTE_SOURCES.get(n, ""), 36, CYAN).next_to(card, DOWN, buff=0.15).set_z_index(41)
    s.run(FadeOut(st), *[FadeOut(m) for m in extra_mobs], FadeIn(card), reveal_words(q, 1.0),
          FadeIn(srcq),
          s.caption("Y de premio, el halago:", rt=0.8, accents={"halago:": GOLD}), rt=1.1)
    s.until(t0 + dur - 0.35, focus=card)
    s.run(FadeOut(VGroup(card, q, srcq)), rt=0.3)
    return ev


def block2(s):
    """0:36–1:16 · Acertijos 1–4 (compromiso: pequeños síes)."""
    s.transition(None)
    s.run(*s.stage_chip(2), rt=0.5)
    t, ev = s.now, None
    dur = (76 - t) / 4
    for k, spec in enumerate(TRIALS_A):
        ev = trial_beat(s, spec, t + k * dur, dur, ev)
        s.until(t + (k + 1) * dur)
    s.until(76.0)


def block3(s):
    """1:16–1:52 · Acertijos 5–8 (escalada: urgencia + élite)."""
    s.transition(None)
    s.run(*s.stage_chip(3), rt=0.5)
    t, ev = s.now, None
    dur = (112 - t) / 4
    for k, spec in enumerate(TRIALS_B):
        ev = trial_beat(s, spec, t + k * dur, dur, ev)
        s.until(t + (k + 1) * dur)
    s.until(112.0)


def block4(s):
    """1:52–2:16 · Acertijo 9: el coste hundido, dicho con su nombre."""
    s.transition(None)
    s.run(*s.stage_chip(4), rt=0.5)
    head = s.header("ACERTIJO 9/9 · EL ÚLTIMO", PURPLE)
    s.hook_mob = head
    ev = Evidence("sunkcost")
    s.run(FadeIn(head), FadeIn(ev, shift=UP * 0.3), s.caption("Antes del último acertijo, esto:",
                                                             font=FONT_SANS), rt=1.0)
    s.run(s.source("The-Lens-of-Clarity.pdf · Trial 09"), rt=0.3)
    s.focus = ev
    s.until(115.5)
    box, lp, veil = s.zoom_highlight(ev, 1, caption="«El coste hundido exige completarlo.»",
                                     accents={"hundido": ALERT})
    s.until(119.6, focus=lp)
    s.clear_zoom(box, lp, veil)
    box, lp, veil = s.zoom_highlight(ev, 0, caption="«Abandonar sería traicionarte a ti mismo.»",
                                     accents={"traicionarte": ALERT})
    s.until(123.6, focus=lp)
    lit = stamp("LO DICEN LITERALMENTE", ALERT, size=58, angle=-0.06).move_to([0, -1.4, 0])
    lit.set_z_index(45)
    s.run(FadeIn(lit, scale=1.8), rt=0.4)
    s.until(126.2, focus=lit)
    s.clear_zoom(box, lp, veil, lit)
    ev2 = Evidence("ignite")
    s.swap_evidence(ev, ev2, rt=0.5)
    s.run(s.source("Telegram · Sol13 · 11:36"), rt=0.3)
    st = s.solve("IGNITE", "11:36")
    b = ev2.box(1, color=GOLD)
    s.run(Create(b), s.caption("Protocolo completo: 9/9.", font=FONT_SANS), rt=0.9)
    s.until(136.0, focus=st)


def block5(s):
    """2:16–2:44 · El pitch y el precio."""
    s.transition(None)
    s.run(*s.stage_chip(5), s.set_clock("11:37"), rt=0.5)
    head = s.header("11:37 · EL PITCH", ALERT)
    s.hook_mob = head
    ev = Evidence("clearance1")
    s.run(FadeIn(head), FadeIn(ev, shift=UP * 0.3), rt=0.6)
    s.run(s.source("Telegram · Sol13 · 11:37"), rt=0.3)
    box, lp, veil = s.zoom_highlight(ev, 1, caption="«Exactamente 130 plazas. Ni una más.»",
                                     accents={"130": CYAN})
    s.until(141.2, focus=lp)
    s.clear_zoom(box, lp, veil)
    box, lp, veil = s.zoom_highlight(ev, 0, caption="«Ventana estricta de 48 horas.»")
    s.until(145.0, focus=lp)
    s.clear_zoom(box, lp, veil)
    ev2 = Evidence("clearance2")
    s.swap_evidence(ev, ev2, rt=0.5)
    box, lp, veil = s.zoom_highlight(ev2, 0, caption="«Altos estándares, alta fricción.»")
    s.until(148.4, focus=lp)
    s.clear_zoom(box, lp, veil)
    b = ev2.box(1, color=GOLD)
    s.run(Create(b), s.caption("Botón: «Reclama tu asiento».", accents={"asiento».": GOLD}),
          rt=0.9)
    s.until(150.6, focus=ev2)
    # Whop: el precio
    ev3 = Evidence("whop")
    s.swap_evidence(Group(ev2, b), ev3, rt=0.5)
    s.run(s.source("whop.com · MALZIRN · 11:54"), rt=0.3)
    bp = ev3.box(0)
    price = sans("313 US$", 170, ALERT).move_to([0, Y_EVID, 0]).set_z_index(45)
    s.run(Create(bp), rt=0.3)
    s.run(FadeIn(price, scale=2.3), s.caption("¿Qué compras? No lo dicen.",
                                              accents={"dicen.": ALERT}), rt=0.8)
    s.glitch(0.2, strength=0.25)
    s.until(156.0, focus=price)
    # La contradicción de sus propias cifras
    s.run(FadeOut(price), rt=0.3)
    bc = ev3.box(1)
    s.run(Create(bc), rt=0.3)
    left = VGroup(mono("BOT", 44, CYAN), sans("1/1000", 92, BONE),
                  mono("«menos de 1 de cada mil»", 32, BONE)).arrange(DOWN, buff=0.15)
    right = VGroup(mono("WHOP", 44, CYAN), sans("1/100", 92, BONE),
                   mono("«el 99% descartado»", 32, BONE)).arrange(DOWN, buff=0.15)
    vs = sans("≠", 120, ALERT)
    duo = VGroup(left, vs, right).arrange(RIGHT, buff=0.5)
    card = RoundedRectangle(width=8.2, height=duo.height + 0.7, corner_radius=0.2, stroke_width=4,
                            color=ALERT).set_fill(BG, 0.96)
    grp = VGroup(card, duo).move_to([0, Y_EVID, 0]).set_z_index(45)
    duo.move_to(card)
    s.run(FadeIn(grp, scale=0.8), s.caption("Ni sus propias cifras cuadran.",
                                            accents={"cuadran.": ALERT}), rt=0.9)
    s.until(164.0, focus=grp)


SIGNS = ["Te llama «elegido»", "Te mete prisa", "Te halaga sin parar",
         "Usa tu coste hundido", "No dice qué vende"]


def block6(s):
    """2:44–3:00 · No pagué + 5 señales + CTA."""
    s.transition(None)
    st = stamp("NO PAGUÉ", CYAN, size=104, angle=-0.08).move_to([0, 1.2, 0])
    s.run(FadeIn(st, scale=2.2), rt=0.4)
    s.run(Flash(st.get_center(), color=CYAN, flash_radius=2.2, num_lines=20), rt=0.5)
    s.until(166.6, focus=st)
    rows = VGroup()
    for i, t in enumerate(SIGNS, 1):
        num = sans(str(i), 64, BG)
        disc = Circle(radius=0.36, stroke_width=0).set_fill(ALERT, 1)
        num.move_to(disc)
        rows.add(VGroup(VGroup(disc, num), sans(t, 58, BONE)).arrange(RIGHT, buff=0.35))
    rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT).move_to([0, 0.9, 0])
    title = mono("LAS 5 SEÑALES", 56, GOLD).next_to(rows, UP, buff=0.4)
    s.run(FadeOut(st, scale=0.6), FadeIn(title), rt=0.4)
    s.run(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.5) for r in rows], lag_ratio=0.45), rt=3.2)
    s.focus = rows
    s.until(172.0)
    banner = RoundedRectangle(width=8.2, height=1.45, corner_radius=0.22, stroke_width=3,
                              color=GOLD).set_fill(BG, 0.95).move_to([0, -3.2, 0]).set_z_index(61)
    cta = kinetic_text("¿Te ha pasado? Cuéntamelo en comentarios.", size=54, font=FONT_SANS,
                       accents={"cuéntamelo": GOLD}).move_to(banner).set_z_index(62)
    follow = kinetic_text("Sígueme para más.", size=50, font=FONT_SANS, color=CYAN)
    follow.move_to([0, -4.45, 0]).set_z_index(62)
    arrow = Arrow([2.6, 3.0, 0], [3.5, 4.55, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.25)
    arrow.add_updater(blink_updater(7))
    s.run(VGroup(title, rows).animate.scale(0.9).shift(UP * 0.4), FadeIn(banner),
          reveal_words(cta, 1.0), rt=1.1)
    s.add(arrow)
    s.run(reveal_words(follow, 0.8), rt=0.8)
    s.until(180.0, focus=rows)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]


class _Block(FunnelScene):
    INDEX = 0

    def construct(self):
        self.k_setup(self.INDEX)
        BLOCKS[self.INDEX](self)
        assert self.frames == ENDS[self.INDEX] * FPS, (self.INDEX, self.frames)


Block0 = type("Block0", (_Block,), {"INDEX": 0})
Block1 = type("Block1", (_Block,), {"INDEX": 1})
Block2 = type("Block2", (_Block,), {"INDEX": 2})
Block3 = type("Block3", (_Block,), {"INDEX": 3})
Block4 = type("Block4", (_Block,), {"INDEX": 4})
Block5 = type("Block5", (_Block,), {"INDEX": 5})
Block6 = type("Block6", (_Block,), {"INDEX": 6})


class FullVideo(FunnelScene):
    def construct(self):
        self.k_setup(0)
        for i, block in enumerate(BLOCKS):
            assert self.frames == STARTS[i] * FPS, (i, self.frames)
            block(self)
            assert self.frames == ENDS[i] * FPS, (i, self.frames)
        assert self.frames == TOTAL * FPS
