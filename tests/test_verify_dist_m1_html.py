"""
Empirical adversarial verification test for Milestone 1:
HTML parsing and asset verification of built Astro Starlight site (blog/dist/).

Verifies:
1. HTML files exist for all 4 languages (ko, en, de, ja) for Series 2 Part 1.
2. Raw HTML contains zero occurrences of legacy or unlocalized image links.
3. DOM parsing finds exactly the 4 required normalized images with strict language isolation.
4. Referenced image files physically exist in both blog/dist/ and blog/public/, have valid PNG headers,
   and match in byte size.
5. Global scan across all HTML files in blog/dist/ confirms zero occurrences of legacy fig1_friction_vs_gear.
"""

from pathlib import Path
import re
from bs4 import BeautifulSoup
import pytest

BLOG_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = BLOG_ROOT / "dist"
PUBLIC_DIR = BLOG_ROOT / "public"

LANGUAGES = ["ko", "en", "de", "ja"]
CHAPTER_REL_PATH = "series2-architecture/part01-diff-geom/01-litvin-kinematics/index.html"
EXPECTED_DIAGRAM_BASENAMES = [
    "fig1a_friction_drive.png",
    "fig1b_gear_drive.png",
    "fig2_willis_law_geometry.png",
    "fig3_contact_velocity_vectors.png",
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


def test_html_files_exist():
    """Verify built HTML files exist for all 4 target languages."""
    for lang in LANGUAGES:
        target = DIST_DIR / lang / CHAPTER_REL_PATH
        assert target.exists(), f"Missing built HTML: {target}"
        assert target.stat().st_size > 0, f"HTML file is empty: {target}"


def test_raw_html_no_legacy_image_references(parsed_html_pages):
    """Aggressively inspect raw HTML text for any trace of legacy or unlocalized paths."""
    legacy_patterns = [
        "fig1_friction_vs_gear",
        "/images/part1/fig1.png",
        "/images/part1/fig2.png",
        "/images/part1/fig3.png",
    ]
    # Regex for /images/part1/fig without a language directory
    unlocalized_regex = re.compile(r"/images/part1/fig\d")

    for lang, data in parsed_html_pages.items():
        raw = data["raw"]
        for pat in legacy_patterns:
            matches = [m.start() for m in re.finditer(re.escape(pat), raw)]
            assert len(matches) == 0, (
                f"[{lang}] Legacy pattern '{pat}' detected in raw HTML at positions {matches}"
            )

        unlocalized_matches = unlocalized_regex.findall(raw)
        assert len(unlocalized_matches) == 0, (
            f"[{lang}] Unlocalized image reference detected: {unlocalized_matches}"
        )


def test_html_dom_images_language_isolation(parsed_html_pages):
    """Parse DOM <img> tags, check count, ordering, and strict language isolation."""
    for lang, data in parsed_html_pages.items():
        soup = data["soup"]
        # Find all <img> tags that reference /images/part1
        imgs = soup.find_all("img")
        part1_imgs = [img for img in imgs if "/images/part1" in (img.get("src") or "")]

        assert len(part1_imgs) == 4, (
            f"[{lang}] Expected exactly 4 part1 images, found {len(part1_imgs)}: "
            f"{[img.get('src') for img in part1_imgs]}"
        )

        for i, img in enumerate(part1_imgs):
            src = img.get("src", "")
            alt = img.get("alt", "")

            # Verify basename matches expected sequence
            expected_base = EXPECTED_DIAGRAM_BASENAMES[i]
            assert src.endswith(expected_base), (
                f"[{lang}] Image index {i} mismatch: expected ending '{expected_base}', got '{src}'"
            )

            # Strict language directory verification
            expected_prefix = f"/images/part1/{lang}/"
            assert expected_prefix in src, (
                f"[{lang}] Image src '{src}' does not belong to language '{lang}'"
            )

            # Ensure NO other language directory is present in the path
            for other_lang in LANGUAGES:
                if other_lang != lang:
                    assert f"/images/part1/{other_lang}/" not in src, (
                        f"[{lang}] Cross-language contamination! Found '{other_lang}' in src '{src}'"
                    )

            # Alt text verification
            assert alt.strip(), f"[{lang}] Image {src} has empty alt text"
            assert "[object Object]" not in alt, f"[{lang}] Alt text contains JS artifact: '{alt}'"
            assert "undefined" not in alt, f"[{lang}] Alt text contains 'undefined': '{alt}'"


def test_physical_image_files_exist_and_valid(parsed_html_pages):
    """Verify that every <img> src resolves to a physically existing, valid PNG in both dist/ and public/."""
    for lang, data in parsed_html_pages.items():
        soup = data["soup"]
        part1_imgs = [img for img in soup.find_all("img") if "/images/part1" in (img.get("src") or "")]

        for img in part1_imgs:
            src = img.get("src")
            clean_rel = src.lstrip("/")

            dist_path = DIST_DIR / clean_rel
            public_path = PUBLIC_DIR / clean_rel

            # 1. Check in dist/
            assert dist_path.exists(), f"Image referenced in HTML missing from dist: {dist_path}"
            assert dist_path.is_file(), f"Dist asset is not a regular file: {dist_path}"
            dist_size = dist_path.stat().st_size
            assert dist_size > 1000, f"Dist asset suspiciously small ({dist_size} bytes): {dist_path}"

            # Validate PNG header in dist
            with open(dist_path, "rb") as f:
                header = f.read(8)
                assert header == PNG_SIGNATURE, (
                    f"Dist asset {dist_path} has invalid PNG header: {header!r}"
                )

            # 2. Check in public/
            assert public_path.exists(), f"Source image missing from public: {public_path}"
            assert public_path.is_file(), f"Public asset is not a regular file: {public_path}"
            public_size = public_path.stat().st_size
            assert public_size > 1000, f"Public asset suspiciously small ({public_size} bytes): {public_path}"

            # Validate PNG header in public
            with open(public_path, "rb") as f:
                header = f.read(8)
                assert header == PNG_SIGNATURE, (
                    f"Public asset {public_path} has invalid PNG header: {header!r}"
                )

            # 3. Check byte consistency between dist and public
            assert dist_size == public_size, (
                f"Size mismatch between dist ({dist_size} B) and public ({public_size} B) for {clean_rel}"
            )


def test_global_dist_no_legacy_fig1_friction_vs_gear():
    """Scan ALL HTML files in blog/dist/ to ensure fig1_friction_vs_gear is completely purged."""
    html_files = list(DIST_DIR.rglob("*.html"))
    assert len(html_files) > 0, "No HTML files found in dist directory!"

    offending_files = []
    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8")
        if "fig1_friction_vs_gear" in content:
            offending_files.append(str(html_file.relative_to(DIST_DIR)))

    assert len(offending_files) == 0, (
        f"Legacy reference 'fig1_friction_vs_gear' found in {len(offending_files)} dist HTML files: {offending_files}"
    )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
