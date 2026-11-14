#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H-GEAR STUDIO Blog - 다국어 이미지 참조 무결성 자동 검증 하네스 (Linter)
Lint Multi-Language Image References in MDX Documents.

5대 검증 규칙 (Linter Rules):
  - Rule L1 (언어간 1:1 대응 무결성, Parity):
      동일 문서의 ko, en, de, ja 버전 간 이미지 태그 개수 및 정규화 도안 식별자 1:1 일치.
  - Rule L2 (언어 격리 무결성, Language Isolation):
      {lang} 디렉토리 내의 MDX 파일은 오직 /images/.../{lang}/ 하위의 이미지만 참조.
      타 언어 경로 혼재 및 루트 비격리 경로(/images/part1/xxx.png) 차단.
  - Rule L3 (물리 파일 실재성, Asset Existence & Minimum Size):
      MDX에 기재된 모든 이미지 경로가 blog/public/ 상의 실재 파일로 매핑되어야 함.
      파일 크기가 20 KB 이상이어야 함 (더미/빈 파일 차단).
  - Rule L4 (폐기 에셋 참조 금지, Deprecated Asset Ban):
      구버전 마찰차 도안 (fig1_friction_vs_gear.png 등) 및 폐기 에셋 참조 시 즉각 에러.
  - Rule L5 (프론트매터-본문 바이제션, Frontmatter Bijection):
      프론트매터에 required_diagrams / diagrams 목록이 명시된 경우 본문 이미지와 1:1 일치 검증.

종료 코드:
  - 위반 0건: sys.exit(0)
  - 위반 1건 이상: sys.exit(1)
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Set


SUPPORTED_LANGUAGES = ["ko", "en", "de", "ja"]
MIN_ASSET_SIZE_BYTES = 20 * 1024  # 20 KB

DEPRECATED_ASSET_NAMES = {
    "fig1_friction_vs_gear.png",
    "fig1_friction_vs_gear.svg",
}


class LintViolation:
    def __init__(self, rule: str, file_path: Path, line_number: int, message: str, url: str = ""):
        self.rule = rule
        self.file_path = file_path
        self.line_number = line_number
        self.message = message
        self.url = url

    def __str__(self) -> str:
        loc = f"{self.file_path}:{self.line_number}" if self.line_number > 0 else str(self.file_path)
        return f"[ERROR] {loc} [{self.rule}] {self.message}"


class ImageReference:
    def __init__(self, raw_url: str, line_number: int, doc_lang: str, file_path: Path):
        self.raw_url = raw_url
        self.line_number = line_number
        self.doc_lang = doc_lang
        self.file_path = file_path

    @property
    def clean_url(self) -> str:
        # Strip query parameters or hash anchors
        url = self.raw_url.split("?")[0].split("#")[0].strip()
        return url

    @property
    def filename(self) -> str:
        return Path(self.clean_url).name

    def normalized_id(self) -> str:
        """언어 태그를 {lang} 플레이스홀더로 정규화한 고유 식별자 반환"""
        clean = self.clean_url
        for lang in SUPPORTED_LANGUAGES:
            clean = re.sub(rf"/{lang}/", "/{lang}/", clean)
        return clean


def extract_frontmatter(content: str) -> Tuple[Optional[str], str, int]:
    """YAML 프론트매터 블록(있는 경우), 본문 텍스트, 프론트매터 끝 라인 번호 반환"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body_text = parts[2]
            fm_lines = fm_text.count("\n") + 2
            return fm_text, body_text, fm_lines
    return None, content, 0


def parse_frontmatter_diagrams(fm_text: str) -> List[str]:
    """프론트매터 내 required_diagrams 또는 diagrams 목록 추출"""
    diagrams = []
    lines = fm_text.splitlines()
    in_diagram_block = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^(required_diagrams|diagrams|images)\s*:\s*$", stripped):
            in_diagram_block = True
            continue
        if in_diagram_block:
            if stripped.startswith("-"):
                val = stripped.lstrip("-").strip().strip('"').strip("'")
                if val:
                    diagrams.append(val)
            elif re.match(r"^[a-zA-Z0-9_-]+\s*:", stripped):
                # 새로운 키 시작 시 블록 종료
                in_diagram_block = False
    return diagrams


def extract_image_references(content: str, doc_lang: str, file_path: Path) -> List[ImageReference]:
    """MDX 본문에서 마크다운 및 HTML 이미지 참조 추출 (라인 번호 포함)"""
    refs: List[ImageReference] = []
    lines = content.splitlines()
    md_pattern = re.compile(r"!\[.*?\]\((.*?)\)")
    html_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')

    for line_idx, line in enumerate(lines, start=1):
        # 1. Markdown 이미지 문법 ![alt](url)
        for match in md_pattern.finditer(line):
            url = match.group(1).strip()
            # 마크다운 타이틀 "..." 제거
            url = url.split()[0].strip('"\'>')
            refs.append(ImageReference(url, line_idx, doc_lang, file_path))

        # 2. HTML <img> 태그
        for match in html_pattern.finditer(line):
            url = match.group(1).strip()
            refs.append(ImageReference(url, line_idx, doc_lang, file_path))

    return refs


def resolve_physical_path(url: str, public_dir: Path, file_path: Path) -> Path:
    """웹 URL 경로를 로컬 blog/public/ 물리 파일 경로로 변환"""
    clean_url = url.split("?")[0].split("#")[0].strip()
    if clean_url.startswith("/"):
        # 절대 웹 경로: /images/... -> public_dir / images/...
        rel = clean_url.lstrip("/")
        return public_dir / rel
    else:
        # 상대 웹 경로인 경우 MDX 파일 기준
        return (file_path.parent / clean_url).resolve()


def lint_document(
    file_path: Path,
    doc_lang: str,
    public_dir: Path,
    verbose: bool = False
) -> Tuple[List[ImageReference], List[LintViolation]]:
    """단일 MDX 문서에 대해 Rule L2, L3, L4, L5 감사 수행"""
    violations: List[LintViolation] = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        violations.append(LintViolation("IO_ERROR", file_path, 0, f"Failed to read file: {e}"))
        return [], violations

    fm_text, body_text, fm_offset = extract_frontmatter(content)
    refs = extract_image_references(content, doc_lang, file_path)

    for ref in refs:
        url = ref.clean_url
        filename = ref.filename

        # ----------------------------------------------------
        # Rule L4: 폐기 에셋 참조 금지 (Deprecated Asset Ban)
        # ----------------------------------------------------
        if filename in DEPRECATED_ASSET_NAMES:
            violations.append(
                LintViolation(
                    rule="Rule L4 (Deprecated Asset)",
                    file_path=file_path,
                    line_number=ref.line_number,
                    message=f"Deprecated asset referenced: '{filename}'. Use current individual/normalized assets instead.",
                    url=url,
                )
            )

        # ----------------------------------------------------
        # Rule L2: 언어 격리 무결성 (Language Isolation)
        # ----------------------------------------------------
        # 이미지가 /images/ 하위인 경우 언어 폴더 검증
        if "/images/" in url or url.startswith("images/"):
            # 2.1 타 언어 경로 혼재 감사
            foreign_langs = [l for l in SUPPORTED_LANGUAGES if l != doc_lang]
            found_foreign = None
            for fl in foreign_langs:
                if f"/{fl}/" in url:
                    found_foreign = fl
                    break

            if found_foreign:
                violations.append(
                    LintViolation(
                        rule="Rule L2 (Language Isolation)",
                        file_path=file_path,
                        line_number=ref.line_number,
                        message=f"Cross-language image leak detected: Document is '{doc_lang}', but image points to '{found_foreign}': '{url}'",
                        url=url,
                    )
                )
            else:
                # 2.2 루트 비격리 경로 감사: /{doc_lang}/ 폴더 없이 /images/part1/xxx.png 형태로 직접 참조하는 경우
                has_current_lang = f"/{doc_lang}/" in url
                # 만약 SVG나 PNG 다이어그램인데 언어 폴더가 생략되어 있다면 위반
                is_diagram_path = re.search(r"/images/(part\d+|series\d+)/", url)
                if is_diagram_path and not has_current_lang:
                    violations.append(
                        LintViolation(
                            rule="Rule L2 (Language Isolation)",
                            file_path=file_path,
                            line_number=ref.line_number,
                            message=f"Root non-isolated image path without '{doc_lang}' folder: '{url}'",
                            url=url,
                        )
                    )

        # ----------------------------------------------------
        # Rule L3: 물리 파일 실재성 및 최소 크기 (Asset Existence & >= 20KB)
        # ----------------------------------------------------
        physical_path = resolve_physical_path(url, public_dir, file_path)
        if not physical_path.exists():
            violations.append(
                LintViolation(
                    rule="Rule L3 (Asset Existence)",
                    file_path=file_path,
                    line_number=ref.line_number,
                    message=f"Physical asset does not exist on disk: '{url}' (resolved: {physical_path})",
                    url=url,
                )
            )
        else:
            try:
                size = physical_path.stat().st_size
                # SVG 벡터 파일은 텍스트 기반이므로 2KB 이상, PNG/비트맵 이미지는 20KB 이상
                min_size = 2 * 1024 if physical_path.suffix.lower() == ".svg" else MIN_ASSET_SIZE_BYTES
                if size < min_size:
                    violations.append(
                        LintViolation(
                            rule="Rule L3 (Asset Min Size)",
                            file_path=file_path,
                            line_number=ref.line_number,
                            message=f"Asset file size ({size:,} bytes) is below minimum threshold ({min_size:,} bytes): '{url}'",
                            url=url,
                        )
                    )
            except OSError as e:
                violations.append(
                    LintViolation(
                        rule="Rule L3 (Asset Stat Error)",
                        file_path=file_path,
                        line_number=ref.line_number,
                        message=f"Could not stat asset file '{physical_path}': {e}",
                        url=url,
                    )
                )

    # ----------------------------------------------------
    # Rule L5: 프론트매터-본문 바이제션 (Frontmatter Bijection)
    # ----------------------------------------------------
    if fm_text:
        expected_diagrams = parse_frontmatter_diagrams(fm_text)
        if expected_diagrams:
            actual_stems = {Path(ref.filename).stem for ref in refs}
            expected_stems = {Path(d).stem for d in expected_diagrams}
            missing_in_body = expected_stems - actual_stems
            extra_in_body = actual_stems - expected_stems

            if missing_in_body or extra_in_body:
                details = []
                if missing_in_body:
                    details.append(f"declared in frontmatter but missing in body: {sorted(missing_in_body)}")
                if extra_in_body:
                    details.append(f"present in body but missing in frontmatter: {sorted(extra_in_body)}")
                violations.append(
                    LintViolation(
                        rule="Rule L5 (Frontmatter Bijection)",
                        file_path=file_path,
                        line_number=1,
                        message=f"Frontmatter-body diagram bijection failed ({'; '.join(details)})",
                    )
                )

    return refs, violations


def check_language_parity(
    doc_groups: Dict[str, Dict[str, List[ImageReference]]],
    docs_dir: Path
) -> List[LintViolation]:
    """Rule L1: 동일 문서의 ko, en, de, ja 버전 간 이미지 태그 개수 및 식별자 1:1 패리티 감사"""
    parity_violations: List[LintViolation] = []

    for rel_doc_path, lang_map in doc_groups.items():
        # 각 언어별 정규화된 이미지 식별자 리스트
        normalized_map: Dict[str, List[str]] = {}
        for lang in SUPPORTED_LANGUAGES:
            refs = lang_map.get(lang, [])
            normalized_map[lang] = [r.normalized_id() for r in refs]

        # 참조 기준: ko (또는 존재하는 첫 번째 언어)
        base_lang = "ko" if "ko" in normalized_map and normalized_map["ko"] else None
        if not base_lang:
            for l, ids in normalized_map.items():
                if ids:
                    base_lang = l
                    break

        if not base_lang:
            # 모든 언어에 이미지가 없는 문서 (예: index.mdx)
            continue

        base_ids = normalized_map[base_lang]
        for lang in SUPPORTED_LANGUAGES:
            target_ids = normalized_map.get(lang, [])
            target_file = docs_dir / lang / rel_doc_path
            if len(target_ids) != len(base_ids) or target_ids != base_ids:
                parity_violations.append(
                    LintViolation(
                        rule="Rule L1 (Language Parity)",
                        file_path=target_file,
                        line_number=1,
                        message=(
                            f"Image parity mismatch across languages for '{rel_doc_path}'. "
                            f"{base_lang.upper()} has {len(base_ids)} diagram(s) ({base_ids}), "
                            f"while {lang.upper()} has {len(target_ids)} diagram(s) ({target_ids})."
                        ),
                    )
                )

    return parity_violations


def run_linter(
    docs_dir: Path,
    public_dir: Path,
    verbose: bool = False
) -> int:
    """모든 MDX 문서를 스캔하고 5대 규칙 감사 실행. 위반 건수 반환."""
    print("=" * 70)
    print("H-GEAR STUDIO Blog - 다국어 이미지 참조 무결성 자동 검증 하네스")
    print("=" * 70)
    print(f"Docs Directory  : {docs_dir}")
    print(f"Public Directory: {public_dir}")
    print(f"Languages       : {', '.join(SUPPORTED_LANGUAGES)}")
    print("-" * 70)

    if not docs_dir.exists():
        print(f"[FATAL] Docs directory does not exist: {docs_dir}")
        return 1
    if not public_dir.exists():
        print(f"[FATAL] Public directory does not exist: {public_dir}")
        return 1

    all_violations: List[LintViolation] = []
    total_docs = 0
    total_refs = 0

    # rel_doc_path -> {lang: List[ImageReference]}
    doc_groups: Dict[str, Dict[str, List[ImageReference]]] = {}

    for lang in SUPPORTED_LANGUAGES:
        lang_dir = docs_dir / lang
        if not lang_dir.exists():
            continue

        for mdx_file in sorted(lang_dir.rglob("*.mdx")):
            total_docs += 1
            rel_to_lang = mdx_file.relative_to(lang_dir).as_posix()
            if rel_to_lang not in doc_groups:
                doc_groups[rel_to_lang] = {}

            refs, violations = lint_document(mdx_file, lang, public_dir, verbose=verbose)
            total_refs += len(refs)
            doc_groups[rel_to_lang][lang] = refs
            all_violations.extend(violations)

            if verbose:
                print(f"[{lang.upper()}] {rel_to_lang}: {len(refs)} image(s) found, {len(violations)} violation(s)")

    # Rule L1: 언어간 패리티 감사 실행
    parity_violations = check_language_parity(doc_groups, docs_dir)
    all_violations.extend(parity_violations)

    # 결과 통계 분류
    rule_stats: Dict[str, int] = {
        "Rule L1 (Language Parity)": 0,
        "Rule L2 (Language Isolation)": 0,
        "Rule L3 (Asset Existence & Size)": 0,
        "Rule L4 (Deprecated Asset)": 0,
        "Rule L5 (Frontmatter Bijection)": 0,
    }

    print("\n[검사 결과 상세 내역]")
    if all_violations:
        for v in all_violations:
            print(v)
            for rule_key in rule_stats:
                short_key = rule_key.split()[0] + " " + rule_key.split()[1]
                if short_key in v.rule:
                    rule_stats[rule_key] += 1
    else:
        print("  위반 사항 없음 (All Checks Clean).")

    print("\n" + "=" * 70)
    print("Image Reference Linter Summary")
    print("-" * 70)
    print(f"Total MDX Documents Scanned  : {total_docs}")
    print(f"Total Image References Found : {total_refs}")
    print(f"Total Violations Detected    : {len(all_violations)}")
    for rule_name, count in rule_stats.items():
        print(f"  - {rule_name:<34} : {count} violation(s)")
    print("=" * 70)

    if len(all_violations) > 0:
        print(f"\n[FAIL] Image reference integrity check FAILED with {len(all_violations)} violation(s).")
        return 1
    else:
        print("\n[PASS] All multi-language image references passed integrity inspection with 0 errors!")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Multi-language image reference linter for H-GEAR STUDIO Blog")
    parser.add_argument("--check", action="store_true", default=True, help="Run in check mode (default)")
    parser.add_argument("--docs-dir", type=str, default=None, help="Path to docs directory (default: blog/src/content/docs)")
    parser.add_argument("--public-dir", type=str, default=None, help="Path to public directory (default: blog/public)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging per file")

    args = parser.parse_args()

    # 경로 자동 탐색: 현재 작업 디렉토리 또는 스크립트 위치 기준
    script_dir = Path(__file__).resolve().parent
    blog_dir = script_dir.parent

    if args.docs_dir:
        docs_dir = Path(args.docs_dir).resolve()
    else:
        candidate_1 = Path("blog/src/content/docs").resolve()
        candidate_2 = (blog_dir / "src" / "content" / "docs").resolve()
        docs_dir = candidate_1 if candidate_1.exists() else candidate_2

    if args.public-dir if hasattr(args, "public-dir") else args.public_dir:
        public_dir = Path(args.public_dir).resolve()
    else:
        candidate_1 = Path("blog/public").resolve()
        candidate_2 = (blog_dir / "public").resolve()
        public_dir = candidate_1 if candidate_1.exists() else candidate_2

    exit_code = run_linter(docs_dir=docs_dir, public_dir=public_dir, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
