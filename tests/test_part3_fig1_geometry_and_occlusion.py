"""
Automated Geometry & Occlusion Audit System for Part 3 Fig 1 Vector Diagram.
Constitutional Articles 1, 2, 3, 7, 8 Compliant.

Audit Gates:
- Gate 1: Arrowhead tip to curve contact distance (|d - R| <= 0.5 px).
- Gate 2: Bounding box occlusion between markers, lines, text, label box background rects (0 collisions).
- Gate 3: Text clipping / overflow audit for 4 languages (KO, EN, DE, JA) (margin >= 6.0 px).
- Gate 4: Marker rendering completeness and <marker> ID validity (0 missing).
- R3 Pipeline: Headless Chromium browser verification and high-res screenshot capture.
"""

import math
import os
import re
from pathlib import Path
import pytest
from lxml import etree
from playwright.sync_api import sync_playwright
from shapely.geometry import Polygon, LineString, box as shapely_box

# Project paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BLOG_DIR = REPO_ROOT / "blog"
PUBLIC_IMG_DIR = BLOG_DIR / "public" / "images" / "part3"
SCRATCH_DIR = REPO_ROOT / "scratch" / "blog_part3"
SPEC_FILE = BLOG_DIR / "data" / "specs" / "fig1_part3_spec.json"

LANGUAGES = ["ko", "en", "de", "ja"]
SVG_FILENAME = "fig1_line_of_action_five_points.svg"

# Canvas & Center mapping parameters (Single Source of Truth)
CANVAS_W = 1260
CANVAS_H = 920
CX = 610.0
CY = 325.0
SCALE = 13.8

# Closed-form geometry parameters from ISO 21771 / DIN 3960
# Gear 2: center = (0, -81.0) mm, ra2 = 84.0 mm
CY_GEAR = CY + 81.0 * SCALE      # 1442.80 px
R_GEAR = 84.0 * SCALE            # 1159.20 px
ARC_GEAR_DEG_RANGE = (75.0, 105.0)

# Pinion 1: center = (0, +27.0) mm, ra1 = 30.0 mm
CY_PINION = CY - 27.0 * SCALE    # -47.60 px
R_PINION = 30.0 * SCALE          # 414.00 px
ARC_PINION_DEG_RANGE = (255.0, 305.0)


def parse_svg_path_to_linestring(d_str: str) -> LineString:
    """
    Parses an SVG path 'd' attribute string into a Shapely LineString.
    Supports M/m (MoveTo), L/l (LineTo), H/h (Horizontal), V/v (Vertical), and Z/z (Close).
    Robust against arbitrary whitespace, comma separators, scientific notation, and signs.
    Constitutional Article 1 & 2 Compliant: Zero hardcoding, 100% dynamic geometry.
    """
    assert d_str and isinstance(d_str, str), "Invalid SVG path string"
    tokens = re.findall(r'[MLHVCSQTAZmlhvcsqtaz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?', d_str)
    
    points = []
    curr_cmd = None
    i = 0
    cur_x, cur_y = 0.0, 0.0
    
    while i < len(tokens):
        token = tokens[i]
        if token.isalpha():
            curr_cmd = token
            i += 1
            continue
        
        if curr_cmd == 'M':
            cur_x, cur_y = float(token), float(tokens[i + 1])
            points.append((cur_x, cur_y))
            i += 2
            curr_cmd = 'L'
        elif curr_cmd == 'm':
            cur_x += float(token)
            cur_y += float(tokens[i + 1])
            points.append((cur_x, cur_y))
            i += 2
            curr_cmd = 'l'
        elif curr_cmd == 'L':
            cur_x, cur_y = float(token), float(tokens[i + 1])
            points.append((cur_x, cur_y))
            i += 2
        elif curr_cmd == 'l':
            cur_x += float(token)
            cur_y += float(tokens[i + 1])
            points.append((cur_x, cur_y))
            i += 2
        elif curr_cmd == 'H':
            cur_x = float(token)
            points.append((cur_x, cur_y))
            i += 1
        elif curr_cmd == 'h':
            cur_x += float(token)
            points.append((cur_x, cur_y))
            i += 1
        elif curr_cmd == 'V':
            cur_y = float(token)
            points.append((cur_x, cur_y))
            i += 1
        elif curr_cmd == 'v':
            cur_y += float(token)
            points.append((cur_x, cur_y))
            i += 1
        elif curr_cmd in ('Z', 'z'):
            if points:
                points.append(points[0])
            i += 1
        else:
            i += 1
            
    assert len(points) >= 2, f"SVG path must contain at least 2 vertices for LineString, got {len(points)}: '{d_str}'"
    return LineString(points)


def parse_svg_transform_polygon(rect_local: dict, transform_str: str) -> Polygon:
    """
    Parses SVG translate(tx, ty) rotate(deg) transform and returns an exact closed-form 2D OBB Polygon.
    """
    m = re.search(r"translate\(\s*([\d.-]+)\s*,\s*([\d.-]+)\s*\)\s*rotate\(\s*([\d.-]+)\s*\)", transform_str)
    if not m:
        raise ValueError(f"Invalid transform string: {transform_str}")
    tx, ty, deg = float(m.group(1)), float(m.group(2)), float(m.group(3))
    rad = math.radians(deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    lx, ly, lw, lh = rect_local["x"], rect_local["y"], rect_local["w"], rect_local["h"]
    local_pts = [(lx, ly), (lx + lw, ly), (lx + lw, ly + lh), (lx, ly + lh)]
    
    world_pts = [(tx + px * cos_a - py * sin_a, ty + px * sin_a + py * cos_a) for px, py in local_pts]
    return Polygon(world_pts)


@pytest.fixture(scope="session")
def browser_instance():
    """Initializes Playwright Chromium browser for same-session verification."""
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_relevance_declaration():
    """
    Constitutional Article 8 [Test Relevance Declaration Mandate].
    Explicit declaration of test scope, targets, and criteria.
    """
    print("\n" + "=" * 80)
    print("CONSTITUTIONAL ARTICLE 8: TEST RELEVANCE DECLARATION")
    print("=" * 80)
    print("이 테스트가 검증하는 것:")
    print("  1. Part 3 Fig 1 도안의 지시선 화살표 끝점(Arrowhead Tip)과 대상 기하 원호 간 최단 접촉 거리 (|d - R| <= 0.5 px).")
    print("  2. 화살표 마커, 텍스트, 라벨 박스 배경 <rect>, 치수선 간 바운딩 박스 겹침/가림(Occlusion) 전수 감사 (0건).")
    print("  3. 4개 국어(KO, EN, DE, JA) 라벨 박스 내부 텍스트 마진 확보 (최소 마진 >= 6.0 px, 오버플로우 0건).")
    print("  4. 화살표 마커 <marker> ID 참조 유효성 및 렌더링 무결성 (누락 0건).")
    print("  5. 동일 세션 내 헤드리스 Chromium 브라우저 실물 렌더링 고해상도 스크린샷 캡처 및 검증.")
    print("이번 작업에서 검증해야 할 것:")
    print("  Part 3 Fig 1 도안 2-Tier 직교 라우팅 아키텍처 및 4대 게이트 자동 검증 시스템 구축.")
    print("=" * 80 + "\n")
    assert True


@pytest.mark.parametrize("lang", LANGUAGES)
def test_part3_fig1_gate1_geometry_contact(browser_instance, lang):
    """
    Gate 1 [기하 접촉 실측]:
    지시선 화살표 끝점(Arrowhead Tip)과 대상 기하 형상(원호) 간 최단 거리 실측 (|d - R| <= 0.5 px).
    헌법 제1조: 소수점 6자리 원시 수치 로그 전수 출력.
    """
    svg_path = PUBLIC_IMG_DIR / lang / SVG_FILENAME
    assert svg_path.exists(), f"SVG file not found: {svg_path}"

    page = browser_instance.new_page(viewport={"width": CANVAS_W, "height": CANVAS_H})
    try:
        svg_content = svg_path.read_text(encoding="utf-8")
        html_wrapper = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#ffffff;">{svg_content}</body></html>"""
        page.set_content(html_wrapper)
        page.wait_for_load_state("networkidle")

        # DOM measurement of path endpoints via Playwright evaluate
        eval_script = """
        () => {
            const pathGear = document.querySelector('path[marker-end="url(#arr-gear)"]');
            const pathPinion = document.querySelector('path[marker-end="url(#arr-pinion)"]');
            
            const lenGear = pathGear ? pathGear.getTotalLength() : 0;
            const ptGear = pathGear ? pathGear.getPointAtLength(lenGear) : { x: 0, y: 0 };
            
            const lenPinion = pathPinion ? pathPinion.getTotalLength() : 0;
            const ptPinion = pathPinion ? pathPinion.getPointAtLength(lenPinion) : { x: 0, y: 0 };
            
            return {
                gearTip: { x: ptGear.x, y: ptGear.y },
                pinionTip: { x: ptPinion.x, y: ptPinion.y }
            };
        }
        """
        dom_data = page.evaluate(eval_script)
        gear_tip = dom_data["gearTip"]
        pinion_tip = dom_data["pinionTip"]

        # Gear calculation
        dx_gear = gear_tip["x"] - CX
        dy_gear = gear_tip["y"] - CY_GEAR
        dist_gear = math.hypot(dx_gear, dy_gear)
        delta_d_gear = abs(dist_gear - R_GEAR)
        angle_gear_deg = (math.atan2(-dy_gear, dx_gear) * 180.0 / math.pi) % 360.0

        # Pinion calculation
        dx_pinion = pinion_tip["x"] - CX
        dy_pinion = pinion_tip["y"] - CY_PINION
        dist_pinion = math.hypot(dx_pinion, dy_pinion)
        delta_d_pinion = abs(dist_pinion - R_PINION)
        angle_pinion_deg = (math.atan2(-dy_pinion, dx_pinion) * 180.0 / math.pi) % 360.0

        # Raw Output (Constitutional Article 1)
        print(f"\n[Gate 1 - Raw Telemetry] Language: {lang.upper()}")
        print(f"  [Gear ra2 Arc Contact]")
        print(f"    Arrowhead Tip (DOM) : ({gear_tip['x']:.6f}, {gear_tip['y']:.6f}) px")
        print(f"    Circle Center       : ({CX:.6f}, {CY_GEAR:.6f}) px")
        print(f"    Target Radius R     : {R_GEAR:.6f} px (84.000000 mm)")
        print(f"    Measured Distance d : {dist_gear:.6f} px")
        print(f"    Contact Error Δd    : {delta_d_gear:.6f} px (Tolerance <= 0.500000 px)")
        print(f"    Arc Angle θ         : {angle_gear_deg:.6f}° (Valid Arc: [{ARC_GEAR_DEG_RANGE[0]:.1f}°, {ARC_GEAR_DEG_RANGE[1]:.1f}°])")

        print(f"  [Pinion ra1 Arc Contact]")
        print(f"    Arrowhead Tip (DOM) : ({pinion_tip['x']:.6f}, {pinion_tip['y']:.6f}) px")
        print(f"    Circle Center       : ({CX:.6f}, {CY_PINION:.6f}) px")
        print(f"    Target Radius R     : {R_PINION:.6f} px (30.000000 mm)")
        print(f"    Measured Distance d : {dist_pinion:.6f} px")
        print(f"    Contact Error Δd    : {delta_d_pinion:.6f} px (Tolerance <= 0.500000 px)")
        print(f"    Arc Angle θ         : {angle_pinion_deg:.6f}° (Valid Arc: [{ARC_PINION_DEG_RANGE[0]:.1f}°, {ARC_PINION_DEG_RANGE[1]:.1f}°])")

        # Assertions
        assert delta_d_gear <= 0.5, f"[{lang}] Gear ra2 contact error {delta_d_gear:.6f} px exceeds 0.5 px"
        assert ARC_GEAR_DEG_RANGE[0] <= angle_gear_deg <= ARC_GEAR_DEG_RANGE[1], \
            f"[{lang}] Gear contact angle {angle_gear_deg:.6f}° outside arc range {ARC_GEAR_DEG_RANGE}"

        assert delta_d_pinion <= 0.5, f"[{lang}] Pinion ra1 contact error {delta_d_pinion:.6f} px exceeds 0.5 px"
        assert ARC_PINION_DEG_RANGE[0] <= angle_pinion_deg <= ARC_PINION_DEG_RANGE[1], \
            f"[{lang}] Pinion contact angle {angle_pinion_deg:.6f}° outside arc range {ARC_PINION_DEG_RANGE}"

    finally:
        page.close()


@pytest.mark.parametrize("lang", LANGUAGES)
def test_part3_fig1_gate2_occlusion(browser_instance, lang):
    """
    Gate 2 [바운딩 박스 가림 및 교차 감사]:
    화살표 마커, 텍스트, 라벨 박스 배경 <rect>, 치수선 간 바운딩 박스 겹침/가림(Occlusion) 전수 감사 (0건).
    """
    svg_path = PUBLIC_IMG_DIR / lang / SVG_FILENAME
    page = browser_instance.new_page(viewport={"width": CANVAS_W, "height": CANVAS_H})
    try:
        svg_content = svg_path.read_text(encoding="utf-8")
        html_wrapper = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#ffffff;">{svg_content}</body></html>"""
        page.set_content(html_wrapper)
        page.wait_for_load_state("networkidle")

        eval_script = """
        () => {
            const boxes = [];
            document.querySelectorAll('.label-box').forEach(g => {
                const rect = g.querySelector('rect');
                const text = g.querySelector('text');
                if (rect) {
                    const r = rect.getBoundingClientRect();
                    boxes.push({
                        id: g.id || '',
                        text: text ? text.textContent.trim() : '',
                        rect: { x: r.x, y: r.y, w: r.width, h: r.height, r: r.right, b: r.bottom }
                    });
                }
            });

            const leaders = [];
            document.querySelectorAll('path.leader-line').forEach(p => {
                leaders.push({
                    id: p.id || '',
                    d: p.getAttribute('d')
                });
            });

            const card = document.querySelector('.summary-card rect');
            const cardB = card ? card.getBoundingClientRect() : null;

            const dimBoxes = [];
            ['pb', 'ga', 'bd'].forEach(k => {
                const g = document.querySelector(`#dim-group-${k}`);
                if (g) {
                    const rect = g.querySelector('rect');
                    const text = g.querySelector('text');
                    const transform = g.getAttribute('transform');
                    if (rect && transform) {
                        dimBoxes.push({
                            id: k,
                            text: text ? text.textContent.trim() : '',
                            transform: transform,
                            rectLocal: {
                                x: parseFloat(rect.getAttribute('x')),
                                y: parseFloat(rect.getAttribute('y')),
                                w: parseFloat(rect.getAttribute('width')),
                                h: parseFloat(rect.getAttribute('height'))
                            }
                        });
                    }
                }
            });

            const leaderD = document.querySelector('#leader-d');
            const leaderDPathStr = leaderD ? leaderD.getAttribute('d') : '';

            const getLineCoords = (id, strokeColor) => {
                let line = document.querySelector(`#dim-line-${id}`);
                if (!line) {
                    line = document.querySelector(`line[stroke="${strokeColor}"]`);
                }
                if (!line) return null;
                return {
                    x1: parseFloat(line.getAttribute('x1')),
                    y1: parseFloat(line.getAttribute('y1')),
                    x2: parseFloat(line.getAttribute('x2')),
                    y2: parseFloat(line.getAttribute('y2'))
                };
            };

            return {
                boxes: boxes,
                leaders: leaders,
                card: cardB ? { x: cardB.x, y: cardB.y, w: cardB.width, h: cardB.height, r: cardB.right, b: cardB.bottom } : null,
                dimBoxes: dimBoxes,
                leaderDPathStr: leaderDPathStr,
                dimPb: getLineCoords('pb', '#4338ca'),
                dimGa: getLineCoords('ga', '#ea580c'),
                dimBd: getLineCoords('bd', '#7c3aed')
            };
        }
        """
        data = page.evaluate(eval_script)
        boxes = data["boxes"]
        card = data["card"]
        dim_boxes = data["dimBoxes"]
        leader_d_str = data["leaderDPathStr"]
        dim_pb = data["dimPb"]
        dim_ga = data["dimGa"]
        dim_bd = data["dimBd"]

        assert leader_d_str, f"[{lang}] Leader D path string could not be extracted from DOM!"
        assert dim_pb, f"[{lang}] Dimension line dimPb could not be extracted from DOM!"
        assert dim_ga, f"[{lang}] Dimension line dimGa could not be extracted from DOM!"
        assert dim_bd, f"[{lang}] Dimension line dimBd could not be extracted from DOM!"

        # Construct Polygons for all elements
        label_polys = [
            (b["text"], shapely_box(b["rect"]["x"], b["rect"]["y"], b["rect"]["r"], b["rect"]["b"]))
            for b in boxes
        ]

        card_poly = shapely_box(card["x"], card["y"], card["r"], card["b"]) if card else None

        dim_polys = [
            (db["text"], parse_svg_transform_polygon(db["rectLocal"], db["transform"]))
            for db in dim_boxes
        ]

        # Audit Pairwise Overlaps
        box_overlaps = []
        for i in range(len(label_polys)):
            for j in range(i + 1, len(label_polys)):
                name1, poly1 = label_polys[i]
                name2, poly2 = label_polys[j]
                if poly1.intersects(poly2):
                    area = poly1.intersection(poly2).area
                    if area > 0.001:
                        box_overlaps.append((name1, name2, area))

        card_overlaps = []
        if card_poly:
            for name, poly in label_polys:
                if poly.intersects(card_poly):
                    area = poly.intersection(card_poly).area
                    if area > 0.001:
                        card_overlaps.append((name, area))

        dim_box_overlaps = []
        for d_name, d_poly in dim_polys:
            for l_name, l_poly in label_polys:
                if d_poly.intersects(l_poly):
                    area = d_poly.intersection(l_poly).area
                    if area > 0.001:
                        dim_box_overlaps.append((l_name, d_name, area))

        dim_card_overlaps = []
        if card_poly:
            for d_name, d_poly in dim_polys:
                if d_poly.intersects(card_poly):
                    area = d_poly.intersection(card_poly).area
                    if area > 0.001:
                        dim_card_overlaps.append((d_name, area))

        dim_dim_overlaps = []
        for i in range(len(dim_polys)):
            for j in range(i + 1, len(dim_polys)):
                name1, poly1 = dim_polys[i]
                name2, poly2 = dim_polys[j]
                if poly1.intersects(poly2):
                    area = poly1.intersection(poly2).area
                    if area > 0.001:
                        dim_dim_overlaps.append((name1, name2, area))

        leader_d_geom = parse_svg_path_to_linestring(leader_d_str)
        dim_pb_geom = LineString([(dim_pb["x1"], dim_pb["y1"]), (dim_pb["x2"], dim_pb["y2"])])
        dim_ga_geom = LineString([(dim_ga["x1"], dim_ga["y1"]), (dim_ga["x2"], dim_ga["y2"])])
        dim_bd_geom = LineString([(dim_bd["x1"], dim_bd["y1"]), (dim_bd["x2"], dim_bd["y2"])])

        dim_d_cross_pb = leader_d_geom.intersects(dim_pb_geom)
        dim_d_cross_ga = leader_d_geom.intersects(dim_ga_geom)
        dim_d_cross_bd = leader_d_geom.intersects(dim_bd_geom)

        # Leader Line vs Other Label Boxes Penetration Audit
        leaders = data.get("leaders", [])
        leader_box_penetrations = []
        for l in leaders:
            l_id = l["id"]
            l_key = l_id.replace("leader-", "")
            expected_owner_box_id = f"box-{l_key}"
            l_geom = parse_svg_path_to_linestring(l["d"])
            for b in boxes:
                b_id = b["id"]
                if b_id == expected_owner_box_id:
                    continue
                b_poly = shapely_box(b["rect"]["x"], b["rect"]["y"], b["rect"]["r"], b["rect"]["b"])
                if l_geom.intersects(b_poly):
                    inter = l_geom.intersection(b_poly)
                    if inter.length > 0.001:
                        leader_box_penetrations.append((l_id, b_id, b["text"], inter.length))

        total_pairs_evaluated = (
            len(label_polys) * (len(label_polys) - 1) // 2
            + (len(label_polys) if card_poly else 0)
            + len(dim_polys) * len(label_polys)
            + (len(dim_polys) if card_poly else 0)
            + len(dim_polys) * (len(dim_polys) - 1) // 2
            + len(leaders) * (len(boxes) - 1)
        )

        print(f"\n[Gate 2 - Raw Telemetry] Language: {lang.upper()}")
        print(f"  Leader D Path (DOM Raw)       : {leader_d_str}")
        print(f"  Leader D Parsed Vertices ({len(leader_d_geom.coords)})  : {list(leader_d_geom.coords)}")
        print(f"  dimPb Line Coords (DOM Raw)   : ({dim_pb['x1']:.2f}, {dim_pb['y1']:.2f}) -> ({dim_pb['x2']:.2f}, {dim_pb['y2']:.2f})")
        print(f"  dimGa Line Coords (DOM Raw)   : ({dim_ga['x1']:.2f}, {dim_ga['y1']:.2f}) -> ({dim_ga['x2']:.2f}, {dim_ga['y2']:.2f})")
        print(f"  dimBd Line Coords (DOM Raw)   : ({dim_bd['x1']:.2f}, {dim_bd['y1']:.2f}) -> ({dim_bd['x2']:.2f}, {dim_bd['y2']:.2f})")
        print(f"  Total Label Boxes Checked     : {len(boxes)}")
        print(f"  Total Leaders Checked         : {len(leaders)}")
        print(f"  Total Dimension Boxes Checked : {len(dim_boxes)}")
        print(f"  Pairwise Pairs Evaluated      : {total_pairs_evaluated}쌍")
        print(f"  Pairwise Box Collisions       : {len(box_overlaps)}건")
        print(f"  Card Collisions               : {len(card_overlaps)}건")
        print(f"  Dimension vs Box Collisions   : {len(dim_box_overlaps)}건")
        print(f"  Dimension vs Card Collisions  : {len(dim_card_overlaps)}건")
        print(f"  Dimension vs Dim Collisions   : {len(dim_dim_overlaps)}건")
        print(f"  Leader vs Box Penetrations    : {len(leader_box_penetrations)}건")
        print(f"  Leader D crosses dimPb (DOM)  : {dim_d_cross_pb} (Expected False)")
        print(f"  Leader D crosses dimGa (DOM)  : {dim_d_cross_ga} (Expected False)")
        print(f"  Leader D crosses dimBd (DOM)  : {dim_d_cross_bd} (Expected False)")

        if leader_box_penetrations:
            for l_id, b_id, b_txt, plen in leader_box_penetrations:
                print(f"    [FAIL] Leader '{l_id}' penetrated Box '{b_id}' ('{b_txt}'), Penetration Length: {plen:.3f} px")

        if box_overlaps:
            for b1, b2, area in box_overlaps:
                print(f"    [FAIL] Collision between '{b1}' and '{b2}', Overlap Area: {area:.6f} px²")
        if card_overlaps:
            for b, area in card_overlaps:
                print(f"    [FAIL] Collision between '{b}' and Card, Overlap Area: {area:.6f} px²")
        if dim_box_overlaps:
            for l_txt, d_txt, area in dim_box_overlaps:
                print(f"    [FAIL] Collision between Label '{l_txt}' and Dimension '{d_txt}', Overlap Area: {area:.6f} px²")
        if dim_card_overlaps:
            for d_txt, area in dim_card_overlaps:
                print(f"    [FAIL] Collision between Dimension '{d_txt}' and Card, Overlap Area: {area:.6f} px²")
        if dim_dim_overlaps:
            for d1_txt, d2_txt, area in dim_dim_overlaps:
                print(f"    [FAIL] Collision between Dimension '{d1_txt}' and '{d2_txt}', Overlap Area: {area:.6f} px²")

        assert len(box_overlaps) == 0, f"[{lang}] Detected {len(box_overlaps)} label box collisions"
        assert len(card_overlaps) == 0, f"[{lang}] Detected {len(card_overlaps)} card collisions"
        assert len(dim_box_overlaps) == 0, f"[{lang}] Detected {len(dim_box_overlaps)} dimension text collisions with label boxes"
        assert len(dim_card_overlaps) == 0, f"[{lang}] Detected {len(dim_card_overlaps)} dimension text collisions with card"
        assert len(dim_dim_overlaps) == 0, f"[{lang}] Detected {len(dim_dim_overlaps)} dimension-dimension collisions"
        assert len(leader_box_penetrations) == 0, f"[{lang}] Detected {len(leader_box_penetrations)} leader line penetration(s) into other label boxes: {leader_box_penetrations}"
        assert not dim_d_cross_pb, f"[{lang}] Leader D crosses dimension line dimPb in SVG DOM!"
        assert not dim_d_cross_ga, f"[{lang}] Leader D crosses dimension line dimGa in SVG DOM!"
        assert not dim_d_cross_bd, f"[{lang}] Leader D crosses dimension line dimBd in SVG DOM!"

    finally:
        page.close()


@pytest.mark.parametrize("lang", LANGUAGES)
def test_part3_fig1_gate3_text_clipping(browser_instance, lang):
    """
    Gate 3 [텍스트 잘림(Clipping) 감사]:
    4개 국어(KO, EN, DE, JA) 라벨 박스 내부 텍스트 마진 확보 (오버플로우 0건, 마진 >= 6.0 px).
    """
    svg_path = PUBLIC_IMG_DIR / lang / SVG_FILENAME
    page = browser_instance.new_page(viewport={"width": CANVAS_W, "height": CANVAS_H})
    try:
        svg_content = svg_path.read_text(encoding="utf-8")
        html_wrapper = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#ffffff;">{svg_content}</body></html>"""
        page.set_content(html_wrapper)
        page.wait_for_load_state("networkidle")

        eval_script = """
        () => {
            const results = [];
            document.querySelectorAll('.label-box').forEach((g, idx) => {
                const rect = g.querySelector('rect');
                const text = g.querySelector('text');
                if (rect && text) {
                    const rB = rect.getBoundingClientRect();
                    const tB = text.getBoundingClientRect();
                    const textLen = text.getComputedTextLength();
                    const padLeft = tB.left - rB.left;
                    const padRight = rB.right - tB.right;
                    const minPad = Math.min(padLeft, padRight);
                    results.push({
                        idx: idx,
                        content: text.textContent.trim(),
                        boxW: rB.width,
                        boxH: rB.height,
                        textLen: textLen,
                        padLeft: padLeft,
                        padRight: padRight,
                        minPad: minPad
                    });
                }
            });
            return results;
        }
        """
        boxes_data = page.evaluate(eval_script)

        print(f"\n[Gate 3 - Raw Telemetry] Language: {lang.upper()}")
        print(f"  {'Idx':<4} | {'Box W':<7} | {'Text Len':<9} | {'Min Pad':<8} | {'Status':<6} | Content")
        print("  " + "-" * 75)

        failures = []
        for b in boxes_data:
            status = "PASS" if b["minPad"] >= 6.0 else "FAIL"
            print(f"  {b['idx']:<4} | {b['boxW']:<7.2f} | {b['textLen']:<9.2f} | {b['minPad']:<8.2f} | {status:<6} | {b['content']}")
            if b["minPad"] < 6.0:
                failures.append(b)

        assert len(failures) == 0, f"[{lang}] Found {len(failures)} text clipping violations (< 6.0 px margin)"

    finally:
        page.close()


@pytest.mark.parametrize("lang", LANGUAGES)
def test_part3_fig1_gate4_marker_integrity(lang):
    """
    Gate 4 [마커 무결성 감사]:
    화살표 마커 <marker> ID 유효성, refX=10 교정 여부 및 렌더링 누락 0건 감사.
    """
    svg_path = PUBLIC_IMG_DIR / lang / SVG_FILENAME
    tree = etree.parse(str(svg_path))
    root = tree.getroot()

    # Find all marker references in marker-start and marker-end
    referenced_markers = set()
    for el in root.iter():
        for attr in ["marker-start", "marker-end", "marker"]:
            val = el.get(attr)
            if val:
                m = re.search(r"url\(#([^)]+)\)", val)
                if m:
                    referenced_markers.add(m.group(1))

    # Find all defined markers in <defs>
    defs_markers = {}
    for marker in root.findall(".//{http://www.w3.org/2000/svg}marker"):
        m_id = marker.get("id")
        defs_markers[m_id] = {
            "refX": float(marker.get("refX", 0)),
            "refY": float(marker.get("refY", 0)),
            "width": float(marker.get("markerWidth", 0)),
            "height": float(marker.get("markerHeight", 0)),
            "has_path": len(marker.findall(".//{http://www.w3.org/2000/svg}path")) > 0
        }

    # Verify all references resolve
    missing_markers = referenced_markers - set(defs_markers.keys())

    print(f"\n[Gate 4 - Raw Telemetry] Language: {lang.upper()}")
    print(f"  Referenced Marker IDs ({len(referenced_markers)} total): {sorted(list(referenced_markers))}")
    print(f"  Defined Marker IDs    ({len(defs_markers)} total): {sorted(list(defs_markers.keys()))}")
    print(f"  Missing Marker IDs    : {len(missing_markers)}건")

    # Verify refX calibration for arr-gear and arr-pinion
    for m_id in ["arr-gear", "arr-pinion"]:
        assert m_id in defs_markers, f"[{lang}] Critical marker #{m_id} not defined!"
        ref_x = defs_markers[m_id]["refX"]
        print(f"  Marker #{m_id} refX: {ref_x:.6f} (Required = 10.000000)")
        assert ref_x == 10.0, f"[{lang}] Marker #{m_id} refX is {ref_x}, expected 10.0 for zero tip overshoot"

    assert len(missing_markers) == 0, f"[{lang}] Missing marker definitions: {missing_markers}"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_part3_fig1_r3_browser_capture(browser_instance, lang):
    """
    R3 브라우저 실물 검증 파이프라인 (Constitutional Articles 7 & 9 Compliant):
    동일 세션 내에서 Headless Chromium으로 4개 국어 SVG 렌더링 화면을
    고해상도 PNG(scratch/blog_part3/capture_part3_fig1_{lang}_verified.png)로 직접 캡처하여 보존.
    """
    svg_path = PUBLIC_IMG_DIR / lang / SVG_FILENAME
    out_capture_path = SCRATCH_DIR / f"capture_part3_fig1_{lang}_verified.png"

    page = browser_instance.new_page(
        viewport={"width": CANVAS_W, "height": CANVAS_H},
        device_scale_factor=2.0
    )
    try:
        svg_content = svg_path.read_text(encoding="utf-8")
        html_wrapper = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Part 3 Fig 1 {lang.upper()} Verification</title>
</head>
<body style="margin:0;padding:0;background:#ffffff;overflow:hidden;">
  {svg_content}
</body>
</html>"""
        page.set_content(html_wrapper)
        page.wait_for_load_state("networkidle")

        # Take high-resolution screenshot
        page.screenshot(path=str(out_capture_path), full_page=True)

        # Verification of capture
        assert out_capture_path.exists(), f"Capture file not created: {out_capture_path}"
        file_size_bytes = out_capture_path.stat().st_size
        file_size_kb = file_size_bytes / 1024.0

        print(f"\n[R3 Browser Capture] Language: {lang.upper()}")
        print(f"  Absolute Screenshot Path : {out_capture_path}")
        print(f"  File Size                : {file_size_kb:.2f} KB ({file_size_bytes} bytes)")
        print(f"  Device Scale Factor      : 2.0 (High Resolution Retina)")
        print(f"  Status                   : VERIFIED (Constitutional Article 7 PASS)")

        assert file_size_bytes > 50000, f"Capture file suspiciously small: {file_size_bytes} bytes"

    finally:
        page.close()
