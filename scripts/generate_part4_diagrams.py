"""
H-GEAR STUDIO Blog Part 4 Academic Diagram Generator (Multilingual & High-Precision)
=====================================================================================
Generates high-precision, publication-quality SVG and PNG diagrams for Chapter 4:
  1. Fig 1: Rack Cutter Profile Shift & Undercut Elimination (fig1_rack_cutter_shift_undercut)
  2. Fig 2: Operating Mesh Geometry (Working Center Distance a' & Pressure Angle alpha_w) (fig2_operating_mesh_geometry)
  3. Fig 3: Specific Sliding Balancing Curves (k1, k2 Along Path of Contact) (fig3_specific_sliding_balancing)

Applied Engineering Design Standards:
  - 100% Regular font weights (no bold fonts)
  - Mathematical font scaling for web container (~720px~768px)
  - Strict line-weight hierarchy:
      * Core curve / Line of action: 1.4 ~ 1.5 pt
      * Fundamental circles: 1.0 ~ 1.2 pt
      * Dimension & leader lines: 0.8 ~ 1.0 pt
      * Centerlines & reference: 0.6 ~ 0.8 pt
      * Contact path highlight band: 3.6 ~ 4.8 pt
  - Zero-overlap layout: radial offsets, leader lines, isolated callout cards
  - Dynamic multilingual typography (ko, en, de, ja)
  - Lossless vector SVG (svg.fonttype='path') and publication 300 DPI PNG (W>=2400, H>=1600)
"""

import os
import sys
import json
import math
import argparse
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "prototype2" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
from core.tooth_geometry import GearToothGeometry
from core.tooth_options import ToothOptions

BLOG_DIR = REPO_ROOT / "blog"
LOCALES_DIR = BLOG_DIR / "data" / "locales"
SPECS_DIR = BLOG_DIR / "data" / "specs"
DEFAULT_OUTPUT_DIR = BLOG_DIR / "public" / "images" / "part4"

# ---------------------------------------------------------------------------
# High-Contrast Academic Engineering Palette
# ---------------------------------------------------------------------------
COLOR_BG = "#FFFFFF"
COLOR_PINION = "#1D4ED8"       # Royal Deep Blue (Pinion geometry / Flank)
COLOR_GEAR = "#0F766E"         # Forest Teal (Gear geometry / Tip circle)
COLOR_NORMAL = "#E11D48"       # Vivid Crimson (Line of action / Contact points)
COLOR_TANGENT = "#7C3AED"      # Slate Violet (Pitch circle / Tangents)
COLOR_CONTACT = "#D97706"      # Amber Gold (Contact point / Pure rolling)
COLOR_HIGHLIGHT = "#EA580C"    # Intense Orange (Single tooth contact 100% load band)
COLOR_DOUBLE = "#0284C7"       # Sky Blue (Double tooth contact 50% load band)
COLOR_TEXT_MAIN = "#0F172A"    # Dark Slate 900
COLOR_TEXT_MUTED = "#64748B"   # Muted Slate 500
COLOR_GRID = "#E2E8F0"         # Light Gray grid/border
COLOR_AXIS = "#94A3B8"         # Neutral Slate centerline / reference
COLOR_CARD_BG = "#F8FAFC"      # Card container background
COLOR_CARD_BORDER = "#94A3B8"  # Card container border
COLOR_RACK = "#475569"         # Slate for rack cutter

LANGUAGE_FONT_PROFILES = {
    'ko': ['Malgun Gothic', 'Noto Sans KR', 'Segoe UI', 'DejaVu Sans', 'Arial'],
    'ja': ['Meiryo', 'Yu Gothic', 'MS Gothic', 'Noto Sans JP', 'Segoe UI', 'DejaVu Sans', 'Arial'],
    'de': ['Segoe UI', 'DejaVu Sans', 'Arial', 'Liberation Sans'],
    'en': ['Segoe UI', 'DejaVu Sans', 'Arial', 'Liberation Sans'],
}

SOUND_ROOT_LABELS = {
    'ko': "건전 치근 (No Undercut)",
    'en': "Sound Root (No Undercut)",
    'de': "Gesunder Zahnfuss (Kein Hinterschnitt)",
    'ja': "健全歯元 (アンダーカットなし)",
}

IDENTITY_LABELS = {
    'ko': ("항등식: $(1 - k_1)(1 - k_2) \\equiv 1.0$", "(무전위 시 $s_A < 0$ 언더컷 발산 -> 전위 후 건전 구간 안착)"),
    'en': ("Identity: $(1 - k_1)(1 - k_2) \\equiv 1.0$", "(Unshifted: $s_A < 0$ Undercut Divergence -> Shifted: Stable Region)"),
    'de': ("Identitaet: $(1 - k_1)(1 - k_2) \\equiv 1.0$", "(Ohne Verschiebung: $s_A < 0$ Hinterschnitt -> Mit Verschiebung: Stabil)"),
    'ja': ("恒等式: $(1 - k_1)(1 - k_2) \\equiv 1.0$", "(無転位時: $s_A < 0$ アンダーカット発散 -> 転位後: 健全領域)"),
}


def apply_language_typography(lang: str):
    """
    Configures Matplotlib typography profile per language.
    Guarantees CJK glyph coverage, regular weight hierarchy, and vector SVG export.
    """
    if lang not in LANGUAGE_FONT_PROFILES:
        lang = 'en'
    font_list = LANGUAGE_FONT_PROFILES[lang]
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['font.weight'] = 'normal'
    plt.rcParams['axes.labelweight'] = 'normal'
    plt.rcParams['axes.titleweight'] = 'normal'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['mathtext.fontset'] = 'dejavusans'
    plt.rcParams['svg.fonttype'] = 'path'


def load_locale_dict(lang: str) -> dict:
    """Loads localized strings for Chapter 4."""
    fpath = LOCALES_DIR / lang / "part4_labels.json"
    if fpath.is_file():
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _inject_svg_markers(svg_path: Path):
    """
    Injects standard ISO 128 / ISO 129-1 compliant marker definitions into SVG,
    guaranteeing refX=10.0 apex alignment (tip overshoot = 0.000 px).
    Binds markers to dimension and leader lines using SVG marker-end attribute.
    """
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = '{http://www.w3.org/2000/svg}'

    defs_elem = root.find(f"{ns}defs")
    if defs_elem is None:
        defs_elem = root.find("defs")
    if defs_elem is None:
        defs_elem = ET.Element(f"{ns}defs")
        root.insert(0, defs_elem)

    markers_to_add = [
        ('arr-pinion', COLOR_PINION, '10.0', '5.0', 'M 0 1.5 L 10 5 L 0 8.5 z'),
        ('arr-gear', COLOR_GEAR, '10.0', '5.0', 'M 0 1.5 L 10 5 L 0 8.5 z'),
        ('arr-action', COLOR_NORMAL, '10.0', '5.0', 'M 0 1.5 L 10 5 L 0 8.5 z'),
        ('arr-limit', '#7C3AED', '10.0', '5.0', 'M 0 1.5 L 10 5 L 0 8.5 z'),
        ('arr-contact', COLOR_CONTACT, '10.0', '5.0', 'M 0 1.5 L 10 5 L 0 8.5 z'),
        ('arr-end-norm', COLOR_NORMAL, '10.0', '5.0', 'M 0 1.5 L 10 5 L 0 8.5 z'),
        ('arr-start-norm', COLOR_NORMAL, '0.0', '5.0', 'M 10 1.5 L 0 5 L 10 8.5 z'),
    ]

    existing_ids = set()
    for m in defs_elem.findall(f"{ns}marker") + defs_elem.findall("marker"):
        m_id = m.get("id")
        if m_id:
            existing_ids.add(m_id)

    for m_id, color, ref_x, ref_y, path_d in markers_to_add:
        if m_id not in existing_ids:
            marker = ET.SubElement(defs_elem, f"{ns}marker", {
                'id': m_id,
                'viewBox': '0 0 10 10',
                'refX': ref_x,
                'refY': ref_y,
                'markerWidth': '6',
                'markerHeight': '6',
                'orient': 'auto-start-reverse'
            })
            ET.SubElement(marker, f"{ns}path", {
                'd': path_d,
                'fill': color
            })

    # Real marker bindings to dimension and leader line elements
    marker_bindings = {
        # Fig 1 dimension lines and leader lines
        'dim_line_sF_panel_a': 'arr-end-norm',
        'dim_line_sF_panel_b': 'arr-end-norm',
        'dim_line_sF_panel_c': 'arr-end-norm',
        'leader_shift_panel_a': 'arr-pinion',
        'leader_shift_panel_c': 'arr-pinion',
        # Fig 2 leader arrows
        'leader_point_a': 'arr-action',
        'leader_point_b': 'arr-limit',
        'leader_point_p': 'arr-contact',
        'leader_point_d': 'arr-limit',
        'leader_point_e': 'arr-gear',
        # Fig 3 leader arrows (leader_point_a, leader_point_e, leader_point_p)
    }

    for elem in root.iter():
        elem_id = elem.get('id', '')
        if elem_id in marker_bindings:
            m_id = marker_bindings[elem_id]
            paths = elem.findall(f"{ns}path") + elem.findall("path")
            if len(paths) >= 1:
                paths[0].set('marker-end', f'url(#{m_id})')
                if len(paths) >= 2:
                    elem.remove(paths[1])
            elif elem.tag.endswith('path'):
                elem.set('marker-end', f'url(#{m_id})')

    tree.write(svg_path, encoding='utf-8', xml_declaration=True)


def _verify_and_stamp_png_dpi(png_path: Path, target_dpi: int = 300):
    """
    Guarantees exact 5,250 x 3,833 px dimensions and exact 300 DPI metadata in PNG.
    """
    target_size = (5250, 3833)
    with Image.open(png_path) as img:
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
        img.save(png_path, format="PNG", dpi=(target_dpi, target_dpi))


def save_diagram(fig, base_name: str, output_dir: Path, dpi: int, formats: str):
    """Saves figure in requested formats with exact 5,250 x 3,833 px 300 DPI canvas dimensions and refX=10.0 markers."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    if formats in ('all', 'svg'):
        svg_path = output_dir / f"{base_name}.svg"
        fig.savefig(svg_path, format='svg', facecolor=COLOR_BG, edgecolor='none')
        _inject_svg_markers(svg_path)
        saved_paths.append(svg_path)
    if formats in ('all', 'png'):
        png_path = output_dir / f"{base_name}.png"
        fig.savefig(png_path, format='png', dpi=dpi, facecolor=COLOR_BG, edgecolor='none')
        _verify_and_stamp_png_dpi(png_path, target_dpi=300)
        saved_paths.append(png_path)
    plt.close(fig)
    for p in saved_paths:
        size_kb = p.stat().st_size / 1024
        print(f"  [SAVED] {p.name:<44} ({size_kb:6.1f} KB) -> {p.parent.name}")


# ==============================================================================
# Diagram 1: Rack Cutter Profile Shift & Undercut Elimination
# ==============================================================================
def create_diagram_1(output_dir: Path, dpi: int = 300, formats: str = 'all', lang: str = 'ko'):
    apply_language_typography(lang)
    tr = load_locale_dict(lang)

    fig = plt.figure(figsize=(17.5, 3833.0 / 300.0), dpi=dpi, facecolor=COLOR_BG)
    fig.suptitle(tr.get('fig1_title', 'Fig 1'), fontsize=15.5, color=COLOR_TEXT_MAIN, y=0.96)

    # 3-Panel comparison for x = -0.30, x = 0.00, x = +0.35
    axes = [
        fig.add_axes([0.06, 0.22, 0.28, 0.68]),
        fig.add_axes([0.37, 0.22, 0.28, 0.68]),
        fig.add_axes([0.68, 0.22, 0.28, 0.68])
    ]

    panel_configs = [
        {
            'panel_id': 'panel_a',
            'ax': axes[0],
            'title': tr.get('fig1_panel_a_title', 'x = -0.30 (Undercut)'),
            'x_shift': -0.30,
            'rf': 16.35,
            'ra': 23.10,
            'sF': 3.62,
            'undercut': True,
            'notch_color': '#DC2626',
            'box_color': '#FEE2E2',
            'border_color': '#EF4444'
        },
        {
            'panel_id': 'panel_b',
            'ax': axes[1],
            'title': tr.get('fig1_panel_b_title', 'x = 0.00 (Standard)'),
            'x_shift': 0.00,
            'rf': 17.25,
            'ra': 24.00,
            'sF': 4.38,
            'undercut': True,
            'notch_color': '#EA580C',
            'box_color': '#FEF3C7',
            'border_color': '#F59E0B'
        },
        {
            'panel_id': 'panel_c',
            'ax': axes[2],
            'title': tr.get('fig1_panel_c_title', 'x = +0.35 (Positive Shift)'),
            'x_shift': +0.35,
            'rf': 18.30,
            'ra': 25.05,
            'sF': 5.24,
            'undercut': False,
            'notch_color': '#059669',
            'box_color': '#ECFDF5',
            'border_color': '#10B981'
        }
    ]

    m = 3.0
    z1 = 14
    alpha0_deg = 20.0
    alpha0 = math.radians(alpha0_deg)
    r_pitch = z1 * m / 2.0  # 21.0
    r_base = r_pitch * math.cos(alpha0)  # 19.733545
    pitch = math.pi * m  # 9.424778
    y_N = r_pitch * (math.cos(alpha0) ** 2)  # 18.543 mm (Interference limit)

    for p in panel_configs:
        ax = p['ax']
        pid = p['panel_id']
        x_shift = p['x_shift']
        shift_mm = x_shift * m

        # Concentric Reference Circles
        theta = np.linspace(-0.6, 0.6, 150)
        ax.plot(r_pitch * np.sin(theta), r_pitch * np.cos(theta), '--', color=COLOR_TANGENT, lw=1.1, label=tr.get('fig1_pitch_line', 'Pitch Circle'), gid=f"pitch_circle_{pid}")
        ax.plot(r_base * np.sin(theta), r_base * np.cos(theta), '-.', color=COLOR_PINION, lw=1.1, label=tr.get('fig1_base_circle', 'Base Circle'), gid=f"base_circle_{pid}")
        ax.plot(p['rf'] * np.sin(theta), p['rf'] * np.cos(theta), ':', color=COLOR_AXIS, lw=1.0, label=tr.get('fig1_root_circle', 'Root Circle'), gid=f"root_circle_{pid}")
        ax.plot(p['ra'] * np.sin(theta), p['ra'] * np.cos(theta), '-', color=COLOR_GEAR, lw=1.2, label=tr.get('fig1_tip_circle', 'Tip Circle'), gid=f"tip_circle_{pid}")

        # Interference Limit Line N (Theoretical Limit of Involute Action)
        ax.plot(r_pitch * np.sin(theta) * 0.9, np.full_like(theta, y_N), ':', color='#DC2626', lw=0.9, alpha=0.75, label=f"N (y={y_N:.2f} mm)", gid=f"interference_N_{pid}")

        # Exact Involute & Litvin Rack Cutter Trochoid Fillet Profile (Backend Single Source of Truth)
        g = GearToothGeometry(ToothOptions(
            module=m,
            z=z1,
            x=x_shift,
            alpha_n_deg=alpha0_deg,
            fillet_rho_coeff=0.38,
            num_involute_pts=80,
            num_fillet_pts=80,
            num_tip_pts=30
        ))

        # Flanks: Left & Right (Exact Analytical Involute, Tapered sa < sp < sb)
        ax.plot(-g.x_inv_std, g.y_inv_std, '-', color=COLOR_PINION, lw=1.8, gid=f"flank_left_{pid}")
        ax.plot(g.x_inv_std, g.y_inv_std, '-', color=COLOR_PINION, lw=1.8, gid=f"flank_right_{pid}")

        # Top Land
        ax.plot(g.x_tip_std, g.y_tip_std, '-', color=COLOR_GEAR, lw=1.6, gid=f"tip_{pid}")

        # Root & Trochoid Fillet (Exact Litvin Rack Cutter Generation)
        fillet_lw = 1.6
        if p['undercut']:
            ax.plot(-g.x_fil_std, g.y_fil_std, '--', color=p['notch_color'], lw=fillet_lw, gid=f"fillet_left_{pid}")
            ax.plot(g.x_fil_std, g.y_fil_std, '--', color=p['notch_color'], lw=fillet_lw, gid=f"fillet_right_{pid}")
            ax.text(0.0, p['rf'] + 0.55, tr.get('fig1_undercut_trochoid', 'Undercut Notch'),
                    fontsize=8.2, color=p['notch_color'], ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.50", fc=p['box_color'], ec=p['border_color'], lw=0.8))
        else:
            ax.plot(-g.x_fil_std, g.y_fil_std, '-', color=COLOR_PINION, lw=fillet_lw, gid=f"fillet_left_{pid}")
            ax.plot(g.x_fil_std, g.y_fil_std, '-', color=COLOR_PINION, lw=fillet_lw, gid=f"fillet_right_{pid}")
            sound_label = SOUND_ROOT_LABELS.get(lang, "Sound Root (No Undercut)")
            ax.text(0.0, p['rf'] + 0.55, sound_label,
                    fontsize=8.2, color=p['notch_color'], ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.50", fc=p['box_color'], ec=p['border_color'], lw=0.8))

        # Root Circle bottom arc connecting fillets
        ang_root = math.atan2(float(g.x_fil_std[0]), float(g.y_fil_std[0]))
        th_root = np.linspace(-ang_root, ang_root, 30)
        ax.plot(p['rf'] * np.sin(th_root), p['rf'] * np.cos(th_root), '-', color=COLOR_AXIS, lw=1.2, gid=f"root_bottom_{pid}")

        # Fill Gear Tooth Body with subtle tint
        poly_full_x = np.concatenate([
            -g.x_inv_std[::-1],
            g.x_tip_std,
            g.x_inv_std,
            g.x_fil_std[::-1],
            p['rf'] * np.sin(th_root[::-1]),
            -g.x_fil_std
        ])
        poly_full_y = np.concatenate([
            g.y_inv_std[::-1],
            g.y_tip_std,
            g.y_inv_std,
            g.y_fil_std[::-1],
            p['rf'] * np.cos(th_root[::-1]),
            g.y_fil_std
        ])
        ax.fill(poly_full_x, poly_full_y, color='#DBEAFE', alpha=0.35, zorder=2)

        # Rack Cutter Tool in Physical Engagement
        y_rack_datum = r_pitch + shift_mm
        ax.axhline(y=y_rack_datum, color=COLOR_RACK, lw=1.1, linestyle='-', alpha=0.85, gid=f"rack_datum_{pid}", label=tr.get('fig1_rack_datum_line', 'Rack Datum Line') if p == panel_configs[0] else None)

        # Draw Rack Cutter Teeth (Trapezoidal cutting tool engaging the spaces)
        y_tip_rack = y_rack_datum - 1.25 * m
        y_root_rack = y_rack_datum + 1.0 * m
        for xc in [-pitch / 2.0, pitch / 2.0]:
            w_tip = pitch / 4.0 - (y_tip_rack - y_rack_datum) * math.tan(alpha0)
            w_root = pitch / 4.0 - (y_root_rack - y_rack_datum) * math.tan(alpha0)
            rack_poly = [
                (xc - w_root, y_root_rack),
                (xc + w_root, y_root_rack),
                (xc + w_tip, y_tip_rack),
                (xc - w_tip, y_tip_rack)
            ]
            rack_patch = patches.Polygon(rack_poly, closed=True, facecolor='#FEF3C7', edgecolor='#D97706',
                                         lw=1.1, alpha=0.40, linestyle='--', zorder=1)
            ax.add_patch(rack_patch)

        # Mark rack tip line
        ax.plot([-5.5, 5.5], [y_tip_rack, y_tip_rack], ':', color='#D97706', lw=0.9, alpha=0.8)

        # Critical root thickness dimension (sF)
        sF_y = p['rf'] + 1.25
        sF_half = p['sF'] / 2.0
        ax.plot([-sF_half, sF_half], [sF_y, sF_y], '-', color=COLOR_NORMAL, lw=1.1, gid=f"dim_line_sF_{pid}")
        ax.scatter([-sF_half, sF_half], [sF_y, sF_y], color=COLOR_NORMAL, s=16, zorder=5)
        ax.text(0.0, sF_y + 0.42, f"{tr.get('fig1_critical_root_thickness', 'sF')} = {p['sF']:.2f} mm",
                fontsize=8.5, color=COLOR_NORMAL, ha='center', va='bottom',
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_NORMAL, lw=0.7))

        # Shift annotation arrow
        if abs(x_shift) > 0.01:
            ann_shift = ax.annotate(f"{tr.get('fig1_shift_amount', 'x*m')} = {shift_mm:+.2f} mm",
                        xy=(2.4, (r_pitch + y_rack_datum) / 2.0), xytext=(2.4, (r_pitch + y_rack_datum) / 2.0 + 1.2),
                        fontsize=8.0, color=COLOR_RACK, ha='right',
                        arrowprops=dict(arrowstyle="->", color=COLOR_RACK, lw=0.8),
                        bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_RACK, lw=0.7))
            ann_shift.arrow_patch.set_gid(f"leader_shift_{pid}")

        # Top Land thickness badge
        sa_calc = float(g.x_tip_std.max() - g.x_tip_std.min())
        ax.text(0.0, p['ra'] + 0.35, f"sa = {sa_calc:.2f} mm", fontsize=7.8, color=COLOR_GEAR, ha='center', va='bottom')

        ax.set_xlim(-6.5, 6.5)
        ax.set_ylim(14.5, 27.0)
        ax.set_aspect('equal')
        wrapped_title = textwrap.fill(p['title'], width=28) if len(p['title']) > 28 else p['title']
        ax.set_title(wrapped_title, fontsize=10.5, color=COLOR_TEXT_MAIN, pad=10)
        ax.grid(True, linestyle="--", alpha=0.4, color=COLOR_GRID)
        if p == panel_configs[0]:
            ax.legend(loc="upper left", fontsize=7.6, framealpha=0.92)

    # Bottom Summary Card
    card_ax = fig.add_axes([0.06, 0.025, 0.88, 0.15])
    card_ax.axis('off')
    card_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.04",
                                        fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0)
    card_ax.add_patch(card_patch)
    card_text = (
        f"{tr.get('fig1_summary_title', '[Summary]')}\n\n"
        f"{tr.get('fig1_summary_1', '')}\n"
        f"{tr.get('fig1_summary_2', '')}\n"
        f"{tr.get('fig1_summary_3', '')}\n"
        f"{tr.get('fig1_summary_note', '')}"
    )
    card_ax.text(0.5, 0.5, card_text, fontsize=8.6, color=COLOR_TEXT_MAIN, ha='center', va='center', linespacing=1.30)

    save_diagram(fig, "fig1_rack_cutter_shift_undercut", output_dir, dpi, formats)


# ==============================================================================
# Diagram 2: Operating Mesh Geometry (a -> a', alpha0 -> alphaw)
# ==============================================================================
def create_diagram_2(output_dir: Path, dpi: int = 300, formats: str = 'all', lang: str = 'ko'):
    apply_language_typography(lang)
    tr = load_locale_dict(lang)

    fig = plt.figure(figsize=(17.5, 3833.0 / 300.0), dpi=dpi, facecolor=COLOR_BG)
    fig.suptitle(tr.get('fig2_title', 'Fig 2'), fontsize=15.5, color=COLOR_TEXT_MAIN, y=0.96)

    ax = fig.add_axes([0.08, 0.23, 0.84, 0.67])

    # Theoretical Parameters
    m = 3.0
    z1 = 14
    z2 = 42
    alpha0_deg = 20.0
    alpha0 = math.radians(alpha0_deg)
    x1 = 0.35
    x2 = 0.15

    r1 = z1 * m / 2.0  # 21.0
    r2 = z2 * m / 2.0  # 63.0
    rb1 = r1 * math.cos(alpha0)  # 19.733545
    rb2 = r2 * math.cos(alpha0)  # 59.200635

    inv_alpha0 = math.tan(alpha0) - alpha0
    inv_alphaw = inv_alpha0 + 2.0 * (x1 + x2) / (z1 + z2) * math.tan(alpha0)

    alphaw = alpha0
    for _ in range(50):
        f = math.tan(alphaw) - alphaw - inv_alphaw
        df = math.tan(alphaw) ** 2
        alphaw -= f / df

    alphaw_deg = math.degrees(alphaw)
    a_std = (z1 + z2) * m / 2.0  # 84.0
    a_prime = a_std * math.cos(alpha0) / math.cos(alphaw)  # 85.414904
    delta_a = a_prime - a_std  # 1.414904

    rw1 = r1 * math.cos(alpha0) / math.cos(alphaw)  # 21.353726
    rw2 = r2 * math.cos(alpha0) / math.cos(alphaw)  # 64.061178

    O1 = np.array([0.0, rw1])
    O2 = np.array([0.0, -rw2])
    u_loa = np.array([math.cos(alphaw), -math.sin(alphaw)])

    # Tangency Points on Base Circles (T1, T2)
    s_T1 = -rw1 * math.sin(alphaw)  # -8.158972 mm
    s_T2 = rw2 * math.sin(alphaw)   # +24.476915 mm
    T1 = s_T1 * u_loa
    T2 = s_T2 * u_loa

    # Tip circles
    y_shift = delta_a / m
    k_shift = (x1 + x2) - y_shift
    ha1 = (1.0 + x1 - k_shift) * m
    ha2 = (1.0 + x2 - k_shift) * m
    ra1 = r1 + ha1  # 24.964904
    ra2 = r2 + ha2  # 66.364904

    # 5 Cardinal Points along LOA
    s_A = rw2 * math.sin(alphaw) - math.sqrt(ra2 ** 2 - rb2 ** 2)  # -5.515948
    s_E = -rw1 * math.sin(alphaw) + math.sqrt(ra1 ** 2 - rb1 ** 2)  # 7.132648
    pb = math.pi * m * math.cos(alpha0)  # 8.855998
    s_B = s_E - pb  # -1.723405
    s_D = s_A + pb  # 3.340446
    s_P = 0.0

    pts = {
        'T1': T1,
        'A': s_A * u_loa,
        'B': s_B * u_loa,
        'P': np.array([0.0, 0.0]),
        'D': s_D * u_loa,
        'E': s_E * u_loa,
        'T2': T2
    }

    # Concentric Circles
    th1 = np.linspace(-math.pi * 0.70, -math.pi * 0.30, 200)
    th2 = np.linspace(math.pi * 0.30, math.pi * 0.70, 200)

    # Working Pitch Circles (Tangent at P)
    ax.plot(O1[0] + rw1 * np.cos(th1), O1[1] + rw1 * np.sin(th1), '--', color=COLOR_TANGENT, lw=1.2, label=tr.get('fig2_op_pitch_pinion', 'Working Pitch dw1'), gid="op_pitch_pinion")
    ax.plot(O2[0] + rw2 * np.cos(th2), O2[1] + rw2 * np.sin(th2), '--', color=COLOR_GEAR, lw=1.2, label=tr.get('fig2_op_pitch_gear', 'Working Pitch dw2'), gid="op_pitch_gear")

    # Standard Pitch Circles (Thin dotted, separated by delta_a = 1.415 mm)
    ax.plot(O1[0] + r1 * np.cos(th1), O1[1] + r1 * np.sin(th1), ':', color=COLOR_AXIS, lw=0.9, label=tr.get('fig2_std_pitch_pinion', 'Std Pitch d1'), gid="std_pitch_pinion")
    ax.plot(O2[0] + r2 * np.cos(th2), O2[1] + r2 * np.sin(th2), ':', color=COLOR_AXIS, lw=0.9, gid="std_pitch_gear")

    # Base Circles
    ax.plot(O1[0] + rb1 * np.cos(th1), O1[1] + rb1 * np.sin(th1), '-.', color=COLOR_PINION, lw=1.1, label=tr.get('fig2_base_pinion', 'Base Circle db1'), gid="base_pinion")
    ax.plot(O2[0] + rb2 * np.cos(th2), O2[1] + rb2 * np.sin(th2), '-.', color=COLOR_GEAR, lw=1.1, label=tr.get('fig2_base_gear', 'Base Circle db2'), gid="base_gear")

    # Tip Circles
    ax.plot(O1[0] + ra1 * np.cos(th1), O1[1] + ra1 * np.sin(th1), '-', color=COLOR_PINION, lw=1.3, label=tr.get('fig2_tip_pinion', 'Tip Circle da1'), gid="tip_pinion")
    ax.plot(O2[0] + ra2 * np.cos(th2), O2[1] + ra2 * np.sin(th2), '-', color=COLOR_GEAR, lw=1.3, label=tr.get('fig2_tip_gear', 'Tip Circle da2'), gid="tip_gear")

    # Full Operating Line of Action (Passes through T1, P, T2)
    s_loa_full = np.linspace(s_T1 - 2.5, s_T2 + 2.5, 200)
    loa_full_pts = np.outer(s_loa_full, u_loa)
    ax.plot(loa_full_pts[:, 0], loa_full_pts[:, 1], '-', color=COLOR_NORMAL, lw=1.4, label=tr.get('fig2_loa_operating', 'Operating LOA'), gid="loa_line")

    # Base Circle Tangency Normal Radius Lines (O1-T1 and O2-T2)
    ax.plot([O1[0], T1[0]], [O1[1], T1[1]], '--', color=COLOR_PINION, lw=1.0, alpha=0.65, gid="rad_O1_T1")
    ax.plot([O2[0], T2[0]], [O2[1], T2[1]], '--', color=COLOR_GEAR, lw=1.0, alpha=0.65, gid="rad_O2_T2")

    # Working Pitch Tangent (Horizontal line through P)
    ax.axhline(0.0, color=COLOR_TANGENT, lw=1.0, linestyle='--', label=tr.get('fig2_pitch_tangent', 'Pitch Tangent'), gid="pitch_tangent")

    # Contact path highlight bands
    # Single tooth contact BD
    s_bd = np.linspace(s_B, s_D, 40)
    bd_pts = np.outer(s_bd, u_loa)
    ax.plot(bd_pts[:, 0], bd_pts[:, 1], '-', color=COLOR_HIGHLIGHT, lw=4.2, alpha=0.55, label=tr.get('fig2_dim_bd', 'Single Contact BD (100% Load)'), gid="single_contact_bd")

    # Active contact length AE
    s_ae = np.linspace(s_A, s_E, 60)
    ae_pts = np.outer(s_ae, u_loa)
    ax.plot(ae_pts[:, 0], ae_pts[:, 1], '-', color=COLOR_DOUBLE, lw=2.2, alpha=0.45, gid="active_contact_ae")

    # Contacting Involute Teeth meeting at P!
    r_p = np.linspace(rb1, ra1, 150)
    cos_ap = np.clip(rb1 / r_p, -1.0, 1.0)
    ap = np.arccos(cos_ap)
    inv_ap = np.tan(ap) - ap
    phi_p = -math.pi / 2.0 - (inv_ap - inv_alphaw)
    pinion_flank_x = O1[0] + r_p * np.cos(phi_p)
    pinion_flank_y = O1[1] + r_p * np.sin(phi_p)
    ax.plot(pinion_flank_x, pinion_flank_y, '-', color=COLOR_PINION, lw=2.2, alpha=0.90, gid="contact_flank_pinion")

    r_g = np.linspace(rb2, ra2, 200)
    cos_ag = np.clip(rb2 / r_g, -1.0, 1.0)
    ag = np.arccos(cos_ag)
    inv_ag = np.tan(ag) - ag
    phi_g = math.pi / 2.0 + (inv_ag - inv_alphaw)
    gear_flank_x = O2[0] + r_g * np.cos(phi_g)
    gear_flank_y = O2[1] + r_g * np.sin(phi_g)
    ax.plot(gear_flank_x, gear_flank_y, '-', color=COLOR_GEAR, lw=2.2, alpha=0.90, gid="contact_flank_gear")

    # Plot Point markers & Callouts
    ax.scatter([pts['T1'][0], pts['T2'][0]], [pts['T1'][1], pts['T2'][1]], color=COLOR_PINION, s=60, zorder=6)
    ax.scatter([pts['A'][0], pts['E'][0]], [pts['A'][1], pts['E'][1]], color=COLOR_NORMAL, s=55, zorder=6)
    ax.scatter([pts['B'][0], pts['D'][0]], [pts['B'][1], pts['D'][1]], color='#7C3AED', s=50, zorder=6)
    ax.scatter([pts['P'][0]], [pts['P'][1]], color=COLOR_CONTACT, s=65, zorder=7)

    # Orthogonal callout boxes with non-overlapping geometry
    ann_T1 = ax.annotate(tr.get('fig2_point_t1', 'T1 (Pinion Base Tangency)'), xy=pts['T1'], xytext=(pts['T1'][0] - 8.5, pts['T1'][1] + 4.2),
                fontsize=8.3, color=COLOR_PINION,
                arrowprops=dict(arrowstyle="->", color=COLOR_PINION, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_PINION, lw=0.8))
    ann_T1.arrow_patch.set_gid("leader_point_t1")

    ann_A = ax.annotate(tr.get('fig2_point_a', 'Point A (SAP)'), xy=pts['A'], xytext=(pts['A'][0] - 8.5, pts['A'][1] + 1.2),
                fontsize=8.5, color=COLOR_NORMAL,
                arrowprops=dict(arrowstyle="->", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_NORMAL, lw=0.8))
    ann_A.arrow_patch.set_gid("leader_point_a")

    ann_B = ax.annotate(tr.get('fig2_point_b', 'Point B (LPSTC)'), xy=pts['B'], xytext=(pts['B'][0] - 6.5, pts['B'][1] - 4.5),
                fontsize=8.5, color='#7C3AED',
                arrowprops=dict(arrowstyle="->", color='#7C3AED', lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec='#7C3AED', lw=0.8))
    ann_B.arrow_patch.set_gid("leader_point_b")

    ann_P = ax.annotate(tr.get('fig2_point_p', 'Point P (Working Pitch Point)'), xy=pts['P'], xytext=(pts['P'][0] + 3.2, pts['P'][1] + 5.2),
                fontsize=9.0, color=COLOR_CONTACT,
                arrowprops=dict(arrowstyle="->", color=COLOR_CONTACT, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_CONTACT, lw=0.9))
    ann_P.arrow_patch.set_gid("leader_point_p")

    ann_D = ax.annotate(tr.get('fig2_point_d', 'Point D (HPSTC)'), xy=pts['D'], xytext=(pts['D'][0] + 5.8, pts['D'][1] + 3.5),
                fontsize=8.5, color='#7C3AED',
                arrowprops=dict(arrowstyle="->", color='#7C3AED', lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec='#7C3AED', lw=0.8))
    ann_D.arrow_patch.set_gid("leader_point_d")

    ann_E = ax.annotate(tr.get('fig2_point_e', 'Point E (EAP)'), xy=pts['E'], xytext=(pts['E'][0] + 7.8, pts['E'][1] - 3.5),
                fontsize=8.5, color=COLOR_NORMAL,
                arrowprops=dict(arrowstyle="->", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_NORMAL, lw=0.8))
    ann_E.arrow_patch.set_gid("leader_point_e")

    ann_T2 = ax.annotate(tr.get('fig2_point_t2', 'T2 (Gear Base Tangency)'), xy=pts['T2'], xytext=(pts['T2'][0] - 2.5, pts['T2'][1] - 4.5),
                fontsize=8.3, color=COLOR_GEAR,
                arrowprops=dict(arrowstyle="->", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.50", fc="white", ec=COLOR_GEAR, lw=0.8))
    ann_T2.arrow_patch.set_gid("leader_point_t2")

    # Center distance & Operating parameters banner box
    param_box_text = (
        f"{tr.get('fig2_dim_center_distance', '')}\n"
        f"{tr.get('fig2_dim_g_alpha', '')}\n"
        f"{tr.get('fig2_dim_pb', '')}\n"
        f"{tr.get('fig2_dim_clearance', '')}"
    )
    ax.text(-24.5, -9.5, param_box_text, fontsize=8.5, color=COLOR_TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.50", fc="#F8FAFC", ec=COLOR_AXIS, lw=0.8), linespacing=1.35)

    ax.set_xlim(-26.0, 24.0)
    ax.set_ylim(-16.0, 16.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle="--", alpha=0.4, color=COLOR_GRID)
    ax.legend(loc="upper right", fontsize=8.0, framealpha=0.94)

    # Bottom Summary Card
    card_ax = fig.add_axes([0.08, 0.025, 0.84, 0.15])
    card_ax.axis('off')
    card_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.04",
                                        fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0)
    card_ax.add_patch(card_patch)
    card_text = (
        f"{tr.get('fig2_summary_title', '[Summary]')}\n\n"
        f"{tr.get('fig2_summary_1', '')}\n"
        f"{tr.get('fig2_summary_2', '')}\n"
        f"{tr.get('fig2_summary_3', '')}\n"
        f"{tr.get('fig2_summary_note', '')}"
    )
    card_ax.text(0.5, 0.5, card_text, fontsize=8.6, color=COLOR_TEXT_MAIN, ha='center', va='center', linespacing=1.30)

    save_diagram(fig, "fig2_operating_mesh_geometry", output_dir, dpi, formats)


# ==============================================================================
# Diagram 3: Specific Sliding Balancing Curves (k1, k2)
# ==============================================================================
def create_diagram_3(output_dir: Path, dpi: int = 300, formats: str = 'all', lang: str = 'ko'):
    apply_language_typography(lang)
    tr = load_locale_dict(lang)

    fig = plt.figure(figsize=(17.5, 3833.0 / 300.0), dpi=dpi, facecolor=COLOR_BG)
    fig.suptitle(tr.get('fig3_title', 'Fig 3'), fontsize=15.5, color=COLOR_TEXT_MAIN, y=0.96)

    ax = fig.add_axes([0.08, 0.23, 0.84, 0.67])

    # Parameters: u = 3.0, T1T2 = 32.635887 mm
    # Coordinate s from T1 (0 to 18 mm)
    u = 3.0
    T1T2 = 32.635887
    s = np.linspace(1.2, 17.5, 300)

    # Involute sliding ratios
    rho1 = s
    rho2 = T1T2 - s
    k1 = 1.0 - rho2 / (u * rho1)
    k2 = 1.0 - (u * rho1) / rho2

    # Standard unshifted curve comparison (sA_std < 0 leads to severe asymptote)
    s_std = np.linspace(0.8, 17.5, 300)
    T1T2_std = 28.729692
    k1_std = 1.0 - (T1T2_std - s_std) / (u * s_std)

    # Plot Curves
    ax.plot(s, k1, '-', color=COLOR_PINION, lw=1.8, label=tr.get('fig3_curve_k1', 'Pinion k1 (Shifted)'), gid="curve_k1")
    ax.plot(s, k2, '-', color=COLOR_GEAR, lw=1.8, label=tr.get('fig3_curve_k2', 'Gear k2 (Shifted)'), gid="curve_k2")
    ax.plot(s_std, k1_std, ':', color='#DC2626', lw=1.3, alpha=0.75, label=tr.get('fig3_curve_k1_std', 'Unshifted Pinion k1 (Undercut Divergence)'), gid="curve_k1_std")

    # Zero Line (Pure rolling)
    ax.axhline(0.0, color=COLOR_AXIS, lw=1.0, linestyle='--')

    # Singular Points along contact path:
    # A = 2.643 mm, B = 6.435 mm, P = 8.159 mm, D = 11.499 mm, E = 15.292 mm
    s_pts = {
        'A': 2.642798,
        'B': 6.435226,
        'P': 8.158972,
        'D': 11.499193,
        'E': 15.291620
    }

    # Plot vertical markers for singular points
    for pt_name, s_val in s_pts.items():
        ax.axvline(s_val, color=COLOR_GRID, lw=0.9, linestyle=':')

    # Marked points on Pinion k1 curve
    k1_A = 1.0 - (T1T2 - s_pts['A']) / (u * s_pts['A']) # -2.783
    k2_A = 1.0 - (u * s_pts['A']) / (T1T2 - s_pts['A']) # +0.736
    k1_E = 1.0 - (T1T2 - s_pts['E']) / (u * s_pts['E']) # +0.622
    k2_E = 1.0 - (u * s_pts['E']) / (T1T2 - s_pts['E']) # -1.645

    ax.scatter([s_pts['A']], [k1_A], color=COLOR_NORMAL, s=55, zorder=6)
    ax.scatter([s_pts['E']], [k2_E], color=COLOR_GEAR, s=55, zorder=6)
    ax.scatter([s_pts['P']], [0.0], color=COLOR_CONTACT, s=65, zorder=7)

    # Point Annotations
    ann_A = ax.annotate(tr.get('fig3_point_a', 'Point A (SAP): k1 = -2.783'),
                xy=(s_pts['A'], k1_A), xytext=(s_pts['A'] + 0.6, k1_A - 0.35),
                fontsize=8.5, color=COLOR_NORMAL,
                arrowprops=dict(arrowstyle="->", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.55", fc="white", ec=COLOR_NORMAL, lw=0.8))
    ann_A.arrow_patch.set_gid("leader_point_a")

    ann_E = ax.annotate(tr.get('fig3_point_e', 'Point E (EAP): k2 = -1.645'),
                xy=(s_pts['E'], k2_E), xytext=(s_pts['E'] - 4.5, k2_E - 0.45),
                fontsize=8.5, color=COLOR_GEAR,
                arrowprops=dict(arrowstyle="->", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.55", fc="white", ec=COLOR_GEAR, lw=0.8))
    ann_E.arrow_patch.set_gid("leader_point_e")

    ann_P = ax.annotate(tr.get('fig3_point_p', 'Point P (Pitch Point, Pure Rolling k=0)'),
                xy=(s_pts['P'], 0.0), xytext=(s_pts['P'] - 3.8, 0.45),
                fontsize=8.8, color=COLOR_CONTACT,
                arrowprops=dict(arrowstyle="->", color=COLOR_CONTACT, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.55", fc="white", ec=COLOR_CONTACT, lw=0.8))
    ann_P.arrow_patch.set_gid("leader_point_p")

    # Invariant & Balancing Ratio Card
    id_header, id_footer = IDENTITY_LABELS.get(lang, IDENTITY_LABELS['en'])
    info_box_text = (
        f"{id_header}\n"
        f"{tr.get('fig3_balancing_ratio', 'Balancing Ratio: |k1A| / |k2E| = 1.692')}\n"
        f"{id_footer}"
    )
    ax.text(1.2, 0.80, info_box_text, fontsize=8.6, color=COLOR_TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.55", fc="#FFFBEB", ec="#F59E0B", lw=0.8), linespacing=1.35)

    ax.set_xticks([s_pts['A'], s_pts['B'], s_pts['P'], s_pts['D'], s_pts['E']])
    ax.set_xticklabels([
        f"A (SAP)\n{s_pts['A']:.2f}",
        f"B (LPSTC)\n{s_pts['B']:.2f}",
        f"P (Pitch)\n{s_pts['P']:.2f}",
        f"D (HPSTC)\n{s_pts['D']:.2f}",
        f"E (EAP)\n{s_pts['E']:.2f}"
    ], fontsize=8.5)

    ax.set_xlim(0.0, 18.0)
    ax.set_ylim(-3.5, 1.5)
    ax.set_xlabel(tr.get('fig3_axis_s', 'Contact Path Coordinate s (mm)'), fontsize=9.2, color=COLOR_TEXT_MAIN)
    ax.set_ylabel(tr.get('fig3_axis_k', 'Specific Sliding k'), fontsize=9.2, color=COLOR_TEXT_MAIN)
    ax.grid(True, linestyle="--", alpha=0.4, color=COLOR_GRID)
    ax.legend(loc="lower right", fontsize=8.2, framealpha=0.94)

    # Bottom Summary Card
    card_ax = fig.add_axes([0.08, 0.025, 0.84, 0.15])
    card_ax.axis('off')
    card_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.04",
                                        fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0)
    card_ax.add_patch(card_patch)
    card_text = (
        f"{tr.get('fig3_summary_title', '[Summary]')}\n\n"
        f"{tr.get('fig3_summary_1', '')}\n"
        f"{tr.get('fig3_summary_2', '')}\n"
        f"{tr.get('fig3_summary_3', '')}\n"
        f"{tr.get('fig3_summary_note', '')}"
    )
    card_ax.text(0.5, 0.5, card_text, fontsize=8.6, color=COLOR_TEXT_MAIN, ha='center', va='center', linespacing=1.30)

    save_diagram(fig, "fig3_specific_sliding_balancing", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="H-GEAR STUDIO Blog Part 4 Academic Diagram Generator")
    parser.add_argument('--lang', choices=['all', 'ko', 'en', 'de', 'ja'], default='all')
    parser.add_argument('--fig', choices=['all', 'fig1', 'fig2', 'fig3'], default='all')
    parser.add_argument('--format', choices=['all', 'png', 'svg'], default='all')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--output-dir', type=str, default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    languages = ['ko', 'en', 'de', 'ja'] if args.lang == 'all' else [args.lang]
    figs = ['fig1', 'fig2', 'fig3'] if args.fig == 'all' else [args.fig]

    dispatch = {
        'fig1': create_diagram_1,
        'fig2': create_diagram_2,
        'fig3': create_diagram_3,
    }

    base_out = Path(args.output_dir)
    total_generated = 0

    print("=" * 80)
    print("H-GEAR STUDIO Part 4 Academic Diagram Generation Pipeline")
    print(f"  Languages: {languages}")
    print(f"  Diagrams:  {figs}")
    print(f"  Formats:   {args.format}")
    print(f"  DPI:       {args.dpi}")
    print(f"  Output:    {args.output_dir}")
    print("=" * 80)

    for lang in languages:
        lang_out = base_out / lang
        lang_out.mkdir(parents=True, exist_ok=True)
        print(f"\n--- Generating Language: [{lang.upper()}] ---")
        for fig_key in figs:
            fn = dispatch[fig_key]
            fn(output_dir=lang_out, dpi=args.dpi, formats=args.format, lang=lang)
            total_generated += (2 if args.format == 'all' else 1)

    print("\n" + "=" * 80)
    print(f"Pipeline Completed! Total Part 4 Assets Generated: {total_generated}")
    print("=" * 80)


if __name__ == '__main__':
    main()
