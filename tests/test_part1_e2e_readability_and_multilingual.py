"""
================================================================================
H-GEAR STUDIO: Comprehensive 4-Tier E2E Test Suite
Part 1: Readability Mathematical Scaling & Multilingual Publishing Architecture
Target: blog/tests/test_part1_e2e_readability_and_multilingual.py

Architecture Overview:
  - 4-Tier Test Architecture (Tier 1 ~ Tier 4) covering Features F1 ~ F8.
  - Dual Execution Mode:
      1. Pytest runner: `pytest blog/tests/test_part1_e2e_readability_and_multilingual.py -v`
      2. Standalone CLI: `python blog/tests/test_part1_e2e_readability_and_multilingual.py [--tier {all,1,2,3,4}]`
  - High-Diagnostic Pre/Post Implementation Reporting:
      Outputs exact floating-point S_render values, 32-asset audit, MDX mappings,
      KaTeX equations_hash invariance, and Astro static build verification.
================================================================================
"""

import os
import sys
import re
import ast
import json
import hashlib
import tempfile
import argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# -----------------------------------------------------------------------------
# Pytest Integration & Graceful Fallback Mock
# -----------------------------------------------------------------------------
try:
    import pytest
except ImportError:
    # Graceful fallback for standalone CLI execution when pytest is not installed
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

import numpy as np
from PIL import Image

# -----------------------------------------------------------------------------
# Dynamic Path Resolution & Environment Configuration
# -----------------------------------------------------------------------------
_CURRENT_FILE = Path(__file__).resolve()

_BLOG_DIR = None
for p in [_CURRENT_FILE] + list(_CURRENT_FILE.parents):
    if (p / "scripts" / "generate_part1_diagrams.py").is_file():
        _BLOG_DIR = p
        break
    elif (p / "blog" / "scripts" / "generate_part1_diagrams.py").is_file():
        _BLOG_DIR = p / "blog"
        break

if _BLOG_DIR is None:
    _BLOG_DIR = Path("blog").resolve()

_PROJECT_ROOT = _BLOG_DIR.parent if (_BLOG_DIR.parent / "prototype2").is_dir() else _BLOG_DIR
SCRIPT_PATH = _BLOG_DIR / "scripts" / "generate_part1_diagrams.py"
HASH_SCRIPT_PATH = _BLOG_DIR / "scripts" / "compute_equations_hash.py"
ASSETS_DIR = _BLOG_DIR / "public" / "images" / "part1"
DOCS_DIR = _BLOG_DIR / "src" / "content" / "docs"
DIST_DIR = _BLOG_DIR / "dist"

LANGUAGES = ["ko", "en", "de", "ja"]
FIGURE_KEYS = ["fig1a", "fig1b", "fig2", "fig3"]
FIGURE_FILENAMES = [
    "fig1a_friction_drive",
    "fig1b_gear_drive",
    "fig2_willis_law_geometry",
    "fig3_contact_velocity_vectors",
]
FORMATS = ["png", "svg"]

if str(_BLOG_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(_BLOG_DIR / "scripts"))


# =============================================================================
# Core Mathematical Font Scaling Verification Engine
# =============================================================================

def compute_rendered_font_size(pt: float, figsize_w_in: float, container_w_px: float) -> float:
    """
    Computes effective rendered font size in browser CSS pixels.
    Mathematical Formula: S_render = (pt * container_w_px) / (72.0 * figsize_w_in)
    DPI Invariance: ∂(S_render) / ∂(DPI) ≡ 0
    """
    if figsize_w_in <= 0.0 or container_w_px <= 0.0:
        raise ValueError(f"Invalid dimensions: figsize_w={figsize_w_in}, container_w={container_w_px}")
    return (pt * container_w_px) / (72.0 * figsize_w_in)


def verify_font_scaling(
    pt: float,
    figsize_w_in: float,
    min_threshold_px: float = 14.0,
    container_range: Tuple[float, float] = (720.0, 768.0),
) -> Dict[str, Any]:
    """
    Verifies font scaling theorem across Starlight container width range.
    Returns audit details with pass/fail status and exact floating point values.
    """
    w_min, w_max = container_range
    s_min = compute_rendered_font_size(pt, figsize_w_in, w_min)
    s_max = compute_rendered_font_size(pt, figsize_w_in, w_max)
    passed = s_min >= min_threshold_px

    return {
        "pt": pt,
        "figsize_w_in": figsize_w_in,
        "container_range": container_range,
        "s_render_min": s_min,
        "s_render_max": s_max,
        "threshold_px": min_threshold_px,
        "margin_min_px": s_min - min_threshold_px,
        "passed": passed,
    }


def parse_script_ast_typography(script_path: Path) -> Dict[str, Any]:
    """
    Statically analyzes generate_part1_diagrams.py AST to extract figsize,
    typography constants, and translation dictionary keys without heavy execution.
    """
    if not script_path.is_file():
        return {"exists": False, "error": f"File not found: {script_path}"}

    source_code = script_path.read_text(encoding="utf-8")
    tree = ast.parse(source_code, filename=str(script_path))

    results = {
        "exists": True,
        "constants": {},
        "functions": {},
        "translations_keys": [],
        "cli_args": [],
    }

    # Extract top-level constants and structures
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    if isinstance(node.value, ast.Constant):
                        results["constants"][var_name] = node.value.value
                    elif isinstance(node.value, ast.Dict):
                        if var_name == "TRANSLATIONS":
                            for k in node.value.keys:
                                if isinstance(k, ast.Constant):
                                    results["translations_keys"].append(k.value)

        elif isinstance(node, ast.FunctionDef):
            fn_name = node.name
            figsizes = []
            font_sizes = []
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    for kw in subnode.keywords:
                        if kw.arg == "figsize" and isinstance(kw.value, (ast.Tuple, ast.List)):
                            elts = kw.value.elts
                            if len(elts) == 2 and all(isinstance(e, ast.Constant) for e in elts):
                                figsizes.append((elts[0].value, elts[1].value))
                        elif kw.arg == "fontsize" and isinstance(kw.value, ast.Constant):
                            font_sizes.append(kw.value.value)
            results["functions"][fn_name] = {
                "figsizes": figsizes,
                "font_sizes": font_sizes,
            }

    return results


# =============================================================================
# TIER 1: Sanity & Static Specification Tests
# =============================================================================

class TestTier1StaticSanity:
    """
    Tier 1: Fast static specification tests (AST & file schema checks).
    Execution time: < 1.5 seconds.
    Covers Features: F1, F3, F4, F6, F7.
    """

    def test_cli_argument_specification(self):
        """[F4] Verify CLI supports --lang, --fig, --format, --dpi, --output-dir."""
        assert SCRIPT_PATH.is_file(), f"Script must exist at {SCRIPT_PATH}"
        cmd = [sys.executable, str(SCRIPT_PATH), "--help"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"Script --help failed: {res.stderr}"

        help_text = res.stdout
        assert "--lang" in help_text, "CLI must support --lang option for multilingual generation"
        assert "--fig" in help_text, "CLI must support --fig option"
        assert "--format" in help_text, "CLI must support --format option (all, svg, png)"
        assert "--dpi" in help_text, "CLI must support --dpi option"
        assert "--output-dir" in help_text, "CLI must support --output-dir option"

    def test_ast_diagram_function_definitions(self):
        """[F1] Verify script contains split diagram creation routines for Fig 1A and Fig 1B."""
        ast_data = parse_script_ast_typography(SCRIPT_PATH)
        assert ast_data["exists"], f"AST parse failed: {ast_data.get('error')}"
        fns = ast_data["functions"]

        has_fig1a = "create_diagram_1a" in fns or any("1a" in fn for fn in fns)
        has_fig1b = "create_diagram_1b" in fns or any("1b" in fn for fn in fns)
        assert has_fig1a, "Script must define Fig 1A generator (e.g. create_diagram_1a)"
        assert has_fig1b, "Script must define Fig 1B generator (e.g. create_diagram_1b)"
        assert "create_diagram_2" in fns or any("2" in fn for fn in fns), "Script must define Fig 2 generator"
        assert "create_diagram_3" in fns or any("3" in fn for fn in fns), "Script must define Fig 3 generator"

    def test_ast_canvas_width_within_container_limit(self):
        """[F1, F3] Verify all canvas widths in diagram functions are <= 8.6 inches for web responsive fit."""
        ast_data = parse_script_ast_typography(SCRIPT_PATH)
        fns = ast_data["functions"]
        target_diagram_fns = [fn for fn in fns if "diagram" in fn or "fig" in fn]
        
        checked_any = False
        for fn_name in target_diagram_fns:
            fn_meta = fns[fn_name]
            for w, h in fn_meta.get("figsizes", []):
                checked_any = True
                assert w <= 8.6, (
                    f"Canvas width {w} in in function {fn_name} exceeds responsive limit 8.6 in! "
                    f"Wide canvases cause severe font scaling shrinkage."
                )
        assert checked_any, "No figsize definitions detected in diagram functions via AST"

    def test_ast_font_constant_lower_bound(self):
        """[F3] Verify font size constants defined in the script meet the >= 11.2 pt lower bound."""
        ast_data = parse_script_ast_typography(SCRIPT_PATH)
        constants = ast_data["constants"]
        # Check standard typography constants if present
        for name, val in constants.items():
            if isinstance(val, (int, float)) and ("FONT_SIZE" in name or "FS_" in name):
                if "TITLE" in name or "SUBTITLE" in name or "BODY" in name or "LABEL" in name:
                    assert val >= 11.2, f"Font constant {name} = {val} pt is below the 11.2 pt lower bound"

    def test_translations_dictionary_schema(self):
        """[F4] Verify TRANSLATIONS dictionary covers all 4 languages (ko, en, de, ja)."""
        ast_data = parse_script_ast_typography(SCRIPT_PATH)
        keys = ast_data["translations_keys"]
        for lang in LANGUAGES:
            assert lang in keys, f"TRANSLATIONS dictionary must include language key '{lang}'"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_mdx_frontmatter_required_diagrams_contract(self, lang):
        """[F6] Verify MDX frontmatter required_diagrams has exactly 4 items in correct contract."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        assert mdx_file.is_file(), f"MDX file missing: {mdx_file}"

        content = mdx_file.read_text(encoding="utf-8")
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        assert match is not None, f"MDX file {mdx_file} has no frontmatter"

        fm_text = match.group(1)
        req_match = re.search(r"required_diagrams:\s*\n((?:\s*-\s*\"[^\"]+\"\s*\n?)+)", fm_text)
        assert req_match is not None, f"required_diagrams block not found in {lang} MDX frontmatter"

        raw_items = req_match.group(1)
        diagram_ids = [d.strip(' -\t\r\n"') for d in raw_items.strip().splitlines() if d.strip()]

        assert len(diagram_ids) == 4, (
            f"Expected 4 required diagrams in {lang} frontmatter, found {len(diagram_ids)}: {diagram_ids}"
        )
        for expected_id in FIGURE_FILENAMES:
            assert expected_id in diagram_ids, (
                f"Missing '{expected_id}' in required_diagrams of {lang} MDX frontmatter!"
            )

    @pytest.mark.parametrize("fig_arg", ["fig1a", "fig1b", "fig2", "fig3"])
    def test_cli_single_figure_isolation_support(self, fig_arg):
        """[F1] Verify CLI accepts individual figure arguments without error."""
        cmd = [sys.executable, str(SCRIPT_PATH), "--help"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0
        assert fig_arg in res.stdout, f"CLI choices must include '{fig_arg}'"


# =============================================================================
# TIER 2: Boundary & Corner Cases Tests
# =============================================================================

class TestTier2BoundaryAndCornerCases:
    """
    Tier 2: Mathematical closed-form verification, DPI invariance, CJK rendering, SVG/PNG checks, CLI errors.
    Execution time: 5.0 ~ 15.0 seconds.
    Covers Features: F1, F3, F4, F5.
    """

    def test_theorem_closed_form_exact_values(self):
        """[F3] Closed-form verification of font scaling theorem at boundary conditions."""
        # Benchmark 1: pt=11.5, w_in=8.0, container=720px -> S_render = 14.375000 px
        s1 = compute_rendered_font_size(pt=11.5, figsize_w_in=8.0, container_w_px=720.0)
        assert abs(s1 - 14.375) < 1e-6, f"Expected 14.375 px, got {s1:.6f}"

        # Benchmark 2: pt=11.5, w_in=8.0, container=768px -> S_render = 15.333333 px
        s2 = compute_rendered_font_size(pt=11.5, figsize_w_in=8.0, container_w_px=768.0)
        assert abs(s2 - 15.333333) < 1e-4, f"Expected 15.3333 px, got {s2:.6f}"

        # Benchmark 3: Legacy failure case (pt=8.5, w_in=15.5, container=720px) -> S_render = 5.483871 px (< 14px)
        s_legacy = compute_rendered_font_size(pt=8.5, figsize_w_in=15.5, container_w_px=720.0)
        assert s_legacy < 6.0, f"Legacy case should fail severely: {s_legacy:.2f} px"

    def test_dpi_invariance_property(self):
        """[F3] Mathematical and numerical proof that S_render is strictly invariant to DPI."""
        pt = 12.0
        w_in = 8.0
        container_w = 720.0

        for dpi in [72, 150, 300, 600, 1200]:
            h_px = (pt / 72.0) * dpi
            total_img_w_px = w_in * dpi
            scale_ratio = container_w / total_img_w_px
            s_render = h_px * scale_ratio
            assert abs(s_render - 15.0) < 1e-9, f"DPI invariance violated at DPI={dpi}: {s_render}"

    @pytest.mark.parametrize("fig_key,figsize_w,pt_body", [
        ("fig1a", 8.0, 11.5),
        ("fig1b", 8.0, 11.5),
        ("fig2", 8.5, 12.0),
        ("fig3", 8.2, 11.5),
    ])
    def test_diagram_font_scaling_specifications(self, fig_key, figsize_w, pt_body):
        """[F3] Verify proposed specifications for each diagram strictly satisfy S_render >= 14.0 px."""
        audit = verify_font_scaling(pt=pt_body, figsize_w_in=figsize_w, min_threshold_px=14.0)
        assert audit["passed"], (
            f"Diagram {fig_key} font scaling failed: S_render_min = {audit['s_render_min']:.3f} px "
            f"(Margin: {audit['margin_min_px']:.3f} px, Required >= 14.0 px)"
        )
        assert audit["s_render_min"] >= 14.0, f"S_render_min {audit['s_render_min']:.2f} must be >= 14.0"

    @pytest.mark.parametrize("lang,font_family,sample_text", [
        ("ko", "Malgun Gothic", "마찰차 구동 메커니즘 (접촉점 P, 수직항력 FN, 인볼류트 치형)"),
        ("ja", "Yu Gothic", "摩擦車駆動機構とインボリュート歯車のかみ合い (接触点K, 作用線, ピッチ円)"),
        ("de", "Segoe UI", "Reibradgetriebe und Evolventenverzahnung (Eingriffslinie n-n, Wälzkreis)"),
        ("en", "Segoe UI", "Friction Wheel Drive and Involute Conjugate Mesh (Line of Action, Pitch Circle)"),
    ])
    def test_cjk_and_western_glyph_rendering_no_tofu(self, lang, font_family, sample_text):
        """[F4] Verify multilingual font rendering produces 0 UserWarning: Glyph missing / tofu."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import warnings

        fig, ax = plt.subplots(figsize=(4, 2))
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            ax.text(0.5, 0.5, sample_text, fontfamily=font_family, fontsize=12)
            fig.canvas.draw()

            glyph_warnings = [
                w for w in recorded_warnings
                if "Glyph" in str(w.message) or "missing" in str(w.message).lower()
            ]
            assert len(glyph_warnings) == 0, (
                f"Language '{lang}' with font '{font_family}' produced {len(glyph_warnings)} missing glyph warnings! "
                f"First warning: {glyph_warnings[0].message if glyph_warnings else ''}"
            )
        plt.close(fig)

    @pytest.mark.parametrize("invalid_arg", [
        ["--lang", "es"],
        ["--fig", "fig99"],
        ["--format", "bmp"],
        ["--dpi", "not_a_number"],
    ])
    def test_cli_invalid_arguments_exit_code_2(self, invalid_arg):
        """[F4] Verify CLI strictly rejects invalid options with argparse exit code 2."""
        cmd = [sys.executable, str(SCRIPT_PATH)] + invalid_arg
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 2, f"Expected exit code 2 for invalid args {invalid_arg}, got {res.returncode}"
        assert "error:" in res.stderr.lower() or "invalid" in res.stderr.lower(), (
            f"Expected error message in stderr, got: {res.stderr}"
        )


# =============================================================================
# TIER 3: Cross-Feature Combinations & Pairwise Integration Tests
# =============================================================================

# Construct 32 asset matrix parameter tuples: (lang, fig_name, fmt, tc_id)
ASSET_32_TEST_CASES = []
_tc_counter = 1
for _lang in LANGUAGES:
    for _fig in FIGURE_FILENAMES:
        for _fmt in FORMATS:
            _tc_id = f"TC-T3-{_tc_counter:03d}"
            ASSET_32_TEST_CASES.append((_lang, _fig, _fmt, _tc_id))
            _tc_counter += 1


class TestTier3CrossFeatureAndPairwise:
    """
    Tier 3: 44-case exhaustive cross-feature matrix and file system integration.
      - 32 Assets exhaustive matrix (TC-T3-001 ~ TC-T3-032)
      - MDX Image Paths ↔ Filesystem consistency (TC-T3-033 ~ TC-T3-036)
      - MDX Frontmatter ↔ Body 1:1 Bijection (TC-T3-037 ~ TC-T3-044)
    Execution time: 10.0 ~ 20.0 seconds.
    Covers Features: F1, F2, F4, F5, F6, F7, F8.
    """

    @pytest.mark.parametrize("lang,fig_name,fmt,tc_id", ASSET_32_TEST_CASES)
    def test_asset_32_files_matrix(self, lang, fig_name, fmt, tc_id):
        """[F5] Exhaustive 32-asset matrix verification (existence, size, metadata, vector integrity)."""
        asset_path = ASSETS_DIR / lang / f"{fig_name}.{fmt}"
        if not asset_path.is_file():
            pytest.skip(f"[{tc_id}] Asset not yet generated: {asset_path}")

        file_size = asset_path.stat().st_size
        min_size = 50_000 if fmt == "png" else 15_000
        assert file_size >= min_size, (
            f"[{tc_id}] {asset_path.name} size {file_size} bytes is below threshold {min_size} bytes"
        )

        if fmt == "png":
            with Image.open(asset_path) as img:
                assert img.format == "PNG", f"[{tc_id}] Expected PNG format"
                dpi = img.info.get("dpi")
                assert dpi is not None, f"[{tc_id}] PNG missing DPI metadata"
                assert round(dpi[0]) == 300, f"[{tc_id}] Expected 300 DPI, got {dpi[0]}"
                assert round(dpi[1]) == 300, f"[{tc_id}] Expected 300 DPI, got {dpi[1]}"

                w, h = img.size
                assert w >= 2000, f"[{tc_id}] Width {w}px too low (must be >= 2000 for 300 DPI)"
                assert h >= 1600, f"[{tc_id}] Height {h}px too low (must be >= 1600)"

                arr = np.array(img.convert("RGB"))
                std_dev = float(np.std(arr))
                assert std_dev > 15.0, f"[{tc_id}] Low pixel standard deviation ({std_dev:.2f})"

                # Check non-white pixel ratio
                non_white_ratio = float(np.mean(arr < 250))
                assert non_white_ratio > 0.03, f"[{tc_id}] Blank image detected (non-white: {non_white_ratio:.3f})"

        elif fmt == "svg":
            tree = ET.parse(asset_path)
            root = tree.getroot()

            # Ensure 0 raw text elements
            text_tags = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
            assert len(text_tags) == 0, (
                f"[{tc_id}] SVG {asset_path.name} contains {len(text_tags)} raw <text> elements! "
                f"All text must be rendered to vector paths via svg.fonttype='path'."
            )

            # Ensure rich path vectors exist
            path_tags = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")
            assert len(path_tags) >= 15, f"[{tc_id}] SVG must have multiple vector paths, found {len(path_tags)}"

    @pytest.mark.parametrize("lang,tc_id", [
        ("ko", "TC-T3-033"),
        ("en", "TC-T3-034"),
        ("de", "TC-T3-035"),
        ("ja", "TC-T3-036"),
    ])
    def test_mdx_multilingual_image_references_consistency(self, lang, tc_id):
        """[F6] Verify MDX references diagram files in its own language directory and files exist physically."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        assert mdx_file.is_file(), f"[{tc_id}] MDX missing: {mdx_file}"

        content = mdx_file.read_text(encoding="utf-8")

        for fig_name in FIGURE_FILENAMES:
            expected_ref = f"/images/part1/{lang}/{fig_name}.png"
            assert expected_ref in content, (
                f"[{tc_id}] MDX for '{lang}' missing reference to '{expected_ref}'! "
                f"All diagrams must be referenced from language-specific directory."
            )

            physical_file = _BLOG_DIR / "public" / expected_ref.lstrip("/")
            if physical_file.is_file():
                assert physical_file.stat().st_size > 0, f"[{tc_id}] Referenced file is empty: {physical_file}"

        # Ensure legacy unified fig1 reference is completely eradicated
        assert "fig1_friction_vs_gear" not in content, (
            f"[{tc_id}] MDX for '{lang}' still references legacy 'fig1_friction_vs_gear'! "
            f"Must be replaced by fig1a and fig1b."
        )

    @pytest.mark.parametrize("lang,tc_id", [
        ("ko", "TC-T3-037"),
        ("en", "TC-T3-038"),
        ("de", "TC-T3-039"),
        ("ja", "TC-T3-040"),
    ])
    def test_mdx_frontmatter_required_diagrams_exact_match(self, lang, tc_id):
        """[F6] Verify MDX frontmatter required_diagrams has exactly 4 split diagram identifiers."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        content = mdx_file.read_text(encoding="utf-8")

        match = re.search(r"required_diagrams:\s*\n((?:\s*-\s*\"[^\"]+\"\s*\n?)+)", content)
        assert match is not None, f"[{tc_id}] required_diagrams block not found in {lang} MDX frontmatter"

        diagram_ids = [d.strip(' -\t\r\n"') for d in match.group(1).strip().splitlines() if d.strip()]
        assert diagram_ids == FIGURE_FILENAMES, (
            f"[{tc_id}] Frontmatter diagrams in {lang} do not match contract!\n"
            f"  Expected: {FIGURE_FILENAMES}\n"
            f"  Found:    {diagram_ids}"
        )

    @pytest.mark.parametrize("lang,tc_id", [
        ("ko", "TC-T3-041"),
        ("en", "TC-T3-042"),
        ("de", "TC-T3-043"),
        ("ja", "TC-T3-044"),
    ])
    def test_mdx_frontmatter_body_bijection(self, lang, tc_id):
        """[F6] Verify 1:1 bijection between frontmatter required_diagrams and body image embeds."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        content = mdx_file.read_text(encoding="utf-8")

        fm_match = re.search(r"required_diagrams:\s*\n((?:\s*-\s*\"[^\"]+\"\s*\n?)+)", content)
        assert fm_match is not None, f"[{tc_id}] Frontmatter missing required_diagrams"
        fm_set = set(d.strip(' -\t\r\n"') for d in fm_match.group(1).strip().splitlines() if d.strip())

        # Extract image filename stems referenced in body: ![](/images/part1/.../{stem}.png)
        body_images = re.findall(r'!\[.*?\]\(/images/part1/[^/]+/([^/]+)\.(?:png|svg)\)', content)
        body_set = set(body_images)

        diff = fm_set.symmetric_difference(body_set)
        assert len(diff) == 0, (
            f"[{tc_id}] Bijection failure between frontmatter and body in {lang} MDX!\n"
            f"  Frontmatter: {fm_set}\n"
            f"  Body refs:   {body_set}\n"
            f"  Difference:  {diff}"
        )


# =============================================================================
# TIER 4: Real-World Application Scenarios
# =============================================================================

class TestTier4RealWorldScenarios:
    """
    Tier 4: 6 End-to-End production scenarios:
      - SC-01: Full Astro static build (Exit Code 0)
      - SC-02: HTML output generation and image link integrity
      - SC-03: KaTeX Display Math $$...$$ SHA-256 invariance
      - SC-04: MDX comparison markdown table structure
      - SC-05: KS/ISO/DIN/JIS engineering terminology consistency
      - SC-06: Built HTML native <table> rendering
    Execution time: 30.0 ~ 60.0 seconds.
    Covers Features: F2, F7, F8.
    """

    def test_sc01_astro_starlight_static_build(self):
        """[SC-01 / F8] Execute npm --prefix blog run build and verify exit code 0."""
        package_json = _BLOG_DIR / "package.json"
        if not package_json.is_file():
            pytest.skip("blog/package.json not found")

        cmd = ["npm", "--prefix", str(_BLOG_DIR), "run", "build"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180, shell=True)
        assert res.returncode == 0, (
            f"[SC-01] Astro Starlight build failed with exit code {res.returncode}!\n"
            f"STDOUT:\n{res.stdout[-1500:]}\nSTDERR:\n{res.stderr[-1000:]}"
        )
        assert "[build] complete" in res.stdout or "Complete in" in res.stdout or "dist" in res.stdout, (
            "[SC-01] Build completed without standard success message"
        )

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_sc02_built_html_image_links(self, lang):
        """[SC-02 / F8] Verify built HTML files exist and contain valid image links."""
        html_file = DIST_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears" / "index.html"
        if not html_file.is_file():
            pytest.skip(f"[SC-02] Built HTML not found at {html_file}. Run SC-01 build first.")

        content = html_file.read_text(encoding="utf-8")
        assert len(content) >= 15_000, f"[SC-02] HTML file {html_file} is unusually small ({len(content)} bytes)"

        for fig_name in FIGURE_FILENAMES:
            expected_src = f"/images/part1/{lang}/{fig_name}.png"
            assert expected_src in content, (
                f"[SC-02] Built HTML for '{lang}' missing diagram link '{expected_src}'!"
            )

        # Ensure no invalid src attributes
        assert 'src=""' not in content, "[SC-02] Empty src attribute found in built HTML"
        assert 'src="undefined"' not in content, "[SC-02] 'undefined' src found in built HTML"
        assert 'src="null"' not in content, "[SC-02] 'null' src found in built HTML"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_sc03_katex_equations_hash_invariance(self, lang):
        """[SC-03 / F8] Verify display math $$...$$ blocks are preserved and equations_hash is invariant."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        assert mdx_file.is_file(), f"[SC-03] MDX missing: {mdx_file}"

        content = mdx_file.read_text(encoding="utf-8")
        match_fm = re.search(r'equations_hash:\s*"([a-f0-9]{64})"', content)
        assert match_fm is not None, f"[SC-03] equations_hash missing in frontmatter of {lang} MDX"
        expected_hash = match_fm.group(1)

        display_blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
        assert len(display_blocks) >= 3, f"[SC-03] Expected at least 3 display math blocks in {lang} MDX"

        normalized = "\n---\n".join(b.strip() for b in display_blocks)
        current_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        assert current_hash == expected_hash, (
            f"[SC-03] equations_hash mismatch in {lang} MDX!\n"
            f"  Frontmatter: {expected_hash}\n"
            f"  Calculated:  {current_hash}\n"
            f"Display math blocks must NOT be modified during diagram/table restructuring."
        )

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_sc04_mdx_comparison_table_structure(self, lang):
        """[F2, SC-04] Verify MDX contains native markdown comparison table with 4 columns and >= 4 rows."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        assert mdx_file.is_file(), f"[SC-04] MDX missing: {mdx_file}"
        content = mdx_file.read_text(encoding="utf-8")

        # Partition markdown tables (contiguous blocks of lines starting with '|')
        tables: List[List[str]] = []
        current_table: List[str] = []
        for line in content.splitlines():
            s = line.strip()
            if s.startswith("|") and s.endswith("|"):
                current_table.append(s)
            else:
                if current_table:
                    tables.append(current_table)
                    current_table = []
        if current_table:
            tables.append(current_table)

        assert len(tables) > 0, f"[SC-04] No markdown tables found in {lang} MDX"

        # Search specifically for comparison table (features keywords like friction/gear or item/merkmale)
        comparison_keywords = {
            "ko": ["마찰차", "인벌류트", "인볼류트", "비교", "항목"],
            "en": ["friction", "involute", "gear", "item", "comparison"],
            "de": ["reibrad", "evolvente", "zahnrad", "merkmal", "vergleich"],
            "ja": ["摩擦車", "インボリュート", "歯車", "項目", "比較"],
        }
        kw_list = comparison_keywords.get(lang, ["friction", "gear"])

        target_table = None
        for tbl in tables:
            tbl_text = "\n".join(tbl).lower()
            if any(kw.lower() in tbl_text for kw in kw_list):
                # Verify header columns count is 3 or 4
                header_cols = [c.strip() for c in tbl[0].split("|") if c.strip()]
                if len(header_cols) in [3, 4] and len(tbl) >= 4:
                    target_table = tbl
                    break

        assert target_table is not None, (
            f"[SC-04] Comparison table (4 columns, >= 4 rows) not found in {lang} MDX!\n"
            f"Found {len(tables)} tables, but none matched the comparison table signature."
        )

        # Verify separator exists
        has_separator = any("---" in line and "|" in line for line in target_table)
        assert has_separator, f"[SC-04] Comparison table in '{lang}' MDX missing header separator line"

    @pytest.mark.parametrize("lang,required_terms", [
        ("ko", ["마찰차", ("인벌류트", "인볼류트"), "접촉", "동력"]),
        ("en", ["Friction", "Involute", "Contact", "Power"]),
        ("de", ["Reibrad", "Evolvente", "Kontakt", "Leistung"]),
        ("ja", ["摩擦車", "インボリュート", "接触", "動力"]),
    ])
    def test_sc05_engineering_terminology_consistency(self, lang, required_terms):
        """[SC-05 / F7] Verify standardized engineering terminology is respected in comparison table / MDX."""
        mdx_file = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears.mdx"
        content = mdx_file.read_text(encoding="utf-8")

        missing_terms = []
        for item in required_terms:
            if isinstance(item, tuple):
                if not any(term in content for term in item):
                    missing_terms.append(f"({' or '.join(item)})")
            elif isinstance(item, str):
                if item not in content:
                    missing_terms.append(item)

        assert len(missing_terms) == 0, (
            f"[SC-05] Missing standardized engineering terms in {lang} MDX: {missing_terms}"
        )

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_sc06_built_html_native_table_elements(self, lang):
        """[SC-06 / F2] Verify built HTML contains native <table>, <th>, <tr> elements rendered from markdown table."""
        html_file = DIST_DIR / lang / "series1-theory" / "part-a-spur" / "01-why-gears" / "index.html"
        if not html_file.is_file():
            pytest.skip(f"[SC-06] Built HTML not found at {html_file}. Run SC-01 build first.")

        content = html_file.read_text(encoding="utf-8")
        assert "<table" in content, f"[SC-06] No <table> tag found in built HTML for {lang}"
        assert "<th" in content, f"[SC-06] No <th> tag found in built HTML for {lang}"
        assert "<tr" in content, f"[SC-06] No <tr> tag found in built HTML for {lang}"


# =============================================================================
# Standalone CLI Test Runner & Diagnostic Reporting
# =============================================================================

def run_diagnostics(selected_tier: str = "all") -> int:
    """
    Executes tests with standalone reporting, outputting high-contrast ANSI diagnostic tables.
    """
    print("\n" + "=" * 80)
    print("  H-GEAR STUDIO: Part 1 Readability & Multilingual E2E Test Suite")
    print("  4-Tier Architecture & Comprehensive Ground-Truth Verification")
    print("=" * 80)

    results = []

    def record(tier: int, code: str, desc: str, passed: bool, details: str = ""):
        results.append({
            "tier": tier,
            "code": code,
            "desc": desc,
            "status": "PASS" if passed else "FAIL",
            "details": details,
        })

    # -------------------------------------------------------------------------
    # Tier 1 Execution
    # -------------------------------------------------------------------------
    if selected_tier in ["all", "1"]:
        print("\n--- Executing Tier 1: Sanity & Static Specification Tests ---")
        t1 = TestTier1StaticSanity()

        try:
            t1.test_cli_argument_specification()
            record(1, "TC-T1-001", "CLI Argument Specification (--lang, --fig, etc.)", True, "All 5 CLI options supported")
        except Exception as e:
            record(1, "TC-T1-001", "CLI Argument Specification", False, str(e))

        try:
            t1.test_ast_diagram_function_definitions()
            record(1, "TC-T1-002", "AST Fig 1A / Fig 1B Generator Definitions", True, "create_diagram_1a/1b defined")
        except Exception as e:
            record(1, "TC-T1-002", "AST Fig 1A / Fig 1B Definitions", False, str(e))

        try:
            t1.test_ast_canvas_width_within_container_limit()
            record(1, "TC-T1-003", "AST Canvas Width Limit (<= 8.6 in)", True, "All widths <= 8.6 in")
        except Exception as e:
            record(1, "TC-T1-003", "AST Canvas Width Limit", False, str(e))

        try:
            t1.test_ast_font_constant_lower_bound()
            record(1, "TC-T1-004", "AST Font Size Constants (>= 11.2 pt)", True, "Constants meet lower bound")
        except Exception as e:
            record(1, "TC-T1-004", "AST Font Size Constants", False, str(e))

        try:
            t1.test_translations_dictionary_schema()
            record(1, "TC-T1-005", "TRANSLATIONS Schema (ko, en, de, ja)", True, "All 4 languages present")
        except Exception as e:
            record(1, "TC-T1-005", "TRANSLATIONS Schema", False, str(e))

        for lang in LANGUAGES:
            try:
                t1.test_mdx_frontmatter_required_diagrams_contract(lang)
                record(1, f"TC-T1-FM-{lang}", f"MDX Frontmatter required_diagrams ({lang})", True, "4 diagrams contract met")
            except Exception as e:
                record(1, f"TC-T1-FM-{lang}", f"MDX Frontmatter ({lang})", False, str(e))

        for fig_arg in ["fig1a", "fig1b", "fig2", "fig3"]:
            try:
                t1.test_cli_single_figure_isolation_support(fig_arg)
                record(1, f"TC-T1-ISO-{fig_arg}", f"CLI Single Figure Isolation ({fig_arg})", True, f"Arg '{fig_arg}' supported")
            except Exception as e:
                record(1, f"TC-T1-ISO-{fig_arg}", f"CLI Single Figure Isolation ({fig_arg})", False, str(e))

    # -------------------------------------------------------------------------
    # Tier 2 Execution
    # -------------------------------------------------------------------------
    if selected_tier in ["all", "2"]:
        print("\n--- Executing Tier 2: Boundary & Corner Cases Tests ---")
        t2 = TestTier2BoundaryAndCornerCases()

        try:
            t2.test_theorem_closed_form_exact_values()
            record(2, "TC-T2-001", "Theorem Closed-Form Exact Values", True, "Benchmark: S_render=14.375px")
        except Exception as e:
            record(2, "TC-T2-001", "Theorem Closed-Form", False, str(e))

        try:
            t2.test_dpi_invariance_property()
            record(2, "TC-T2-002", "DPI Invariance Property (∂S/∂DPI ≡ 0)", True, "DPI=72..1200 verified")
        except Exception as e:
            record(2, "TC-T2-002", "DPI Invariance Property", False, str(e))

        for fig_k, w, pt in [("fig1a", 8.0, 11.5), ("fig1b", 8.0, 11.5), ("fig2", 8.5, 12.0), ("fig3", 8.2, 11.5)]:
            try:
                t2.test_diagram_font_scaling_specifications(fig_k, w, pt)
                s_val = compute_rendered_font_size(pt, w, 720.0)
                record(2, f"TC-T2-SCALE-{fig_k}", f"Font Scaling {fig_k} (pt={pt}, w={w}in)", True, f"S_render={s_val:.3f}px >= 14px")
            except Exception as e:
                record(2, f"TC-T2-SCALE-{fig_k}", f"Font Scaling {fig_k}", False, str(e))

        cjk_tests = [
            ("ko", "Malgun Gothic", "마찰차 구동 메커니즘 (접촉점 P, 수직항력 FN)"),
            ("ja", "Yu Gothic", "摩擦車駆動機構とインボリュート歯車のかみ合い (接触点K, 作用線)"),
            ("de", "Segoe UI", "Reibradgetriebe und Evolventenverzahnung (Eingriffslinie n-n)"),
            ("en", "Segoe UI", "Friction Wheel Drive and Involute Conjugate Mesh (Line of Action)"),
        ]
        for lang, font_f, text in cjk_tests:
            try:
                t2.test_cjk_and_western_glyph_rendering_no_tofu(lang, font_f, text)
                record(2, f"TC-T2-GLYPH-{lang}", f"Glyph Rendering & No Tofu ({lang} / {font_f})", True, "0 missing glyph warnings")
            except Exception as e:
                record(2, f"TC-T2-GLYPH-{lang}", f"Glyph Rendering ({lang})", False, str(e))

        for invalid_arg in [["--lang", "es"], ["--fig", "fig99"], ["--format", "bmp"]]:
            arg_str = " ".join(invalid_arg)
            try:
                t2.test_cli_invalid_arguments_exit_code_2(invalid_arg)
                record(2, f"TC-T2-ERR-{invalid_arg[1]}", f"CLI Error Handling ({arg_str})", True, "Exit code 2 verified")
            except Exception as e:
                record(2, f"TC-T2-ERR-{invalid_arg[1]}", f"CLI Error Handling ({arg_str})", False, str(e))

    # -------------------------------------------------------------------------
    # Tier 3 Execution
    # -------------------------------------------------------------------------
    if selected_tier in ["all", "3"]:
        print("\n--- Executing Tier 3: Cross-Feature Combinations & Pairwise Tests ---")
        t3 = TestTier3CrossFeatureAndPairwise()

        # Audit 32 assets
        for lang, fig_name, fmt, tc_id in ASSET_32_TEST_CASES:
            try:
                t3.test_asset_32_files_matrix(lang, fig_name, fmt, tc_id)
                asset_p = ASSETS_DIR / lang / f"{fig_name}.{fmt}"
                size_kb = asset_p.stat().st_size / 1024.0 if asset_p.is_file() else 0.0
                record(3, tc_id, f"Asset Matrix: {lang}/{fig_name}.{fmt}", True, f"Valid ({size_kb:.1f} KB)")
            except Exception as e:
                err_msg = str(e)
                if "Asset not yet generated" in err_msg:
                    record(3, tc_id, f"Asset Matrix: {lang}/{fig_name}.{fmt}", False, "[Pending Generation]")
                else:
                    record(3, tc_id, f"Asset Matrix: {lang}/{fig_name}.{fmt}", False, err_msg[:50])

        # MDX references
        for lang, tc_id in [("ko", "TC-T3-033"), ("en", "TC-T3-034"), ("de", "TC-T3-035"), ("ja", "TC-T3-036")]:
            try:
                t3.test_mdx_multilingual_image_references_consistency(lang, tc_id)
                record(3, tc_id, f"MDX Image Path Consistency ({lang})", True, f"/images/part1/{lang}/... verified")
            except Exception as e:
                record(3, tc_id, f"MDX Image Path Consistency ({lang})", False, str(e)[:50])

        # MDX frontmatter exact match
        for lang, tc_id in [("ko", "TC-T3-037"), ("en", "TC-T3-038"), ("de", "TC-T3-039"), ("ja", "TC-T3-040")]:
            try:
                t3.test_mdx_frontmatter_required_diagrams_exact_match(lang, tc_id)
                record(3, tc_id, f"MDX Frontmatter Exact Match ({lang})", True, "4 diagrams exact match")
            except Exception as e:
                record(3, tc_id, f"MDX Frontmatter Exact Match ({lang})", False, str(e)[:50])

        # MDX bijection
        for lang, tc_id in [("ko", "TC-T3-041"), ("en", "TC-T3-042"), ("de", "TC-T3-043"), ("ja", "TC-T3-044")]:
            try:
                t3.test_mdx_frontmatter_body_bijection(lang, tc_id)
                record(3, tc_id, f"MDX Frontmatter ↔ Body Bijection ({lang})", True, "1:1 bijection verified")
            except Exception as e:
                record(3, tc_id, f"MDX Frontmatter ↔ Body Bijection ({lang})", False, str(e)[:50])

    # -------------------------------------------------------------------------
    # Tier 4 Execution
    # -------------------------------------------------------------------------
    if selected_tier in ["all", "4"]:
        print("\n--- Executing Tier 4: Real-World Application Scenarios ---")
        t4 = TestTier4RealWorldScenarios()

        # SC-03 KaTeX equations hash
        for lang in LANGUAGES:
            try:
                t4.test_sc03_katex_equations_hash_invariance(lang)
                record(4, f"SC-03-{lang}", f"KaTeX Math Block Invariance ({lang})", True, "SHA-256 match 100%")
            except Exception as e:
                record(4, f"SC-03-{lang}", f"KaTeX Math Block Invariance ({lang})", False, str(e)[:50])

        # SC-04 MDX comparison table
        for lang in LANGUAGES:
            try:
                t4.test_sc04_mdx_comparison_table_structure(lang)
                record(4, f"SC-04-{lang}", f"MDX Comparison Table Structure ({lang})", True, "Markdown table verified")
            except Exception as e:
                record(4, f"SC-04-{lang}", f"MDX Comparison Table Structure ({lang})", False, str(e)[:50])

        # SC-05 Engineering terminology
        for lang, terms in [("ko", ["마찰차", ("인벌류트", "인볼류트")]), ("en", ["Friction", "Involute"]), ("de", ["Reibrad", "Evolvente"]), ("ja", ["摩擦車", "インボリュート"])]:
            try:
                t4.test_sc05_engineering_terminology_consistency(lang, terms)
                record(4, f"SC-05-{lang}", f"Engineering Terminology Consistency ({lang})", True, "Standard terms present")
            except Exception as e:
                record(4, f"SC-05-{lang}", f"Engineering Terminology Consistency ({lang})", False, str(e)[:50])

        # SC-01 Astro static build
        try:
            t4.test_sc01_astro_starlight_static_build()
            record(4, "SC-01", "Astro Starlight Static Build", True, "Exit Code 0 verified")
        except Exception as e:
            record(4, "SC-01", "Astro Starlight Static Build", False, str(e)[:60])

        # SC-02 Built HTML image links
        for lang in LANGUAGES:
            try:
                t4.test_sc02_built_html_image_links(lang)
                record(4, f"SC-02-{lang}", f"Built HTML Image Links ({lang})", True, "Links verified")
            except Exception as e:
                record(4, f"SC-02-{lang}", f"Built HTML Image Links ({lang})", False, str(e)[:50])

        # SC-06 Built HTML native table tags
        for lang in LANGUAGES:
            try:
                t4.test_sc06_built_html_native_table_elements(lang)
                record(4, f"SC-06-{lang}", f"Built HTML Native Table Tags ({lang})", True, "<table>/<th>/<tr> verified")
            except Exception as e:
                record(4, f"SC-06-{lang}", f"Built HTML Native Table Tags ({lang})", False, str(e)[:50])

    # -------------------------------------------------------------------------
    # Diagnostic Summary Table
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("  E2E Test Execution Summary & Diagnostics Table")
    print("=" * 80)
    print(f"{'Tier':<6} | {'Test ID':<14} | {'Status':<6} | {'Description':<32} | {'Details'}")
    print("-" * 80)

    all_passed = True
    for r in results:
        status_color = "\033[92mPASS\033[0m" if r["status"] == "PASS" else "\033[91mFAIL\033[0m"
        print(f"Tier {r['tier']:<2} | {r['code']:<14} | {status_color:<15} | {r['desc'][:32]:<32} | {r['details'][:35]}")
        if r["status"] == "FAIL":
            all_passed = False

    print("=" * 80)
    passed_count = sum(1 for r in results if r["status"] == "PASS")
    total_count = len(results)
    print(f"Total Tests Executed: {total_count} | Passed: {passed_count} | Failed: {total_count - passed_count}")

    if all_passed:
        print("\033[92m★ ALL TESTS PASSED: E2E Readability & Multilingual Architecture Verified!\033[0m\n")
        return 0
    else:
        print("\033[93m⚠ PRE-IMPLEMENTATION / DIAGNOSTIC MODE: Actions Required on Failed Items Above.\033[0m\n")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Part 1 E2E Test Suite Runner")
    parser.add_argument("--tier", choices=["all", "1", "2", "3", "4"], default="all", help="Target test tier")
    args = parser.parse_args()
    sys.exit(run_diagnostics(selected_tier=args.tier))
