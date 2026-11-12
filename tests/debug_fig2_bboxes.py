import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "blog" / "scripts"))
import generate_part1_diagrams as gpd

def debug_fig2(dpi):
    captured_figs = {}
    original_save = gpd.save_diagram
    def capture_save(f, name, od, d, fmt):
        captured_figs[name] = f
        # do not save to disk to be fast
    gpd.save_diagram = capture_save
    
    gpd.create_diagram_2(output_dir='.', dpi=dpi, formats='png')
    fig2 = captured_figs['fig2_willis_law_geometry']
    fig2.canvas.draw()
    renderer = fig2.canvas.get_renderer()
    ax = fig2.axes[0]
    
    print(f"=== Fig 2 at DPI {dpi} ===")
    for i, t in enumerate(ax.texts):
        b = t.get_window_extent(renderer)
        print(f"[{i:2d}] '{t.get_text()[:25]:<25}' -> x:[{b.x0:6.1f}, {b.x1:6.1f}], y:[{b.y0:6.1f}, {b.y1:6.1f}]")

    gpd.save_diagram = original_save

if __name__ == "__main__":
    debug_fig2(150)
    debug_fig2(300)
