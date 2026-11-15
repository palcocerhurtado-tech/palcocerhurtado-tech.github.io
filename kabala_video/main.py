"""
main.py — «CÁBALA: EL CÓDIGO OCULTO DEL UNIVERSO»
Video vertical 9:16 · 1080×1920 · 30 fps · 180 s exactos · Manim Community Edition.

Uso:
    manim -qh --disable_caching main.py FullVideo     # video completo
    manim -qh --disable_caching main.py Block3        # un bloque suelto
    python main.py                                   # equivalente a FullVideo
    python main.py --scene Block2 --preview          # vista previa 540×960

La resolución y los fps se fijan en utils.py (sobrescriben los flags -q*).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (  # noqa: E402  (config global 1080×1920 @ 30 fps)
    BLOCK_ENDS, BLOCK_STARTS, FPS, TOTAL_SECONDS, KabalaScene, config,
)
from blocks import BLOCKS  # noqa: E402


class _BlockScene(KabalaScene):
    INDEX = 0

    def construct(self):
        self.k_setup(self.INDEX)
        BLOCKS[self.INDEX](self)
        expected = BLOCK_ENDS[self.INDEX] * FPS
        assert self.frames == expected, f"Bloque {self.INDEX}: {self.frames} ≠ {expected} frames"


class Block0(_BlockScene):
    """0:00–0:15 · Gancho + CTA de apertura."""
    INDEX = 0


class Block1(_BlockScene):
    """0:15–0:45 · Origen: la Merkavá."""
    INDEX = 1


class Block2(_BlockScene):
    """0:45–1:15 · El Árbol de la Vida."""
    INDEX = 2


class Block3(_BlockScene):
    """1:15–1:45 · Ein Sof y los nombres."""
    INDEX = 3


class Block4(_BlockScene):
    """1:45–2:15 · El Árbol de la Muerte (Qlifot)."""
    INDEX = 4


class Block5(_BlockScene):
    """2:15–2:45 · Cábala y masonería."""
    INDEX = 5


class Block6(_BlockScene):
    """2:45–3:00 · Cierre + CTA final."""
    INDEX = 6


class FullVideo(KabalaScene):
    """Los 7 bloques encadenados: el HUD del Árbol persiste y evoluciona."""

    def construct(self):
        self.k_setup(0)
        for i, block in enumerate(BLOCKS):
            assert self.frames == BLOCK_STARTS[i] * FPS, (i, self.frames)
            block(self)
            assert self.frames == BLOCK_ENDS[i] * FPS, (i, self.frames)
        assert self.frames == TOTAL_SECONDS * FPS == 5400


SCENES = {c.__name__: c for c in (FullVideo, Block0, Block1, Block2, Block3, Block4, Block5, Block6)}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Renderiza el video de Cábala con Manim CE.")
    ap.add_argument("--scene", default="FullVideo", choices=list(SCENES))
    ap.add_argument("--preview", action="store_true", help="540×960 para revisión rápida")
    args = ap.parse_args()
    if args.preview:
        config.pixel_width, config.pixel_height = 540, 960
    config.disable_caching = True
    config.output_file = args.scene
    SCENES[args.scene]().render()
    print("Video:", config.get_dir("video_dir"), args.scene + ".mp4")
