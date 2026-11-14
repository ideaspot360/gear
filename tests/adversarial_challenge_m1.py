#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial Verification Suite for Milestone 1 (Series 2 Chapter 1 Image Normalization)
Created by Challenger 1 (critic, specialist).
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set

# Set workspace root and blog root
BLOG_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = BLOG_ROOT / "src" / "content" / "docs"
PUBLIC_ROOT = BLOG_ROOT / "public"
DIST_ROOT = BLOG_ROOT / "dist"

LANGUAGES = ["ko", "en", "de", "ja"]
M1_REL_PATH = Path("series2-architecture") / "part01-diff-geom" / "01-litvin-kinematics.mdx"
EXPECTED_M1_DIAGRAMS = [
    "fig1a_friction_drive",
    "fig1b_gear_drive",
    "fig2_willis_law_geometry",
    "fig3_contact_velocity_vectors"
]

class AdversarialReport:
    def __init__(self):
        self.tests_run = 0
        self.tests_failed = 0
        self.errors = []
        self.warnings = []
        self.details = []

    def log(self, msg: str):
        print(msg)
        self.details.append(msg)

    def fail(self, test_name: str, msg: str):
        self.tests_failed += 1
        err_msg = f"[FAIL] {test_name}: {msg}"
        self.errors.append(err_msg)
        print(err_msg)

    def warn(self, test_name: str, msg: str):
        warn_msg = f"[WARN] {test_name}: {msg}"
        self.warnings.append(warn_msg)
        print(warn_msg)

    def success(self, test_name: str, msg: str):
        print(f"[PASS] {test_name}: {msg}")


def test_1_residual_deprecated_assets(report: AdversarialReport):
    """Test 1: Global scan for deprecated asset name 'fig1_friction_vs_gear' in all MDX files."""
    report.tests_run += 1
    test_name = "T1_Residual_fig1_friction_vs_gear"
    all_mdx = list(DOCS_ROOT.rglob("*.mdx"))
    found_occurrences = []

    for mdx_file in all_mdx:
        content = mdx_file.read_text(encoding="utf-8")
        for idx, line in enumerate(content.splitlines(), start=1):
            if "fig1_friction_vs_gear" in line:
                found_occurrences.append((mdx_file, idx, line.strip()))

    if found_occurrences:
        for f, idx, line in found_occurrences:
            report.fail(test_name, f"Found deprecated reference in {f.relative_to(DOCS_ROOT)}:{idx}: {line}")
    else:
        report.success(test_name, f"Zero occurrences of 'fig1_friction_vs_gear' found across {len(all_mdx)} MDX documents.")


def extract_images_from_mdx(content: str) -> List[Tuple[int, str, str]]:
    """Extract (line_num, alt, url) from MDX."""
    results = []
    lines = content.splitlines()
    md_img_re = re.compile(r"!\[(.*?)\]\((.*?)\)")
    html_img_re = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')

    for idx, line in enumerate(lines, start=1):
        for m in md_img_re.finditer(line):
            raw_url = m.group(2).strip().split()[0].strip('"\'>')
            results.append((idx, m.group(1), raw_url))
        for m in html_img_re.finditer(line):
            raw_url = m.group(1).strip()
            results.append((idx, "html_img", raw_url))
    return results


def test_2_language_isolation_and_root_paths(report: AdversarialReport):
    """Test 2: Check all image links across all MDX documents for language isolation and root paths."""
    report.tests_run += 1
    test_name = "T2_Language_Isolation_And_Root_Paths"
    all_mdx = list(DOCS_ROOT.rglob("*.mdx"))
    total_images = 0
    violations = []

    for mdx_file in all_mdx:
        rel = mdx_file.relative_to(DOCS_ROOT)
        doc_lang = rel.parts[0]
        if doc_lang not in LANGUAGES:
            continue

        content = mdx_file.read_text(encoding="utf-8")
        images = extract_images_from_mdx(content)
        total_images += len(images)

        for line_num, alt, url in images:
            # Check 1: Cross-language leaks
            other_langs = [l for l in LANGUAGES if l != doc_lang]
            for ol in other_langs:
                if f"/{ol}/" in url:
                    violations.append((mdx_file, line_num, f"Cross-language leak ({doc_lang} references {ol}): {url}"))

            # Check 2: Unlocalized root paths (e.g. /images/part1/fig... without lang)
            if re.search(r"/images/(part\d+|series\d+)/fig", url):
                if f"/{doc_lang}/" not in url:
                    violations.append((mdx_file, line_num, f"Unlocalized root path without /{doc_lang}/: {url}"))

    if violations:
        for f, idx, msg in violations:
            report.fail(test_name, f"{f.relative_to(DOCS_ROOT)}:{idx} {msg}")
    else:
        report.success(test_name, f"All {total_images} image references in {len(all_mdx)} MDX documents satisfy language isolation and localization.")


def test_3_m1_series2_ch1_parity(report: AdversarialReport):
    """Test 3: Deep check of Series 2 Chapter 1 across all 4 languages."""
    report.tests_run += 1
    test_name = "T3_Series2_Ch1_Parity"
    lang_refs = {}

    for lang in LANGUAGES:
        m1_file = DOCS_ROOT / lang / M1_REL_PATH
        if not m1_file.exists():
            report.fail(test_name, f"Missing file: {m1_file}")
            return

        content = m1_file.read_text(encoding="utf-8")
        images = extract_images_from_mdx(content)
        lang_refs[lang] = images

        # Check frontmatter required_diagrams
        fm_match = re.search(r"required_diagrams:\s*\n((?:\s*-\s*[^\n]+\n)+)", content)
        if not fm_match:
            report.fail(test_name, f"No required_diagrams in frontmatter of {m1_file}")
        else:
            fm_raw = fm_match.group(1)
            diagram_keys = [re.sub(r'["\']', '', k.strip().lstrip("-").strip()) for k in fm_raw.splitlines() if k.strip()]
            if diagram_keys != EXPECTED_M1_DIAGRAMS:
                report.fail(test_name, f"Frontmatter required_diagrams mismatch in {lang}: {diagram_keys} != {EXPECTED_M1_DIAGRAMS}")
            else:
                report.log(f"  [{lang}] Frontmatter required_diagrams: {diagram_keys} (MATCH)")

    # Compare count and sequence
    counts = {lang: len(refs) for lang, refs in lang_refs.items()}
    if len(set(counts.values())) > 1:
        report.fail(test_name, f"Image count mismatch between languages: {counts}")
    else:
        expected_count = len(EXPECTED_M1_DIAGRAMS)
        actual_count = list(counts.values())[0]
        if actual_count != expected_count:
            report.fail(test_name, f"Expected {expected_count} images per language, got {actual_count}")
        else:
            # Check stems
            for lang, refs in lang_refs.items():
                stems = [Path(r[2]).stem for r in refs]
                if stems != EXPECTED_M1_DIAGRAMS:
                    report.fail(test_name, f"Diagram stem sequence mismatch in {lang}: {stems} != {EXPECTED_M1_DIAGRAMS}")
                else:
                    report.log(f"  [{lang}] Body image stems sequence: {stems} (MATCH)")

            # Check precise URLs
            for lang, refs in lang_refs.items():
                for idx, (l_no, alt, url) in enumerate(refs):
                    expected_stem = EXPECTED_M1_DIAGRAMS[idx]
                    expected_url = f"/images/part1/{lang}/{expected_stem}.png"
                    if url != expected_url:
                        report.fail(test_name, f"Exact URL mismatch in {lang}:{l_no}: expected '{expected_url}', got '{url}'")

    if report.tests_failed == 0:
        report.success(test_name, "Series 2 Chapter 1 has 100% identical image structure, naming, and frontmatter parity across all 4 languages.")


def test_4_physical_asset_integrity(report: AdversarialReport):
    """Test 4: Verify physical image files exist, have size > 10KB, and valid PNG headers."""
    report.tests_run += 1
    test_name = "T4_Physical_Asset_Integrity"
    all_mdx = list(DOCS_ROOT.rglob("*.mdx"))
    verified_files = set()
    failed = False

    for mdx_file in all_mdx:
        content = mdx_file.read_text(encoding="utf-8")
        images = extract_images_from_mdx(content)
        for line_num, alt, url in images:
            if not url.startswith("/images/"):
                continue
            rel_asset = url.lstrip("/")
            physical = PUBLIC_ROOT / rel_asset.replace("/", os.sep)

            if physical in verified_files:
                continue
            verified_files.add(physical)

            if not physical.exists():
                report.fail(test_name, f"Physical file does not exist: {physical} (from {mdx_file.name}:{line_num})")
                failed = True
                continue

            size = physical.stat().st_size
            if size == 0:
                report.fail(test_name, f"File is EMPTY (0 bytes): {physical}")
                failed = True
            elif size < 10 * 1024:
                report.fail(test_name, f"File is suspiciously small (<10KB): {size} bytes: {physical}")
                failed = True

            # If PNG, verify magic number
            if physical.suffix.lower() == ".png":
                with open(physical, "rb") as f:
                    magic = f.read(8)
                if magic != b"\x89PNG\r\n\x1a\n":
                    report.fail(test_name, f"Invalid PNG magic bytes: {physical}")
                    failed = True

            # If SVG, verify XML/svg start
            if physical.suffix.lower() == ".svg":
                txt = physical.read_text(encoding="utf-8", errors="ignore")
                if "<svg" not in txt:
                    report.fail(test_name, f"Invalid SVG file (no <svg tag): {physical}")
                    failed = True

            report.log(f"  Verified asset: {rel_asset} ({size:,} bytes) - OK")

    if not failed:
        report.success(test_name, f"All {len(verified_files)} referenced physical assets exist, valid magic bytes, and size > 10KB.")


def test_5_m1_rendered_html_inspection(report: AdversarialReport):
    """Test 5: Inspect built HTML in blog/dist for Series 2 Chapter 1 to verify correct rendering."""
    report.tests_run += 1
    test_name = "T5_Rendered_HTML_Inspection"

    if not DIST_ROOT.exists():
        report.warn(test_name, f"dist directory does not exist at {DIST_ROOT}. Run build first.")
        return

    for lang in LANGUAGES:
        # Route in starlight: dist/{lang}/series2-architecture/part01-diff-geom/01-litvin-kinematics/index.html
        html_file = DIST_ROOT / lang / "series2-architecture" / "part01-diff-geom" / "01-litvin-kinematics" / "index.html"
        if not html_file.exists():
            report.fail(test_name, f"Built HTML file not found: {html_file}")
            continue

        html_content = html_file.read_text(encoding="utf-8")

        # Check for deprecated image in HTML
        if "fig1_friction_vs_gear" in html_content:
            report.fail(test_name, f"Deprecated asset found in built HTML: {html_file}")

        # Check that all 4 expected images are rendered in <img> tags
        for stem in EXPECTED_M1_DIAGRAMS:
            expected_src = f"/images/part1/{lang}/{stem}.png"
            if expected_src not in html_content:
                report.fail(test_name, f"Expected image src '{expected_src}' not found in built HTML: {html_file}")
            else:
                report.log(f"  [{lang} HTML] Found rendered src: {expected_src}")

    if report.tests_failed == 0:
        report.success(test_name, "All 4 language HTML outputs render correct normalized images without legacy artifacts.")


def run_all_adversarial_tests():
    print("=" * 70)
    print("STARTING ADVERSARIAL CHALLENGER VERIFICATION (MILESTONE 1)")
    print("=" * 70)

    report = AdversarialReport()

    test_1_residual_deprecated_assets(report)
    test_2_language_isolation_and_root_paths(report)
    test_3_m1_series2_ch1_parity(report)
    test_4_physical_asset_integrity(report)
    test_5_m1_rendered_html_inspection(report)

    print("=" * 70)
    print("ADVERSARIAL VERIFICATION SUMMARY")
    print(f"Total Tests Run   : {report.tests_run}")
    print(f"Total Tests Failed : {report.tests_failed}")
    print(f"Total Warnings     : {len(report.warnings)}")
    print("=" * 70)

    if report.tests_failed > 0:
        print("VERDICT: REJECT")
        for err in report.errors:
            print(f"  {err}")
        return 1
    else:
        print("VERDICT: APPROVE")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_adversarial_tests())
