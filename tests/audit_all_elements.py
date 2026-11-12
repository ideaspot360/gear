"""
Examines text vs lines/arrows/patches collisions across Fig 1, Fig 2, Fig 3.
"""

import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "blog" / "scripts"))
import generate_part1_diagrams as gpd

def audit_all():
    captured_figs = {}
    original_save = gpd.save_diagram
    def capture_save(f, name, od, d, fmt):
        captured_figs[name] = f
    gpd.save_diagram = capture_save
    
    gpd.create_diagram_1(output_dir='.', dpi=300, formats='png')
    gpd.create_diagram_2(output_dir='.', dpi=300, formats='png')
    gpd.create_diagram_3(output_dir='.', dpi=300, formats='png')
    
    for name, fig in captured_figs.items():
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        print(f"\n==================== {name} ====================")
        for ax_idx, ax in enumerate(fig.axes):
            print(f"--- Axes {ax_idx} ---")
            texts = [t for t in ax.texts if t.get_text().strip()]
            patches = [p for p in ax.patches if isinstance(p, (FancyArrowPatch, FancyBboxPatch))]
            lines = ax.lines
            
            print(f"Texts: {len(texts)}, Patches: {len(patches)}, Lines: {len(lines)}")
            # Check text vs text
            for i in range(len(texts)):
                b1 = texts[i].get_window_extent(renderer)
                for j in range(i+1, len(texts)):
                    b2 = texts[j].get_window_extent(renderer)
                    dx = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
                    dy = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
                    if dx > 0 and dy > 0:
                        t1 = texts[i].get_text().replace('\n', ' ')[:30]
                        t2 = texts[j].get_text().replace('\n', ' ')[:30]
                        print(f"  [TEXT-TEXT OVERLAP] '{t1}' <-> '{t2}' : dx={dx:.1f}px, dy={dy:.1f}px, area={dx*dy:.1f}px^2")

    gpd.save_diagram = original_save

if __name__ == '__main__':
    audit_all()
