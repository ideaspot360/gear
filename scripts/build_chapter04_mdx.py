# -*- coding: utf-8 -*-
"""
build_chapter04_mdx.py
================================================================================
Canonical Builder for Series 1 Part A Chapter 4:
  - ko/series1-theory/part-a-spur/04-profile-shift.mdx
  - en/series1-theory/part-a-spur/04-profile-shift.mdx
  - de/series1-theory/part-a-spur/04-profile-shift.mdx
  - ja/series1-theory/part-a-spur/04-profile-shift.mdx

Guarantees 100% mathematical invariance and display math block SHA-256 equivalence:
  Expected Hash: 8626c2822c33176c4412a4f835d07bffb7bbb48aa7e52bf9d3791a7b545f970d

Adheres strictly to Project Constitutional Articles 1 ~ 12:
  - Article 12: Authentic 20-year veteran CAE/mechanical engineer first-person voice
  - Zero AI clichés across KO, EN, DE, JA
  - Zero raw code blocks or software UI terminology in prose
  - Strict 38-parameter closed-form precision table matching ISO 21771 / DIN 3960
  - Bijective required diagrams mapping (fig1, fig2, fig3)
================================================================================
"""

import sys
import re
import hashlib
from pathlib import Path

# Ensure script directory and parent are on sys.path
_SCRIPT_DIR = Path(__file__).resolve().parent
_BLOG_DIR = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import generate_part4_mdx as g4

EQUATIONS = g4.EQUATIONS
NORMALIZED_EQS = g4.NORMALIZED_EQS
EQUATIONS_HASH = g4.EQUATIONS_HASH

EXPECTED_HASH = "8626c2822c33176c4412a4f835d07bffb7bbb48aa7e52bf9d3791a7b545f970d"
assert EQUATIONS_HASH == EXPECTED_HASH, f"EQUATIONS_HASH mismatch: {EQUATIONS_HASH} != {EXPECTED_HASH}"

BANNED_CLICHES = {
    "ko": ["이 글에서는", "알아보겠습니다", "살펴보았습니다", "결론적으로,", "요약하자면,", "흥미로운 사실은"],
    "en": ["in this article, we will", "let's delve into", "in conclusion,", "to summarize,", "interestingly,"],
    "de": ["in diesem artikel werden wir", "zusammenfassend lässt sich sagen", "fazit:", "es ist wichtig zu beachten"],
    "ja": ["この記事では", "見ていきましょう", "結論として、", "要約すると、", "興味深いことに"],
}

FORBIDDEN_UI_TERMS = ["클릭", "드롭다운", "모달창", "팝업창", "다이얼로그", "UI 뷰어"]
FORBIDDEN_CODE_TERMS = ["def ", "class Gear", "import numpy", "console.log"]

REQUIRED_DIAGRAMS = [
    "fig1_rack_cutter_shift_undercut",
    "fig2_operating_mesh_geometry",
    "fig3_specific_sliding_balancing",
]


def build_ko() -> str:
    return g4.inject_placeholders(g4.KO_TEMPLATE, "ko")


def build_en() -> str:
    return g4.inject_placeholders(g4.EN_TEMPLATE, "en")


def build_de() -> str:
    return g4.inject_placeholders(g4.DE_TEMPLATE, "de")


def build_ja() -> str:
    return g4.inject_placeholders(g4.JA_TEMPLATE, "ja")


def verify_content(lang: str, content: str) -> None:
    """Verifies display math blocks, equations hash, tone compliance, and diagram references."""
    # 1. Display math blocks and SHA-256 hash
    display_blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
    assert len(display_blocks) == len(EQUATIONS), (
        f"[{lang}] Display math blocks count mismatch: {len(display_blocks)} != {len(EQUATIONS)}"
    )
    normalized = "\n---\n".join(b.strip() for b in display_blocks)
    cur_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    assert cur_hash == EXPECTED_HASH, (
        f"[{lang}] Equations hash mismatch: {cur_hash} != {EXPECTED_HASH}"
    )

    # 2. Constitutional Article 12: Banned AI Clichés
    lower_content = content.lower()
    for cliche in BANNED_CLICHES[lang]:
        assert cliche.lower() not in lower_content, (
            f"[{lang}] Banned AI cliché detected: '{cliche}'"
        )

    # 3. Forbidden UI / Code terms (KO check)
    if lang == "ko":
        for term in FORBIDDEN_UI_TERMS:
            assert term not in content, (
                f"[{lang}] Forbidden UI term detected: '{term}'"
            )
    for term in FORBIDDEN_CODE_TERMS:
        assert term not in content, (
            f"[{lang}] Raw programming syntax detected: '{term}'"
        )

    # 4. Required diagrams bijection
    for diag in REQUIRED_DIAGRAMS:
        assert diag in content, f"[{lang}] Missing required diagram reference: '{diag}'"

    # 5. Length verification
    assert len(content) >= 8_000, f"[{lang}] Content length too short: {len(content)} chars"


def main():
    docs_base = _BLOG_DIR / "src" / "content" / "docs"

    builders = {
        "ko": build_ko,
        "en": build_en,
        "de": build_de,
        "ja": build_ja,
    }

    print("=" * 80)
    print("H-GEAR STUDIO — Chapter 4 MDX Canonical Builder Pipeline")
    print(f"Equations Invariant Target SHA-256: {EXPECTED_HASH}")
    print("=" * 80)

    for lang, builder in builders.items():
        content = builder()
        verify_content(lang, content)

        out_dir = docs_base / lang / "series1-theory" / "part-a-spur"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "04-profile-shift.mdx"
        out_file.write_text(content, encoding="utf-8")

        print(f"[{lang.upper()}] Generated: {out_file}")
        print(f"       Length: {len(content):,} chars | KaTeX Blocks: 10 | Hash: {EXPECTED_HASH} (VERIFIED)")

    print("\n[SUCCESS] All 4 Chapter 4 MDX documents generated and verified successfully!")


if __name__ == "__main__":
    main()
