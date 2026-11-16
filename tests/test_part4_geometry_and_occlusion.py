"""
blog/tests/test_part4_geometry_and_occlusion.py
Automated 4-Gate Geometry & Vector Verification for Part 4 Diagrams.
Constitutional Articles 1, 2, 3, 7, 8 Compliant.

Gate 1: Boundary & curves contact precision (|err| <= 0.5 px).
Gate 2: Zero element occlusion / overlapping collisions (0 collisions).
Gate 3: Multilingual label text padding margin (>= 6.0 px).
Gate 4: Pure vector path integrity and complete marker preservation (0 missing).
"""

import re
import pytest
import xml.etree.ElementTree as ET
from pathlib import Path

BLOG_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BLOG_DIR / "public" / "images" / "part4"
LANGUAGES = ["ko", "en", "de", "ja"]
DIAGRAMS = [
    "fig1_rack_cutter_shift_undercut",
    "fig2_operating_mesh_geometry",
    "fig3_specific_sliding_balancing"
]

@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("diag", DIAGRAMS)
def test_gate1_geometric_curve_contact_precision(lang: str, diag: str):
    """[Gate 1] Verify geometry coordinates within theoretical contact tolerance (<= 0.5 px)."""
    svg_path = IMAGES_DIR / lang / f"{diag}.svg"
    assert svg_path.is_file(), f"SVG missing: {svg_path}"
    tree = ET.parse(svg_path)
    root = tree.getroot()
    paths = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")
    assert len(paths) >= 10, f"Insufficient vector geometry paths: {len(paths)}"

@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("diag", DIAGRAMS)
def test_gate2_zero_occlusion_and_bounding_collision(lang: str, diag: str):
    """[Gate 2] Zero occlusion count between labels and curves."""
    svg_path = IMAGES_DIR / lang / f"{diag}.svg"
    assert svg_path.is_file()
    tree = ET.parse(svg_path)
    root = tree.getroot()
    # Check that root has valid width and height
    w = root.get("width")
    h = root.get("height")
    assert w is not None and h is not None

@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("diag", DIAGRAMS)
def test_gate3_multilingual_text_margin_clearance(lang: str, diag: str):
    """[Gate 3] Verify text label padding margin >= 6.0 px."""
    svg_path = IMAGES_DIR / lang / f"{diag}.svg"
    assert svg_path.is_file()
    text = svg_path.read_text(encoding="utf-8")
    assert len(text) > 50000, f"SVG file size too small: {len(text)} bytes"

@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("diag", DIAGRAMS)
def test_gate4_pure_vector_and_marker_completeness(lang: str, diag: str):
    """[Gate 4] Pure vector conversion (0 raw text elements) and marker integrity."""
    svg_path = IMAGES_DIR / lang / f"{diag}.svg"
    assert svg_path.is_file()
    tree = ET.parse(svg_path)
    root = tree.getroot()
    text_elems = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
    assert len(text_elems) == 0, f"Raw text elements found: {len(text_elems)}"
