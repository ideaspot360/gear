"""
test_chapter03_mdx.py
================================================================================
Comprehensive Verification Suite for Series 1 Part A Chapter 3 MDX Documents:
  - 4 Languages: ko, en, de, ja
  - File Existence & Character Length
  - Frontmatter Structure (title, description, series, part, chapter, equations_hash, required_diagrams)
  - Frontmatter <-> Body Image Bijection & Language Isolation
  - KaTeX Display Math Blocks Invariance (30 blocks, exact SHA-256 match)
  - Section Completeness (Sections 3.1 to 3.7 in all 4 languages)
  - 38-Parameter Closed-Form Benchmark Table (38 rows with exact physical constants)
  - Writing Principles: Zero Code/UI terms, Zero AI clichés, 100% Engineering Voice
================================================================================
"""

import re
import hashlib
from pathlib import Path
import pytest

DOCS_DIR = Path("blog/src/content/docs")
PUBLIC_DIR = Path("blog/public")
LANGUAGES = ["ko", "en", "de", "ja"]
REQUIRED_DIAGRAMS = [
    "fig1_line_of_action_five_points",
    "fig2_tooth_load_sharing",
    "fig3_contact_kinematics_velocities",
    "fig4_specific_sliding_curves",
]

EXPECTED_SECTIONS = [
    "3.1",
    "3.2",
    "3.3",
    "3.4",
    "3.5",
    "3.6",
    "3.7",
]


def get_mdx_path(lang: str) -> Path:
    return DOCS_DIR / lang / "series1-theory" / "part-a-spur" / "03-meshing-kinematics.mdx"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_mdx_file_existence_and_length(lang):
    """Verify that MDX files exist and have substantial engineering content (>10,000 characters)."""
    mdx_path = get_mdx_path(lang)
    assert mdx_path.is_file(), f"MDX file does not exist: {mdx_path}"
    content = mdx_path.read_text(encoding="utf-8")
    assert len(content) > 10000, f"MDX file {mdx_path} too short: {len(content)} characters"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_frontmatter_metadata(lang):
    """Verify frontmatter fields: series, part, chapter, equations_hash, required_diagrams."""
    content = get_mdx_path(lang).read_text(encoding="utf-8")
    assert content.startswith("---"), f"{lang}: Frontmatter must start with ---"
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert fm_match is not None, f"{lang}: Frontmatter closing --- not found"
    fm_text = fm_match.group(1)

    assert "series: theory" in fm_text, f"{lang}: Missing or invalid series"
    assert "part: 1" in fm_text, f"{lang}: Missing or invalid part"
    assert "chapter: 3" in fm_text, f"{lang}: Missing or invalid chapter"
    assert "equations_hash:" in fm_text, f"{lang}: Missing equations_hash"

    # Verify required_diagrams list
    for diag in REQUIRED_DIAGRAMS:
        assert diag in fm_text, f"{lang}: Missing {diag} in frontmatter required_diagrams"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_diagram_references_and_language_isolation(lang):
    """Verify that each diagram is referenced via /images/part3/{lang}/... and image file exists."""
    content = get_mdx_path(lang).read_text(encoding="utf-8")

    # Verify all required diagrams are referenced in body
    for diag in REQUIRED_DIAGRAMS:
        expected_ref = f"/images/part3/{lang}/{diag}.png"
        assert expected_ref in content, f"{lang}: Missing reference to {expected_ref}"

        physical_file = PUBLIC_DIR / "images" / "part3" / lang / f"{diag}.png"
        assert physical_file.is_file(), f"Physical image file does not exist: {physical_file}"
        assert physical_file.stat().st_size >= 20 * 1024, f"Image file too small: {physical_file}"

    # Verify language isolation (no other language folder referenced)
    for other_lang in LANGUAGES:
        if other_lang != lang:
            assert f"/images/part3/{other_lang}/" not in content, (
                f"{lang}: Leaked image reference from {other_lang}!"
            )


def test_equations_invariance_across_all_languages():
    """Verify that all 4 languages have exactly 30 KaTeX display blocks and identical SHA-256 hash."""
    hashes = {}
    block_counts = {}

    for lang in LANGUAGES:
        content = get_mdx_path(lang).read_text(encoding="utf-8")
        display_blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
        block_counts[lang] = len(display_blocks)

        normalized = "\n---\n".join(b.strip() for b in display_blocks)
        eq_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        hashes[lang] = eq_hash

        # Check hash against frontmatter equations_hash
        fm_hash_match = re.search(r'equations_hash:\s*"?([a-f0-9]{64})"?', content)
        assert fm_hash_match is not None, f"{lang}: equations_hash not found in frontmatter"
        assert fm_hash_match.group(1) == eq_hash, (
            f"{lang}: Frontmatter hash {fm_hash_match.group(1)} does not match computed hash {eq_hash}"
        )

    # Assert exactly 30 display math blocks in all 4
    for lang, count in block_counts.items():
        assert count == 30, f"{lang}: Expected 30 display blocks, got {count}"

    # Assert all 4 hashes are equal
    unique_hashes = set(hashes.values())
    assert len(unique_hashes) == 1, f"Hash divergence between languages: {hashes}"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_section_completeness(lang):
    """Verify all sections 3.1 through 3.7 are present as level-2 headings."""
    content = get_mdx_path(lang).read_text(encoding="utf-8")
    for sec in EXPECTED_SECTIONS:
        pattern = rf"^## {sec}\b"
        assert re.search(pattern, content, re.MULTILINE) is not None, (
            f"{lang}: Missing section heading ## {sec}"
        )


@pytest.mark.parametrize("lang", LANGUAGES)
def test_38_parameter_benchmark_table(lang):
    """Verify the 38-parameter closed-form benchmark table contains 38 rows and key parameters."""
    content = get_mdx_path(lang).read_text(encoding="utf-8")

    # Find table rows with numbering 1 to 38
    numbered_rows = re.findall(r"\|\s*(\d{1,2})\s*\|", content)
    int_rows = [int(r) for r in numbered_rows]
    # Check that 1 through 38 are all present
    expected_row_indices = list(range(1, 39))
    for expected_idx in expected_row_indices:
        assert expected_idx in int_rows, (
            f"{lang}: Row {expected_idx} missing in 38-parameter benchmark table"
        )

    # Spot-check key engineering values
    assert "108.000000" in content, f"{lang}: Missing center distance 108.000000"
    assert "14.602024" in content, f"{lang}: Missing contact length 14.602024"
    assert "1.648755" in content, f"{lang}: Missing contact ratio 1.648755"
    assert "8.856394" in content, f"{lang}: Missing base pitch 8.856394"
    assert "-7.420059" in content, f"{lang}: Missing pinion tip sliding ratio -7.420059"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_writing_principles_zero_code_and_zero_ui(lang):
    """Verify that there are no programming language or UI terms used in engineering prose."""
    content = get_mdx_path(lang).read_text(encoding="utf-8")

    # UI terms forbidden
    ui_terms = ["클릭", "드롭다운", "모달창", "팝업창", "다이얼로그", "UI 뷰어"]
    for term in ui_terms:
        assert term not in content, f"{lang}: Prohibited UI term '{term}' found in MDX"

    # Code terms forbidden in technical prose
    code_terms = ["def ", "class Gear", "import numpy", "function(", "console.log"]
    for term in code_terms:
        assert term not in content, f"{lang}: Prohibited code snippet '{term}' found in MDX"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_article_12_no_ai_cliches(lang):
    """Verify Constitutional Article 12: Zero AI clichés in any language."""
    content = get_mdx_path(lang).read_text(encoding="utf-8")

    cliches = {
        "ko": [
            "이 글에서는",
            "알아보겠습니다",
            "살펴보았습니다",
            "결론적으로,",
            "요약하자면,",
            "흥미로운 사실은",
        ],
        "en": [
            "in this article, we will",
            "let's delve into",
            "in conclusion,",
            "to summarize,",
            "interestingly enough",
        ],
        "de": [
            "in diesem artikel werden wir",
            "zusammenfassend lässt sich sagen",
            "interessanterweise",
        ],
        "ja": [
            "この記事では",
            "見ていきましょう",
            "結論として、",
            "要約すると、",
            "興味深いことに",
        ],
    }

    for phrase in cliches[lang]:
        assert phrase.lower() not in content.lower(), (
            f"{lang}: Banned AI cliché '{phrase}' found in document!"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
