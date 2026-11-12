from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = PROJECT_ROOT / "blog" / "public" / "images" / "part1"

def crop_fig3():
    fig3_path = IMG_DIR / "fig3_contact_velocity_vectors.png"
    if fig3_path.exists():
        with Image.open(fig3_path) as img:
            w, h = img.size
            print("Fig 3 size:", w, h)
            # Crop 1: contact point K and velocity vectors
            crop1 = (int(w * 0.25), int(h * 0.20), int(w * 0.75), int(h * 0.70))
            img.crop(crop1).save(PROJECT_ROOT / "blog" / "tests" / "crop_fig3_vectors.png")
            # Crop 2: tangent line bottom vs summary box top
            crop2 = (int(w * 0.40), int(h * 0.55), int(w * 0.70), int(h * 0.85))
            img.crop(crop2).save(PROJECT_ROOT / "blog" / "tests" / "crop_fig3_summary_box.png")
            print("Saved crop_fig3_vectors.png and crop_fig3_summary_box.png")

if __name__ == '__main__':
    crop_fig3()
