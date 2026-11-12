from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = PROJECT_ROOT / "blog" / "public" / "images" / "part1"

def crop_fig1_parts():
    fig1_path = IMG_DIR / "fig1_friction_vs_gear.png"
    if fig1_path.exists():
        with Image.open(fig1_path) as img:
            w, h = img.size
            # Crop 1: Fig 1(A) contact P, FN, Ft
            crop1 = (int(w * 0.15), int(h * 0.35), int(w * 0.45), int(h * 0.65))
            img.crop(crop1).save(PROJECT_ROOT / "blog" / "tests" / "crop_fig1_A_contact.png")
            
            # Crop 2: Fig 1(B) top gear mesh
            crop2 = (int(w * 0.52), int(h * 0.05), int(w * 0.98), int(h * 0.50))
            img.crop(crop2).save(PROJECT_ROOT / "blog" / "tests" / "crop_fig1_B_mesh.png")
            print("Saved crop_fig1_A_contact.png and crop_fig1_B_mesh.png")

if __name__ == '__main__':
    crop_fig1_parts()
