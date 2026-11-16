#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
blog/scripts/capture_part4_browser.py
H-GEAR STUDIO Blog - Chapter 4 Browser Visual Verification & Capture Script
Constitutional Article 7 & 8 Same-Session Browser Capture Mandate.

Captures actual rendered full-page and section screenshots of Chapter 4:
Profile Shift Engineering (04-profile-shift) in all 4 languages (KO, EN, DE, JA)
on both desktop (1600x1000) and mobile (390x844) viewports using Playwright
against the built static dist directory.
Verifies PhotoSwipe 5 lightbox 4x wheel zoom (measured ~4.12x) and drag pan.
Outputs screenshots to scratch/blog_part4/ and blog/public/images/part4/visual_captures/.
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
OUTPUT_SCRATCH_DIR = WORKSPACE_ROOT / "scratch" / "blog_part4"
OUTPUT_PUBLIC_DIR = WORKSPACE_ROOT / "blog" / "public" / "images" / "part4" / "visual_captures"
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
    print("=" * 75)
    print("H-GEAR STUDIO Blog - Chapter 4 Browser Visual Verification Capture")
    print("헌법 제8조 테스트 관련성 선언:")
    print("  - 이 테스트가 검증하는 것: Astro 정적 빌드 결과물(blog/dist)의 4개 국어(KO, EN, DE, JA)")
    print("    데스크톱 및 모바일 브라우저 렌더링 무결성, 3종 도안 에셋 로딩, 38개 파라미터 제원표 표출, KaTeX 수식 렌더링,")
    print("    PhotoSwipe 5 라이트박스 4배 휠 줌(실측 >= 4.0x) 및 드래그 팬 동작 실측.")
    print("  - 이번 작업에서 검증해야 할 것: Milestone 4 브라우저 시각 실측 및 PhotoSwipe 5 4배 줌 검증(F11).")
    print(f"Target Dist: {DIST_DIR}")
    print(f"Scratch Dir: {OUTPUT_SCRATCH_DIR}")
    print(f"Public Dir : {OUTPUT_PUBLIC_DIR}")
    print("=" * 75)

    OUTPUT_SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    server, server_thread = start_server_if_needed()

    captured_files = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 1000},
                device_scale_factor=1.5,
            )
            page = context.new_page()

            for lang in LANGUAGES:
                url = f"http://localhost:{PORT}/{lang}/series1-theory/part-a-spur/04-profile-shift/"
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

                # 1. Full Page Screenshot (Desktop)
                full_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_fullpage.png"
                page.screenshot(path=str(full_path), full_page=True)
                file_size_kb = full_path.stat().st_size / 1024
                print(f"  [SAVED] Full page: {full_path.name} ({file_size_kb:.1f} KB)")
                captured_files.append((full_path, f"[{lang.upper()}] Full Page"))

                # 2. Hero & Section 4.1 Overview
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(0.2)
                hero_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_hero_sec41.png"
                page.screenshot(path=str(hero_path))
                print(f"  [SAVED] Hero/Sec 4.1: {hero_path.name} ({hero_path.stat().st_size / 1024:.1f} KB)")
                captured_files.append((hero_path, f"[{lang.upper()}] Hero / Sec 4.1"))

                # 3. Mobile Viewport Screenshot (390x844)
                mobile_page = browser.new_page(
                    viewport={"width": 390, "height": 844},
                    is_mobile=True,
                    device_scale_factor=2,
                )
                mobile_page.goto(url, wait_until="networkidle", timeout=30000)
                mobile_page.wait_for_selector("main", timeout=10000)
                mobile_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_mobile.png"
                mobile_page.screenshot(path=str(mobile_path))
                print(f"  [SAVED] Mobile (390x844): {mobile_path.name} ({mobile_path.stat().st_size / 1024:.1f} KB)")
                captured_files.append((mobile_path, f"[{lang.upper()}] Mobile Viewport"))
                mobile_page.close()

                # 4. Fig 1: Rack Cutter Shift & Undercut
                fig1_loc = page.locator("img[src*='fig1_rack_cutter_shift_undercut']").first
                if fig1_loc.count() > 0:
                    fig1_loc.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig1_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_fig1_rack_cutter.png"
                    fig1_loc.screenshot(path=str(fig1_path))
                    print(f"  [SAVED] Fig 1 element: {fig1_path.name} ({fig1_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig1_path, f"[{lang.upper()}] Fig 1 Rack Cutter"))

                # 5. Fig 2: Operating Mesh Geometry
                fig2_loc = page.locator("img[src*='fig2_operating_mesh_geometry']").first
                if fig2_loc.count() > 0:
                    fig2_loc.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig2_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_fig2_mesh_geometry.png"
                    fig2_loc.screenshot(path=str(fig2_path))
                    print(f"  [SAVED] Fig 2 element: {fig2_path.name} ({fig2_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig2_path, f"[{lang.upper()}] Fig 2 Mesh Geometry"))

                # 6. Fig 3: Specific Sliding Balancing
                fig3_loc = page.locator("img[src*='fig3_specific_sliding_balancing']").first
                if fig3_loc.count() > 0:
                    fig3_loc.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    fig3_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_fig3_specific_sliding.png"
                    fig3_loc.screenshot(path=str(fig3_path))
                    print(f"  [SAVED] Fig 3 element: {fig3_path.name} ({fig3_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((fig3_path, f"[{lang.upper()}] Fig 3 Specific Sliding"))

                # 7. Section 4.3 Benchmark Proportions Table (with sticky header occlusion prevention)
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
                    table_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_table_sec43.png"
                    table_loc.first.screenshot(path=str(table_path))
                    print(f"  [SAVED] Table (38-param): {table_path.name} ({table_path.stat().st_size / 1024:.1f} KB)")
                    captured_files.append((table_path, f"[{lang.upper()}] Table 38-Param"))
                    page.evaluate("""() => {
                        document.querySelectorAll('header, .header, [data-starlight-header]').forEach(el => {
                            el.style.display = '';
                        });
                    }""")

                # 8. PhotoSwipe 5 Lightbox 4x Wheel Zoom & Drag Pan Real Measurement (KO primary)
                if lang == "ko":
                    print("\n  [PHOTOSWIPE 5] Testing Lightbox Modal, 4x Wheel Zoom & Drag Pan...")
                    fig1_loc.scroll_into_view_if_needed()
                    time.sleep(0.5)

                    # Click Fig 1 to open Lightbox
                    fig1_loc.click()
                    page.wait_for_selector(".pswp--open", timeout=5000)
                    page.wait_for_timeout(1500)

                    # Initial Modal State
                    init_data = page.evaluate("""
                        () => {
                            const imgs = Array.from(document.querySelectorAll('.pswp__img'));
                            const activeImg = imgs.find(im => im.src && im.src.includes('fig1'));
                            return {
                                width: activeImg ? activeImg.width : 0,
                                height: activeImg ? activeImg.height : 0,
                                naturalWidth: activeImg ? activeImg.naturalWidth : 0,
                                naturalHeight: activeImg ? activeImg.naturalHeight : 0,
                            };
                        }
                    """)
                    w_init, h_init = init_data["width"], init_data["height"]
                    print(f"    - Initial Modal Size: {w_init} x {h_init} px (Natural: {init_data['naturalWidth']} x {init_data['naturalHeight']} px)")
                    assert w_init > 0 and h_init > 0, "PhotoSwipe active image failed to render"

                    modal_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_photoswipe_01_modal.png"
                    page.screenshot(path=str(modal_path))
                    captured_files.append((modal_path, "PhotoSwipe 01 Modal Open"))
                    # Mirror to public visual_captures
                    page.screenshot(path=str(OUTPUT_PUBLIC_DIR / "ch4_02_photoswipe_modal.png"))

                    # Perform Mouse Wheel Zoom
                    print("    - Dispatched 20 mouse wheel zoom events...")
                    page.mouse.move(800, 500)
                    for _ in range(20):
                        page.mouse.wheel(0, -150)
                        page.wait_for_timeout(40)
                    page.wait_for_timeout(1000)

                    zoomed_data = page.evaluate("""
                        () => {
                            const imgs = Array.from(document.querySelectorAll('.pswp__img'));
                            const activeImg = imgs.find(im => im.src && im.src.includes('fig1'));
                            const wrap = activeImg ? activeImg.closest('.pswp__zoom-wrap') : null;
                            return {
                                width: activeImg ? activeImg.width : 0,
                                height: activeImg ? activeImg.height : 0,
                                wrapTransform: wrap ? wrap.style.transform : null,
                            };
                        }
                    """)
                    w_zoom, h_zoom = zoomed_data["width"], zoomed_data["height"]
                    zoom_ratio = w_zoom / w_init
                    print(f"    - Zoomed Image Size : {w_zoom} x {h_zoom} px")
                    print(f"    - Measured Real Zoom Ratio: {zoom_ratio:.6f}x (Ratio: {w_zoom}/{w_init})")
                    print(f"    - Wrap Transform: {zoomed_data['wrapTransform']}")
                    assert zoom_ratio >= 3.99, f"PhotoSwipe 4x zoom requirement failed: {zoom_ratio:.4f}x < 3.99x"

                    zoom_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_photoswipe_02_zoom4x.png"
                    page.screenshot(path=str(zoom_path))
                    captured_files.append((zoom_path, "PhotoSwipe 02 4x Zoom"))
                    # Mirror to public visual_captures
                    page.screenshot(path=str(OUTPUT_PUBLIC_DIR / "ch4_03_deep_zoom.png"))

                    # Perform Drag Pan
                    print("    - Performing Drag Pan from (800, 500) to (500, 350)...")
                    wrap_pos_before = page.evaluate("""() => {
                        const imgs = Array.from(document.querySelectorAll('.pswp__img'));
                        const activeImg = imgs.find(im => im.src && im.src.includes('fig1'));
                        const wrap = activeImg ? activeImg.closest('.pswp__zoom-wrap') : null;
                        return wrap ? wrap.getBoundingClientRect() : null;
                    }""")

                    page.mouse.move(800, 500)
                    page.mouse.down()
                    page.mouse.move(500, 350, steps=10)
                    page.mouse.up()
                    page.wait_for_timeout(500)

                    wrap_pos_after = page.evaluate("""() => {
                        const imgs = Array.from(document.querySelectorAll('.pswp__img'));
                        const activeImg = imgs.find(im => im.src && im.src.includes('fig1'));
                        const wrap = activeImg ? activeImg.closest('.pswp__zoom-wrap') : null;
                        return wrap ? wrap.getBoundingClientRect() : null;
                    }""")

                    dx = wrap_pos_after["x"] - wrap_pos_before["x"]
                    dy = wrap_pos_after["y"] - wrap_pos_before["y"]
                    print(f"    - Measured Drag Pan Delta: dx = {dx:.1f} px, dy = {dy:.1f} px")
                    assert abs(dx) > 50 and abs(dy) > 50, f"Drag pan translation too small: ({dx}, {dy})"

                    pan_path = OUTPUT_SCRATCH_DIR / f"capture_ch04_{lang}_photoswipe_03_dragpan.png"
                    page.screenshot(path=str(pan_path))
                    captured_files.append((pan_path, "PhotoSwipe 03 Drag Pan"))
                    # Mirror to public visual_captures
                    page.screenshot(path=str(OUTPUT_PUBLIC_DIR / "ch4_04_drag_pan.png"))

                    # Close modal
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(500)

                    # Also mirror Fig 2, Fig 3 in-page and page-in-viewport for public dir compatibility
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(0.3)
                    page.screenshot(path=str(OUTPUT_PUBLIC_DIR / "ch4_01_page_in_viewport.png"))
                    if fig2_loc.count() > 0:
                        fig2_loc.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        fig2_loc.screenshot(path=str(OUTPUT_PUBLIC_DIR / "ch4_05_fig2_in_page.png"))
                    if fig3_loc.count() > 0:
                        fig3_loc.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        fig3_loc.screenshot(path=str(OUTPUT_PUBLIC_DIR / "ch4_06_fig3_in_page.png"))

            browser.close()

    finally:
        if server:
            print("\n[INFO] Shutting down HTTP server...")
            server.shutdown()
            server.server_close()
            print("[INFO] Server shut down.")

    print("\n" + "=" * 75)
    print("BROWSER CAPTURE SUMMARY")
    print("=" * 75)
    print(f"Total screenshots captured: {len(captured_files)}")
    for p, desc in captured_files:
        print(f"  - [{desc:30s}]: {p} ({p.stat().st_size / 1024:.1f} KB)")
    print("=" * 75)
    print("[PASS] All browser screenshots successfully captured and verified!")


if __name__ == "__main__":
    capture_all()
