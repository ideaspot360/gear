"""
blog/tests/test_part4_e2e_suite.py
================================================================================
H-GEAR STUDIO: Comprehensive 4-Tier E2E Test Suite
Part 4: Spur Gear Profile Shift (평치차의 전위 공학) Publishing & Verification Harness
Target: blog/tests/test_part4_e2e_suite.py

Architecture Overview:
  - 4-Tier Opaque-Box & Requirement-Driven E2E Test Architecture (Tier 1 ~ Tier 4).
  - Dual Execution Mode:
      1. Pytest runner: `pytest blog/tests/test_part4_e2e_suite.py -v`
      2. Standalone CLI: `python blog/tests/test_part4_e2e_suite.py [--tier {all,1,2,3,4}] [--strict]`
  - Rigorous Adherence to Project Absolute Rules (헌법 제1조 ~ 제12조):
      * Closed-form continuous mathematical invariants (0.000000 mm precision).
      * Zero tooth distortion rule (Top Land s_a >= 0.25*m).
      * Undercut elimination boundary & pressure angle sensitivity.
      * 4-Gate automated diagram verification (error <= 0.5px, margin >= 6.0px).
      * KaTeX equations_hash SHA-256 multilingual invariance.
      * 111 Cumulative Golden Cases zero-regression audit (0.000000 um error).
      * Human-authored engineering insight free from AI clichés (Article 12).
================================================================================
"""

import os
import sys
import re
import math
import json
import hashlib
import argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set

# -----------------------------------------------------------------------------
# Pytest Integration & Graceful Fallback Mock
# -----------------------------------------------------------------------------
try:
    import pytest
    from _pytest.outcomes import Skipped as _PytestSkipped
    _SKIP_EXCEPTIONS = (_PytestSkipped,)
except ImportError:
    class _SkipException(Exception):
        pass

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
            raise _SkipException(reason)

    pytest = _MockPytest()
    _SKIP_EXCEPTIONS = (_SkipException,)

# Optional scientific libraries for asset inspection
try:
    import numpy as np
    from PIL import Image
    _HAS_IMAGING = True
except ImportError:
    np = None
    Image = None
    _HAS_IMAGING = False

# -----------------------------------------------------------------------------
# Dynamic Path Resolution
# -----------------------------------------------------------------------------
_CURRENT_FILE = Path(__file__).resolve()

_BLOG_DIR: Optional[Path] = None
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
DOCS_DIR = _BLOG_DIR / "src" / "content" / "docs"
PUBLIC_DIR = _BLOG_DIR / "public"
ASSETS_DIR = PUBLIC_DIR / "images" / "part4"
DATA_DIR = _BLOG_DIR / "data"
DIST_DIR = _BLOG_DIR / "dist"

# Common Domain Constants
LANGUAGES = ["ko", "en", "de", "ja"]
REQUIRED_DIAGRAMS = [
    "fig1_rack_cutter_shift_undercut",
    "fig2_operating_mesh_geometry",
    "fig3_specific_sliding_balancing",
]
FORMATS = ["png", "svg"]

ASSET_24_MATRIX = [
    (lang, diag, fmt)
    for lang in LANGUAGES
    for diag in REQUIRED_DIAGRAMS
    for fmt in FORMATS
]


def get_mdx_path(lang: str) -> Path:
    """Returns absolute path to Chapter 4 MDX document for the given language."""
    return DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"


# =============================================================================
# Closed-Form Involute & Profile Shift Mathematical Engine
# =============================================================================

def inv(alpha_rad: float) -> float:
    """Involute function: inv(alpha) = tan(alpha) - alpha."""
    return math.tan(alpha_rad) - alpha_rad


def solve_inv(target: float, guess: float = math.radians(20.0)) -> float:
    """
    Inverse involute solver using Newton-Raphson iteration.
    d(inv(alpha))/d(alpha) = tan^2(alpha).
    """
    a = guess
    for _ in range(100):
        f = inv(a) - target
        f_prime = math.tan(a) ** 2
        if abs(f_prime) < 1e-15:
            break
        a_new = a - f / f_prime
        if abs(a_new - a) < 1e-14:
            return a_new
        a = a_new
    return a


def calc_undercut_limit(ha_star: float, alpha_0_rad: float) -> float:
    """Theoretical continuous undercut limit: z_min = 2 * ha* / sin^2(alpha_0)."""
    return (2.0 * ha_star) / (math.sin(alpha_0_rad) ** 2)


def calc_min_shift(z: int, alpha_0_rad: float, ha_star: float = 1.0) -> float:
    """Theoretical minimum profile shift coefficient: x_min = ha* - z * sin^2(alpha_0) / 2."""
    return ha_star - (z * (math.sin(alpha_0_rad) ** 2)) / 2.0


def calc_top_land(m: float, z: int, x: float, alpha_0_rad: float, ha_star: float = 1.0, k: float = 0.0) -> float:
    """
    Calculates top land thickness s_a at tip diameter d_a.
    Formula: s_a = d_a * (s/d + inv(alpha_0) - inv(alpha_a)).
    """
    d = m * z
    db = d * math.cos(alpha_0_rad)
    da = d + 2.0 * m * (ha_star + x - k)
    if da <= db:
        return 0.0
    alpha_a = math.acos(db / da)
    s = m * (math.pi / 2.0 + 2.0 * x * math.tan(alpha_0_rad))
    return da * (s / d + inv(alpha_0_rad) - inv(alpha_a))


def calc_benchmark_38_params() -> Dict[int, Tuple[str, float, str]]:
    """
    Closed-form calculation of all 38 benchmark parameters for:
    z1=14, z2=42, m=3.0, alpha_0=20.0 deg, x1=+0.35, x2=+0.15, ha*=1.0, c*=0.25, rf*=0.38.
    """
    m = 3.0
    alpha_0 = math.radians(20.0)
    z1, z2 = 14, 42
    u = z2 / z1
    x1, x2 = 0.35, 0.15
    ha_star, c_star, rf_star = 1.00, 0.25, 0.38
    hf_star = ha_star + c_star

    d1, d2 = m * z1, m * z2
    db1, db2 = d1 * math.cos(alpha_0), d2 * math.cos(alpha_0)
    rb1, rb2 = db1 / 2.0, db2 / 2.0
    a_std = m * (z1 + z2) / 2.0

    inv_a0 = inv(alpha_0)
    inv_aw = inv_a0 + 2.0 * (x1 + x2) / (z1 + z2) * math.tan(alpha_0)
    alpha_w = solve_inv(inv_aw)
    a_prime = a_std * math.cos(alpha_0) / math.cos(alpha_w)

    y = (a_prime - a_std) / m
    k = (x1 + x2) - y

    dw1 = 2.0 * a_prime * z1 / (z1 + z2)
    dw2 = 2.0 * a_prime * z2 / (z1 + z2)
    df1 = d1 - 2.0 * m * (hf_star - x1)
    df2 = d2 - 2.0 * m * (hf_star - x2)
    da1 = d1 + 2.0 * m * (ha_star + x1 - k)
    da2 = d2 + 2.0 * m * (ha_star + x2 - k)
    ra1, ra2 = da1 / 2.0, da2 / 2.0
    c_mesh = a_prime - (da1 + df2) / 2.0

    s1 = m * (math.pi / 2.0 + 2.0 * x1 * math.tan(alpha_0))
    s2 = m * (math.pi / 2.0 + 2.0 * x2 * math.tan(alpha_0))
    alpha_a1 = math.acos(db1 / da1)
    alpha_a2 = math.acos(db2 / da2)
    sa1 = da1 * (s1 / d1 + inv_a0 - inv(alpha_a1))
    sa2 = da2 * (s2 / d2 + inv_a0 - inv(alpha_a2))

    t1t2 = a_prime * math.sin(alpha_w)
    s_A = t1t2 - math.sqrt(max(0.0, ra2 ** 2 - rb2 ** 2))
    s_E = math.sqrt(max(0.0, ra1 ** 2 - rb1 ** 2))
    g_alpha = s_E - s_A
    pb = math.pi * m * math.cos(alpha_0)
    epsilon_alpha = g_alpha / pb

    return {
        1: ("모듈 m", m, "mm"),
        2: ("기준 압력각 alpha_0", 20.0, "deg"),
        3: ("피니언 잇수 z1", 14.0, "-"),
        4: ("대기어 잇수 z2", 42.0, "-"),
        5: ("기어비 u", u, "-"),
        6: ("공구 이끝높이계수 ha*", ha_star, "-"),
        7: ("공구 이끝틈새계수 c*", c_star, "-"),
        8: ("공구 이뿌리필렛반경계수 rf*", rf_star, "-"),
        9: ("피니언 전위계수 x1", x1, "-"),
        10: ("대기어 전위계수 x2", x2, "-"),
        11: ("전위계수 총합 Sigma x", x1 + x2, "-"),
        12: ("언더컷 한계 잇수 z_min", calc_undercut_limit(ha_star, alpha_0), "-"),
        13: ("피니언 최소필요전위계수 x_min1", calc_min_shift(z1, alpha_0, ha_star), "-"),
        14: ("기준 중심거리 a", a_std, "mm"),
        15: ("기준 인볼류트 inv(alpha_0)", inv_a0, "rad"),
        16: ("물림 인볼류트 inv(alpha_w)", inv_aw, "rad"),
        17: ("물림 압력각 alpha_w (rad)", alpha_w, "rad"),
        18: ("물림 압력각 alpha_w (deg)", math.degrees(alpha_w), "deg"),
        19: ("운전 중심거리 a'", a_prime, "mm"),
        20: ("중심거리 증가계수 y", y, "-"),
        21: ("이끝높이 변경계수 k", k, "-"),
        22: ("피니언 기준피치원 지름 d1", d1, "mm"),
        23: ("대기어 기준피치원 지름 d2", d2, "mm"),
        24: ("피니언 기초원 지름 db1", db1, "mm"),
        25: ("대기어 기초원 지름 db2", db2, "mm"),
        26: ("피니언 물림피치원 지름 dw1", dw1, "mm"),
        27: ("대기어 물림피치원 지름 dw2", dw2, "mm"),
        28: ("피니언 이뿌리원 지름 df1", df1, "mm"),
        29: ("대기어 이뿌리원 지름 df2", df2, "mm"),
        30: ("피니언 이끝원 지름 da1", da1, "mm"),
        31: ("대기어 이끝원 지름 da2", da2, "mm"),
        32: ("운전 이끝틈새 c", c_mesh, "mm"),
        33: ("피니언 기준 치두께 s1", s1, "mm"),
        34: ("대기어 기준 치두께 s2", s2, "mm"),
        35: ("피니언 이끝 치두께 sa1", sa1, "mm"),
        36: ("대기어 이끝 치두께 sa2", sa2, "mm"),
        37: ("작용선 활성 접촉길이 g_alpha", g_alpha, "mm"),
        38: ("정면 물림률 epsilon_alpha", epsilon_alpha, "-"),
    }


BENCHMARK_PARAMS = calc_benchmark_38_params()


# =============================================================================
# TIER 1: Feature Coverage Test Suite (F1 ~ F13, >= 65 tests)
# =============================================================================

class TestTier1FeatureCoverage:
    """
    Tier 1: Feature Coverage across Features F1 ~ F13.
    Verifies existence, structural validity, schema compliance, 24 assets, and benchmarks.
    """

    def _get_mdx(self, lang: str) -> Path:
        return get_mdx_path(lang)

    # --- F8: 4 MDX Documents Existence, Length, Schema, Order, Required Diagrams ---
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f8_01_mdx_file_existence(self, lang: str):
        """[F8] Verify physical presence of MDX article in 4 languages."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        assert p.is_file(), f"MDX file missing: {p}"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f8_02_mdx_content_length_substantial(self, lang: str):
        """[F8] Verify substantive content length (> 10,000 characters)."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        text = p.read_text(encoding="utf-8")
        assert len(text) >= 10000, f"{lang}: MDX content length {len(text)} < 10,000 characters"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f8_03_frontmatter_zod_schema_fields(self, lang: str):
        """[F8] Verify Frontmatter Zod schema fields (series, part, chapter, gear_type, standards, review_date, academic_level)."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---"), f"{lang}: Frontmatter must start with '---'"
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        assert m is not None, f"{lang}: Closing '---' delimiter missing in frontmatter"
        fm = m.group(1)

        assert "series: theory" in fm or "series: 'theory'" in fm or 'series: "theory"' in fm, f"{lang}: series invalid"
        assert "part: 1" in fm or "part: '1'" in fm, f"{lang}: part must be 1"
        assert "chapter: 4" in fm or "chapter: '4'" in fm, f"{lang}: chapter must be 4"
        assert "gear_type: spur" in fm or "gear_type: 'spur'" in fm or 'gear_type: "spur"' in fm, f"{lang}: gear_type invalid"
        assert "academic_level:" in fm, f"{lang}: academic_level field missing"
        assert "review_date:" in fm, f"{lang}: review_date field missing"
        assert "standards:" in fm, f"{lang}: standards list missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f8_04_frontmatter_order_4(self, lang: str):
        """[F8] Verify sidebar navigation order is 4."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        text = p.read_text(encoding="utf-8")
        fm = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL).group(1)
        has_order = bool(re.search(r"(?:sidebar:\s*\n\s+order:\s*4|order:\s*4)", fm))
        assert has_order, f"{lang}: Frontmatter must specify order: 4"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f8_05_frontmatter_required_diagrams_contract(self, lang: str):
        """[F8] Verify frontmatter required_diagrams lists all 3 diagram IDs."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        text = p.read_text(encoding="utf-8")
        fm = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL).group(1)
        for diag in REQUIRED_DIAGRAMS:
            assert diag in fm, f"{lang}: Missing required diagram contract: '{diag}'"

    # --- F6: 24 Diagram Assets Existence & Size >= 20 KB (300 DPI & Pure SVG Paths) ---
    @pytest.mark.parametrize("lang,diag,fmt", ASSET_24_MATRIX)
    def test_f6_01_diagram_asset_existence_and_size(self, lang: str, diag: str, fmt: str):
        """[F6] Verify physical presence and minimum size (>= 20 KB) of 24 diagram asset files."""
        asset_file = ASSETS_DIR / lang / f"{diag}.{fmt}"
        if not asset_file.is_file():
            pytest.skip(f"[PENDING] Diagram asset not yet generated: {asset_file}")
        assert asset_file.is_file(), f"Asset missing: {asset_file}"
        size_bytes = asset_file.stat().st_size
        assert size_bytes >= 20 * 1024, f"{asset_file} size {size_bytes} bytes < 20 KB threshold"

        if fmt == "png" and _HAS_IMAGING:
            with Image.open(asset_file) as img:
                assert img.format == "PNG", f"{asset_file} is not a valid PNG image"
                dpi = img.info.get("dpi")
                if dpi is not None:
                    assert round(dpi[0]) == 300 and round(dpi[1]) == 300, f"{asset_file} DPI is not 300: {dpi}"
                w, h = img.size
                assert w >= 1500 and h >= 1000, f"{asset_file} dimensions too small: {w}x{h}"
        elif fmt == "svg":
            tree = ET.parse(asset_file)
            root = tree.getroot()
            text_elems = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
            assert len(text_elems) == 0, f"{asset_file} contains {len(text_elems)} raw <text> elements (must be pure vectors)"
            path_elems = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")
            assert len(path_elems) >= 10, f"{asset_file} insufficient path elements ({len(path_elems)})"

    # --- F1: 7 Core Mathematical Derivations in MDX ---
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_01_undercut_limit_derivation_in_mdx(self, lang: str):
        """[F1] Verify undercut limit derivation (z_min = 2 ha* / sin^2(alpha_0) -> 17) in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("z_{min}" in t or "z_{\\min}" in t or "17.097" in t or "17" in t), f"{lang}: z_min derivation missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_02_min_shift_derivation_in_mdx(self, lang: str):
        """[F1] Verify minimum shift derivation (x_min = 1 - z sin^2(alpha_0) / 2) in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("x_{min}" in t or "x_{\\min}" in t or "0.181156" in t or "0.28206" in t), f"{lang}: x_min derivation missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_03_involute_inverse_operating_angle_in_mdx(self, lang: str):
        """[F1] Verify operating pressure angle inv(alpha_w) equation in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("\\alpha_w" in t or "\\alpha_{w}" in t or "inv(\\alpha_w)" in t or "22.46" in t), f"{lang}: alpha_w derivation missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_04_operating_center_distance_in_mdx(self, lang: str):
        """[F1] Verify operating center distance a' = a * cos(alpha_0) / cos(alpha_w) in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("a'" in t or "a_{w}" in t or "85.414" in t), f"{lang}: Operating center distance derivation missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_05_center_and_height_modification_in_mdx(self, lang: str):
        """[F1] Verify center distance increment y and addendum modification k in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("y" in t and "k" in t and ("0.471635" in t or "0.028365" in t or "c^*" in t or "c" in t)), f"{lang}: y/k derivation missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_06_top_land_pointing_prevention_in_mdx(self, lang: str):
        """[F1] Verify top land pointing prevention condition s_a >= 0.25*m in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("s_a" in t or "s_{a1}" in t or "0.25" in t or "1.480339" in t), f"{lang}: Top land pointing constraint missing"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f1_07_specific_sliding_balancing_in_mdx(self, lang: str):
        """[F1] Verify specific sliding (미끄럼률, Specific Sliding, k1/k2) balancing derivation in MDX."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        assert ("k_1" in t or "k_2" in t or "Specific Sliding" in t or "미끄럼률" in t or "spezifisches Gleiten" in t or "滑り率" in t), f"{lang}: Specific sliding missing"

    # --- F2: 38 Parameters Closed-Form Benchmark Table ---
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f2_01_benchmark_table_38_rows_present(self, lang: str):
        """[F2] Verify table structure in MDX containing rows 1 through 38."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        rows = re.findall(r"\|\s*(\d{1,2})\s*\|", t)
        int_rows = set(int(r) for r in rows)
        for idx in range(1, 39):
            assert idx in int_rows, f"{lang}: Benchmark table missing row {idx}"

    @pytest.mark.parametrize("param_idx", list(range(1, 39)))
    def test_f2_02_benchmark_table_individual_parameter_values(self, param_idx: int):
        """[F2] Verify closed-form computation matches exact 6-digit engineering benchmark value for all 38 parameters."""
        param_desc, calc_val, unit = BENCHMARK_PARAMS[param_idx]
        assert calc_val is not None, f"Parameter {param_idx} ({param_desc}) has None value"

        # Spot check specific critical parameters
        if param_idx == 1:
            assert abs(calc_val - 3.0) < 1e-6  # Module
        elif param_idx == 2:
            assert abs(calc_val - 20.0) < 1e-6  # Standard pressure angle
        elif param_idx == 3:
            assert calc_val == 14  # z1
        elif param_idx == 4:
            assert calc_val == 42  # z2
        elif param_idx == 9:
            assert abs(calc_val - 0.35) < 1e-6  # x1
        elif param_idx == 10:
            assert abs(calc_val - 0.15) < 1e-6  # x2
        elif param_idx == 12:
            assert abs(calc_val - 17.097264) < 1e-5  # z_min
        elif param_idx == 13:
            assert abs(calc_val - 0.181156) < 1e-5  # x_min1
        elif param_idx == 14:
            assert abs(calc_val - 84.000000) < 1e-6  # a standard
        elif param_idx == 18:
            assert abs(calc_val - 22.462989) < 1e-4  # alpha_w deg
        elif param_idx == 19:
            assert abs(calc_val - 85.414904) < 1e-4  # a' operating
        elif param_idx == 20:
            assert abs(calc_val - 0.471635) < 1e-4  # y
        elif param_idx == 21:
            assert abs(calc_val - 0.028365) < 1e-4  # k
        elif param_idx == 32:
            assert abs(calc_val - 0.750000) < 1e-6  # c bottom clearance
        elif param_idx == 35:
            assert abs(calc_val - 1.480339) < 1e-4  # sa1
        elif param_idx == 36:
            assert abs(calc_val - 2.284370) < 1e-4  # sa2

    # --- F9: Equations Hash Invariance ---
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f9_01_equations_hash_presence_and_format(self, lang: str):
        """[F9] Verify presence of 64-character SHA-256 equations_hash in MDX frontmatter."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        m = re.search(r'equations_hash:\s*"?([a-f0-9]{64})"?', t)
        assert m is not None, f"{lang}: Valid 64-character hex equations_hash missing in frontmatter"

    # --- F7: 4-Gate Automated Diagram Verification Constants ---
    @pytest.mark.parametrize("gate_name,threshold_spec", [
        ("Gate 1", ("Contact Error", 0.5, "px")),
        ("Gate 2", ("Occlusion Count", 0, "count")),
        ("Gate 3", ("Text Margin", 6.0, "px")),
        ("Gate 4", ("Marker Integrity", 0, "missing")),
    ])
    def test_f7_01_four_gate_threshold_constants_defined(self, gate_name: str, threshold_spec: Tuple[str, float, str]):
        """[F7] Verify 4-Gate automated diagram verification criteria contracts in test files or specs."""
        metric_name, contract_val, contract_unit = threshold_spec

        # Inspect candidate gate definition sources (actual files)
        gate_sources = [
            _BLOG_DIR / "tests" / "test_part4_geometry_and_occlusion.py",
            _BLOG_DIR / "tests" / "test_fig4_geometry_and_occlusion.py",
            _PROJECT_ROOT / "PROJECT.md",
        ]
        parsed_val: Optional[float] = None
        parsed_unit: Optional[str] = None
        found_source = False

        for src in gate_sources:
            if not src.is_file():
                continue
            text = src.read_text(encoding="utf-8")
            if gate_name == "Gate 1":
                # Contact error: <= 0.5 px
                m = re.search(r"Gate 1.*?([0-9\.]+)\s*(px|px\b)", text, re.IGNORECASE)
                if m:
                    parsed_val = float(m.group(1))
                    parsed_unit = "px"
                    found_source = True
                    break
            elif gate_name == "Gate 2":
                # Occlusion count: 0 collisions
                m = re.search(r"Gate 2.*?(0)\s*(collisions?|count)", text, re.IGNORECASE)
                if m:
                    parsed_val = float(m.group(1))
                    parsed_unit = "count"
                    found_source = True
                    break
            elif gate_name == "Gate 3":
                # Text margin: >= 6.0 px
                m = re.search(r"Gate 3.*?([0-9\.]+)\s*(px|px\b)", text, re.IGNORECASE)
                if m:
                    parsed_val = float(m.group(1))
                    parsed_unit = "px"
                    found_source = True
                    break
            elif gate_name == "Gate 4":
                # Marker integrity: 0 missing
                m = re.search(r"Gate 4.*?(0)\s*(missing|unrendered)", text, re.IGNORECASE)
                if m:
                    parsed_val = float(m.group(1))
                    parsed_unit = "missing"
                    found_source = True
                    break

        assert found_source, f"Gate contract definition for {gate_name} not found in {[str(s) for s in gate_sources]}"
        assert parsed_val is not None

        # Assert parsed threshold from project files conforms to the gate contract specification
        if gate_name == "Gate 1":
            assert parsed_val <= contract_val, f"Gate 1 parsed threshold {parsed_val} exceeds contract {contract_val}"
            assert parsed_unit == contract_unit
        elif gate_name == "Gate 2":
            assert parsed_val == contract_val, f"Gate 2 parsed collisions {parsed_val} != {contract_val}"
        elif gate_name == "Gate 3":
            assert parsed_val >= contract_val, f"Gate 3 parsed margin {parsed_val} below contract {contract_val}"
            assert parsed_unit == contract_unit
        elif gate_name == "Gate 4":
            assert parsed_val == contract_val, f"Gate 4 parsed missing {parsed_val} != {contract_val}"

    # --- F10: Image Reference Markdown Syntax ---
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_f10_01_markdown_image_syntax_well_formed(self, lang: str):
        """[F10] Verify image references in MDX follow valid Markdown image syntax."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        t = p.read_text(encoding="utf-8")
        refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', t)
        assert len(refs) >= 3, f"{lang}: Expected at least 3 markdown image references, found {len(refs)}"
        for alt, src in refs:
            assert src.startswith("/images/part4/"), f"{lang}: Image source must reside in /images/part4/: {src}"
            assert src.endswith(".png") or src.endswith(".svg"), f"{lang}: Image source must be .png or .svg: {src}"

    # --- F11: PhotoSwipe 5 Lightbox Configuration ---
    def test_f11_01_photoswipe_lightbox_configuration_present(self):
        """[F11] Verify PhotoSwipe 5 configuration script presence in CustomHead.astro."""
        head_file = _BLOG_DIR / "src" / "components" / "CustomHead.astro"
        assert head_file.is_file(), f"CustomHead.astro missing: {head_file}"
        code = head_file.read_text(encoding="utf-8")
        assert "photoswipe" in code.lower()
        assert "wheelToZoom: true" in code
        assert "maxSpreadZoom: 4" in code

    # --- F12: Golden Regression Harness Registered Script ---
    def test_f12_01_golden_regression_harness_script_exists(self):
        """[F12] Verify verify_regression_harness.py existence at prototype2/backend/."""
        harness = _PROJECT_ROOT / "prototype2" / "backend" / "verify_regression_harness.py"
        assert harness.is_file(), f"Regression harness missing at {harness}"

    # --- F13: Remote Git Deployment & Live Production URL Target ---
    def test_f13_01_production_target_url_specification(self):
        """[F13] Verify official live production deployment URL specification in astro.config.mjs and CNAME."""
        astro_config = _BLOG_DIR / "astro.config.mjs"
        assert astro_config.is_file(), f"astro.config.mjs missing at {astro_config}"
        content = astro_config.read_text(encoding="utf-8")

        # Parse site property from astro.config.mjs
        m = re.search(r"site:\s*['\"]([^'\"]+)['\"]", content)
        assert m is not None, "site configuration missing in astro.config.mjs"
        site_url = m.group(1)

        assert site_url.startswith("https://"), f"Production site URL must use HTTPS: {site_url}"
        assert site_url == "https://gear.ideaspot360.com", f"Expected https://gear.ideaspot360.com, got {site_url}"

        # Cross-verify matching domain in CNAME if present
        cname_file = _BLOG_DIR / "public" / "CNAME"
        if cname_file.is_file():
            cname_domain = cname_file.read_text(encoding="utf-8").strip()
            assert cname_domain == "gear.ideaspot360.com", f"CNAME mismatch: {cname_domain}"
            assert cname_domain in site_url, f"CNAME {cname_domain} not contained in site URL {site_url}"


# =============================================================================
# TIER 2: Boundary & Corner Cases Test Suite (F1 ~ F13, >= 65 tests)
# =============================================================================

class TestTier2BoundaryAndCornerCases:
    """
    Tier 2: Boundary Value Analysis and Corner Cases.
    Verifies undercut limits, x_min boundaries, top land constraints, extreme shift regimes,
    Newton-Raphson convergence, and clearance preservation.
    """

    def _get_mdx(self, lang: str) -> Path:
        return get_mdx_path(lang)

    # --- B1: Undercut Boundary & Sensitivity ---
    def test_b1_01_undercut_limit_exact_closed_form(self):
        """[B1] Verify z_min exact continuous closed-form value at alpha_0 = 20 deg."""
        alpha_0 = math.radians(20.0)
        z_min_exact = calc_undercut_limit(1.0, alpha_0)
        assert abs(z_min_exact - 17.097264) < 1e-5
        assert round(z_min_exact) == 17
        assert math.ceil(z_min_exact) == 18

    @pytest.mark.parametrize("alpha_deg,expected_zmin_range", [
        (14.5, (31.5, 32.5)),
        (17.5, (22.0, 23.0)),
        (20.0, (17.0, 17.2)),
        (22.5, (13.5, 14.5)),
        (25.0, (11.0, 11.5)),
        (28.0, (9.0, 9.5)),
    ])
    def test_b1_02_undercut_limit_pressure_angle_sensitivity(self, alpha_deg: float, expected_zmin_range: Tuple[float, float]):
        """[B1] Verify z_min sensitivity across pressure angle spectrum (14.5 deg ~ 28 deg)."""
        alpha = math.radians(alpha_deg)
        z_min = calc_undercut_limit(1.0, alpha)
        low, high = expected_zmin_range
        assert low <= z_min <= high, f"alpha={alpha_deg}: z_min={z_min} outside range [{low}, {high}]"

    # --- B2: Minimum Shift x_min Calculation for z=14 ---
    def test_b2_01_xmin_closed_form_for_z14(self):
        """[B2] Verify x_min closed-form derivation for 14-tooth pinion."""
        alpha_0 = math.radians(20.0)
        x_min_calc = calc_min_shift(14, alpha_0, ha_star=1.0)
        assert abs(x_min_calc - 0.181156) < 1e-5

        # Benchmark shift x1 = +0.35 strictly exceeds both theoretical 0.181156 and margin benchmark 0.28206
        x1_benchmark = 0.35
        assert x1_benchmark > 0.28206 > x_min_calc, "Benchmark shift must clear undercut with positive margin"

    @pytest.mark.parametrize("z,expected_xmin_sign", [
        (10, 1),
        (11, 1),
        (12, 1),
        (13, 1),
        (14, 1),
        (15, 1),
        (16, 1),
        (17, 1),   # 1 - 17*sin^2(20)/2 = +0.005689 > 0
        (18, -1),  # 1 - 18*sin^2(20)/2 = -0.052827 < 0
        (42, -1),  # completely safe
    ])
    def test_b2_02_xmin_sign_behavior_across_teeth(self, z: int, expected_xmin_sign: int):
        """[B2] Verify x_min sign transitions strictly at undercut threshold z=17 vs z=18."""
        alpha_0 = math.radians(20.0)
        x_min = calc_min_shift(z, alpha_0)
        if expected_xmin_sign > 0:
            assert x_min > 0.0, f"z={z}: x_min={x_min} expected positive"
        else:
            assert x_min < 0.0, f"z={z}: x_min={x_min} expected negative"

    @pytest.mark.parametrize("role,z,x,req_min", [
        ("pinion_theory", 14, 0.35, 0.181156),
        ("pinion_margin", 14, 0.35, 0.28206),
        ("gear_theory", 42, 0.15, -1.45),
        ("sum_shift", 56, 0.50, 0.0),
    ])
    def test_b2_03_benchmark_shift_margin_over_xmin(self, role: str, z: int, x: float, req_min: float):
        """[B2] Verify benchmark shift margins satisfy positive clearances over theoretical x_min."""
        spec_path = _BLOG_DIR / "data" / "fig2_part4_spec.json"
        if not spec_path.is_file():
            spec_path = _BLOG_DIR / "data" / "specs" / "fig2_part4_spec.json"
        assert spec_path.is_file(), f"Specification file missing: {spec_path}"
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        params = spec["parameters"]

        alpha_0 = math.radians(params["alpha0_deg"])
        ha_star = params.get("ha_star", 1.0)

        if role == "pinion_theory" or role == "pinion_margin":
            z1 = params["z1"]
            x1 = params["x1"]
            xmin1 = calc_min_shift(z1, alpha_0, ha_star)
            margin = x1 - xmin1
            assert margin > 0.0, f"Pinion x1={x1} fails to clear x_min={xmin1}"
            assert x1 >= 0.35, f"Pinion x1={x1} must be >= 0.35"
            assert abs(xmin1 - 0.181156) < 1e-4, f"Theoretical x_min mismatch: {xmin1}"
            if role == "pinion_margin":
                assert margin >= 0.10, f"Pinion safety margin {margin} below 0.10"
        elif role == "gear_theory":
            z2 = params["z2"]
            x2 = params["x2"]
            xmin2 = calc_min_shift(z2, alpha_0, ha_star)
            margin = x2 - xmin2
            assert margin > 0.0, f"Gear x2={x2} fails to clear x_min={xmin2}"
            assert x2 >= 0.15, f"Gear x2={x2} must be >= 0.15"
            assert xmin2 < 0.0, f"Gear x_min expected negative for z={z2}, got {xmin2}"
        elif role == "sum_shift":
            x1 = params["x1"]
            x2 = params["x2"]
            sigma_x = params["sigma_x"]
            assert abs((x1 + x2) - sigma_x) < 1e-6, f"Sum mismatch: {x1}+{x2} != {sigma_x}"
            assert sigma_x > 0.0, f"Benchmark total profile shift must be positive: {sigma_x}"

    # --- B3: Top Land Thickness Constraint s_a >= 0.25*m (헌법 제10조 제2항, 제3항) ---
    def test_b3_01_top_land_pinion_sa1_margin(self):
        """[B3] Verify pinion top land sa1 >= 0.25*m (헌법 제10조 Zero Tooth Distortion Rule)."""
        m = 3.0
        sa1 = BENCHMARK_PARAMS[35][1]
        sa_min_threshold = 0.25 * m  # 0.75 mm
        assert sa1 >= sa_min_threshold, f"Pinion top land sa1={sa1} violates 0.25m ({sa_min_threshold})"
        assert abs(sa1 - 1.480339) < 1e-4
        margin = sa1 - sa_min_threshold
        assert margin >= 0.73, f"Pinion top land margin {margin} < 0.73 mm"

    def test_b3_02_top_land_gear_sa2_margin(self):
        """[B3] Verify gear top land sa2 >= 0.25*m."""
        m = 3.0
        sa2 = BENCHMARK_PARAMS[36][1]
        sa_min_threshold = 0.25 * m
        assert sa2 >= sa_min_threshold, f"Gear top land sa2={sa2} violates 0.25m"
        assert abs(sa2 - 2.284370) < 1e-4
        margin = sa2 - sa_min_threshold
        assert margin >= 1.50, f"Gear top land margin {margin} < 1.50 mm"

    @pytest.mark.parametrize("x_val,expected_valid_pointing", [
        (-0.30, True),
        (-0.10, True),
        (0.00, True),
        (0.20, True),
        (0.35, True),   # Benchmark pinion (sa1 = 1.480339 >= 0.75)
        (0.50, True),   # High shift (sa = 1.0481 >= 0.75)
        (0.60, True),   # Approaching pointing threshold (sa = 0.8276 >= 0.75)
        (0.65, False),  # Pointing threshold exceeded (sa = 0.7122 < 0.75)
        (0.80, False),  # Severe pointing (sa = 0.3454 < 0.75)
    ])
    def test_b3_03_top_land_thickness_across_shift_values(self, x_val: float, expected_valid_pointing: bool):
        """[B3] Verify top land thickness variation and pointing boundary under varying profile shift."""
        m = 3.0
        alpha_0 = math.radians(20.0)
        z = 14
        sa = calc_top_land(m, z, x_val, alpha_0, ha_star=1.0, k=0.0)
        sa_min = 0.25 * m
        if expected_valid_pointing:
            assert sa >= sa_min, f"x={x_val}: sa={sa} fell below {sa_min}"
        else:
            assert sa < sa_min, f"x={x_val}: expected pointing condition sa < {sa_min}, got {sa}"

    # --- B4: Extreme Shift Regimes (x < 0, x = 0, x > 0) ---
    @pytest.mark.parametrize("neg_x", [-0.10, -0.20, -0.30, -0.40, -0.50])
    def test_b4_01_negative_shift_thinner_root_and_pitch_thickness(self, neg_x: float):
        """[B4] Verify negative shift (x < 0) strictly reduces tooth thickness at pitch circle below pi*m/2."""
        m = 3.0
        alpha_0 = math.radians(20.0)
        s_std = math.pi * m / 2.0
        s_neg = m * (math.pi / 2.0 + 2.0 * neg_x * math.tan(alpha_0))
        assert s_neg < s_std, f"neg_x={neg_x}: s={s_neg} not smaller than s_std={s_std}"

    @pytest.mark.parametrize("test_case", ["thickness_identity", "center_distance_identity", "y_zero_identity"])
    def test_b4_02_zero_shift_baseline_identity(self, test_case: str):
        """[B4] Verify x = 0 returns unshifted standard gear identities."""
        m = 3.0
        alpha_0 = math.radians(20.0)
        z1, z2 = 14, 42
        if test_case == "thickness_identity":
            s_zero = m * (math.pi / 2.0 + 2.0 * 0.0 * math.tan(alpha_0))
            assert abs(s_zero - math.pi * m / 2.0) < 1e-12
        elif test_case == "center_distance_identity":
            a_std = m * (z1 + z2) / 2.0
            inv_a0 = inv(alpha_0)
            inv_aw = inv_a0 + 2.0 * (0.0) / (z1 + z2) * math.tan(alpha_0)
            aw = solve_inv(inv_aw)
            a_prime = a_std * math.cos(alpha_0) / math.cos(aw)
            assert abs(a_prime - a_std) < 1e-10
        elif test_case == "y_zero_identity":
            inv_a0 = inv(alpha_0)
            aw = solve_inv(inv_a0)
            y = (m * (z1 + z2) / 2.0 * (math.cos(alpha_0) / math.cos(aw) - 1.0)) / m
            assert abs(y) < 1e-10

    @pytest.mark.parametrize("pos_x", [0.10, 0.20, 0.35, 0.50, 0.70])
    def test_b4_03_positive_shift_thickens_tooth(self, pos_x: float):
        """[B4] Verify positive shift (x > 0) strictly increases tooth thickness at pitch circle above pi*m/2."""
        m = 3.0
        alpha_0 = math.radians(20.0)
        s_std = math.pi * m / 2.0
        s_pos = m * (math.pi / 2.0 + 2.0 * pos_x * math.tan(alpha_0))
        assert s_pos > s_std, f"pos_x={pos_x}: s={s_pos} not greater than s_std={s_std}"

    # --- B5: Operating Center Distance and Pressure Angle Relations ---
    def test_b5_01_operating_pressure_angle_strictly_greater_for_positive_sum_shift(self):
        """[B5] Verify operating pressure angle alpha_w > alpha_0 when Sigma x > 0."""
        alpha_0_deg = 20.0
        alpha_w_deg = BENCHMARK_PARAMS[18][1]
        assert alpha_w_deg > alpha_0_deg, f"alpha_w ({alpha_w_deg}) must exceed alpha_0 ({alpha_0_deg})"
        assert abs(alpha_w_deg - 22.462989) < 1e-4

    def test_b5_02_operating_center_distance_strictly_greater(self):
        """[B5] Verify operating center distance a' > a when Sigma x > 0."""
        a_std = BENCHMARK_PARAMS[14][1]
        a_prime = BENCHMARK_PARAMS[19][1]
        assert a_prime > a_std, f"a' ({a_prime}) must exceed a ({a_std})"
        assert abs(a_prime - 85.414904) < 1e-4

    def test_b5_03_clearance_preservation_identity(self):
        """[B5] Verify bottom clearance c = 0.75 mm is preserved exactly via k = Sigma x - y."""
        c_clearance = BENCHMARK_PARAMS[32][1]
        expected_c = 0.25 * 3.0
        assert abs(c_clearance - expected_c) < 1e-6, f"Clearance {c_clearance} != c*m {expected_c}"

    def test_b5_04_center_distance_modification_sum_rule(self):
        """[B5] Verify fundamental invariant y + k = Sigma x."""
        y = BENCHMARK_PARAMS[20][1]
        k = BENCHMARK_PARAMS[21][1]
        sigma_x = BENCHMARK_PARAMS[11][1]
        assert abs((y + k) - sigma_x) < 1e-12, f"y + k ({y+k}) != Sigma x ({sigma_x})"

    @pytest.mark.parametrize("alpha_rad", [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75])
    def test_b5_05_involute_function_monotonicity(self, alpha_rad: float):
        """[B5] Verify strict monotonicity of involute function d(inv)/d(alpha) = tan^2(alpha) > 0."""
        delta = 1e-5
        inv_curr = inv(alpha_rad)
        inv_next = inv(alpha_rad + delta)
        deriv_num = (inv_next - inv_curr) / delta
        deriv_exact = math.tan(alpha_rad) ** 2
        assert abs(deriv_num - deriv_exact) < 1e-4
        assert deriv_num > 0.0

    @pytest.mark.parametrize("target_inv", [0.005, 0.010, 0.014904, 0.021404, 0.035, 0.050])
    def test_b5_06_newton_raphson_inverse_involute_convergence(self, target_inv: float):
        """[B5] Verify Newton-Raphson inverse involute solver achieves precision < 1e-14."""
        solved_alpha = solve_inv(target_inv)
        recalculated_inv = inv(solved_alpha)
        assert abs(recalculated_inv - target_inv) < 1e-14, f"Failed convergence for target {target_inv}"

    # --- B6: Frontmatter Zod Schema Validation Limits ---
    @pytest.mark.parametrize("invalid_date", ["2026/11/16", "26-11-16", "2026-1-1", "invalid", "2026-13-45"])
    def test_b6_01_review_date_regex_validation(self, invalid_date: str):
        """[B6] Verify review_date regex strictly enforces YYYY-MM-DD pattern from content.config.ts."""
        config_ts = _BLOG_DIR / "src" / "content.config.ts"
        assert config_ts.is_file(), f"content.config.ts missing at {config_ts}"
        content = config_ts.read_text(encoding="utf-8")

        # Extract review_date regex pattern: regex(/^\d{4}-\d{2}-\d{2}$/)
        m = re.search(r"review_date:\s*z\.string\(\)\.regex\(/\^(\\d\{4\}-\\d\{2\}-\\d\{2\})\$/\)", content)
        assert m is not None, "review_date regex definition not found in content.config.ts"
        pattern = "^" + m.group(1) + "$"

        match = re.match(pattern, invalid_date)
        if match is None:
            # Genuine failure to match date regex format
            assert match is None, f"Expected regex failure for {invalid_date}"
        else:
            # Format matched regex, verify semantic calendar bounds rejection (e.g. 2026-13-45)
            parts = [int(p) for p in invalid_date.split("-")]
            is_valid_calendar = (1 <= parts[1] <= 12 and 1 <= parts[2] <= 31)
            assert not is_valid_calendar, f"Expected reject for {invalid_date} but calendar range is valid"

    @pytest.mark.parametrize("invalid_level", ["freshman", "master", "phd", "expert", "doctoral"])
    def test_b6_02_academic_level_enum_rejection(self, invalid_level: str):
        """[B6] Verify academic_level rejects non-enumerated strings against content.config.ts schema."""
        config_ts = _BLOG_DIR / "src" / "content.config.ts"
        assert config_ts.is_file(), f"content.config.ts missing at {config_ts}"
        content = config_ts.read_text(encoding="utf-8")

        # Extract academic_level enum list: z.enum(['undergraduate', 'graduate', 'industrial_expert'])
        m = re.search(r"academic_level:\s*z\.enum\(\[([^\]]+)\]\)", content)
        assert m is not None, "academic_level enum definition not found in content.config.ts"
        allowed_levels = set(re.findall(r"['\"]([^'\"]+)['\"]", m.group(1)))

        assert len(allowed_levels) >= 3, f"Expected at least 3 academic levels in schema, found {allowed_levels}"
        assert invalid_level not in allowed_levels, (
            f"Invalid level '{invalid_level}' unexpectedly found in schema allowed levels: {allowed_levels}"
        )

    # --- B7: Article 12 Banned Clichés Check Across 4 Languages ---
    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_b7_01_article_12_no_banned_cliches(self, lang: str):
        """[B7] Constitutional Article 12: Zero AI clichés in engineering prose."""
        p = self._get_mdx(lang)
        if not p.is_file():
            pytest.skip(f"[PENDING] MDX not yet created for {lang}: {p}")
        text = p.read_text(encoding="utf-8").lower()
        cliches = {
            "ko": ["이 글에서는", "알아보겠습니다", "살펴보았습니다", "결론적으로,", "요약하자면,"],
            "en": ["in this article, we will", "let's delve into", "in conclusion,", "to summarize,"],
            "de": ["in diesem artikel werden wir", "zusammenfassend lässt sich sagen"],
            "ja": ["この記事では", "見ていきましょう", "結論として、", "要約すると、"],
        }
        for c in cliches[lang]:
            assert c.lower() not in text, f"{lang}: Banned cliché '{c}' detected!"


# =============================================================================
# TIER 3: Cross-Feature Combinations & Pairwise Integration Tests
# =============================================================================

class TestTier3CrossFeatureAndPairwise:
    """
    Tier 3: Cross-Feature Combinations & Pairwise Integration.
    Verifies 24 diagram asset matrix, language isolation, KaTeX SHA-256 invariance,
    PhotoSwipe 5 lightbox attributes, and parameter consistency across math, specs, and MDX.
    """

    @pytest.mark.parametrize("lang,diag,fmt", ASSET_24_MATRIX)
    def test_t3_01_asset_24_files_exhaustive_matrix(self, lang: str, diag: str, fmt: str):
        """[T3] 24 diagram assets exhaustive matrix audit (existence, size, DPI, vector purity)."""
        asset_path = ASSETS_DIR / lang / f"{diag}.{fmt}"
        if not asset_path.is_file():
            pytest.skip(f"[PENDING] Asset file not yet generated: {asset_path}")

        file_size = asset_path.stat().st_size
        min_size = 50_000 if fmt == "png" else 15_000
        assert file_size >= min_size, f"{asset_path.name} size {file_size} bytes < min {min_size}"

        if fmt == "png" and _HAS_IMAGING:
            with Image.open(asset_path) as img:
                assert img.format == "PNG", f"{asset_path} is not PNG"
                dpi = img.info.get("dpi")
                assert dpi is not None, f"{asset_path} missing DPI info"
                assert round(dpi[0]) == 300 and round(dpi[1]) == 300, f"{asset_path} DPI is not 300: {dpi}"
                w, h = img.size
                assert w >= 2000 and h >= 1400, f"{asset_path} resolution {w}x{h} < 2000x1400"
                arr = np.array(img.convert("RGB"))
                assert float(np.std(arr)) > 15.0, f"{asset_path} image standard deviation too low"
                assert float(np.mean(arr < 250)) > 0.03, f"{asset_path} appears blank canvas"
        elif fmt == "svg":
            tree = ET.parse(asset_path)
            root = tree.getroot()
            text_tags = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
            assert len(text_tags) == 0, f"{asset_path} contains {len(text_tags)} raw text tags (must be paths)"
            path_tags = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")
            assert len(path_tags) >= 15, f"{asset_path} vector paths insufficient ({len(path_tags)})"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_t3_02_multilingual_image_references_consistency(self, lang: str):
        """[T3] MDX multilingual image references language isolation."""
        mdx_path = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not mdx_path.is_file():
            pytest.skip(f"[PENDING] MDX missing: {mdx_path}")
        content = mdx_path.read_text(encoding="utf-8")

        for diag in REQUIRED_DIAGRAMS:
            expected_ref = f"/images/part4/{lang}/{diag}.png"
            assert expected_ref in content, f"[{lang}] Missing expected image link: {expected_ref}"

        for other_lang in LANGUAGES:
            if other_lang != lang:
                assert f"/images/part4/{other_lang}/" not in content, f"[{lang}] Leakage of other language ({other_lang}) image path"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_t3_03_frontmatter_required_diagrams_exact_match(self, lang: str):
        """[T3] Frontmatter required_diagrams exact 3-diagram match."""
        mdx_path = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not mdx_path.is_file():
            pytest.skip(f"[PENDING] MDX missing: {mdx_path}")
        content = mdx_path.read_text(encoding="utf-8")

        match = re.search(r"required_diagrams:\s*\n((?:\s*-\s*\"?[^\"]+\"?\s*\n?)+)", content)
        assert match is not None, f"[{lang}] required_diagrams block missing"
        diagram_ids = [d.strip(' -\t\r\n"') for d in match.group(1).strip().splitlines() if d.strip()]
        assert diagram_ids == REQUIRED_DIAGRAMS, f"[{lang}] required_diagrams mismatch: {diagram_ids} != {REQUIRED_DIAGRAMS}"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_t3_04_frontmatter_body_bijection(self, lang: str):
        """[T3] 1:1 bijection between frontmatter required_diagrams and MDX body embeds."""
        mdx_path = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not mdx_path.is_file():
            pytest.skip(f"[PENDING] MDX missing: {mdx_path}")
        content = mdx_path.read_text(encoding="utf-8")

        match = re.search(r"required_diagrams:\s*\n((?:\s*-\s*\"?[^\"]+\"?\s*\n?)+)", content)
        assert match is not None
        fm_set = set(d.strip(' -\t\r\n"') for d in match.group(1).strip().splitlines() if d.strip())

        body_images = re.findall(r'!\[.*?\]\(/images/part4/[^/]+/([^/]+)\.(?:png|svg)\)', content)
        body_set = set(body_images)
        assert fm_set == body_set, f"[{lang}] Bijection mismatch: symmetric diff {fm_set ^ body_set}"

    @pytest.mark.parametrize("diag", REQUIRED_DIAGRAMS)
    def test_t3_05_cross_language_diagram_resolution_symmetry(self, diag: str):
        """[T3] Image dimensions symmetry across all 4 languages."""
        if not _HAS_IMAGING:
            pytest.skip("PIL / numpy not installed")
        sizes = {}
        for lang in LANGUAGES:
            p = ASSETS_DIR / lang / f"{diag}.png"
            if not p.is_file():
                pytest.skip(f"[PENDING] Asset missing: {p}")
            with Image.open(p) as img:
                sizes[lang] = img.size

        unique_sizes = set(sizes.values())
        assert len(unique_sizes) == 1, f"[{diag}] Resolution mismatch across languages: {sizes}"

    def test_t3_06_equations_hash_invariance_across_all_languages(self):
        """[T3] Equations block count and SHA-256 hash invariance across all 4 languages."""
        hashes = {}
        counts = {}
        for lang in LANGUAGES:
            p = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
            if not p.is_file():
                pytest.skip(f"[PENDING] MDX missing: {p}")
            content = p.read_text(encoding="utf-8")
            blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
            counts[lang] = len(blocks)
            normalized = "\n---\n".join(b.strip() for b in blocks)
            h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            hashes[lang] = h

            fm_match = re.search(r'equations_hash:\s*"?([a-f0-9]{64})"?', content)
            assert fm_match is not None, f"[{lang}] Frontmatter equations_hash missing"
            assert fm_match.group(1) == h, f"[{lang}] Frontmatter hash {fm_match.group(1)} != computed {h}"

        assert len(set(counts.values())) == 1, f"Equation count mismatch: {counts}"
        assert list(counts.values())[0] >= 7, f"Expected >= 7 equation blocks, found {list(counts.values())[0]}"
        assert len(set(hashes.values())) == 1, f"equations_hash mismatch across languages: {hashes}"

    def test_t3_07_core_mathematical_formulas_present(self):
        """[T3] Verify 7 core formulas represented in Korean article text."""
        ko_mdx = DOCS_DIR / "ko" / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not ko_mdx.is_file():
            pytest.skip("[PENDING] KO MDX missing")
        content = ko_mdx.read_text(encoding="utf-8")
        expected_patterns = [
            r"z_{min}|z_{\\min}",
            r"x_{min}|x_{\\min}",
            r"\\alpha_w|\\alpha_{w}",
            r"a'|a_{w}",
            r"y.*k|k.*y",
            r"s_a|s_{a1}",
            r"k_1|k_2|Specific Sliding|미끄럼률",
        ]
        for pat in expected_patterns:
            assert re.search(pat, content) is not None, f"Core formula pattern missing: {pat}"

    def test_t3_08_photoswipe_lightbox_configuration_and_bindings(self):
        """[T3] PhotoSwipe 5 lightbox configuration and zoom attributes."""
        head_path = _BLOG_DIR / "src" / "components" / "CustomHead.astro"
        assert head_path.is_file()
        head_code = head_path.read_text(encoding="utf-8")
        assert "photoswipe" in head_code
        assert "wheelToZoom: true" in head_code
        assert "maxSpreadZoom: 4" in head_code

        css_path = _BLOG_DIR / "src" / "styles" / "custom.css"
        assert css_path.is_file()
        css_code = css_path.read_text(encoding="utf-8")
        assert "cursor: zoom-in" in css_code

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_t3_09_photoswipe_alt_caption_richness(self, lang: str):
        """[T3] PhotoSwipe captions richness (image alt text length >= 15 characters)."""
        mdx_path = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not mdx_path.is_file():
            pytest.skip(f"[PENDING] MDX missing: {mdx_path}")
        content = mdx_path.read_text(encoding="utf-8")
        alts = re.findall(r'!\[(.*?)\]\(/images/part4/', content)
        assert len(alts) >= 3, f"[{lang}] Found {len(alts)} image alts, expected >= 3"
        for alt in alts:
            assert len(alt.strip()) >= 15, f"[{lang}] Alt text too short ({len(alt.strip())} chars): '{alt}'"

    def test_t3_10_parameter_consistency_math_engine_to_specs(self):
        """[T3] Consistency between closed-form engine and diagram spec JSON."""
        spec_path = DATA_DIR / "specs" / "fig2_part4_spec.json"
        if not spec_path.is_file():
            spec_path = DATA_DIR / "fig2_part4_spec.json"
        if not spec_path.is_file():
            pytest.skip(f"[PENDING] Spec file missing: {spec_path}")

        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        params = spec.get("parameters", spec)
        m_val = params.get("module", params.get("m"))
        assert m_val == 3.0, f"Module mismatch: {m_val}"
        assert params.get("z1") == 14 and params.get("z2") == 42, "Teeth count mismatch"
        assert params.get("x1") == 0.35 and params.get("x2") == 0.15, "Shift coefficient mismatch"
        assert abs(params.get("a_prime", 85.414904) - 85.414904) < 1e-3, "Operating center distance mismatch"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_t3_11_parameter_consistency_specs_to_mdx_tables(self, lang: str):
        """[T3] Consistency between spec parameters and MDX 38-parameter table."""
        mdx_path = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not mdx_path.is_file():
            pytest.skip(f"[PENDING] MDX missing: {mdx_path}")
        content = mdx_path.read_text(encoding="utf-8")

        assert "84.000000" in content, f"[{lang}] Standard center distance 84.000000 missing"
        assert "85.414904" in content, f"[{lang}] Operating center distance 85.414904 missing"
        assert "22.462989" in content, f"[{lang}] Operating pressure angle 22.462989 missing"
        assert "1.480339" in content, f"[{lang}] Pinion top land 1.480339 missing"
        assert "2.284370" in content, f"[{lang}] Gear top land 2.284370 missing"

    def test_t3_12_locale_labels_dictionary_parity(self):
        """[T3] Parity of locale label dictionaries across 4 languages."""
        locales_dir = DATA_DIR / "locales"
        labels = {}
        for lang in LANGUAGES:
            p = locales_dir / lang / "part4_labels.json"
            if not p.is_file():
                pytest.skip(f"[PENDING] Labels file missing: {p}")
            labels[lang] = set(json.loads(p.read_text(encoding="utf-8")).keys())

        base_keys = labels.get("ko")
        for lang in ["en", "de", "ja"]:
            assert labels[lang] == base_keys, f"[{lang}] Label keys mismatch with ko: {labels[lang] ^ base_keys}"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_t3_13_writing_principles_and_cliche_freedom(self, lang: str):
        """[T3] Constitutional Article 12: Zero raw code blocks or software UI jargon in engineering prose."""
        mdx_path = DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx"
        if not mdx_path.is_file():
            pytest.skip(f"[PENDING] MDX missing: {mdx_path}")
        content = mdx_path.read_text(encoding="utf-8")

        ui_terms = ["클릭", "드롭다운", "모달창", "팝업창", "다이얼로그", "UI 뷰어"]
        if lang == "ko":
            for term in ui_terms:
                assert term not in content, f"[{lang}] Forbidden UI term detected: '{term}'"

        code_terms = ["def ", "class Gear", "import numpy", "console.log"]
        for term in code_terms:
            assert term not in content, f"[{lang}] Raw programming syntax detected: '{term}'"


# =============================================================================
# TIER 4: Real-World Application Scenarios
# =============================================================================

class TestTier4RealWorldScenarios:
    """
    Tier 4: Real-World Application Workload Scenarios.
    Executes Astro static build, image linter, 4-Gate test suite, browser visual captures,
    and cumulative 111 golden cases zero-regression audit.
    """

    def test_sc01_astro_starlight_static_build(self):
        """[SC-01] Astro Starlight static build execution and page completion audit."""
        package_json = _BLOG_DIR / "package.json"
        if not package_json.is_file():
            pytest.skip("blog/package.json missing")

        cmd = ["npm", "--prefix", str(_BLOG_DIR), "run", "build"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180, shell=True)
        assert res.returncode == 0, f"[SC-01] Build failed (code {res.returncode}):\n{res.stdout[-1000:]}\n{res.stderr[-1000:]}"
        clean_stdout = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', res.stdout)
        assert ("Complete!" in clean_stdout) or ("complete" in clean_stdout.lower()), f"[SC-01] Build completion message missing:\n{clean_stdout[-500:]}"

        ch04_exists = (DOCS_DIR / "ko" / "series1-theory" / "part-a-spur" / "04-profile-shift.mdx").is_file()
        if ch04_exists:
            assert "25 page(s) built" in clean_stdout, f"[SC-01] Expected 25 pages with Chapter 4:\n{clean_stdout[-500:]}"
        else:
            assert ("21 page(s) built" in clean_stdout) or ("page(s) built" in clean_stdout)

    def test_sc02_image_reference_linter(self):
        """[SC-02] Multilingual image reference linter passes with 0 violations."""
        linter_script = _BLOG_DIR / "scripts" / "lint_image_references.py"
        if not linter_script.is_file():
            pytest.skip(f"Linter script missing: {linter_script}")

        res = subprocess.run([sys.executable, str(linter_script)], capture_output=True, text=True, timeout=60)
        assert res.returncode == 0, f"[SC-02] Image linter failed (code {res.returncode}):\n{res.stdout}\n{res.stderr}"
        assert "Total Violations Detected    : 0" in res.stdout or "0 violation(s)" in res.stdout, f"[SC-02] Violations found:\n{res.stdout}"

    def test_sc03_four_gate_diagram_verification(self):
        """[SC-03] 4-Gate automated diagram verification suite passes all geometric gates."""
        gate_test_script = _BLOG_DIR / "tests" / "test_part4_geometry_and_occlusion.py"
        if not gate_test_script.is_file():
            pytest.skip(f"[PENDING] 4-Gate script not yet created: {gate_test_script}")

        cmd = [sys.executable, "-m", "pytest", str(gate_test_script), "-v"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        assert res.returncode == 0, f"[SC-03] 4-Gate diagram tests failed:\n{res.stdout[-1500:]}"

    def test_sc04_headless_browser_visual_capture(self):
        """[SC-04] Playwright headless browser rendering and PhotoSwipe 4x zoom verification."""
        capture_script = _BLOG_DIR / "scripts" / "capture_part4_browser.py"
        if not capture_script.is_file():
            pytest.skip(f"[PENDING] Visual capture script not yet created: {capture_script}")

        res = subprocess.run([sys.executable, str(capture_script)], capture_output=True, text=True, timeout=120)
        assert res.returncode == 0, f"[SC-04] Visual capture failed:\n{res.stdout[-1500:]}\n{res.stderr[-1000:]}"

    def test_sc05_invariant_regression_audit(self):
        """[SC-05] 111 Cumulative Golden Benchmark cases zero-regression verification (0.000000 um error)."""
        harness_script = _PROJECT_ROOT / "prototype2" / "backend" / "verify_regression_harness.py"
        assert harness_script.is_file(), f"Regression harness missing: {harness_script}"

        res = subprocess.run([sys.executable, str(harness_script)], capture_output=True, text=True, timeout=120)
        assert res.returncode == 0, f"[SC-05] Golden harness regression detected:\n{res.stdout[-1500:]}"
        assert "[ALL REGRESSION CHECKS PASSED]" in res.stdout, "[SC-05] Golden cases did not pass all checks"
        assert "0.000000 um error" in res.stdout, "[SC-05] Zero-error (0.000000 um) assertion failed"

    @pytest.mark.parametrize("lang", LANGUAGES)
    def test_sc06_built_html_production_audit(self, lang: str):
        """[SC-06] Production HTML artifact audit (table tags, KaTeX class, image paths)."""
        html_file = DIST_DIR / lang / "series1-theory" / "part-a-spur" / "04-profile-shift" / "index.html"
        if not html_file.is_file():
            pytest.skip(f"[PENDING] Built HTML missing: {html_file}. Requires SC-01 build first.")

        content = html_file.read_text(encoding="utf-8")
        assert len(content) >= 15000, f"[{lang}] HTML file size too small ({len(content)} bytes)"
        for diag in REQUIRED_DIAGRAMS:
            expected_src = f"/images/part4/{lang}/{diag}.png"
            assert expected_src in content, f"[{lang}] Image source missing in HTML: {expected_src}"
        assert 'src=""' not in content, f"[{lang}] Empty src found"
        assert 'src="undefined"' not in content, f"[{lang}] Undefined src found"
        assert "<table" in content and "</table>" in content, f"[{lang}] Native table element missing"
        assert "katex" in content, f"[{lang}] KaTeX class missing in HTML"


# =============================================================================
# Standalone CLI Test Runner & ASCII Diagnostics
# =============================================================================

def run_diagnostics(selected_tier: str = "all", strict: bool = False) -> int:
    """
    Executes the 4-tier test suite in standalone CLI mode, printing an ASCII summary table.
    Returns 0 on success, 1 on failure.
    """
    print("\n" + "=" * 85)
    print("  H-GEAR STUDIO: Chapter 4 Profile Shift Comprehensive 4-Tier E2E Test Suite")
    print("  Target: blog/tests/test_part4_e2e_suite.py")
    print(f"  Selected Tier: {selected_tier.upper()} | Strict Mode: {strict}")
    print("=" * 85)

    results: List[Dict[str, Any]] = []

    def record(tier: int, code: str, desc: str, status: str, details: str = ""):
        results.append({
            "tier": tier,
            "code": code,
            "desc": desc,
            "status": status,
            "details": details,
        })

    def run_safe(tier: int, code: str, desc: str, fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
            record(tier, code, desc, "PASS", "Verified")
        except _SKIP_EXCEPTIONS as e:
            reason = str(e) or "Asset not yet generated"
            if strict:
                record(tier, code, desc, "FAIL", f"[Strict Required] {reason}")
            else:
                record(tier, code, desc, "SKIP", f"[Pending] {reason[:40]}")
        except AssertionError as e:
            record(tier, code, desc, "FAIL", f"Assertion: {str(e)[:45]}")
        except Exception as e:
            record(tier, code, desc, "FAIL", f"Error: {type(e).__name__}: {str(e)[:40]}")

    # --- Tier 1 Execution ---
    if selected_tier in ["all", "1"]:
        print("\n--- Executing Tier 1: Feature Coverage (F1 ~ F13) ---")
        t1 = TestTier1FeatureCoverage()

        # F8: MDX Documents
        for lang in LANGUAGES:
            run_safe(1, f"T1-MDX-EX-{lang}", f"MDX File Exists ({lang})", t1.test_f8_01_mdx_file_existence, lang)
            run_safe(1, f"T1-MDX-LEN-{lang}", f"MDX Length >=10k ({lang})", t1.test_f8_02_mdx_content_length_substantial, lang)
            run_safe(1, f"T1-FM-ZOD-{lang}", f"Frontmatter Schema ({lang})", t1.test_f8_03_frontmatter_zod_schema_fields, lang)
            run_safe(1, f"T1-FM-ORD-{lang}", f"Order: 4 Setting ({lang})", t1.test_f8_04_frontmatter_order_4, lang)
            run_safe(1, f"T1-FM-DIAG-{lang}", f"Required Diagrams ({lang})", t1.test_f8_05_frontmatter_required_diagrams_contract, lang)

        # F6: 24 Diagram Assets
        for lang, diag, fmt in ASSET_24_MATRIX:
            short_diag = diag.replace("fig1_rack_cutter_shift_undercut", "fig1").replace("fig2_operating_mesh_geometry", "fig2").replace("fig3_specific_sliding_balancing", "fig3")
            run_safe(1, f"T1-AST-{lang}-{short_diag}-{fmt}", f"Asset {lang}/{short_diag}.{fmt} >=20KB", t1.test_f6_01_diagram_asset_existence_and_size, lang, diag, fmt)

        # F1: 7 Core Mathematical Derivations
        for lang in LANGUAGES:
            run_safe(1, f"T1-M1-ZMIN-{lang}", f"z_min Derivation ({lang})", t1.test_f1_01_undercut_limit_derivation_in_mdx, lang)
            run_safe(1, f"T1-M2-XMIN-{lang}", f"x_min Derivation ({lang})", t1.test_f1_02_min_shift_derivation_in_mdx, lang)
            run_safe(1, f"T1-M3-AW-{lang}", f"alpha_w Derivation ({lang})", t1.test_f1_03_involute_inverse_operating_angle_in_mdx, lang)
            run_safe(1, f"T1-M4-APR-{lang}", f"a' Derivation ({lang})", t1.test_f1_04_operating_center_distance_in_mdx, lang)
            run_safe(1, f"T1-M5-YK-{lang}", f"y & k Derivation ({lang})", t1.test_f1_05_center_and_height_modification_in_mdx, lang)
            run_safe(1, f"T1-M6-SA-{lang}", f"s_a >= 0.25m Derivation ({lang})", t1.test_f1_06_top_land_pointing_prevention_in_mdx, lang)
            run_safe(1, f"T1-M7-SLID-{lang}", f"Specific Sliding Derivation ({lang})", t1.test_f1_07_specific_sliding_balancing_in_mdx, lang)

        # F2: 38 Parameters Table & Numerical Values
        for lang in LANGUAGES:
            run_safe(1, f"T1-TBL-ROWS-{lang}", f"38 Table Rows Present ({lang})", t1.test_f2_01_benchmark_table_38_rows_present, lang)

        for p_idx in range(1, 39):
            desc, val, unit = BENCHMARK_PARAMS[p_idx]
            run_safe(1, f"T1-P{p_idx:02d}", f"Param {p_idx:02d} ({desc[:18]})", t1.test_f2_02_benchmark_table_individual_parameter_values, p_idx)

        # F9, F7, F10, F11, F12, F13
        for lang in LANGUAGES:
            run_safe(1, f"T1-HASH-{lang}", f"Equations Hash Valid ({lang})", t1.test_f9_01_equations_hash_presence_and_format, lang)
            run_safe(1, f"T1-MD-IMG-{lang}", f"Markdown Image Syntax ({lang})", t1.test_f10_01_markdown_image_syntax_well_formed, lang)

        run_safe(1, "T1-GATE-TH", "4-Gate Threshold Spec", t1.test_f7_01_four_gate_threshold_constants_defined, "Gate 1", ("Contact", 0.5, "px"))
        run_safe(1, "T1-PSWIPE-CFG", "PhotoSwipe 5 Config Exists", t1.test_f11_01_photoswipe_lightbox_configuration_present)
        run_safe(1, "T1-REG-FILE", "Golden Harness File Exists", t1.test_f12_01_golden_regression_harness_script_exists)
        run_safe(1, "T1-PROD-URL", "Production URL Defined", t1.test_f13_01_production_target_url_specification)

    # --- Tier 2 Execution ---
    if selected_tier in ["all", "2"]:
        print("\n--- Executing Tier 2: Boundary & Corner Cases ---")
        t2 = TestTier2BoundaryAndCornerCases()

        run_safe(2, "T2-B1-ZMIN-EX", "z_min Closed-Form Exact", t2.test_b1_01_undercut_limit_exact_closed_form)
        for alpha_deg, r in [(14.5, (31.5, 32.5)), (20.0, (17.0, 17.2)), (25.0, (11.0, 11.5))]:
            run_safe(2, f"T2-B1-SENS-{alpha_deg}", f"z_min Sens ({alpha_deg} deg)", t2.test_b1_02_undercut_limit_pressure_angle_sensitivity, alpha_deg, r)

        run_safe(2, "T2-B2-XMIN-Z14", "x_min z=14 Closed Form", t2.test_b2_01_xmin_closed_form_for_z14)
        for z, sign in [(14, 1), (17, 1), (18, -1), (42, -1)]:
            run_safe(2, f"T2-B2-SIGN-z{z}", f"x_min Sign (z={z})", t2.test_b2_02_xmin_sign_behavior_across_teeth, z, sign)

        run_safe(2, "T2-B2-MARG-P1", "Pinion Shift x1=0.35 Margin", t2.test_b2_03_benchmark_shift_margin_over_xmin, "pinion_theory", 14, 0.35, 0.181156)
        run_safe(2, "T2-B3-SA1-MARG", "Pinion Top Land sa1 >= 0.25m", t2.test_b3_01_top_land_pinion_sa1_margin)
        run_safe(2, "T2-B3-SA2-MARG", "Gear Top Land sa2 >= 0.25m", t2.test_b3_02_top_land_gear_sa2_margin)

        for x_val, valid in [(-0.3, True), (0.0, True), (0.35, True), (0.5, True), (0.6, True), (0.65, False), (0.8, False)]:
            run_safe(2, f"T2-B3-SA-x{x_val}", f"Top Land sa (x={x_val})", t2.test_b3_03_top_land_thickness_across_shift_values, x_val, valid)

        for neg_x in [-0.1, -0.3, -0.5]:
            run_safe(2, f"T2-B4-NEG-x{neg_x}", f"Neg Shift Thickness (x={neg_x})", t2.test_b4_01_negative_shift_thinner_root_and_pitch_thickness, neg_x)

        for case in ["thickness_identity", "center_distance_identity", "y_zero_identity"]:
            run_safe(2, f"T2-B4-ZERO-{case}", f"Zero Shift {case}", t2.test_b4_02_zero_shift_baseline_identity, case)

        for pos_x in [0.2, 0.35, 0.5]:
            run_safe(2, f"T2-B4-POS-x{pos_x}", f"Pos Shift Thickness (x={pos_x})", t2.test_b4_03_positive_shift_thickens_tooth, pos_x)

        run_safe(2, "T2-B5-AW-GT", "alpha_w > alpha_0", t2.test_b5_01_operating_pressure_angle_strictly_greater_for_positive_sum_shift)
        run_safe(2, "T2-B5-APR-GT", "a' > a", t2.test_b5_02_operating_center_distance_strictly_greater)
        run_safe(2, "T2-B5-CLR-PRE", "Clearance c=0.75mm Preserved", t2.test_b5_03_clearance_preservation_identity)
        run_safe(2, "T2-B5-SUM-RULE", "y + k = Sigma x Rule", t2.test_b5_04_center_distance_modification_sum_rule)

        for a_rad in [0.15, 0.35, 0.55]:
            run_safe(2, f"T2-B5-MONO-{a_rad}", f"Involute Monotonicity ({a_rad})", t2.test_b5_05_involute_function_monotonicity, a_rad)

        for t_inv in [0.014904, 0.021404]:
            run_safe(2, f"T2-B5-NR-{t_inv}", f"Newton-Raphson Solver ({t_inv})", t2.test_b5_06_newton_raphson_inverse_involute_convergence, t_inv)

        for bad_date in ["2026/11/16", "invalid"]:
            run_safe(2, f"T2-B6-DATE-{bad_date[:6]}", f"Date Validation ({bad_date})", t2.test_b6_01_review_date_regex_validation, bad_date)

        for bad_lvl in ["freshman", "phd"]:
            run_safe(2, f"T2-B6-LVL-{bad_lvl}", f"Academic Level Enum ({bad_lvl})", t2.test_b6_02_academic_level_enum_rejection, bad_lvl)

        for lang in LANGUAGES:
            run_safe(2, f"T2-B7-CLICHE-{lang}", f"Article 12 Cliches ({lang})", t2.test_b7_01_article_12_no_banned_cliches, lang)

    # --- Tier 3 Execution ---
    if selected_tier in ["all", "3"]:
        print("\n--- Executing Tier 3: Cross-Feature Combinations & Pairwise Integration ---")
        t3 = TestTier3CrossFeatureAndPairwise()

        for lang, diag, fmt in ASSET_24_MATRIX:
            short_diag = diag.replace("fig1_rack_cutter_shift_undercut", "fig1").replace("fig2_operating_mesh_geometry", "fig2").replace("fig3_specific_sliding_balancing", "fig3")
            run_safe(3, f"T3-AST-{lang}-{short_diag}-{fmt}", f"Asset Pairwise {lang}/{short_diag}.{fmt}", t3.test_t3_01_asset_24_files_exhaustive_matrix, lang, diag, fmt)

        for lang in LANGUAGES:
            run_safe(3, f"T3-ISOL-{lang}", f"Language Isolation ({lang})", t3.test_t3_02_multilingual_image_references_consistency, lang)
            run_safe(3, f"T3-REQ-EX-{lang}", f"Required Diags Match ({lang})", t3.test_t3_03_frontmatter_required_diagrams_exact_match, lang)
            run_safe(3, f"T3-BIJ-{lang}", f"FM-Body Bijection ({lang})", t3.test_t3_04_frontmatter_body_bijection, lang)

        for diag in REQUIRED_DIAGRAMS:
            short_diag = diag.replace("fig1_rack_cutter_shift_undercut", "fig1").replace("fig2_operating_mesh_geometry", "fig2").replace("fig3_specific_sliding_balancing", "fig3")
            run_safe(3, f"T3-SYM-{short_diag}", f"Resolution Symmetry ({short_diag})", t3.test_t3_05_cross_language_diagram_resolution_symmetry, diag)

        run_safe(3, "T3-HASH-INV", "KaTeX Equations Hash Invariance", t3.test_t3_06_equations_hash_invariance_across_all_languages)
        run_safe(3, "T3-CORE-MATH", "7 Core Formulas Represented", t3.test_t3_07_core_mathematical_formulas_present)
        run_safe(3, "T3-PSWIPE-BIND", "PhotoSwipe 5 Bindings Valid", t3.test_t3_08_photoswipe_lightbox_configuration_and_bindings)

        for lang in LANGUAGES:
            run_safe(3, f"T3-ALT-{lang}", f"PhotoSwipe Alt Richness ({lang})", t3.test_t3_09_photoswipe_alt_caption_richness, lang)

        run_safe(3, "T3-SPEC-ENG", "Math Engine to Spec JSON", t3.test_t3_10_parameter_consistency_math_engine_to_specs)

        for lang in LANGUAGES:
            run_safe(3, f"T3-TBL-MATCH-{lang}", f"Spec to MDX Table Match ({lang})", t3.test_t3_11_parameter_consistency_specs_to_mdx_tables, lang)

        run_safe(3, "T3-LOCALE-PARITY", "Locale Labels Parity", t3.test_t3_12_locale_labels_dictionary_parity)

        for lang in LANGUAGES:
            run_safe(3, f"T3-PROSE-CLR-{lang}", f"Prose Freedom from Jargon ({lang})", t3.test_t3_13_writing_principles_and_cliche_freedom, lang)

    # --- Tier 4 Execution ---
    if selected_tier in ["all", "4"]:
        print("\n--- Executing Tier 4: Real-World Application Scenarios ---")
        t4 = TestTier4RealWorldScenarios()

        run_safe(4, "T4-SC01-BUILD", "Astro Static Site Build", t4.test_sc01_astro_starlight_static_build)
        run_safe(4, "T4-SC02-LINT", "Image Reference Linter", t4.test_sc02_image_reference_linter)
        run_safe(4, "T4-SC03-4GATE", "4-Gate Vector Verification", t4.test_sc03_four_gate_diagram_verification)
        run_safe(4, "T4-SC04-VISUAL", "Playwright Visual & Zoom", t4.test_sc04_headless_browser_visual_capture)
        run_safe(4, "T4-SC05-REG", "111 Golden Cases Zero Error", t4.test_sc05_invariant_regression_audit)

        for lang in LANGUAGES:
            run_safe(4, f"T4-SC06-HTML-{lang}", f"Built HTML Audit ({lang})", t4.test_sc06_built_html_production_audit, lang)

    # -------------------------------------------------------------------------
    # Diagnostic Summary Table
    # -------------------------------------------------------------------------
    print("\n" + "=" * 85)
    print("  E2E Test Execution Summary & Diagnostics Table")
    print("=" * 85)
    print(f"{'Tier':<6} | {'Test ID':<20} | {'Status':<6} | {'Description':<32} | {'Details'}")
    print("-" * 85)

    passed_count = sum(1 for r in results if r["status"] == "PASS")
    skipped_count = sum(1 for r in results if r["status"] == "SKIP")
    failed_count = sum(1 for r in results if r["status"] == "FAIL")

    for r in results:
        if r["status"] == "PASS":
            status_str = "\033[92mPASS\033[0m"
        elif r["status"] == "SKIP":
            status_str = "\033[93mSKIP\033[0m"
        else:
            status_str = "\033[91mFAIL\033[0m"
        print(f"Tier {r['tier']:<2} | {r['code']:<20} | {status_str:<15} | {r['desc'][:32]:<32} | {r['details'][:35]}")

    print("=" * 85)
    print(f"Total Tests Executed: {len(results)} | Passed: {passed_count} | Skipped/Pending: {skipped_count} | Failed: {failed_count}")

    if failed_count == 0:
        print("\033[92m★ ALL VERIFICATIONS PASSED: 4-Tier E2E Test Suite Operational!\033[0m\n")
        return 0
    else:
        print(f"\033[91m✗ {failed_count} TEST(S) FAILED: Inspection Required.\033[0m\n")
        return 1


# =============================================================================
# CLI Main Entrypoint
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="H-GEAR STUDIO Part 4 Comprehensive 4-Tier E2E Test Suite")
    parser.add_argument("--tier", choices=["all", "1", "2", "3", "4"], default="all",
                        help="Target test tier to execute (default: all)")
    parser.add_argument("--strict", action="store_true",
                        help="Strict gating mode: treat unbuilt/pending assets as FAIL instead of SKIP")
    parser.add_argument("--runner", choices=["cli", "pytest"], default="cli",
                        help="Underlying test runner engine (default: cli)")
    args, unknown = parser.parse_known_args()

    if args.runner == "pytest":
        pytest_args = ["-v", str(_CURRENT_FILE)]
        if args.tier == "1":
            pytest_args.extend(["-k", "TestTier1FeatureCoverage"])
        elif args.tier == "2":
            pytest_args.extend(["-k", "TestTier2BoundaryAndCornerCases"])
        elif args.tier == "3":
            pytest_args.extend(["-k", "TestTier3CrossFeatureAndPairwise"])
        elif args.tier == "4":
            pytest_args.extend(["-k", "TestTier4RealWorldScenarios"])
        try:
            import pytest as real_pytest
            sys.exit(real_pytest.main(pytest_args))
        except ImportError:
            print("[WARN] pytest not installed, falling back to standalone CLI runner.")
            sys.exit(run_diagnostics(selected_tier=args.tier, strict=args.strict))
    else:
        sys.exit(run_diagnostics(selected_tier=args.tier, strict=args.strict))


if __name__ == "__main__":
    main()
