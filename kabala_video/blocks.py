"""
blocks.py — Los 7 bloques del guion (§4). Cada función recibe la escena
(KabalaScene) y avanza su reloj hasta el segundo ABSOLUTO de fin de bloque.

Tiempos absolutos:  B0 0–15 · B1 15–45 · B2 45–75 · B3 75–105 ·
                    B4 105–135 · B5 135–165 · B6 165–180
"""
from __future__ import annotations

import numpy as np
from manim import (
    BOLD, DOWN, LEFT, NORMAL, ORIGIN, PI, RIGHT, TAU, UP,
    AddTextLetterByLetter, AnimationGroup, Arrow, Circle, Create, Dot, FadeIn,
    FadeOut, Flash, GrowFromCenter, LaggedStart, Line, ReplacementTransform,
    Rectangle, RoundedRectangle, Square, Succession, Text, Transform, UpdateFromAlphaFunc,
    VGroup, VMobject, smooth, there_and_back,
)

import shapes as S
from utils import (
    BG, BONE, CYAN, FONT_MONO, FONT_SANS, FONT_SERIF, GOLD, HEBREW, HUD_POS,
    MAX_W, PATHS, RED, T, RED_GLOW, SIZE_HERO, SIZE_HOOK, Y_CAP, Y_VIS, TreeOfLife,
    blink_updater, flip_recolor, kinetic_text, px, reveal_words, spin_updater,
)

ACC_GOLD = GOLD


def label(text, color=CYAN, size=48, font=FONT_MONO, weight=BOLD):
    """Etiqueta corta (término hebreo / dato) — 48 px mínimo."""
    return T(text, font=font, font_size=px(size), weight=weight, color=color,
                disable_ligatures=True)


def big_tree(color=GOLD, scale=0.9, center=(0, Y_VIS, 0)):
    return TreeOfLife(scale=scale, color=color, stroke=3.2, center=np.array(center))


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 0 — GANCHO + CTA DE APERTURA (0:00–0:15)
# ═════════════════════════════════════════════════════════════════════════════
def block0(s):
    tree = big_tree()
    tree.paths.set_stroke(GOLD, opacity=0.45)
    # 0:00–0:03 · contorno dorado + «El código que la humanidad olvidó.»
    cap = s.caption("El código que la humanidad olvidó.", rt=1.8, size=SIZE_HOOK,
                    accents={"código": GOLD})
    s.run(LaggedStart(Create(tree.nodes, lag_ratio=0.08), Create(tree.paths, lag_ratio=0.05),
                      lag_ratio=0.25), cap, rt=2.6)
    s.focus = tree
    s.until(3.0)

    # 0:03–0:08 · el contorno se ilumina
    s.run(tree.light_all(run_time=2.0), s.caption(
        "Cábala. Merkabá. Nombres divinos.", rt=1.4, size=SIZE_HOOK, font=FONT_SANS,
        accents={"cábala": GOLD, "merkabá": GOLD, "divinos": GOLD}), rt=2.2)
    s.run(s.source("Fuente: Brujería con Efraín (iVoox)"), rt=0.5)
    s.until(8.0)

    # 0:08–0:12 · el árbol se repliega al HUD; ojo de la providencia
    hud_target = s.hud.copy()
    hud_target.light_now([1])
    hud_target.paths.set_stroke(GOLD, opacity=0.7)
    eye = S.providence_eye(3.6).move_to([0, Y_VIS + 0.1, 0])
    s.run(Transform(tree, hud_target), s.drop_source(), rt=1.1)
    s.remove(tree)
    s.hud.light_now([1])
    s.hud.paths.set_stroke(GOLD, opacity=0.7)
    s.add(s.hud)
    s.hud_lit = 1
    s.run(Create(eye.tri), Create(eye.eye), LaggedStart(*[Create(r) for r in eye.rays], lag_ratio=0.05),
          s.caption("Esto es lo que los archivos ocultan.", rt=1.4,
                    accents={"archivos": GOLD, "ocultan": GOLD}), rt=1.9)
    eye.rays.add_updater(spin_updater(0.12))
    s.focus = eye
    s.until(12.0)

    # 0:12–0:15 · CTA de apertura (cintillo inferior + flecha parpadeante)
    ribbon = RoundedRectangle(width=8.3, height=1.75, corner_radius=0.22, stroke_width=3,
                              color=GOLD).set_fill(BG, 0.92).move_to([0, -3.15, 0])
    s.run(s.drop_caption(), FadeIn(ribbon, shift=UP * 0.4), eye.animate.scale(0.85).shift(UP * 0.4),
          rt=0.4)
    q = kinetic_text("Quédate.", size=80, font=FONT_SERIF, color=GOLD).move_to(ribbon)
    arrow = Arrow([2.2, 3.4, 0], [3.65, 5.75, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.22)
    arrow.add_updater(blink_updater(7))
    s.add(arrow)
    s.run(reveal_words(q, 0.5), rt=0.6)
    s.until(13.1, focus=q)
    msg = kinetic_text("El nombre del árbol invertido aparece al final.", size=52,
                       font=FONT_SANS, accents={"invertido": GOLD, "final.": GOLD},
                       max_width=7.8).move_to(ribbon)
    s.run(FadeOut(q, shift=UP * 0.2), rt=0.2)
    s.run(reveal_words(msg, 0.9), rt=0.9)
    s.until(15.0, focus=eye)


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 — ORIGEN: LA MERKAVÁ (0:15–0:45)
# ═════════════════════════════════════════════════════════════════════════════
def block1(s):
    s.transition(hud_index=2)
    # Gancho + carro de fuego
    car = S.merkava().scale(0.95).move_to([0, Y_VIS - 0.2, 0])
    s.run(s.hook("Antes de la Cábala, estaba el Carro.", accents={"carro.": GOLD, "cábala,": GOLD}),
          LaggedStart(Create(car.wheels), FadeIn(car.flames, shift=UP * 0.3),
                      Create(VGroup(car[1], car[4])), FadeIn(car.throne, scale=0.8),
                      lag_ratio=0.3), rt=2.2)
    for w in car.wheels:
        w.add_updater(spin_updater(-1.1))
    car.flames.add_updater(S.flame_updater)
    s.focus = car.throne
    s.run(s.caption("Merkavá: el misticismo del Carro divino.", font=FONT_SERIF,
                    accents={"merkavá:": GOLD}), rt=1.2)
    s.run(s.source("Fuente: The Bart Ehrman Blog"), rt=0.5)
    s.until(22.0)

    # 0:22–0:30 · palacios con siete puertas, el descenso
    pal = S.palaces(7).move_to([0, Y_VIS - 0.25, 0])
    tag = VGroup(label("HEKHALOT", CYAN), label("היכלות", GOLD, font=FONT_SANS))
    tag.arrange(RIGHT, buff=0.35).move_to([0, 2.95, 0])
    s.run(s.drop_hook(), FadeOut(car, shift=UP * 0.6, scale=0.8), rt=0.5)
    for m in car.get_family():
        m.clear_updaters()
    s.run(LaggedStart(*[Create(g) for g in pal.gates], lag_ratio=0.18), Create(pal[0]),
          FadeIn(tag, shift=DOWN * 0.2),
          s.caption("Los practicantes ‘descendían’ a los palacios divinos.",
                    accents={"‘descendían’": GOLD}), rt=1.8)
    s.run(s.source("Fuente: Justin Sledge · The Bart Ehrman Blog"), rt=0.4)
    # La luz del practicante atraviesa las puertas; los guardianes se agitan
    soul = VGroup(Dot(radius=0.11, color=BONE), Circle(radius=0.22, stroke_width=0).set_fill(GOLD, 0.35))
    gates = pal.gates
    p_start = np.array([0, gates[0].get_bottom()[1] + 0.6, 0])
    p_end = gates[-1].get_center() + DOWN * 0.15
    soul.move_to(p_start)
    s.add(soul)

    def travel(m, a):
        m.move_to(p_start + (p_end - p_start) * a)
        m.set_width(0.44 * (1 - 0.6 * a))
        k = int(a * 6.999)
        for j, g in enumerate(pal.guards):
            g.set_opacity(1.0 if j == k else 0.25)

    s.run(UpdateFromAlphaFunc(soul, travel, rate_func=smooth), rt=5.0)
    s.until(30.0, focus=soul)

    # 0:30–0:38 · el Séptimo Palacio brilla en oro (zoom al detalle)
    inner = gates[-1]
    thr = S.throne_icon(0.75).move_to(inner.get_center() + DOWN * 0.1)
    vii = label("VII", GOLD, size=64, font=FONT_SERIF).next_to(inner, UP, buff=0.12)
    s.run(FadeOut(soul, scale=2.5), pal.guards.animate.set_opacity(0.1),
          VGroup(*gates[:-1]).animate.set_stroke(opacity=0.18),
          inner.animate.set_stroke(GOLD, width=7, opacity=1), FadeIn(thr, scale=0.5),
          FadeIn(vii), rt=1.0)
    s.run(Flash(inner.get_center(), color=GOLD, line_length=0.5, num_lines=16, flash_radius=0.9),
          s.caption("Séptimo Palacio: el Trono de Yahvé.", accents={"séptimo": GOLD, "palacio:": GOLD,
                                                                  "yahvé.": GOLD}), rt=1.2)
    s.run(s.source("Fuente: Justin Sledge"), rt=0.4)
    zoom_group = VGroup(pal, thr, vii)
    s.run(zoom_group.animate.scale(1.6, about_point=inner.get_center()).shift(
        (np.array([0, Y_VIS, 0]) - inner.get_center()) * 0.9), FadeOut(tag), rt=2.0)
    s.focus = thr
    s.until(38.0)

    # 0:38–0:45 · el carro se transforma en un árbol de luz
    car2 = S.merkava().scale(0.95).move_to([0, Y_VIS - 0.2, 0])
    tree = big_tree().light_now(range(1, 11))
    tree.paths.set_stroke(GOLD, opacity=0.95)
    s.run(FadeOut(zoom_group, scale=1.3), FadeIn(car2, scale=0.7), rt=0.8)
    s.run(ReplacementTransform(car2, tree), s.caption("De aquí nace la Cábala.",
                                                      accents={"cábala.": GOLD}), rt=2.2)
    s.run(s.source("Fuente: Brujería con Efraín · Religiondigital"), rt=0.4)
    s.until(45.0, focus=tree)


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 — EL ÁRBOL DE LA VIDA (0:45–1:15)
# ═════════════════════════════════════════════════════════════════════════════
def block2(s):
    s.transition(hud_index=3)
    tree = big_tree()
    nums = VGroup(*[label(str(i), BONE, size=44 if i == 10 else 48, font=FONT_SANS)
                    .move_to(tree.pos[i]) for i in range(1, 11)])
    s.run(s.hook("Diez esferas. Veintidós senderos. Un mapa del universo.",
                 accents={"diez": CYAN, "veintidós": CYAN, "universo.": GOLD}), rt=1.5)
    tree.light_now(range(1, 11))
    s.run(LaggedStart(*[AnimationGroup(GrowFromCenter(VGroup(tree.glows[i - 1], tree.node(i))),
                                       FadeIn(nums[i - 1], scale=0.5))
                        for i in range(1, 11)], lag_ratio=0.35),
          s.caption("Las 10 sefirot: emanaciones de Dios.", font=FONT_SANS,
                    accents={"sefirot:": GOLD}), rt=3.0)
    s.run(s.source("Fuente: Sefer Yetzirah"), rt=0.4)
    s.focus = tree
    s.until(55.0)

    # 0:55–1:05 · 22 senderos = 22 letras hebreas
    letters = VGroup()
    for (a, b), ch in zip(PATHS, HEBREW):
        mid = (tree.pos[a] + tree.pos[b]) / 2
        disc = Circle(radius=0.2, stroke_width=0).set_fill(BG, 0.9).move_to(mid)
        t = T(ch, font=FONT_SANS, font_size=px(48), weight=BOLD, color=CYAN).move_to(mid)
        letters.add(VGroup(disc, t))
    s.run(s.drop_hook(), FadeOut(nums), rt=0.3)
    s.run(LaggedStart(*[AnimationGroup(Create(p), FadeIn(l, scale=0.4))
                        for p, l in zip(tree.paths, letters)], lag_ratio=0.12),
          tree.paths.animate.set_stroke(GOLD, opacity=0.95),
          s.caption("22 letras hebreas: los senderos de la sabiduría.", font=FONT_SANS,
                    accents={"sabiduría.": GOLD}), rt=3.2)
    s.add(tree.paths)
    s.run(s.source("Fuente: Sefer Yetzirah (trad. Kaplan)"), rt=0.4)
    eq = kinetic_text("10 + 22 = 32", size=88, font=FONT_SANS, accents={"=": BONE, "+": BONE})
    eq[-1].set_color(GOLD)
    eq.move_to([0, 3.75, 0])
    s.run(reveal_words(eq, 1.0), rt=1.0)
    # Zoom a un detalle: la primera letra (Álef) del primer sendero
    aleph = letters[0][1]
    zoom = aleph.copy().set_z_index(12)
    veil = Rectangle(width=9.4, height=16.4, stroke_width=0).set_fill(BG, 0).set_z_index(11)
    s.add(veil)
    s.run(zoom.animate.scale(5.5).move_to([0, Y_VIS, 0]).set_color(GOLD),
          veil.animate.set_fill(BG, 0.72), rt=0.8)
    s.until(63.4, focus=zoom)
    s.run(zoom.animate.scale(1 / 5.5).move_to(aleph).set_color(CYAN).set_opacity(0),
          veil.animate.set_fill(BG, 0), rt=0.8)
    s.remove(zoom, veil)
    s.until(65.0, focus=tree)

    # 1:05–1:15 · Adam Kadmón: el Árbol sobre una silueta humana
    man = S.adam_kadmon(tree)
    lab_k = label("corona", GOLD, size=48, font=FONT_SANS).next_to(tree.node(1), RIGHT, buff=0.45)
    lab_k.shift(UP * 0.2)
    lab_kn = label("Kéter", BONE, size=48, font=FONT_SANS).next_to(tree.node(1), LEFT, buff=0.45)
    lab_kn.shift(UP * 0.2)
    lab_h = label("hemisferios", CYAN, size=48, font=FONT_SANS)
    lab_h.move_to([0, tree.pos[2][1] - 0.55 * tree.s, 0])
    lab_j = label("Jojmá", BONE, size=48, font=FONT_SANS).next_to(tree.node(2), RIGHT, buff=0.3)
    lab_b = label("Biná", BONE, size=48, font=FONT_SANS).next_to(tree.node(3), LEFT, buff=0.3)
    lab_m = label("Maljut", BONE, size=48, font=FONT_SANS).next_to(tree.node(10), RIGHT, buff=0.45)
    lab_h.next_to(lab_j, DOWN, buff=0.12, aligned_edge=LEFT)
    if lab_h.get_right()[0] > 4.0:
        lab_h.shift(LEFT * (lab_h.get_right()[0] - 4.0))
    labs = VGroup(lab_kn, lab_k, lab_j, lab_h, lab_b, lab_m)
    s.run(FadeOut(letters), FadeOut(eq), FadeIn(man, scale=1.08), rt=1.4)
    s.run(LaggedStart(*[FadeIn(l, shift=LEFT * 0.2) for l in labs], lag_ratio=0.2),
          s.caption("Adam Kadmón: el Hombre Celeste.", accents={"adam": GOLD, "kadmón:": GOLD}),
          rt=1.6)
    s.run(s.source("Fuente: Manly P. Hall, Las enseñanzas secretas"), rt=0.4)
    # recorrido de luz de la corona a los pies
    s.run(LaggedStart(*[Flash(tree.pos[i], color=GOLD, line_length=0.18, flash_radius=0.38,
                              num_lines=10) for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)],
                      lag_ratio=0.25), rt=3.0)
    s.until(75.0, focus=VGroup(tree, man))


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — EIN SOF Y LOS NOMBRES (1:15–1:45)
# ═════════════════════════════════════════════════════════════════════════════
def _rings_updater(n=7, maxr=3.6, speed=0.75):
    def u(m, dt):
        m.t_ = getattr(m, "t_", 0.0) + dt
        for k, c in enumerate(m):
            r = 0.6 + ((m.t_ * speed + k * maxr / n) % maxr)
            c.set(width=2 * r)
            c.set_stroke(opacity=max(0.0, 0.7 * (1 - r / (maxr + 0.6))))
    return u


def block3(s):
    s.transition(hud_index=4)
    c = np.array([0, Y_VIS + 0.3, 0])
    rings = VGroup(*[Circle(radius=1, color=GOLD, stroke_width=3).move_to(c) for _ in range(7)])
    rings.add_updater(_rings_updater())
    ein = Text("EIN SOF", font=FONT_MONO, font_size=px(SIZE_HERO), weight=BOLD, color=GOLD).move_to(c)
    heb = label("אין סוף", BONE, size=56, font=FONT_SANS).next_to(ein, DOWN, buff=0.35)
    s.run(s.hook("Dios no tiene nombre. Solo tiene códigos.", accents={"códigos.": GOLD}), rt=1.3)
    s.add(rings)
    s.run(FadeIn(ein, scale=1.5), FadeIn(heb, shift=UP * 0.2), rt=1.2)
    s.run(s.caption("El Infinito. Sin final.", accents={"infinito.": GOLD}), rt=1.1)
    s.run(s.source("Fuente: Mario Satz, Árbol Verbal"), rt=0.4)
    epi = VGroup(label("Hashem", CYAN), label("·", BONE), label("Adonai", CYAN)).arrange(RIGHT, buff=0.3)
    epi.next_to(heb, DOWN, buff=0.55)
    s.run(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in epi], lag_ratio=0.3), rt=1.0)
    s.focus = ein
    s.until(85.0)

    # 1:25–1:35 · letras flotando + 72 nombres + 40 nombres
    s.run(s.drop_hook(), FadeOut(VGroup(ein, heb, epi)), rings.animate.set_opacity(0), rt=0.5)
    rings.clear_updaters()
    s.remove(rings)
    cols, rows, cell = 9, 8, 0.46
    grid = VGroup(*[Square(side_length=cell * 0.86, color=BONE, stroke_width=2, stroke_opacity=0.6)
                    .set_fill(BONE, 0.04) for _ in range(72)])
    grid.arrange_in_grid(rows=rows, cols=cols, buff=cell * 0.14).move_to([0, Y_VIS - 0.25, 0])
    ref = label("Éxodo 14:19-21", CYAN, size=52).next_to(grid, UP, buff=0.35)
    rng = s.rng
    floating = VGroup()
    for i in range(26):
        ch = HEBREW[i % 22]
        t = T(ch, font=FONT_SANS, font_size=px(rng.uniform(52, 92)), weight=BOLD,
                 color=GOLD if i % 3 == 0 else CYAN)
        t.set_opacity(rng.uniform(0.35, 0.8))
        t.move_to([rng.uniform(-3.7, 3.7), rng.uniform(-2.2, 3.2), 0])
        t.vel = np.array([rng.uniform(-0.25, 0.25), rng.uniform(0.1, 0.35), 0])
        t.spin = rng.uniform(-0.4, 0.4)
        floating.add(t)

    def drift(m, dt):
        for t in m:
            t.shift(t.vel * dt)
            t.rotate(t.spin * dt)
            if t.get_y() > 3.4:
                t.set_y(-2.4)
            if abs(t.get_x()) > 3.9:
                t.set_x(-np.sign(t.get_x()) * 3.8)

    floating.set_z_index(-5)
    s.run(LaggedStart(*[FadeIn(t, scale=0.3) for t in floating], lag_ratio=0.04),
          LaggedStart(*[GrowFromCenter(q) for q in grid], lag_ratio=0.015),
          FadeIn(ref, shift=DOWN * 0.2),
          s.caption("72 nombres. 40 nombres. Poder en cada letra.", font=FONT_SANS,
                    accents={"letra.": GOLD}), rt=2.2)
    floating.add_updater(drift)
    s.run(s.source("Fuente: Benditos Ángeles"), rt=0.4)
    # 40 de los 72 se encienden en oro (subconjunto)
    order = rng.permutation(72)[:40]
    s.run(LaggedStart(*[grid[int(i)].animate.set_fill(GOLD, 0.7).set_stroke(GOLD, opacity=1)
                        for i in order], lag_ratio=0.04), rt=2.0)
    power = label("curación · protección", BONE, size=50, font=FONT_SANS).next_to(ref, UP, buff=0.25)
    s.run(FadeIn(power, shift=UP * 0.2), rt=0.5)
    s.focus = grid
    s.until(95.0)

    # 1:35–1:45 · kamea con un nombre divino
    s.run(FadeOut(VGroup(grid, ref, power)), floating.animate.set_opacity(0.12), rt=0.5)
    km = S.kamea(2.2).move_to([0, Y_VIS, 0])
    km.ring.add_updater(spin_updater(0.15))
    top_tag = label("Kabbalah Ma’asit", GOLD, size=52).move_to([0, 4.15, 0])
    s.run(Create(km[0]), Create(km[1]), Create(km.seal), FadeIn(km[3]),
          LaggedStart(*[FadeIn(t, scale=0.5) for t in km.ring], lag_ratio=0.05),
          FadeIn(km.center_name, scale=1.6), FadeIn(top_tag, shift=DOWN * 0.2),
          s.caption("Cábala práctica: amuletos y sellos.", accents={"amuletos": GOLD, "sellos.": GOLD}),
          rt=2.0)
    km.seal.add_updater(spin_updater(-0.08))
    s.run(s.source("Fuente: Brujería con Efraín"), rt=0.4)
    raz = label("kameot · Sefer Raziel HaMalakh", CYAN, size=48).next_to(top_tag, DOWN, buff=0.22)
    if raz.width > MAX_W:
        raz.scale_to_fit_width(MAX_W)
    s.run(FadeIn(raz, shift=DOWN * 0.15), rt=0.5)
    s.until(100.8, focus=km.center_name)
    # zoom al nombre divino del centro
    s.run(km.animate.scale(1.25, about_point=km.center_name.get_center()), rt=1.2)
    s.until(105.0, focus=km.center_name)


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — EL ÁRBOL DE LA MUERTE (1:45–2:15)
# ═════════════════════════════════════════════════════════════════════════════
def block4(s):
    s.transition(hud_index=5)
    tree = big_tree().light_now(range(1, 11))
    tree.paths.set_stroke(GOLD, opacity=0.95)
    s.run(s.hook("Existe un árbol inverso.", accents={"inverso.": RED_GLOW}),
          FadeIn(tree, scale=0.9), rt=1.2)
    s.focus = tree
    s.until(107.8)
    s.run(s.hook("Y no es una metáfora.", accents={"metáfora.": RED_GLOW}), rt=0.9)
    # 1:45–1:55 · el Árbol se INVIERTE y se vuelve rojo oscuro
    s.run(flip_recolor(tree, RED), rt=2.2)
    s.glitch(0.2, strength=0.25)
    s.run(s.caption("Qlifot: el Árbol de la Muerte.", accents={"qlifot:": RED_GLOW,
                                                              "muerte.": RED_GLOW}), rt=1.2)
    infern = label("«Árbol Infernal»", BONE, size=52, font=FONT_SERIF).move_to([0, 3.2, 0])
    s.run(s.source("Fuente: Les Cahiers de l’Adepte (1968)"), FadeIn(infern, shift=DOWN * 0.2), rt=0.5)
    s.until(115.0)

    # 1:55–2:05 · cáscaras: las esferas se rompen y quedan vacías
    shells = VGroup(*[S.shell(tree.r * 1.05, RED_GLOW, seed=i).move_to(tree.nodes[i].get_center())
                      for i in range(10)])
    word = VGroup(label("קליפות", RED_GLOW, size=60, font=FONT_SANS),
                  label("= «cáscaras», «pieles»", BONE, size=48, font=FONT_SERIF)).arrange(RIGHT, buff=0.3)
    word.move_to([0, 3.2, 0])
    s.run(s.drop_hook(), FadeOut(infern), rt=0.3)
    s.run(*[ReplacementTransform(VGroup(tree.nodes[i], tree.glows[i]), shells[i]) for i in range(10)],
          tree.paths.animate.set_stroke(RED, opacity=0.6), FadeIn(word, shift=DOWN * 0.2),
          s.caption("Cáscaras. Sefirot malignas. Desequilibrio.",
                    accents={"malignas.": RED_GLOW, "desequilibrio.": RED_GLOW}), rt=1.6)
    s.run(s.source("Fuente: Wikipedia (Qlifot) · Sensagent"), rt=0.4)
    rest = VGroup(tree.paths, shells)
    for i, sh in enumerate(shells):
        sh.add_updater(spin_updater(0.5 * (1 if i % 2 else -1)))

    # desequilibrio: el árbol oscila y las cáscaras se separan
    st = {"a": 0.0}
    piv = rest.get_center()

    def wobble(m, a):
        ang = 0.09 * np.sin(a * TAU * 2)
        m.rotate(ang - st["a"], about_point=piv)
        st["a"] = ang

    s.run(UpdateFromAlphaFunc(rest, wobble, suspend_mobject_updating=False),
          *[sh.animate.shift((sh.get_center() - piv) * 0.12) for sh in shells], rt=5.5)
    s.until(125.0, focus=rest)

    # 2:05–2:15 · el Gólem de Praga se forma con el lenguaje
    g = S.golem().scale(0.95).move_to([0, Y_VIS - 0.1, 0])
    ground = Line([-3, g.get_bottom()[1], 0], [3, g.get_bottom()[1], 0], color=BONE, stroke_opacity=0.4)
    for m in rest.get_family():
        m.clear_updaters()
    s.run(FadeOut(rest, shift=DOWN * 0.4), FadeOut(word), Create(ground), rt=0.6)
    s.run(LaggedStart(*[FadeIn(p, shift=UP * 0.8) for p in g.parts], lag_ratio=0.35),
          FadeIn(g[4]), FadeIn(g.eyes),
          s.caption("El Gólem de Praga: el poder del lenguaje.", accents={"gólem": GOLD,
                                                                        "lenguaje.": GOLD}), rt=2.2)
    s.run(s.source("Fuente: Brujería con Efraín"), rt=0.4)
    # el lenguaje sagrado fluye hacia la cabeza
    head = g.head.get_center()
    stream = VGroup()
    rng = s.rng
    for i in range(16):
        t = T(HEBREW[(i * 5) % 22], font=FONT_SANS, font_size=px(56), weight=BOLD, color=GOLD)
        t.move_to([rng.uniform(-3.6, 3.6), rng.uniform(2.6, 3.6), 0])
        stream.add(t)
    s.run(LaggedStart(*[Succession(FadeIn(t, scale=0.4, run_time=0.3),
                                   t.animate(run_time=0.9).move_to(head).scale(0.3).set_opacity(0))
                        for t in stream], lag_ratio=0.18), rt=3.4)
    s.remove(stream)
    s.run(g.eyes.animate.set_color(GOLD).scale(1.6), Flash(head, color=GOLD, flash_radius=0.9,
                                                          num_lines=14), rt=0.8)
    s.until(135.0, focus=g)


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — CÁBALA Y MASONERÍA (2:15–2:45)
# ═════════════════════════════════════════════════════════════════════════════
def block5(s):
    s.transition(hud_index=6)
    tp = S.temple().scale(1.05).move_to([0, Y_VIS - 0.35, 0])
    s.run(s.hook("La masonería no inventó sus símbolos. Los heredó.", accents={"heredó.": GOLD}),
          LaggedStart(Create(tp[0]), Create(tp[1]), Create(tp[4]), Create(tp[2]), Create(tp[3]),
                      lag_ratio=0.3), rt=2.6)
    s.run(tp[1].animate.set_fill(GOLD, 0.06), tp[3].animate.set_stroke(GOLD, width=6), rt=0.4)
    s.run(s.caption("El Templo es la clave del Rito Escocés.",
                    accents={"templo": GOLD, "clave": GOLD}), rt=1.3)
    s.run(s.source("Fuente: Zenit (Joan-Josep Durán, 31º)"), rt=0.4)
    reaa = label("R∴E∴A∴A∴", GOLD, size=56).next_to(tp, UP, buff=0.3)
    s.run(FadeIn(reaa, shift=DOWN * 0.2), rt=0.5)
    s.focus = tp
    s.until(145.0)

    # 2:25–2:35 · escuadra y compás sobre el Árbol
    tree = big_tree(scale=0.78).light_now(range(1, 11))
    tree.paths.set_stroke(GOLD, opacity=0.8)
    sc = S.square_compass(4.6).move_to(tree.get_center() + DOWN * 0.1)
    s.run(s.drop_hook(), FadeOut(tp, shift=UP * 0.4), FadeOut(reaa), rt=0.5)
    s.run(FadeIn(tree, scale=0.9), rt=0.8)
    veil = Rectangle(width=9.4, height=6.4, stroke_width=0).set_fill(BG, 0).move_to(tree)
    s.add(veil)
    s.run(Create(sc.square), Create(sc.compass[:3]), GrowFromCenter(sc.compass[3]),
          veil.animate.set_fill(BG, 0.45),
          s.caption("La Cábala está…", accents={"cábala": GOLD}), rt=1.6)
    s.run(s.source("Fuente: Zenit"), rt=0.4)
    s.until(150.0, focus=sc)
    # (la frase literal tiene 9 palabras: se reparte en dos pantallas ≤ 8)
    s.run(s.caption("…en la base de la masonería.", accents={"base": GOLD, "masonería.": GOLD}),
          rt=1.2)
    st = {"a": 0.0}
    hinge = sc.compass[3].get_center()

    def swing(m, a):            # el compás «mide» el árbol
        ang = 0.06 * np.sin(a * TAU)
        m.compass[0].rotate(ang - st["a"], about_point=hinge)
        m.compass[1].rotate(-(ang - st["a"]), about_point=hinge)
        st["a"] = ang

    s.run(UpdateFromAlphaFunc(sc, swing), rt=3.0)
    s.until(155.0, focus=sc)

    # 2:35–2:45 · nombres de cabalistas — siglos de tradición oculta
    quote = kinetic_text("«sobre hombros de gigantes»", size=58, font=FONT_SERIF, color=GOLD)
    quote.move_to([0, 3.4, 0])
    s.run(FadeOut(VGroup(tree, sc, veil), scale=0.8), reveal_words(quote, 1.0), rt=1.0)
    timeline = Line([-3.5, 1.9, 0], [-3.5, -1.6, 0], color=GOLD, stroke_width=3)
    c1 = S.dossier_card("Pico della Mirandola").move_to([0.25, 1.15, 0])
    c2 = S.dossier_card("Robert Fludd").move_to([0.25, -0.75, 0])
    pins = VGroup(Dot([-3.5, 1.15, 0], color=GOLD, radius=0.09), Dot([-3.5, -0.75, 0], color=GOLD, radius=0.09))
    s.run(Create(timeline), FadeIn(c1[:2], shift=LEFT * 0.6), FadeIn(pins[0]), rt=0.6)
    s.run(AddTextLetterByLetter(c1.label, time_per_char=0.05), rt=1.1)
    s.run(FadeIn(c2[:2], shift=LEFT * 0.6), FadeIn(pins[1]),
          s.caption("Siglos de tradición oculta.", accents={"oculta.": GOLD}), rt=1.0)
    s.run(AddTextLetterByLetter(c2.label, time_per_char=0.06), rt=0.8)
    s.run(s.source("Fuente: Zenit (Joan-Josep Durán, 31º)"), rt=0.4)
    s.until(165.0, focus=VGroup(c1, c2))


# ═════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 — CIERRE + CTA FINAL (2:45–3:00)
# ═════════════════════════════════════════════════════════════════════════════
def block6(s):
    s.transition(hud_index=None)
    # El HUD completa sus 10 sefirot
    s.run(LaggedStart(*[s.hud.light(i) for i in (7, 8, 9, 10)], lag_ratio=0.3), rt=1.0)
    s.hud_lit = 10
    life = big_tree(scale=0.82).light_now(range(1, 11))
    life.paths.set_stroke(GOLD, opacity=0.95)
    death = big_tree(color=RED, scale=0.82).light_now(range(1, 11))
    death.paths.set_stroke(RED_GLOW, opacity=0.9)
    death.rotate(PI, axis=RIGHT, about_point=death.get_center())
    death.set_opacity(0.0)
    lab_life = label("ETZ JAIM", GOLD, size=56).move_to([-2.0, 3.35, 0])
    lab_death = label("QLIFOT", RED_GLOW, size=56).move_to([2.2, 3.35, 0])
    s.run(FadeIn(life, scale=0.9), FadeIn(lab_life), rt=0.8)
    s.add(death)

    def ghost_in(m, a):
        for sm, (fo, so) in zip(m.family_members_with_points(), death_ops):
            sm.set_fill(opacity=fo * a)
            sm.set_stroke(opacity=so * a)

    death_ref = big_tree(color=RED, scale=0.82).light_now(range(1, 11))
    death_ref.paths.set_stroke(RED_GLOW, opacity=0.9)
    death_ops = [(sm.get_fill_opacity() * 0.85, sm.get_stroke_opacity() * 0.85)
                 for sm in death_ref.family_members_with_points()]
    s.run(UpdateFromAlphaFunc(death, ghost_in), FadeIn(lab_death),
          s.caption("10 sefirot. 22 senderos. 72 nombres. 1 pregunta.", font=FONT_SANS,
                    accents={"pregunta.": GOLD}, rt=2.4), rt=2.4)
    # La gran revelación: el HUD también se invierte → Qlifot
    s.run(flip_recolor(s.hud, RED), rt=1.0)
    duo = VGroup(life, death)
    s.until(172.0, focus=duo)

    # 2:52–3:00 · CTA final
    banner = RoundedRectangle(width=8.3, height=1.85, corner_radius=0.22, stroke_width=3,
                              color=GOLD).set_fill(BG, 0.92).move_to([0, -2.45, 0])
    cta = kinetic_text("Si quieres que analice el Sefer Yetzirah, sígueme.", size=52,
                       font=FONT_SANS, accents={"sefer": GOLD, "yetzirah,": GOLD, "sígueme.": GOLD},
                       max_width=7.8).move_to(banner)
    arrow = Arrow([3.05, 4.0, 0], [3.7, 5.8, 0], color=GOLD, stroke_width=8, buff=0,
                  max_tip_length_to_length_ratio=0.2)
    icon = S.comment_icon(1.0).move_to([3.3, -4.2, 0])
    ask = kinetic_text("¿Crees que la Cábala sigue viva? Dímelo.", size=48, font=FONT_SERIF,
                       accents={"viva?": GOLD, "dímelo.": GOLD}, max_width=6.0)
    ask.next_to(icon, LEFT, buff=0.3).set_y(-4.15)
    s.run(s.drop_caption(), s.drop_source(),
          duo.animate.scale(0.82).shift(UP * 0.45),
          FadeIn(banner, shift=UP * 0.4), rt=0.6)
    s.run(reveal_words(cta, 1.2), rt=1.2)
    arrow.add_updater(blink_updater(7))
    s.add(arrow)
    s.run(FadeIn(icon, scale=0.6), reveal_words(ask, 1.2), rt=1.4)
    icon.add_updater(blink_updater(3, lo=0.6))
    s.until(180.0, focus=duo)


BLOCKS = [block0, block1, block2, block3, block4, block5, block6]
