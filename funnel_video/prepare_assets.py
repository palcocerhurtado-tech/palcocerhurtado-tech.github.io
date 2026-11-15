"""
prepare_assets.py — Convierte las capturas originales (evidence_src/IMG_xxxx.png)
en «pruebas» listas para el video (assets/*.png + assets/clips.json):

  * Difumina la foto de perfil de Google Drive (esquina superior derecha).
  * Difumina el contador de chats «28720» de Telegram.
  * Recorta solo el fragmento relevante de cada captura.
  * Guarda las cajas de resaltado normalizadas (0–1) dentro de cada recorte.

Coordenadas en «espacio de vista» 920×2000 (la captura a escala 0.763);
se reescalan al tamaño real (1206×2622). Uso:  python prepare_assets.py
"""
from __future__ import annotations

import json
import os

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "evidence_src")
OUT = os.path.join(HERE, "assets")
VIEW_W = 920

DRIVE = {9585, 9586, 9587, 9588, 9589, 9590, 9591, 9592, 9593, 9594, 9595, 9596, 9597,
         9599, 9600, 9601, 9602, 9603, 9604, 9605, 9606, 9607, 9608, 9612, 9613}
TELEGRAM = set(range(9614, 9634))
AVATAR_BOX = (775, 330, 885, 425)      # foto de perfil en Drive (vista)
BADGE_BOX = (95, 160, 240, 235)         # contador «28720» en Telegram (vista)

# nombre: (IMG, (x0, y0, x1, y1) recorte en vista, [cajas de resaltado en vista])
CLIPS = {
    "start":      (9614, (0, 240, 920, 1790), [(30, 1160, 800, 1410), (30, 1470, 800, 1695)]),
    "walkaway":   (9615, (0, 330, 920, 1120), [(30, 335, 720, 470), (20, 625, 760, 825)]),
    "chosen":     (9616, (0, 1340, 920, 1600), [(590, 1360, 905, 1445)]),
    "palimpsest": (9585, (40, 600, 920, 1320), [(55, 1075, 905, 1160), (55, 1215, 905, 1310)]),
    "emerson":    (9587, (120, 470, 820, 900), []),
    "power":      (9619, (0, 250, 920, 1120), [(610, 250, 905, 330)]),
    "trial03":    (9597, (40, 740, 880, 1400), []),
    "alaric":     (9620, (0, 240, 920, 1040), [(20, 320, 820, 440), (630, 820, 905, 900)]),
    "wordsearch": (9599, (40, 450, 880, 1400), []),
    "ascend":     (9621, (0, 350, 920, 1660), [(30, 465, 800, 570), (600, 1570, 905, 1650)]),
    "trial05":    (9623, (0, 240, 920, 1320), [(30, 975, 800, 1035), (620, 1250, 905, 1325)]),
    "fifth":      (9605, (40, 810, 880, 1340), []),
    "trial06":    (9624, (0, 1040, 920, 1790), [(30, 1150, 800, 1220)]),
    "streetview": (9606, (40, 450, 880, 970), [(100, 610, 860, 640)]),
    "y1933":      (9625, (0, 320, 920, 1300), [(650, 330, 905, 395), (30, 990, 790, 1120)]),
    "trial07":    (9626, (0, 250, 920, 1290), [(30, 980, 790, 1110)]),
    "trial08":    (9628, (0, 250, 920, 1340), [(30, 410, 800, 520)]),
    "clarity":    (9629, (0, 240, 920, 1740), [(610, 250, 905, 330), (30, 1270, 800, 1530)]),
    "sunkcost":   (9613, (90, 590, 830, 1060), [(110, 925, 815, 990), (110, 1005, 815, 1045)]),
    "cipher":     (9613, (90, 1120, 830, 1660), [(115, 1370, 805, 1500)]),
    "ignite":     (9631, (0, 270, 920, 1490), [(630, 280, 905, 350), (30, 500, 790, 580)]),
    "clearance1": (9632, (0, 310, 920, 1700), [(30, 1205, 790, 1320), (30, 1365, 790, 1475)]),
    "clearance2": (9633, (0, 240, 920, 1830), [(30, 815, 790, 875), (20, 1715, 820, 1815)]),
    "whop":       (9634, (0, 300, 920, 1830), [(30, 1015, 260, 1085), (30, 1720, 900, 1830)]),
    "trial02":    (9617, (0, 810, 920, 1800), [(30, 1240, 800, 1340), (30, 1600, 800, 1700)]),
}


def blur_box(img: Image.Image, box, scale: float, radius: int = 28):
    b = tuple(int(v * scale) for v in box)
    region = img.crop(b).filter(ImageFilter.GaussianBlur(radius))
    region = region.filter(ImageFilter.GaussianBlur(radius))
    img.paste(region, b)


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    cache = {}
    for name, (num, crop, highlights) in CLIPS.items():
        if num not in cache:
            img = Image.open(os.path.join(SRC, f"IMG_{num}.png")).convert("RGB")
            scale = img.width / VIEW_W
            if num in DRIVE:
                blur_box(img, AVATAR_BOX, scale)
            if num in TELEGRAM:
                blur_box(img, BADGE_BOX, scale)
            cache[num] = (img, scale)
        img, scale = cache[num]
        x0, y0, x1, y1 = crop
        clip = img.crop(tuple(int(v * scale) for v in crop))
        if clip.width > 1100:
            clip = clip.resize((1100, int(clip.height * 1100 / clip.width)), Image.LANCZOS)
        clip.save(os.path.join(OUT, f"{name}.png"), optimize=True)
        for i, (a, b, c, d) in enumerate(highlights):       # «lupa» de cada resaltado
            pad = 12
            sub = img.crop(tuple(int(v * scale) for v in (max(a - pad, 0), max(b - pad, 0),
                                                         min(c + pad, VIEW_W), d + pad)))
            sub.save(os.path.join(OUT, f"{name}_h{i}.png"), optimize=True)
        w, h = x1 - x0, y1 - y0
        meta[name] = {
            "img": f"IMG_{num}",
            "aspect": h / w,
            "highlights": [[(a - x0) / w, (b - y0) / h, (c - x0) / w, (d - y0) / h]
                           for a, b, c, d in highlights],
        }
    # Imagen del Sol (Trial 08): reducción a 1100 px
    sun = Image.open(os.path.join(SRC, "IMG_9611.png")).convert("RGB")
    sun = sun.resize((1100, int(sun.height * 1100 / sun.width)), Image.LANCZOS)
    sun.save(os.path.join(OUT, "sun.png"), optimize=True)
    meta["sun"] = {"img": "IMG_9611", "aspect": sun.height / sun.width, "highlights": []}
    with open(os.path.join(OUT, "clips.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    print(f"{len(meta)} recortes en {OUT}")


if __name__ == "__main__":
    main()
