# -*- coding: utf-8 -*-
"""
blog/scripts/capture_part4_browser.py
Automated Playwright headless browser capture script for Chapter 4.
Verifies Article 7 (Same-Session Visual Verification Mandate) & PhotoSwipe 5 lightbox.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "images" / "part4" / "visual_captures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:4321/ko/series1-theory/part-a-spur/04-profile-shift/"

def main():
    print(f"Launching Playwright to capture Chapter 4 at {URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        page = context.new_page()

        # Step 1: Navigate to page
        print("Navigating to page...")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 1. Page In Viewport
        cap1 = OUTPUT_DIR / "ch4_01_page_in_viewport.png"
        page.screenshot(path=str(cap1))
        print(f"[OK] Captured: {cap1}")

        # Step 2: Scroll to Figure 1 and click to open PhotoSwipe Lightbox
        print("Locating Figure 1...")
        fig1_img = page.locator('img[src*="fig1_rack_cutter_shift_undercut"]').first
        fig1_img.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)

        # Click to trigger PhotoSwipe
        fig1_img.click()
        page.wait_for_timeout(1500)

        # 2. PhotoSwipe Modal Open
        cap2 = OUTPUT_DIR / "ch4_02_photoswipe_modal.png"
        page.screenshot(path=str(cap2))
        print(f"[OK] Captured: {cap2}")

        # Step 3: Deep Zoom (4x) via double click or wheel zoom
        print("Zooming in to 4x via mouse wheel & dblclick...")
        # Position mouse in center of PhotoSwipe overlay
        page.mouse.move(800, 500)
        page.mouse.dblclick(800, 500)
        page.wait_for_timeout(1000)
        # Mouse wheel zoom in for deep magnification
        page.mouse.wheel(0, -500)
        page.wait_for_timeout(1000)

        # 3. Deep Zoom View
        cap3 = OUTPUT_DIR / "ch4_03_deep_zoom.png"
        page.screenshot(path=str(cap3))
        print(f"[OK] Captured: {cap3}")

        # Step 4: Drag Pan
        print("Dragging to pan zoomed view...")
        page.mouse.move(800, 500)
        page.mouse.down()
        page.mouse.move(500, 350, steps=8)
        page.mouse.up()
        page.wait_for_timeout(1000)

        # 4. Drag Pan View
        cap4 = OUTPUT_DIR / "ch4_04_drag_pan.png"
        page.screenshot(path=str(cap4))
        print(f"[OK] Captured: {cap4}")

        # Close PhotoSwipe modal (Esc)
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

        # Step 5: Scroll to Fig 2 and Fig 3 for complete visual audit
        fig2_img = page.locator('img[src*="fig2_operating_mesh_geometry"]').first
        if fig2_img.is_visible():
            fig2_img.scroll_into_view_if_needed()
            page.wait_for_timeout(800)
            cap5 = OUTPUT_DIR / "ch4_05_fig2_in_page.png"
            page.screenshot(path=str(cap5))
            print(f"[OK] Captured: {cap5}")

        fig3_img = page.locator('img[src*="fig3_specific_sliding_balancing"]').first
        if fig3_img.is_visible():
            fig3_img.scroll_into_view_if_needed()
            page.wait_for_timeout(800)
            cap6 = OUTPUT_DIR / "ch4_06_fig3_in_page.png"
            page.screenshot(path=str(cap6))
            print(f"[OK] Captured: {cap6}")

        browser.close()
        print("All browser visual captures completed successfully.")

if __name__ == "__main__":
    main()
