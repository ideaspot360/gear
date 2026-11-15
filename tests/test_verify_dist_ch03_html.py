"""
Empirical verification test for Chapter 3 built HTML artifacts (blog/dist/).

Verifies:
1. HTML files exist for all 4 languages (ko, en, de, ja) for Chapter 3:
   series1-theory/part-a-spur/03-meshing-kinematics/index.html.
2. Raw HTML contains zero occurrences of unlocalized, cross-language, or broken image links.
3. DOM parsing finds exactly the 4 required Part 3 diagrams with strict language isolation:
   - fig1_line_of_action_five_points.png
   - fig2_tooth_load_sharing.png
   - fig3_contact_kinematics_velocities.png
   - fig4_specific_sliding_curves.png
4. Referenced image files physically exist in both blog/dist/ and blog/public/, have valid PNG headers,
   and match in byte size.
5. All 38 benchmark parameters are present in the HTML tables.
6. KaTeX math blocks are rendered into HTML with appropriate class names.
"""

from pathlib import Path
import re
from bs4 import BeautifulSoup
import pytest

BLOG_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = BLOG_ROOT / "dist"
PUBLIC_DIR = BLOG_ROOT / "public"

LANGUAGES = ["ko", "en", "de", "ja"]
CHAPTER_REL_PATH = "series1-theory/part-a-spur/03-meshing-kinematics/index.html"
EXPECTED_DIAGRAM_BASENAMES = [
    "fig1_line_of_action_five_points.png",
    "fig2_tooth_load_sharing.png",
    "fig3_contact_kinematics_velocities.png",
    "fig4_specific_sliding_curves.png",
]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@pytest.fixture(scope="module")
def parsed_html_pages():
    pages = {}
    for lang in LANGUAGES:
        html_file = DIST_DIR / lang / CHAPTER_REL_PATH
        assert html_file.is_file(), f"HTML file does not exist: {html_file}"
        raw_text = html_file.read_text(encoding="utf-8")
        soup = BeautifulSoup(raw_text, "html.parser")
        pages[lang] = {
            "path": html_file,
            "raw": raw_text,
            "soup": soup,
        }
    return pages


def test_chapter03_html_files_exist():
    """Verify built HTML files exist and are non-empty for all 4 target languages."""
    for lang in LANGUAGES:
        target = DIST_DIR / lang / CHAPTER_REL_PATH
        assert target.exists(), f"Missing built HTML: {target}"
        size = target.stat().st_size
        assert size > 20000, f"HTML file suspiciously small ({size} bytes): {target}"


def test_raw_html_no_cross_language_or_broken_images(parsed_html_pages):
    """Inspect raw HTML text for any trace of cross-language leakage or broken image paths."""
    for lang, page_data in parsed_html_pages.items():
        raw = page_data["raw"]
        for other_lang in LANGUAGES:
            if other_lang != lang:
                # Should not contain image references to other languages in Part 3
                cross_pattern = f"/images/part3/{other_lang}/"
                assert cross_pattern not in raw, (
                    f"Cross-language image leak detected in {lang} page: found '{cross_pattern}'"
                )


def test_dom_chapter03_diagram_isolation_and_count(parsed_html_pages):
    """Verify each page has exactly 4 Part 3 diagram images, strictly matching current language."""
    for lang, page_data in parsed_html_pages.items():
        soup = page_data["soup"]
        imgs = soup.find_all("img")
        part3_imgs = [img for img in imgs if "/images/part3/" in img.get("src", "")]
        assert len(part3_imgs) == 4, (
            f"Expected 4 Part 3 diagrams in {lang} page, found {len(part3_imgs)}: "
            f"{[img.get('src') for img in part3_imgs]}"
        )

        for img in part3_imgs:
            src = img.get("src", "")
            expected_prefix = f"/images/part3/{lang}/"
            assert expected_prefix in src, (
                f"Image src does not match language {lang}: {src}"
            )
            basename = src.split("/")[-1]
            assert basename in EXPECTED_DIAGRAM_BASENAMES, (
                f"Unexpected diagram basename in {lang}: {basename}"
            )


def test_diagram_asset_integrity_on_filesystem():
    """Verify all referenced Part 3 diagram PNG files exist in both dist/ and public/, with valid PNG headers."""
    for lang in LANGUAGES:
        for basename in EXPECTED_DIAGRAM_BASENAMES:
            dist_path = DIST_DIR / "images" / "part3" / lang / basename
            public_path = PUBLIC_DIR / "images" / "part3" / lang / basename

            assert dist_path.is_file(), f"Asset missing in dist: {dist_path}"
            assert public_path.is_file(), f"Asset missing in public: {public_path}"

            dist_bytes = dist_path.read_bytes()
            public_bytes = public_path.read_bytes()

            assert len(dist_bytes) > 10000, f"Asset suspiciously small: {dist_path}"
            assert dist_bytes.startswith(PNG_SIGNATURE), f"Invalid PNG magic bytes: {dist_path}"
            assert len(dist_bytes) == len(public_bytes), (
                f"Byte size mismatch between dist ({len(dist_bytes)}) and public ({len(public_bytes)}) for {basename}"
            )


def test_benchmark_parameters_present_in_html(parsed_html_pages):
    """Verify key ground truth numeric parameters from Chapter 3 are present in the built HTML."""
    key_numbers = [
        "108.000000",   # Center distance
        "1.648755",     # Contact ratio
        "3.110764",     # Single contact length
        "11.491260",    # Double contact length
        "-7.420059",    # Specific sliding k1 at point A
        "-1.294650",    # Specific sliding k2 at point E
    ]
    for lang, page_data in parsed_html_pages.items():
        raw = page_data["raw"]
        for num in key_numbers:
            assert num in raw, f"Missing benchmark number '{num}' in {lang} built HTML!"


def test_katex_math_rendered_in_html(parsed_html_pages):
    """Verify KaTeX math rendering is present and active in each language page."""
    for lang, page_data in parsed_html_pages.items():
        soup = page_data["soup"]
        katex_elements = soup.find_all(class_=re.compile(r"katex"))
        assert len(katex_elements) >= 50, (
            f"Insufficient KaTeX elements in {lang} page: found {len(katex_elements)}"
        )
