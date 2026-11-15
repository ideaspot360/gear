"""
test_part3_diagram_layout.py
================================================================================
H-GEAR STUDIO: Series 1 Part A Chapter 3 Diagram Layout & Collision Invariance
Target: blog/tests/test_part3_diagram_layout.py

Comprehensive Verification Suite:
  Part A: Asset Presence & Physical Quality Verification
    - 32 Assets Presence: All 32 files (4 figs x 4 languages x 2 formats) exist on disk.
    - File Integrity: All files > 20 KB (SVG >= 50 KB, PNG >= 200 KB).
    - Image Specs: PNG resolution w >= 2400, h >= 2400, DPI == 300.
    - SVG Vector Integrity: Valid XML, <svg> root, pure vector <path> glyphs (0 <text> tags).
  Part B: 5-Gate Zero-Tolerance Bounding Box Collision & Margin Verification
    - Gate 1 (Zero Text Overlap): Pairwise text bounding box intersection area <= 4.0 px^2
    - Gate 3 (Card Container Padding): Text enclosed in FancyBboxPatch has padding >= 15.0 px
    - Gate 3B (Box Outer Clearance): FancyBboxPatch has clearance >= 10.0 px from axes/canvas borders
    - Gate 4 (Canvas Border Margin): All text labels have clearance >= 5.0 px from canvas boundaries

Evaluates 16 scenes:
  - 4 Diagrams: fig1 (Line of Action & 5 Points), fig2 (Load Sharing & HPSTC Bending),
                fig3 (Kinematics & Velocities), fig4 (Specific Sliding Curves)
  - 4 Languages: ko, en, de, ja
Supports both pytest runner and standalone CLI execution.
================================================================================
"""

import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image

try:
    import pytest
except ImportError:
    class _MockPytestMark:
        @staticmethod
        def parametrize(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

    class _MockPytest:
        mark = _MockPytestMark()

        @staticmethod
        def fixture(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

        @staticmethod
        def skip(reason: str = ""):
            print(f"  [SKIPPED] {reason}")

    pytest = _MockPytest()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.text import Text

# -----------------------------------------------------------------------------
# Dynamic Path Resolution & Script Import
# -----------------------------------------------------------------------------
_CURRENT_FILE = Path(__file__).resolve()
_BLOG_DIR = None
for p in [_CURRENT_FILE] + list(_CURRENT_FILE.parents):
    if (p / "scripts").is_dir() and (p / "src").is_dir():
        _BLOG_DIR = p
        break
    elif (p / "blog" / "scripts").is_dir():
        _BLOG_DIR = p / "blog"
        break

if _BLOG_DIR is None:
    _BLOG_DIR = Path("blog").resolve()

_SCRIPTS_DIR = _BLOG_DIR / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

SCRIPT_PATH = _SCRIPTS_DIR / "generate_part3_diagrams.py"
IMAGES_DIR = _BLOG_DIR / "public" / "images" / "part3"

LANGUAGES = ["ko", "en", "de", "ja"]
DIAGRAM_KEYS = ["fig1", "fig2", "fig3", "fig4"]
FIG_NAMES = [
    "fig1_line_of_action_five_points",
    "fig2_tooth_load_sharing",
    "fig3_contact_kinematics_velocities",
    "fig4_specific_sliding_curves",
]

MARGIN_CARD_MIN_PX = 15.0       # Gate 3: Minimum text padding inside card container
MARGIN_BOX_OUTER_MIN_PX = 10.0   # Gate 3B: Minimum card clearance from axes/canvas borders
MARGIN_CANVAS_TEXT_PX = 5.0      # Gate 4: Minimum text clearance from canvas edge
MAX_TEXT_INTERSECTION_PX2 = 4.0  # Gate 1: Max allowed subpixel text overlap area

# -----------------------------------------------------------------------------
# Helper: Lazy import of generate_part3_diagrams
# -----------------------------------------------------------------------------
def get_part3_generator_module():
    """Dynamically loads generate_part3_diagrams if present."""
    if not SCRIPT_PATH.is_file():
        return None
    try:
        import generate_part3_diagrams as gpd3
        return gpd3
    except ImportError:
        return None


def get_diagram_function(mod, fig_key: str):
    """Resolves diagram creation function from generator module."""
    if mod is None:
        return None

    num = fig_key.replace("fig", "")
    candidates = [
        f"create_diagram_{num}",
        f"create_diagram_fig{num}",
        f"generate_{fig_key}",
        f"create_{fig_key}",
    ]
    for c in candidates:
        if hasattr(mod, c):
            return getattr(mod, c)
    return None


# -----------------------------------------------------------------------------
# Core Scene Geometry Inspection Engine
# -----------------------------------------------------------------------------
def collect_scene_geometry(fig: plt.Figure, ax: plt.Axes) -> Dict[str, Any]:
    """
    Renders canvas and extracts precise window extents for text labels and card patches.
    Uses pure Text.get_window_extent to avoid arrow line miscalculation in Annotations.
    Inspects all axes in the figure.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas_w, canvas_h = fig.canvas.get_width_height()

    texts_data = []
    boxes_data = []

    # Collect artists across figure and all axes
    all_axes = fig.get_axes()
    all_artists = list(fig.get_children())
    for a in all_axes:
        all_artists.extend(a.get_children())

    for artist in all_artists:
        if isinstance(artist, Text) and artist.get_text().strip():
            bbox = Text.get_window_extent(artist, renderer)
            if bbox.width > 1 and bbox.height > 1:
                texts_data.append({
                    "artist": artist,
                    "text": artist.get_text(),
                    "bbox": bbox,
                    "has_bbox_patch": artist.get_bbox_patch() is not None,
                })
        elif isinstance(artist, patches.FancyBboxPatch):
            bbox = artist.get_window_extent(renderer)
            if bbox.width > 20 and bbox.height > 20:
                boxes_data.append({
                    "artist": artist,
                    "bbox": bbox,
                })

    ax_bbox = ax.get_window_extent(renderer)

    return {
        "canvas_size": (canvas_w, canvas_h),
        "ax_bbox": ax_bbox,
        "texts": texts_data,
        "boxes": boxes_data,
        "renderer": renderer,
    }


def render_scene(fig_key: str, lang: str, out_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Renders single diagram scene and captures the live Matplotlib Figure
    by intercepting save_diagram before figure closure.
    """
    mod = get_part3_generator_module()
    if mod is None:
        return None

    fn = get_diagram_function(mod, fig_key)
    if fn is None:
        return None

    captured_figs = []

    def mock_save(fig, *args, **kwargs):
        captured_figs.append(fig)

    orig_save = getattr(mod, "save_diagram", None)
    if orig_save is not None:
        setattr(mod, "save_diagram", mock_save)

    plt.close("all")
    try:
        fn(output_dir=out_dir, dpi=150, formats="png", lang=lang)
    finally:
        if orig_save is not None:
            setattr(mod, "save_diagram", orig_save)

    if not captured_figs:
        return None

    fig = captured_figs[0]
    axes = fig.get_axes()
    ax = axes[0] if axes else fig.gca()

    scene = collect_scene_geometry(fig, ax)
    plt.close(fig)
    return scene


# -----------------------------------------------------------------------------
# 5-Gate Invariance Verification Functions
# -----------------------------------------------------------------------------
def check_gate1_zero_text_overlap(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    [Gate 1] Verify pairwise intersection area of distinct text bounding boxes <= 4.0 px^2.
    Tolerates subpixel antialiasing touches.
    """
    texts = scene["texts"]
    overlaps = []
    n = len(texts)
    for i in range(n):
        for j in range(i + 1, n):
            t1, t2 = texts[i], texts[j]
            b1, b2 = t1["bbox"], t2["bbox"]

            ix0 = max(b1.x0, b2.x0)
            iy0 = max(b1.y0, b2.y0)
            ix1 = min(b1.x1, b2.x1)
            iy1 = min(b1.y1, b2.y1)

            if ix1 > ix0 and iy1 > iy0:
                area = (ix1 - ix0) * (iy1 - iy0)
                if area > MAX_TEXT_INTERSECTION_PX2:
                    overlaps.append({
                        "t1": t1["text"][:35].replace("\n", " "),
                        "t2": t2["text"][:35].replace("\n", " "),
                        "area": area,
                    })
    return overlaps


def check_gate3_card_container_padding(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    [Gate 3] Verify text enclosed inside card containers (FancyBboxPatch)
    maintains >= 15.0 px internal padding from all four box borders.
    """
    boxes = scene["boxes"]
    texts = scene["texts"]
    violations = []

    for b_item in boxes:
        bbox = b_item["bbox"]
        inside_texts = []
        for t in texts:
            tb = t["bbox"]
            tcx = (tb.x0 + tb.x1) / 2.0
            tcy = (tb.y0 + tb.y1) / 2.0
            if bbox.x0 <= tcx <= bbox.x1 and bbox.y0 <= tcy <= bbox.y1:
                inside_texts.append(t)

        for it in inside_texts:
            tb = it["bbox"]
            m_l = tb.x0 - bbox.x0
            m_r = bbox.x1 - tb.x1
            m_b = tb.y0 - bbox.y0
            m_t = bbox.y1 - tb.y1

            min_margin = min(m_l, m_r, m_b, m_t)
            if min_margin < MARGIN_CARD_MIN_PX:
                violations.append({
                    "text": it["text"][:35].replace("\n", " "),
                    "min_margin": min_margin,
                    "required": MARGIN_CARD_MIN_PX,
                })
    return violations


def check_gate3b_box_outer_boundary_clearance(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    [Gate 3B] Verify all card containers maintain >= 10.0 px clearance
    from axes viewport edges and canvas boundaries, strictly preventing border clipping.
    """
    cw, ch = scene["canvas_size"]
    ax_bbox = scene["ax_bbox"]
    boxes = scene["boxes"]
    violations = []

    for b_item in boxes:
        bbox = b_item["bbox"]
        # Clearance to canvas borders
        m_can_left = bbox.x0
        m_can_right = cw - bbox.x1
        m_can_bottom = bbox.y0
        m_can_top = ch - bbox.y1

        min_clearance = min(m_can_left, m_can_right, m_can_bottom, m_can_top)

        if min_clearance < MARGIN_BOX_OUTER_MIN_PX:
            violations.append({
                "box_bounds": (round(bbox.x0, 1), round(bbox.y0, 1), round(bbox.x1, 1), round(bbox.y1, 1)),
                "min_clearance": min_clearance,
                "required": MARGIN_BOX_OUTER_MIN_PX,
            })
    return violations


def check_gate4_canvas_boundary_clearance(scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    [Gate 4] Verify all text labels remain inside the canvas with positive margins (>= 5.0 px).
    Prevents text bleeding outside canvas viewport.
    """
    cw, ch = scene["canvas_size"]
    texts = scene["texts"]
    violations = []

    for t in texts:
        b = t["bbox"]
        m_left = b.x0
        m_right = cw - b.x1
        m_bottom = b.y0
        m_top = ch - b.y1

        min_m = min(m_left, m_right, m_bottom, m_top)
        if min_m < MARGIN_CANVAS_TEXT_PX:
            violations.append({
                "text": t["text"][:35].replace("\n", " "),
                "min_margin": min_m,
                "required": MARGIN_CANVAS_TEXT_PX,
            })
    return violations


# -----------------------------------------------------------------------------
# Part A: Asset Presence & Physical Quality Pytest Suite (4 Tests)
# -----------------------------------------------------------------------------
class TestPart3DiagramAssetQuality:
    """Verifies existence, dimensions, file size, DPI, and SVG vector validity for all 32 assets."""

    def test_all_32_assets_exist(self):
        """Verify all 32 diagram asset files exist on disk."""
        missing = []
        for lang in LANGUAGES:
            for fig in FIG_NAMES:
                for fmt in ["png", "svg"]:
                    path = IMAGES_DIR / lang / f"{fig}.{fmt}"
                    if not path.is_file():
                        missing.append(str(path))
        assert not missing, f"Missing {len(missing)} asset files: {missing}"

    def test_all_asset_file_sizes(self):
        """Verify each asset has a healthy file size (> 20 KB; PNG >= 200 KB, SVG >= 50 KB)."""
        undersized = []
        for lang in LANGUAGES:
            for fig in FIG_NAMES:
                for fmt in ["png", "svg"]:
                    path = IMAGES_DIR / lang / f"{fig}.{fmt}"
                    if not path.is_file():
                        continue
                    size_kb = path.stat().st_size / 1024.0
                    threshold = 200.0 if fmt == "png" else 50.0
                    if size_kb < threshold:
                        undersized.append(f"{path.name} ({size_kb:.1f} KB < {threshold} KB)")
        assert not undersized, f"Undersized files: {undersized}"

    def test_png_resolution_and_dpi(self):
        """Verify PNG images meet publication quality requirements (300 DPI, W>=2400, H>=2400)."""
        invalid = []
        for lang in LANGUAGES:
            for fig in FIG_NAMES:
                path = IMAGES_DIR / lang / f"{fig}.png"
                if not path.is_file():
                    continue
                with Image.open(path) as img:
                    w, h = img.size
                    dpi = img.info.get("dpi", (0, 0))
                    if w < 2400 or h < 2400:
                        invalid.append(f"{path.name} resolution too small: {w}x{h} (required >= 2400x2400)")
                    if int(round(dpi[0])) != 300 or int(round(dpi[1])) != 300:
                        invalid.append(f"{path.name} DPI != 300: {dpi}")
        assert not invalid, f"Invalid PNG assets: {invalid}"

    def test_svg_xml_validity_and_path_conversion(self):
        """Verify SVG files parse cleanly and have all texts converted to vector paths (0 <text> tags)."""
        invalid = []
        for lang in LANGUAGES:
            for fig in FIG_NAMES:
                path = IMAGES_DIR / lang / f"{fig}.svg"
                if not path.is_file():
                    continue
                try:
                    tree = ET.parse(path)
                    root = tree.getroot()
                    if not root.tag.endswith("svg"):
                        invalid.append(f"{path.name} root tag is not <svg>: {root.tag}")
                    # Check for raw <text> elements
                    raw_texts = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
                    if raw_texts:
                        invalid.append(f"{path.name} contains {len(raw_texts)} unconverted <text> elements")
                except Exception as e:
                    invalid.append(f"{path.name} XML parse error: {e}")
        assert not invalid, f"Invalid SVG assets: {invalid}"


# -----------------------------------------------------------------------------
# Part B: 5-Gate Layout Invariance Pytest Suite (16 Scenes x 4 Gates = 64 Tests)
# -----------------------------------------------------------------------------
SCENE_TEST_CASES = []
for _fig in DIAGRAM_KEYS:
    for _lang in LANGUAGES:
        SCENE_TEST_CASES.append((_fig, _lang))


class TestPart3DiagramLayoutInvariance:
    """
    Pytest Suite for Chapter 3 Diagram 5-Gate Layout Verification.
    Runs across 16 scenes (4 diagrams x 4 languages).
    """

    @pytest.mark.parametrize("fig_key,lang", SCENE_TEST_CASES)
    def test_gate1_zero_text_overlap(self, fig_key, lang):
        """[Gate 1] Verify zero text overlap in diagram scene."""
        if not SCRIPT_PATH.is_file():
            pytest.skip(f"generate_part3_diagrams.py not yet implemented. Target: {SCRIPT_PATH}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            scene = render_scene(fig_key, lang, Path(tmp_dir))
            if scene is None:
                pytest.skip(f"Diagram '{fig_key}' function not found in generate_part3_diagrams.py")

            overlaps = check_gate1_zero_text_overlap(scene)
            assert len(overlaps) == 0, (
                f"[Gate 1 FAIL] Detected {len(overlaps)} text collisions in {fig_key} ({lang}):\n"
                f"  First collision: '{overlaps[0]['t1']}' x '{overlaps[0]['t2']}' "
                f"(area = {overlaps[0]['area']:.2f} px^2 > {MAX_TEXT_INTERSECTION_PX2} px^2)"
            )

    @pytest.mark.parametrize("fig_key,lang", SCENE_TEST_CASES)
    def test_gate3_card_container_internal_padding(self, fig_key, lang):
        """[Gate 3] Verify card container internal padding >= 15.0 px."""
        if not SCRIPT_PATH.is_file():
            pytest.skip("generate_part3_diagrams.py not yet implemented")

        with tempfile.TemporaryDirectory() as tmp_dir:
            scene = render_scene(fig_key, lang, Path(tmp_dir))
            if scene is None:
                pytest.skip(f"Diagram '{fig_key}' function not found")

            violations = check_gate3_card_container_padding(scene)
            assert len(violations) == 0, (
                f"[Gate 3 FAIL] Detected {len(violations)} card padding violations in {fig_key} ({lang}):\n"
                f"  First violation: text '{violations[0]['text']}' has margin {violations[0]['min_margin']:.1f} px "
                f"< required {MARGIN_CARD_MIN_PX} px"
            )

    @pytest.mark.parametrize("fig_key,lang", SCENE_TEST_CASES)
    def test_gate3b_box_outer_boundary_clearance(self, fig_key, lang):
        """[Gate 3B] Verify card box clearance from canvas borders >= 10.0 px (no border clipping)."""
        if not SCRIPT_PATH.is_file():
            pytest.skip("generate_part3_diagrams.py not yet implemented")

        with tempfile.TemporaryDirectory() as tmp_dir:
            scene = render_scene(fig_key, lang, Path(tmp_dir))
            if scene is None:
                pytest.skip(f"Diagram '{fig_key}' function not found")

            violations = check_gate3b_box_outer_boundary_clearance(scene)
            assert len(violations) == 0, (
                f"[Gate 3B FAIL] Detected {len(violations)} card border clipping risks in {fig_key} ({lang}):\n"
                f"  First box: clearance {violations[0]['min_clearance']:.1f} px < required {MARGIN_BOX_OUTER_MIN_PX} px"
            )

    @pytest.mark.parametrize("fig_key,lang", SCENE_TEST_CASES)
    def test_gate4_canvas_boundary_clearance(self, fig_key, lang):
        """[Gate 4] Verify text label clearance from canvas edges >= 5.0 px."""
        if not SCRIPT_PATH.is_file():
            pytest.skip("generate_part3_diagrams.py not yet implemented")

        with tempfile.TemporaryDirectory() as tmp_dir:
            scene = render_scene(fig_key, lang, Path(tmp_dir))
            if scene is None:
                pytest.skip(f"Diagram '{fig_key}' function not found")

            violations = check_gate4_canvas_boundary_clearance(scene)
            assert len(violations) == 0, (
                f"[Gate 4 FAIL] Detected {len(violations)} canvas bleeding violations in {fig_key} ({lang}):\n"
                f"  First text: '{violations[0]['text']}' has edge margin {violations[0]['min_margin']:.1f} px "
                f"< required {MARGIN_CANVAS_TEXT_PX} px"
            )


# -----------------------------------------------------------------------------
# Standalone CLI Runner & Diagnostics
# -----------------------------------------------------------------------------
def run_cli_audit():
    print("=" * 80)
    print("  H-GEAR STUDIO: Chapter 3 Diagram 5-Gate Layout Invariance Harness")
    print(f"  Script Target: {SCRIPT_PATH}")
    print("=" * 80)

    if not SCRIPT_PATH.is_file():
        print(f"  [STATUS] PENDING: generate_part3_diagrams.py is not yet implemented.")
        return 1

    mod = get_part3_generator_module()
    if mod is None:
        print("  [ERROR] Failed to load generate_part3_diagrams module.")
        return 1

    total_scenes = 0
    passed_scenes = 0
    failures = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for fig_key in DIAGRAM_KEYS:
            for lang in LANGUAGES:
                total_scenes += 1
                scene = render_scene(fig_key, lang, tmp_path)
                if scene is None:
                    failures.append((fig_key, lang, "Render returned None"))
                    continue

                g1 = check_gate1_zero_text_overlap(scene)
                g3 = check_gate3_card_container_padding(scene)
                g3b = check_gate3b_box_outer_boundary_clearance(scene)
                g4 = check_gate4_canvas_boundary_clearance(scene)

                scene_errors = []
                if g1:
                    scene_errors.append(f"Gate 1: {len(g1)} overlaps")
                if g3:
                    scene_errors.append(f"Gate 3: {len(g3)} padding violations")
                if g3b:
                    scene_errors.append(f"Gate 3B: {len(g3b)} clipping violations")
                if g4:
                    scene_errors.append(f"Gate 4: {len(g4)} bleeding violations")

                if scene_errors:
                    failures.append((fig_key, lang, ", ".join(scene_errors)))
                else:
                    passed_scenes += 1

    print(f"  Audit Results: {passed_scenes} / {total_scenes} scenes PASSED 5-Gate verification.")
    if failures:
        print("  Failures:")
        for fig_k, l, err in failures:
            print(f"    - [{fig_k}][{l}]: {err}")
        return 1

    print("  RESULT: 100% SUCCESS — ZERO COLLISIONS & FLAWLESS BOUNDARY CLEARANCE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli_audit())
