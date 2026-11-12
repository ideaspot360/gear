"""
Check text bbox intersection with lines and arrow segments.
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


def line_segment_intersects_box(p1, p2, box):
    """
    Checks if a 2D line segment between p1 and p2 intersects an axis-aligned box (x0, y0, x1, y1).
    p1, p2 are (x, y) display coordinates.
    """
    x0, y0, x1, y1 = box
    # Check if either endpoint is inside the box
    if (x0 <= p1[0] <= x1 and y0 <= p1[1] <= y1) or (x0 <= p2[0] <= x1 and y0 <= p2[1] <= y1):
        return True

    # Cohen-Sutherland style segment-box clipping check
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    def intersect(A, B, C, D):
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    edges = [
        (corners[0], corners[1]),
        (corners[1], corners[2]),
        (corners[2], corners[3]),
        (corners[3], corners[0])
    ]

    for c1, c2 in edges:
        if intersect(p1, p2, c1, c2):
            return True
    return False


def audit_text_line_crossings():
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
            trans = ax.transData
            texts = [t for t in ax.texts if t.get_text().strip()]
            lines = ax.lines
            for t in texts:
                txt = t.get_text().replace('\n', ' ')[:25]
                b = t.get_window_extent(renderer)
                box = (b.x0, b.y0, b.x1, b.y1)
                for l in lines:
                    xdata = l.get_xdata()
                    ydata = l.get_ydata()
                    if len(xdata) < 2:
                        continue
                    # Transform points to display coords
                    pts = np.column_stack([xdata, ydata])
                    disp_pts = trans.transform(pts)
                    for k in range(len(disp_pts) - 1):
                        p1 = disp_pts[k]
                        p2 = disp_pts[k+1]
                        if line_segment_intersects_box(p1, p2, box):
                            # Ignore if text has a white opaque bbox that acts as intentional callout
                            has_white_bbox = False
                            if t.get_bbox_patch():
                                fc = t.get_bbox_patch().get_facecolor()
                                has_white_bbox = True
                            print(f"  Line intersection: '{txt}' with line '{l.get_label()}' (white bbox: {has_white_bbox})")

    gpd.save_diagram = original_save


if __name__ == '__main__':
    audit_text_line_crossings()
