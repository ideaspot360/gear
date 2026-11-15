#!/usr/bin/env python3
"""
H-GEAR STUDIO Blog - Chapter 3 Browser Visual Verification & Capture Script
Constitutional Article 7 & 9 Same-Session Browser Capture Mandate.

Captures actual rendered full-page and section screenshots of Chapter 3:
Meshing Kinematics (03-meshing-kinematics) in all 4 languages (KO, EN, DE, JA)
using Playwright against the built static dist directory.
Outputs screenshots to scratch/blog_part3/.
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
OUTPUT_DIR = WORKSPACE_ROOT / "scratch" / "blog_part3"
PORT = 4321
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
        # Suppress verbose access logs
        pass


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_server_if_needed() -> tuple[ThreadingHTTPServer | None, threading.Thread | None]:
    if is_port_in_use(PORT):
        print(f"[INFO] Port {PORT} is already in use. Assuming server is already running.")
        return None, None

    print(f"[INFO] Starting ThreadingHTTPServer on port {PORT} serving {DIST_DIR}...")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), CustomHTTPHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)
    print(f"[INFO] Server started successfully on http://localhost:{PORT}")
    return server, server_thread


def capture_all():
    print("=" * 70)
    print("H-GEAR STUDIO Blog - Chapter 3 Browser Visual Verification Capture")
    print(f"Target Dist: {DIST_DIR}")
    print(f"Output Dir : {OUTPUT_DIR}")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    server, server_thread = start_server_if_needed()

    captured_files = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Standard desktop 1920x1080 with 1.5x device scale factor for high fidelity
            context = browser.new_context(
                viewport={"width": 1600, "height": 1000},
                device_scale_factor=1.5,
            )
            page = context.new_page()

            for lang in LANGUAGES:
                url = f"http://localhost:{PORT}/{lang}/series1-theory/part-a-spur/03-meshing-kinematics/"
                print(f"\n[LANG: {lang.upper()}] Navigating to: {url}")
                page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait for main content and math elements
                page.wait_for_selector("main", timeout=10000)
                page.wait_for_selector(".katex", timeout=10000)

                # Scroll down smoothly to trigger lazy loading of all images
                page.evaluate("""
                    async () => {
                        const distance = 800;
                        const delay = 100;
                        while (document.scrollingElement.scrollTop + window.innerHeight < document.scrollingElement.scrollHeight) {
                            document.scrollingElement.scrollBy(0, distance);
                            await new Promise(resolve => setTimeout(resolve, delay));
                        }
                        window.scrollTo(0, 0);
                        await new Promise(resolve => setTimeout(resolve, 300));
                    }
                """)
                page.wait_for_load_state("networkidle")

                # Verify all images loaded with positive natural dimensions
                images_info = page.evaluate("""
                    () => {
                        const imgs = Array.from(document.querySelectorAll('main img'));
                        return imgs.map(img => ({
                            src: img.src,
                            alt: img.alt,
                            naturalWidth: img.naturalWidth,
                            naturalHeight: img.naturalHeight,
                            complete: img.complete
                        }));
                    }
                """)
                print(f"  [IMAGES] Found {len(images_info)} images in main:")
                for img in images_info:
                    status = "OK" if img["complete"] and img["naturalWidth"] > 0 else "BROKEN"
                    print(f"    - {status}: {img['src'].split('/')[-1]} ({img['naturalWidth']}x{img['naturalHeight']})")
                    if status == "BROKEN":
                        raise RuntimeError(f"Broken image detected: {img['src']}")

                # Verify KaTeX rendered
                katex_count = page.evaluate("() => document.querySelectorAll('.katex').length")
                print(f"  [KATEX] Rendered math elements count: {katex_count}")
                assert katex_count > 30, f"Too few KaTeX elements ({katex_count})"

                # 1. Full Page Screenshot
                full_path = OUTPUT_DIR / f"capture_ch03_{lang}_fullpage.png"
                page.screenshot(path=str(full_path), full_page=True)
                file_size_kb = full_path.stat().st_size / 1024
                print(f"  [SAVED] Full page: {full_path.name} ({file_size_kb:.1f} KB)")
                captured_files.append((full_path, "Full Page"))

                # 2. Hero & Section 3.1 Overview
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(0.2)
                hero_path = OUTPUT_DIR / f"capture_ch03_{lang}_hero_sec31.png"
                page.screenshot(path=str(hero_path))
                print(f"  [SAVED] Hero/Sec 3.1: {hero_path.name} ({hero_path.stat().st_size / 1024:.1f} KB)")
                captured_files.append((hero_path, "Hero / Section 3.1"))

                # 3. Fig 1 & Action Line Singular Points
                fig1_loc = page.locator("img[src*='fig1_line_of_action_five_points']")
                if fig1_loc.count() > 0:
                    fig1_loc.first.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig1_path = OUTPUT_DIR / f"capture_ch03_{lang}_fig1_action_line.png"
                    fig1_loc.first.screenshot(path=str(fig1_path))
                    print(f"  [SAVED] Fig 1 element: {fig1_path.name} ({fig1_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig1_path, "Fig 1 Line of Action"))

                # 4. Fig 2 & Load Sharing Diagram
                fig2_loc = page.locator("img[src*='fig2_tooth_load_sharing']")
                if fig2_loc.count() > 0:
                    fig2_loc.first.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig2_path = OUTPUT_DIR / f"capture_ch03_{lang}_fig2_load_sharing.png"
                    fig2_loc.first.screenshot(path=str(fig2_path))
                    print(f"  [SAVED] Fig 2 element: {fig2_path.name} ({fig2_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig2_path, "Fig 2 Tooth Load Sharing"))

                # 5. Fig 3 & Kinematics Velocities Diagram
                fig3_loc = page.locator("img[src*='fig3_contact_kinematics_velocities']")
                if fig3_loc.count() > 0:
                    fig3_loc.first.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig3_path = OUTPUT_DIR / f"capture_ch03_{lang}_fig3_contact_kinematics.png"
                    fig3_loc.first.screenshot(path=str(fig3_path))
                    print(f"  [SAVED] Fig 3 element: {fig3_path.name} ({fig3_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig3_path, "Fig 3 Contact Kinematics"))

                # 6. Fig 4 & Specific Sliding Curves Diagram
                fig4_loc = page.locator("img[src*='fig4_specific_sliding_curves']")
                if fig4_loc.count() > 0:
                    fig4_loc.first.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig4_path = OUTPUT_DIR / f"capture_ch03_{lang}_fig4_specific_sliding.png"
                    fig4_loc.first.screenshot(path=str(fig4_path))
                    print(f"  [SAVED] Fig 4 element: {fig4_path.name} ({fig4_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig4_path, "Fig 4 Specific Sliding Curves"))

                # 7. Section 3.3 Benchmark Proportions Table
                table_loc = page.locator("table")
                if table_loc.count() > 0:
                    # Hide floating/sticky header to prevent occlusion during table capture (Reviewer Item 3)
                    page.evaluate("""() => {
                        document.querySelectorAll('header, .header, [data-starlight-header]').forEach(el => {
                            el.style.display = 'none';
                        });
                    }""")
                    time.sleep(0.2)
                    table_loc.first.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    table_path = OUTPUT_DIR / f"capture_ch03_{lang}_table_sec33.png"
                    table_loc.first.screenshot(path=str(table_path))
                    print(f"  [SAVED] Table 1 (38-param): {table_path.name} ({table_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((table_path, "Table 1 38-Parameter Proportions"))
                    # Restore header
                    page.evaluate("""() => {
                        document.querySelectorAll('header, .header, [data-starlight-header]').forEach(el => {
                            el.style.display = '';
                        });
                    }""")

            browser.close()

    finally:
        if server:
            print("\n[INFO] Shutting down HTTP server...")
            server.shutdown()
            server.server_close()
            print("[INFO] Server shut down.")

    print("\n" + "=" * 70)
    print("BROWSER CAPTURE SUMMARY")
    print("=" * 70)
    print(f"Total screenshots captured: {len(captured_files)}")
    for p, desc in captured_files:
        print(f"  - [{desc:30s}]: {p} ({p.stat().st_size / 1024:.1f} KB)")
    print("=" * 70)
    print("[PASS] All browser screenshots successfully captured and verified!")


if __name__ == "__main__":
    capture_all()
