"""
Diagnostic script to inspect the exact collision coordinates and visual impact.
"""

from pathlib import Path
from PIL import Image
import numpy as np

IMG_DIR = Path("blog/public/images/part1")

def examine_fig2():
    img_path = IMG_DIR / "fig2_willis_law_geometry.png"
    if not img_path.exists():
        print("File not found:", img_path)
        return
    with Image.open(img_path) as img:
        print("Fig 2 size:", img.size)

def examine_fig1():
    img_path = IMG_DIR / "fig1_friction_vs_gear.png"
    if not img_path.exists():
        print("File not found:", img_path)
        return
    with Image.open(img_path) as img:
        print("Fig 1 size:", img.size)

if __name__ == "__main__":
    examine_fig1()
    examine_fig2()
