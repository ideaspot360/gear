#!/usr/bin/env python3
"""
verify_live_deployment.py

Automated verification suite for live production deployment on https://gear.ideaspot360.com.
Checks:
1. 4-language HTML pages return HTTP 200, valid titles, and KaTeX elements.
2. 24 high-resolution diagram assets (SVG & PNG for Fig 1, 2, 3 in KO, EN, DE, JA)
   return HTTP 200, correct Content-Type, and Content-Length >= 20,480 bytes (20 KB).
3. Outputs structured audit results and exits with 0 on success.
"""

import sys
import urllib.request
import urllib.error
import re
import json

BASE_URL = "https://gear.ideaspot360.com"

PAGES = [
    {
        "lang": "ko",
        "url": f"{BASE_URL}/ko/series1-theory/part-a-spur/04-profile-shift/",
        "title_keyword": "제4장. 평치차의 전위(Profile Shift, x) 공학",
        "h1_keyword": "제4장. 평치차의 전위(Profile Shift, x) 공학",
    },
    {
        "lang": "en",
        "url": f"{BASE_URL}/en/series1-theory/part-a-spur/04-profile-shift/",
        "title_keyword": "Chapter 4. Spur Gear Profile Shift (x) Engineering",
        "h1_keyword": "Chapter 4. Spur Gear Profile Shift (x) Engineering",
    },
    {
        "lang": "de",
        "url": f"{BASE_URL}/de/series1-theory/part-a-spur/04-profile-shift/",
        "title_keyword": "Kapitel 4. Profilverschiebung (x) bei Stirnrädern",
        "h1_keyword": "Kapitel 4. Profilverschiebung (x) bei Stirnrädern",
    },
    {
        "lang": "ja",
        "url": f"{BASE_URL}/ja/series1-theory/part-a-spur/04-profile-shift/",
        "title_keyword": "第4章. 平歯車の転位（Profile Shift, x）工学",
        "h1_keyword": "第4章. 平歯車の転位（Profile Shift, x）工学",
    },
]

LANGUAGES = ["ko", "en", "de", "ja"]
FIGURES = [
    "fig1_rack_cutter_shift_undercut",
    "fig2_operating_mesh_geometry",
    "fig3_specific_sliding_balancing",
]
FORMATS = [
    ("png", "image/png"),
    ("svg", "image/svg+xml"),
]


def check_pages():
    results = []
    all_ok = True
    print("\n[STEP 1] Auditing 4-Language Live Pages HTML...")
    for page in PAGES:
        lang = page["lang"]
        url = page["url"]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "H-Gear-Verifier/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.status
                body = resp.read().decode("utf-8", errors="replace")
                content_len = len(body)
                
                title_match = re.search(r"<title>(.*?)</title>", body)
                title = title_match.group(1) if title_match else ""
                title_ok = page["title_keyword"] in title
                
                h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", body)
                h1 = h1_match.group(1) if h1_match else ""
                h1_ok = page["h1_keyword"] in h1
                
                katex_ok = "katex" in body
                has_fig1 = "fig1_rack_cutter_shift_undercut" in body
                has_fig2 = "fig2_operating_mesh_geometry" in body
                has_fig3 = "fig3_specific_sliding_balancing" in body
                
                passed = status == 200 and title_ok and h1_ok and katex_ok and has_fig1 and has_fig2 and has_fig3
                if not passed:
                    all_ok = False
                
                result = {
                    "lang": lang,
                    "url": url,
                    "status": status,
                    "content_length": content_len,
                    "title_ok": title_ok,
                    "h1_ok": h1_ok,
                    "katex_ok": katex_ok,
                    "fig1_ok": has_fig1,
                    "fig2_ok": has_fig2,
                    "fig3_ok": has_fig3,
                    "passed": passed,
                }
                results.append(result)
                print(f"  [{'PASS' if passed else 'FAIL'}] {lang.upper()}: Status={status}, Length={content_len:,} chars, TitleOK={title_ok}, KaTeX={katex_ok}")
        except Exception as e:
            all_ok = False
            print(f"  [ERROR] {lang.upper()}: {url} -> {e}")
            results.append({"lang": lang, "url": url, "error": str(e), "passed": False})
    return all_ok, results


def check_assets():
    results = []
    all_ok = True
    print("\n[STEP 2] Auditing 24 High-Resolution Diagram Assets on Live Production CDN...")
    total_assets = 0
    passed_assets = 0
    for lang in LANGUAGES:
        for fig in FIGURES:
            for ext, expected_mime in FORMATS:
                total_assets += 1
                asset_url = f"{BASE_URL}/images/part4/{lang}/{fig}.{ext}"
                try:
                    req = urllib.request.Request(asset_url, method="HEAD", headers={"User-Agent": "H-Gear-Verifier/1.0"})
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        status = resp.status
                        content_len = int(resp.headers.get("Content-Length", 0))
                        content_type = resp.headers.get("Content-Type", "")
                        
                        size_ok = content_len >= 20480  # >= 20 KB
                        mime_ok = expected_mime in content_type
                        passed = status == 200 and size_ok and mime_ok
                        
                        if passed:
                            passed_assets += 1
                        else:
                            all_ok = False
                        
                        results.append({
                            "lang": lang,
                            "fig": fig,
                            "ext": ext,
                            "url": asset_url,
                            "status": status,
                            "content_length": content_len,
                            "content_type": content_type,
                            "passed": passed,
                        })
                        status_str = "PASS" if passed else "FAIL"
                        print(f"  [{status_str}] {lang}/{fig}.{ext} -> Status={status}, Size={content_len:,} B, MIME={content_type}")
                except Exception as e:
                    all_ok = False
                    print(f"  [ERROR] {lang}/{fig}.{ext} -> {e}")
                    results.append({"lang": lang, "fig": fig, "ext": ext, "url": asset_url, "error": str(e), "passed": False})
    print(f"\nAsset Summary: {passed_assets}/{total_assets} passed (all >= 20 KB).")
    return all_ok, results


def main():
    print("=" * 80)
    print("H-GEAR STUDIO: Live Production Deployment Verifier")
    print(f"Target Production Site: {BASE_URL}")
    print("=" * 80)
    
    pages_ok, page_results = check_pages()
    assets_ok, asset_results = check_assets()
    
    print("\n" + "=" * 80)
    if pages_ok and assets_ok:
        print("[AUDIT SUCCESS] All 4 language articles and 24 diagram assets verified on live site!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("[AUDIT FAILURE] Some checks failed! See detailed logs above.")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
