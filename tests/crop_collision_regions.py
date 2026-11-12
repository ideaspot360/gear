import sys
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = PROJECT_ROOT / "blog" / "public" / "images" / "part1"

def crop_collisions():
    # Fig 2: K vs alpha
    # In Matplotlib 300 DPI, fig2 is 3750 x 3360 (approx)
    # K bbox: x=[2137.1, 2656.6], y=[1821.9, 1877.9] from bottom-left
    # In PIL image coordinates, y is from top-left (y_pil = height - y_mpl)
    fig2_path = IMG_DIR / "fig2_willis_law_geometry.png"
    if fig2_path.exists():
        with Image.open(fig2_path) as img:
            w, h = img.size
            print("Fig 2 size:", w, h)
            # K is near x ~ 2100..2700
            # Let's crop region around x=1900..2800, y_mpl=1750..1950
            # y_pil = h - y_mpl
            # Since bbox_inches='tight' was used, let's find the exact pixel location
            # Let's save a crop around K and alpha
            crop_box = (int(w * 0.50), int(h * 0.38), int(w * 0.78), int(h * 0.55))
            cropped = img.crop(crop_box)
            cropped.save(PROJECT_ROOT / "blog" / "tests" / "crop_fig2_k_alpha.png")
            print("Saved crop_fig2_k_alpha.png, size:", cropped.size)

    # Fig 1: Table row 3
    fig1_path = IMG_DIR / "fig1_friction_vs_gear.png"
    if fig1_path.exists():
        with Image.open(fig1_path) as img:
            w, h = img.size
            print("Fig 1 size:", w, h)
            # Table is at bottom right: x ~ 0.53..0.97 of figure, y ~ 0.08..0.44
            # Row 3 is near y ~ 0.16
            crop_box = (int(w * 0.65), int(h * 0.80), int(w * 0.95), int(h * 0.95))
            cropped = img.crop(crop_box)
            cropped.save(PROJECT_ROOT / "blog" / "tests" / "crop_fig1_table_row3.png")
            print("Saved crop_fig1_table_row3.png, size:", cropped.size)

if __name__ == '__main__':
    crop_collisions()
