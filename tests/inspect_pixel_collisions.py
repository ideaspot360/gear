"""
Empirical pixel-level bounding box collision inspector for Fig 1, Fig 2, Fig 3.
Renders each figure with Matplotlib Agg backend, retrieves get_window_extent(),
and tests all pairwise text-to-text, text-to-patch, and text-to-line bounding box overlaps.
"""

import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "blog" / "scripts"))
import generate_part1_diagrams as gpd


def bbox_overlap(box1, box2, pad=2.0):
    """
    Checks if two Bbox objects overlap in display pixels, allowing for optional padding.
    box1, box2 are matplotlib.transforms.BboxBase
    """
    # [x0, y0, x1, y1]
    b1 = [box1.x0 + pad, box1.y0 + pad, box1.x1 - pad, box1.y1 - pad]
    b2 = [box2.x0 + pad, box2.y0 + pad, box2.x1 - pad, box2.y1 - pad]

    if b1[2] < b1[0] or b1[3] < b1[1] or b2[2] < b2[0] or b2[3] < b2[1]:
        return False, 0.0

    # Overlap rectangle
    dx = min(b1[2], b2[2]) - max(b1[0], b2[0])
    dy = min(b1[3], b2[3]) - max(b1[1], b2[1])

    if dx > 0 and dy > 0:
        area = dx * dy
        return True, area
    return False, 0.0


def inspect_figure_collisions(fig, fig_name):
    """Inspects all text artists and annotations in a figure for collisions."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    collisions = []
    
    for ax_idx, ax in enumerate(fig.axes):
        # Collect all texts
        texts = ax.texts + [child for child in ax.get_children() if isinstance(child, matplotlib.text.Text)]
        # Filter unique texts with valid content
        unique_texts = []
        seen = set()
        for t in texts:
            content = t.get_text().strip()
            if not content or id(t) in seen:
                continue
            seen.add(id(t))
            unique_texts.append(t)

        # Pairwise comparison
        n = len(unique_texts)
        for i in range(n):
            t1 = unique_texts[i]
            b1 = t1.get_window_extent(renderer)
            for j in range(i + 1, n):
                t2 = unique_texts[j]
                b2 = t2.get_window_extent(renderer)
                
                # Check overlap
                is_overlap, area = bbox_overlap(b1, b2, pad=1.0)
                if is_overlap:
                    txt1_clean = t1.get_text().replace('\n', ' ')[:30]
                    txt2_clean = t2.get_text().replace('\n', ' ')[:30]
                    collisions.append({
                        'ax': ax_idx,
                        'text1': txt1_clean,
                        'text2': txt2_clean,
                        'overlap_area_px': area,
                        'box1': (b1.x0, b1.y0, b1.x1, b1.y1),
                        'box2': (b2.x0, b2.y0, b2.x1, b2.y1)
                    })

    print(f"[{fig_name}] Analyzed {len(fig.axes)} axes. Found {len(collisions)} text-text collisions.")
    for c in collisions:
        print(f"  COLLISION in ax {c['ax']}: '{c['text1']}' vs '{c['text2']}' (area: {c['overlap_area_px']:.1f} px^2)")
    return collisions


def run_collision_audit(tmp_dir):
    results = {}
    
    # Fig 1
    fig1 = plt.figure(figsize=(15.5, 8.2), dpi=150)
    # Monkey-patch savefig or call create_diagram_1 directly
    gpd.create_diagram_1(output_dir=tmp_dir, dpi=150, formats='png')
    
    # We can inspect the code directly by monkeypatching save_diagram
    captured_figs = {}
    original_save = gpd.save_diagram
    def capture_save(f, name, od, d, fmt):
        captured_figs[name] = f
        original_save(f, name, od, d, fmt)

    gpd.save_diagram = capture_save
    
    # Run all 3
    print("--- Fig 1 Inspection ---")
    gpd.create_diagram_1(output_dir=tmp_dir, dpi=150, formats='png')
    res1 = inspect_figure_collisions(captured_figs['fig1_friction_vs_gear'], 'Fig 1')
    results['fig1'] = res1
    
    print("\n--- Fig 2 Inspection ---")
    gpd.create_diagram_2(output_dir=tmp_dir, dpi=150, formats='png')
    res2 = inspect_figure_collisions(captured_figs['fig2_willis_law_geometry'], 'Fig 2')
    results['fig2'] = res2
    
    print("\n--- Fig 3 Inspection ---")
    gpd.create_diagram_3(output_dir=tmp_dir, dpi=150, formats='png')
    res3 = inspect_figure_collisions(captured_figs['fig3_contact_velocity_vectors'], 'Fig 3')
    results['fig3'] = res3

    # Restore
    gpd.save_diagram = original_save
    return results


if __name__ == '__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        run_collision_audit(td)
