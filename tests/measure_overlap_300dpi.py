import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "blog" / "scripts"))
import generate_part1_diagrams as gpd

def get_exact_collision_bboxes(dpi=300):
    captured_figs = {}
    original_save = gpd.save_diagram
    def capture_save(f, name, od, d, fmt):
        captured_figs[name] = f
        original_save(f, name, od, d, fmt)

    gpd.save_diagram = capture_save
    
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        print("Generating at DPI =", dpi)
        gpd.create_diagram_2(output_dir=td, dpi=dpi, formats='png')
        fig2 = captured_figs['fig2_willis_law_geometry']
        fig2.canvas.draw()
        renderer = fig2.canvas.get_renderer()
        
        ax = fig2.axes[0]
        k_text = None
        alpha_text = None
        for t in ax.texts:
            txt = t.get_text()
            if "$K$" in txt:
                k_text = t
            elif r"\alpha" in txt:
                alpha_text = t
                
        if k_text and alpha_text:
            b_k = k_text.get_window_extent(renderer)
            b_alpha = alpha_text.get_window_extent(renderer)
            print(f"K bbox: x=[{b_k.x0:.1f}, {b_k.x1:.1f}], y=[{b_k.y0:.1f}, {b_k.y1:.1f}]")
            print(f"alpha bbox: x=[{b_alpha.x0:.1f}, {b_alpha.x1:.1f}], y=[{b_alpha.y0:.1f}, {b_alpha.y1:.1f}]")
            dx = min(b_k.x1, b_alpha.x1) - max(b_k.x0, b_alpha.x0)
            dy = min(b_k.y1, b_alpha.y1) - max(b_k.y0, b_alpha.y0)
            print(f"Overlap: dx={dx:.1f} px, dy={dy:.1f} px, Area={dx*dy:.1f} px^2")
            
        gpd.create_diagram_1(output_dir=td, dpi=dpi, formats='png')
        fig1 = captured_figs['fig1_friction_vs_gear']
        fig1.canvas.draw()
        renderer1 = fig1.canvas.get_renderer()
        ax_bot = fig1.axes[2] # ax2_bot
        t_fric = None
        t_gear = None
        for t in ax_bot.texts:
            txt = t.get_text()
            if "거대 압축 하중" in txt:
                t_fric = t
            elif "전달 토크에만" in txt:
                t_gear = t
        if t_fric and t_gear:
            b_f = t_fric.get_window_extent(renderer1)
            b_g = t_gear.get_window_extent(renderer1)
            print(f"\nFig 1 Table Row 3:")
            print(f"Fric bbox: x=[{b_f.x0:.1f}, {b_f.x1:.1f}], y=[{b_f.y0:.1f}, {b_f.y1:.1f}]")
            print(f"Gear bbox: x=[{b_g.x0:.1f}, {b_g.x1:.1f}], y=[{b_g.y0:.1f}, {b_g.y1:.1f}]")
            dx = min(b_f.x1, b_g.x1) - max(b_f.x0, b_g.x0)
            dy = min(b_f.y1, b_g.y1) - max(b_f.y0, b_g.y0)
            print(f"Overlap: dx={dx:.1f} px, dy={dy:.1f} px, Area={dx*dy:.1f} px^2")

    gpd.save_diagram = original_save

if __name__ == "__main__":
    get_exact_collision_bboxes(300)
