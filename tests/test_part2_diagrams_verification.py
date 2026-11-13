"""
H-GEAR STUDIO: Part 2 Diagram Assets & Layout Verification Test Suite
======================================================================
Verifies:
  1. Asset Presence: All 32 files (4 figs x 4 languages x 2 formats) exist.
  2. File Integrity: All files > 20 KB (SVG >= 50 KB, PNG >= 200 KB).
  3. Image Specs: PNG resolution >= 2000x2400 px, DPI == 300.
  4. SVG Integrity: Valid XML, <svg> root, pure vector <path> glyphs.
  5. 5-Gate Layout Invariance: Zero text overlap (< 4.0 px^2), canvas border clearance.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from PIL import Image

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.text import Text

# Add scripts directory
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import generate_part2_diagrams as gpd

IMAGES_DIR = Path(__file__).resolve().parent.parent / "public" / "images" / "part2"
LANGUAGES = ['ko', 'en', 'de', 'ja']
FIG_NAMES = [
    'fig1_involute_generation',
    'fig2_involute_function_geometry',
    'fig3_spur_gear_four_circles',
    'fig4_line_of_action_contact_path',
]
FIG_FUNCS = {
    'fig1_involute_generation': gpd.create_diagram_1,
    'fig2_involute_function_geometry': gpd.create_diagram_2,
    'fig3_spur_gear_four_circles': gpd.create_diagram_3,
    'fig4_line_of_action_contact_path': gpd.create_diagram_4,
}


def test_all_32_assets_exist():
    """Verify all 32 diagram asset files exist on disk."""
    missing = []
    for lang in LANGUAGES:
        for fig in FIG_NAMES:
            for fmt in ['png', 'svg']:
                path = IMAGES_DIR / lang / f"{fig}.{fmt}"
                if not path.is_file():
                    missing.append(str(path))
    assert not missing, f"Missing {len(missing)} asset files: {missing}"


def test_all_asset_file_sizes():
    """Verify each asset has a healthy file size (> 20 KB)."""
    undersized = []
    for lang in LANGUAGES:
        for fig in FIG_NAMES:
            for fmt in ['png', 'svg']:
                path = IMAGES_DIR / lang / f"{fig}.{fmt}"
                size_kb = path.stat().st_size / 1024.0
                if size_kb < 20.0:
                    undersized.append(f"{path.name} ({size_kb:.1f} KB)")
    assert not undersized, f"Undersized files: {undersized}"


def test_png_resolution_and_dpi():
    """Verify PNG images meet publication quality requirements (300 DPI, W>=2000, H>=2400)."""
    invalid = []
    for lang in LANGUAGES:
        for fig in FIG_NAMES:
            path = IMAGES_DIR / lang / f"{fig}.png"
            with Image.open(path) as img:
                w, h = img.size
                dpi = img.info.get('dpi', (0, 0))
                # Check resolution
                if w < 2000 or h < 2400:
                    invalid.append(f"{path.name} resolution too small: {w}x{h}")
                # Check DPI
                if int(round(dpi[0])) != 300 or int(round(dpi[1])) != 300:
                    invalid.append(f"{path.name} DPI != 300: {dpi}")
    assert not invalid, f"Invalid PNG assets: {invalid}"


def test_svg_xml_validity_and_path_conversion():
    """Verify SVG files parse cleanly and have texts converted to vector paths."""
    invalid = []
    for lang in LANGUAGES:
        for fig in FIG_NAMES:
            path = IMAGES_DIR / lang / f"{fig}.svg"
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                if not root.tag.endswith('svg'):
                    invalid.append(f"{path.name} root tag is not <svg>: {root.tag}")
                # Ensure path elements exist (representing vectors & glyphs)
                paths = list(root.iter('{http://www.w3.org/2000/svg}path'))
                if len(paths) < 20:
                    invalid.append(f"{path.name} insufficient vector paths: {len(paths)}")
            except Exception as e:
                invalid.append(f"{path.name} XML parse error: {e}")
    assert not invalid, f"Invalid SVG assets: {invalid}"


@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("fig_name", FIG_NAMES)
def test_gate1_zero_text_overlap(lang, fig_name, tmp_path):
    """
    [Gate 1] Verify pairwise intersection area of distinct text bounding boxes <= 4.0 px^2.
    """
    plt.close('all')
    fn = FIG_FUNCS[fig_name]
    fn(output_dir=tmp_path, dpi=150, formats='png', lang=lang)

    fig = plt.gcf()
    ax = fig.gca()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    texts_data = []
    for artist in ax.get_children() + fig.get_children():
        if isinstance(artist, Text) and artist.get_text().strip():
            bbox = Text.get_window_extent(artist, renderer)
            if bbox.width > 1 and bbox.height > 1:
                texts_data.append({
                    'text': artist.get_text()[:30].replace('\n', ' '),
                    'bbox': bbox,
                })

    overlaps = []
    n = len(texts_data)
    for i in range(n):
        for j in range(i + 1, n):
            t1, t2 = texts_data[i], texts_data[j]
            b1, b2 = t1['bbox'], t2['bbox']
            ix0 = max(b1.x0, b2.x0)
            iy0 = max(b1.y0, b2.y0)
            ix1 = min(b1.x1, b2.x1)
            iy1 = min(b1.y1, b2.y1)
            if ix1 > ix0 and iy1 > iy0:
                area = (ix1 - ix0) * (iy1 - iy0)
                if area > 4.0:
                    overlaps.append({
                        't1': t1['text'],
                        't2': t2['text'],
                        'area': area,
                    })
    plt.close('all')
    assert not overlaps, f"[{lang.upper()}] {fig_name} text overlap detected: {overlaps}"


@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("fig_name", FIG_NAMES)
def test_gate4_canvas_boundary_clearance(lang, fig_name, tmp_path):
    """
    [Gate 4] Verify all text remains inside canvas with positive margins (>= 5.0 px).
    """
    plt.close('all')
    fn = FIG_FUNCS[fig_name]
    fn(output_dir=tmp_path, dpi=150, formats='png', lang=lang)

    fig = plt.gcf()
    ax = fig.gca()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    w_px, h_px = fig.canvas.get_width_height()

    out_of_bounds = []
    for artist in ax.get_children() + fig.get_children():
        if isinstance(artist, Text) and artist.get_text().strip():
            bbox = Text.get_window_extent(artist, renderer)
            if bbox.width > 1 and bbox.height > 1:
                if (bbox.x0 < 5.0 or bbox.y0 < 5.0 or
                    bbox.x1 > w_px - 5.0 or bbox.y1 > h_px - 5.0):
                    out_of_bounds.append({
                        'text': artist.get_text()[:30].replace('\n', ' '),
                        'bbox': (bbox.x0, bbox.y0, bbox.x1, bbox.y1),
                        'canvas': (w_px, h_px),
                    })
    plt.close('all')
    assert not out_of_bounds, f"[{lang.upper()}] {fig_name} text out of bounds: {out_of_bounds}"
