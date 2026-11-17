#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blog/scripts/capture_part5_browser.py
H-GEAR STUDIO Blog - Chapter 5 Browser Visual Verification & Capture Script
Constitutional Article 7 & 8 Same-Session Browser Capture Mandate.

Captures actual rendered full-page and section screenshots of Chapter 5:
Profile Shift Allocation (05-profile-shift-allocation) in all 4 languages (KO, EN, DE, JA)
on both desktop (1600x1000) and mobile (390x844) viewports using Playwright
against the built static dist directory.
Outputs screenshots to scratch/blog_part5/ and blog/public/images/part5/visual_captures/.
"""

import sys
import os
import time
import socket
import mimetypes
import threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

WORKSPACE_ROOT = Path("d:/01_ag_gear/01_gear").resolve()
DIST_DIR = WORKSPACE_ROOT / "blog" / "dist"
OUTPUT_SCRATCH_DIR = WORKSPACE_ROOT / "scratch" / "blog_part5"
OUTPUT_PUBLIC_DIR = WORKSPACE_ROOT / "blog" / "public" / "images" / "part5" / "visual_captures"
PORT = 4325
LANGUAGES = ["ko", "en", "de", "ja"]

# Ensure correct MIME types on Windows
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")


class CustomHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_server_if_needed() -> tuple[ThreadingHTTPServer | None, threading.Thread | None]:
    if is_port_in_use(PORT):
        print(f"[HTTP SERVER] Port {PORT} already in use. Reusing existing server.")
        return None, None

    server = ThreadingHTTPServer(("127.0.0.1", PORT), CustomHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[HTTP SERVER] Started local web server on http://127.0.0.1:{PORT} (root: {DIST_DIR})")
    time.sleep(0.5)
    return server, thread


def main():
    print("=" * 80)
    print(" H-GEAR STUDIO Blog Part 5 Browser Verification & Capture Suite")
    print(" Compliance: Constitutional Article 7 (Same-Session Live Visual Verification)")
    print("=" * 80)

    OUTPUT_SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    server, thread = start_server_if_needed()

    captured_files = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            for lang in LANGUAGES:
                print(f"\n[{lang.upper()}] Capturing Chapter 5 Live Browser Views...")
                page = browser.new_page(
                    viewport={"width": 1600, "height": 1000},
                    device_scale_factor=1,
                )

                url = f"http://127.0.0.1:{PORT}/{lang}/series1-theory/part-a-spur/05-profile-shift-allocation/"
                print(f"  Navigating to: {url}")
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_selector("main", timeout=10000)

                # 1. Full Page Screenshot (Desktop)
                full_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_fullpage.png"
                page.screenshot(path=str(full_path), full_page=True)
                file_size_kb = full_path.stat().st_size / 1024
                print(f"  [SAVED] Full page: {full_path.name} ({file_size_kb:.1f} KB)")
                captured_files.append((full_path, f"[{lang.upper()}] Full Page"))

                # 2. Hero & Section 5.1 Overview
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(0.2)
                hero_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_hero_sec51.png"
                page.screenshot(path=str(hero_path))
                print(f"  [SAVED] Hero/Sec 5.1: {hero_path.name} ({hero_path.stat().st_size / 1024:.1f} KB)")
                captured_files.append((hero_path, f"[{lang.upper()}] Hero / Sec 5.1"))

                # 3. Mobile Viewport Screenshot (390x844)
                mobile_page = browser.new_page(
                    viewport={"width": 390, "height": 844},
                    is_mobile=True,
                    device_scale_factor=2,
                )
                mobile_page.goto(url, wait_until="networkidle", timeout=30000)
                mobile_page.wait_for_selector("main", timeout=10000)
                mobile_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_mobile.png"
                mobile_page.screenshot(path=str(mobile_path))
                print(f"  [SAVED] Mobile (390x844): {mobile_path.name} ({mobile_path.stat().st_size / 1024:.1f} KB)")
                captured_files.append((mobile_path, f"[{lang.upper()}] Mobile Viewport"))
                mobile_page.close()

                # 4. Fig 1: Feasible Domain Map
                fig1_loc = page.locator("img[src*='fig1_shift_feasible_domain']").first
                if fig1_loc.count() > 0:
                    fig1_loc.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig1_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_fig1_domain.png"
                    fig1_loc.screenshot(path=str(fig1_path))
                    print(f"  [SAVED] Fig 1 element: {fig1_path.name} ({fig1_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig1_path, f"[{lang.upper()}] Fig 1 Feasible Domain"))

                # 5. Fig 2: Strength Balancing
                fig2_loc = page.locator("img[src*='fig2_bending_strength_balance']").first
                if fig2_loc.count() > 0:
                    fig2_loc.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig2_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_fig2_strength.png"
                    fig2_loc.screenshot(path=str(fig2_path))
                    print(f"  [SAVED] Fig 2 element: {fig2_path.name} ({fig2_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig2_path, f"[{lang.upper()}] Fig 2 Strength Balance"))

                # 6. Fig 3: Asymmetric Meshing Profile
                fig3_loc = page.locator("img[src*='fig3_asymmetric_mesh_profile']").first
                if fig3_loc.count() > 0:
                    fig3_loc.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig3_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_fig3_profile.png"
                    fig3_loc.screenshot(path=str(fig3_path))
                    print(f"  [SAVED] Fig 3 element: {fig3_path.name} ({fig3_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig3_path, f"[{lang.upper()}] Fig 3 Asymmetric Profile"))

                # 7. Section 5.4 Macro Geometry Table
                table_loc = page.locator("table")
                if table_loc.count() > 0:
                    page.evaluate("""() => {
                        document.querySelectorAll('header, .header, [data-starlight-header]').forEach(el => {
                            el.style.display = 'none';
                        });
                    }""")
                    time.sleep(0.2)
                    table_loc.first.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    table_path = OUTPUT_SCRATCH_DIR / f"capture_ch05_{lang}_table_sec54.png"
                    table_loc.first.screenshot(path=str(table_path))
                    print(f"  [SAVED] Table (38-param): {table_path.name} ({table_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((table_path, f"[{lang.upper()}] Table 38-Param"))
                    page.evaluate("""() => {
                        document.querySelectorAll('header, .header, [data-starlight-header]').forEach(el => {
                            el.style.display = '';
                        });
                    }""")

                page.close()

            browser.close()

        # Copy primary captures to public directory as well
        for src_path, desc in captured_files:
            dst_path = OUTPUT_PUBLIC_DIR / src_path.name
            dst_path.write_bytes(src_path.read_bytes())

        print("\n" + "=" * 80)
        print(" BROWSER VISUAL VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Visual Captures Created: {len(captured_files)}")
        for path, desc in captured_files:
            size_kb = path.stat().st_size / 1024
            print(f"  - {desc:<35}: {path.name} ({size_kb:.1f} KB)")
        print("=" * 80)
        print("[PASS] All browser visual captures completed successfully.")

    finally:
        if server:
            server.shutdown()


if __name__ == "__main__":
    main()
