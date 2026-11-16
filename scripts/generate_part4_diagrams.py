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
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
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


def save_diagram(fig, base_name: str, output_dir: Path, dpi: int, formats: str):
    """Saves figure in requested formats with exact 300 DPI canvas dimensions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    if formats in ('all', 'svg'):
        svg_path = output_dir / f"{base_name}.svg"
        fig.savefig(svg_path, format='svg', facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(svg_path)
    if formats in ('all', 'png'):
        png_path = output_dir / f"{base_name}.png"
        fig.savefig(png_path, format='png', dpi=dpi, facecolor=COLOR_BG, edgecolor='none')
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

    fig = plt.figure(figsize=(15.0, 9.8), dpi=dpi, facecolor=COLOR_BG)
    fig.suptitle(tr.get('fig1_title', 'Fig 1'), fontsize=15.5, color=COLOR_TEXT_MAIN, y=0.96)

    # 3-Panel comparison for x = -0.30, x = 0.00, x = +0.35
    axes = [
        fig.add_axes([0.06, 0.22, 0.28, 0.68]),
        fig.add_axes([0.37, 0.22, 0.28, 0.68]),
        fig.add_axes([0.68, 0.22, 0.28, 0.68])
    ]

    panel_configs = [
        {
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

    r_pitch = 21.0
    r_base = 19.734

    for p in panel_configs:
        ax = p['ax']
        x_shift = p['x_shift']
        shift_mm = x_shift * 3.0

        # Concentric Reference Circles
        theta = np.linspace(-0.6, 0.6, 150)
        ax.plot(r_pitch * np.sin(theta), r_pitch * np.cos(theta), '--', color=COLOR_TANGENT, lw=1.1, label=tr.get('fig1_pitch_line', 'Pitch Circle'))
        ax.plot(r_base * np.sin(theta), r_base * np.cos(theta), '-.', color=COLOR_PINION, lw=1.1, label=tr.get('fig1_base_circle', 'Base Circle'))
        ax.plot(p['rf'] * np.sin(theta), p['rf'] * np.cos(theta), ':', color=COLOR_AXIS, lw=1.0, label=tr.get('fig1_root_circle', 'Root Circle'))
        ax.plot(p['ra'] * np.sin(theta), p['ra'] * np.cos(theta), '-', color=COLOR_GEAR, lw=1.2, label=tr.get('fig1_tip_circle', 'Tip Circle'))

        # Rack Cutter Datum Line (shifted by x*m from pitch tangent)
        y_rack_datum = r_pitch + shift_mm
        ax.axhline(y=y_rack_datum, color=COLOR_RACK, lw=1.1, linestyle='-', alpha=0.85)

        # Involute & Trochoid Fillet Profile Sketch
        # Left Flank
        inv_y = np.linspace(r_base, p['ra'], 60)
        inv_x_left = -0.5 * (np.pi * 3.0 / 2.0 + 2.0 * x_shift * 3.0 * np.tan(np.radians(20.0))) * (inv_y / r_pitch)
        inv_x_left += (inv_y - r_base) * 0.28
        ax.plot(inv_x_left, inv_y, '-', color=COLOR_PINION, lw=1.6)

        # Right Flank
        inv_x_right = -inv_x_left
        ax.plot(inv_x_right, inv_y, '-', color=COLOR_PINION, lw=1.6)

        # Top Land
        ax.plot([inv_x_left[-1], inv_x_right[-1]], [p['ra'], p['ra']], '-', color=COLOR_GEAR, lw=1.5)

        # Root & Trochoid Undercut representation
        if p['undercut']:
            # Trochoid scooped undercut notch
            notch_y = np.linspace(p['rf'], r_base, 30)
            scoop = (1.0 - (notch_y - p['rf']) / (r_base - p['rf'])) ** 2 * (0.8 - x_shift) * 0.9
            left_notch_x = inv_x_left[0] + scoop
            right_notch_x = inv_x_right[0] - scoop
            ax.plot([inv_x_left[0], left_notch_x[-1]], [r_base, r_base], '-', color=COLOR_PINION, lw=1.5)
            ax.plot(left_notch_x, notch_y, '--', color=p['notch_color'], lw=1.5)
            ax.plot(right_notch_x, notch_y, '--', color=p['notch_color'], lw=1.5)
            ax.plot([left_notch_x[0], right_notch_x[0]], [p['rf'], p['rf']], '-', color=COLOR_AXIS, lw=1.2)
            # Undercut callout tag
            ax.text(0.0, p['rf'] + 0.6, tr.get('fig1_undercut_trochoid', 'Undercut Notch'),
                    fontsize=8.3, color=p['notch_color'], ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.2", fc=p['box_color'], ec=p['border_color'], lw=0.8))
        else:
            # Healthy thick trochoid root
            root_y = np.linspace(p['rf'], r_base, 30)
            left_smooth_x = np.linspace(inv_x_left[0] - 0.5, inv_x_left[0], 30)
            right_smooth_x = -left_smooth_x
            ax.plot(left_smooth_x, root_y, '-', color=COLOR_PINION, lw=1.6)
            ax.plot(right_smooth_x, root_y, '-', color=COLOR_PINION, lw=1.6)
            ax.plot([left_smooth_x[0], right_smooth_x[0]], [p['rf'], p['rf']], '-', color=COLOR_AXIS, lw=1.2)
            sound_label = SOUND_ROOT_LABELS.get(lang, "Sound Root (No Undercut)")
            ax.text(0.0, p['rf'] + 0.6, sound_label,
                    fontsize=8.3, color=p['notch_color'], ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.2", fc=p['box_color'], ec=p['border_color'], lw=0.8))

        # Critical root thickness dimension (sF)
        sF_y = p['rf'] + 1.2
        sF_half = p['sF'] / 2.0
        ax.annotate('', xy=(-sF_half, sF_y), xytext=(sF_half, sF_y),
                    arrowprops=dict(arrowstyle="<->", color=COLOR_NORMAL, lw=1.1))
        ax.text(0.0, sF_y + 0.35, f"{tr.get('fig1_critical_root_thickness', 'sF')} = {p['sF']:.2f} mm",
                fontsize=8.5, color=COLOR_NORMAL, ha='center', va='bottom')

        # Shift annotation arrow
        if abs(x_shift) > 0.01:
            ax.annotate(f"{tr.get('fig1_shift_amount', 'x*m')} = {shift_mm:+.2f} mm",
                        xy=(2.8, (r_pitch + y_rack_datum)/2.0), xytext=(3.5, (r_pitch + y_rack_datum)/2.0 + 1.2),
                        fontsize=8.2, color=COLOR_RACK,
                        arrowprops=dict(arrowstyle="->", color=COLOR_RACK, lw=0.8),
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOR_RACK, lw=0.7))

        ax.set_xlim(-6.5, 6.5)
        ax.set_ylim(14.5, 27.0)
        ax.set_aspect('equal')
        ax.set_title(p['title'], fontsize=11.5, color=COLOR_TEXT_MAIN, pad=10)
        ax.grid(True, linestyle="--", alpha=0.4, color=COLOR_GRID)
        if p == panel_configs[0]:
            ax.legend(loc="upper left", fontsize=7.8, framealpha=0.92)

    # Bottom Summary Card
    card_ax = fig.add_axes([0.06, 0.025, 0.90, 0.14])
    card_ax.axis('off')
    card_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.03",
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

    fig = plt.figure(figsize=(15.0, 10.2), dpi=dpi, facecolor=COLOR_BG)
    fig.suptitle(tr.get('fig2_title', 'Fig 2'), fontsize=15.5, color=COLOR_TEXT_MAIN, y=0.96)

    ax = fig.add_axes([0.08, 0.22, 0.84, 0.68])

    # Parameters
    # Pinion 1: z1=14, m=3, x1=+0.35 -> r1=21, rb1=19.734, rw1=21.354, ra1=24.965
    # Gear 2:   z2=42, m=3, x2=+0.15 -> r2=63, rb2=59.201, rw2=64.061, ra2=66.365
    # a_std = 84.0, a_prime = 85.415, alpha_w = 22.463 deg
    cx, cy = 0.0, 0.0 # Working Pitch Point P is at (0, 0)
    alpha_w_deg = 22.462989
    alpha_w_rad = math.radians(alpha_w_deg)

    # Pinion center at (0, +rw1) = (0, +21.354)
    # Gear center at (0, -rw2) = (0, -64.061)
    rw1, rw2 = 21.353726, 64.061178
    rb1, rb2 = 19.733545, 59.200635
    ra1, ra2 = 24.965000, 66.365000
    r1, r2 = 21.000000, 63.000000

    o1 = (0.0, rw1)
    o2 = (0.0, -rw2)

    # Working Pitch Circles (Tangent at P)
    th = np.linspace(math.pi * 1.25, math.pi * 1.75, 120)
    ax.plot(o1[0] + rw1 * np.cos(th), o1[1] + rw1 * np.sin(th), '--', color=COLOR_TANGENT, lw=1.2, label=tr.get('fig2_op_pitch_pinion', 'Working Pitch dw1'))
    th2 = np.linspace(math.pi * 0.25, math.pi * 0.75, 120)
    ax.plot(o2[0] + rw2 * np.cos(th2), o2[1] + rw2 * np.sin(th2), '--', color=COLOR_GEAR, lw=1.2, label=tr.get('fig2_op_pitch_gear', 'Working Pitch dw2'))

    # Standard Pitch Circles (Thin dotted)
    ax.plot(o1[0] + r1 * np.cos(th), o1[1] + r1 * np.sin(th), ':', color=COLOR_AXIS, lw=0.9, label=tr.get('fig2_std_pitch_pinion', 'Std Pitch d1'))
    ax.plot(o2[0] + r2 * np.cos(th2), o2[1] + r2 * np.sin(th2), ':', color=COLOR_AXIS, lw=0.9)

    # Base Circles
    ax.plot(o1[0] + rb1 * np.cos(th), o1[1] + rb1 * np.sin(th), '-.', color=COLOR_PINION, lw=1.1, label=tr.get('fig2_base_pinion', 'Base Circle db1'))
    ax.plot(o2[0] + rb2 * np.cos(th2), o2[1] + rb2 * np.sin(th2), '-.', color=COLOR_GEAR, lw=1.1, label=tr.get('fig2_base_gear', 'Base Circle db2'))

    # Tip Circles
    ax.plot(o1[0] + ra1 * np.cos(th), o1[1] + ra1 * np.sin(th), '-', color=COLOR_PINION, lw=1.3, label=tr.get('fig2_tip_pinion', 'Tip Circle da1'))
    ax.plot(o2[0] + ra2 * np.cos(th2), o2[1] + ra2 * np.sin(th2), '-', color=COLOR_GEAR, lw=1.3, label=tr.get('fig2_tip_gear', 'Tip Circle da2'))

    # Working Line of Action (Passes through P at angle alpha_w)
    u_loa = np.array([math.cos(alpha_w_rad), -math.sin(alpha_w_rad)])
    s_loa = np.linspace(-12.0, 18.0, 100)
    loa_pts = np.outer(s_loa, u_loa)
    ax.plot(loa_pts[:, 0], loa_pts[:, 1], '-', color=COLOR_NORMAL, lw=1.4, label=tr.get('fig2_loa_operating', 'Operating LOA'))

    # Working Pitch Tangent (Horizontal line through P)
    ax.axhline(0.0, color=COLOR_TANGENT, lw=1.0, linestyle='--', label=tr.get('fig2_pitch_tangent', 'Pitch Tangent'))

    # Cardinal Points along LOA relative to P:
    # A(SAP) = -5.516 mm, B(LPSTC) = -1.723 mm, P = 0.0 mm, D(HPSTC) = +3.340 mm, E(EAP) = +7.133 mm
    s_A = -5.515948
    s_B = -1.723405
    s_P = 0.0
    s_D = 3.340446
    s_E = 7.132648

    pts = {
        'A': (s_A * u_loa[0], s_A * u_loa[1]),
        'B': (s_B * u_loa[0], s_B * u_loa[1]),
        'P': (s_P * u_loa[0], s_P * u_loa[1]),
        'D': (s_D * u_loa[0], s_D * u_loa[1]),
        'E': (s_E * u_loa[0], s_E * u_loa[1]),
    }

    # Contact path highlight bands
    # Single tooth contact BD
    s_bd = np.linspace(s_B, s_D, 40)
    bd_pts = np.outer(s_bd, u_loa)
    ax.plot(bd_pts[:, 0], bd_pts[:, 1], '-', color=COLOR_HIGHLIGHT, lw=4.2, alpha=0.55, label=tr.get('fig2_dim_bd', 'Single Contact BD (100% Load)'))

    # Active contact length AE
    s_ae = np.linspace(s_A, s_E, 60)
    ae_pts = np.outer(s_ae, u_loa)
    ax.plot(ae_pts[:, 0], ae_pts[:, 1], '-', color=COLOR_DOUBLE, lw=2.2, alpha=0.45)

    # Plot Point markers & Callouts
    ax.scatter([pts['A'][0], pts['E'][0]], [pts['A'][1], pts['E'][1]], color=COLOR_NORMAL, s=55, zorder=6)
    ax.scatter([pts['B'][0], pts['D'][0]], [pts['B'][1], pts['D'][1]], color='#7C3AED', s=50, zorder=6)
    ax.scatter([pts['P'][0]], [pts['P'][1]], color=COLOR_CONTACT, s=65, zorder=7)

    # Orthogonal callout boxes
    ax.annotate(tr.get('fig2_point_a', 'Point A (SAP)'), xy=pts['A'], xytext=(pts['A'][0] - 8.0, pts['A'][1] + 3.5),
                fontsize=8.5, color=COLOR_NORMAL,
                arrowprops=dict(arrowstyle="->", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOR_NORMAL, lw=0.8))

    ax.annotate(tr.get('fig2_point_b', 'Point B (LPSTC)'), xy=pts['B'], xytext=(pts['B'][0] - 6.0, pts['B'][1] - 4.5),
                fontsize=8.5, color='#7C3AED',
                arrowprops=dict(arrowstyle="->", color='#7C3AED', lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec='#7C3AED', lw=0.8))

    ax.annotate(tr.get('fig2_point_p', 'Point P (Working Pitch Point)'), xy=pts['P'], xytext=(pts['P'][0] + 3.0, pts['P'][1] + 5.0),
                fontsize=9.0, color=COLOR_CONTACT,
                arrowprops=dict(arrowstyle="->", color=COLOR_CONTACT, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_CONTACT, lw=0.9))

    ax.annotate(tr.get('fig2_point_d', 'Point D (HPSTC)'), xy=pts['D'], xytext=(pts['D'][0] + 5.5, pts['D'][1] + 3.5),
                fontsize=8.5, color='#7C3AED',
                arrowprops=dict(arrowstyle="->", color='#7C3AED', lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec='#7C3AED', lw=0.8))

    ax.annotate(tr.get('fig2_point_e', 'Point E (EAP)'), xy=pts['E'], xytext=(pts['E'][0] + 7.5, pts['E'][1] - 3.5),
                fontsize=8.5, color=COLOR_NORMAL,
                arrowprops=dict(arrowstyle="->", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOR_NORMAL, lw=0.8))

    # Center distance & Operating parameters banner box
    param_box_text = (
        f"{tr.get('fig2_dim_center_distance', '')}\n"
        f"{tr.get('fig2_dim_g_alpha', '')}\n"
        f"{tr.get('fig2_dim_pb', '')}\n"
        f"{tr.get('fig2_dim_clearance', '')}"
    )
    ax.text(-22.0, -8.0, param_box_text, fontsize=8.5, color=COLOR_TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.25", fc="#F8FAFC", ec=COLOR_AXIS, lw=0.8), linespacing=1.35)

    ax.set_xlim(-26.0, 24.0)
    ax.set_ylim(-16.0, 16.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle="--", alpha=0.4, color=COLOR_GRID)
    ax.legend(loc="upper right", fontsize=8.0, framealpha=0.94)

    # Bottom Summary Card
    card_ax = fig.add_axes([0.08, 0.025, 0.84, 0.14])
    card_ax.axis('off')
    card_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.03",
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

    fig = plt.figure(figsize=(15.0, 10.2), dpi=dpi, facecolor=COLOR_BG)
    fig.suptitle(tr.get('fig3_title', 'Fig 3'), fontsize=15.5, color=COLOR_TEXT_MAIN, y=0.96)

    ax = fig.add_axes([0.08, 0.22, 0.84, 0.68])

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
    ax.plot(s, k1, '-', color=COLOR_PINION, lw=1.8, label=tr.get('fig3_curve_k1', 'Pinion k1 (Shifted)'))
    ax.plot(s, k2, '-', color=COLOR_GEAR, lw=1.8, label=tr.get('fig3_curve_k2', 'Gear k2 (Shifted)'))
    ax.plot(s_std, k1_std, ':', color='#DC2626', lw=1.3, alpha=0.75, label=tr.get('fig3_curve_k1_std', 'Unshifted Pinion k1 (Undercut Divergence)'))

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
    ax.annotate(tr.get('fig3_point_a', 'Point A (SAP): k1 = -2.783'),
                xy=(s_pts['A'], k1_A), xytext=(s_pts['A'] + 0.6, k1_A - 0.35),
                fontsize=8.5, color=COLOR_NORMAL,
                arrowprops=dict(arrowstyle="->", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOR_NORMAL, lw=0.8))

    ax.annotate(tr.get('fig3_point_e', 'Point E (EAP): k2 = -1.645'),
                xy=(s_pts['E'], k2_E), xytext=(s_pts['E'] - 4.5, k2_E - 0.45),
                fontsize=8.5, color=COLOR_GEAR,
                arrowprops=dict(arrowstyle="->", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOR_GEAR, lw=0.8))

    ax.annotate(tr.get('fig3_point_p', 'Point P (Pitch Point, Pure Rolling k=0)'),
                xy=(s_pts['P'], 0.0), xytext=(s_pts['P'] - 3.8, 0.45),
                fontsize=8.8, color=COLOR_CONTACT,
                arrowprops=dict(arrowstyle="->", color=COLOR_CONTACT, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_CONTACT, lw=0.8))

    # Invariant & Balancing Ratio Card
    id_header, id_footer = IDENTITY_LABELS.get(lang, IDENTITY_LABELS['en'])
    info_box_text = (
        f"{id_header}\n"
        f"{tr.get('fig3_balancing_ratio', 'Balancing Ratio: |k1A| / |k2E| = 1.692')}\n"
        f"{id_footer}"
    )
    ax.text(1.2, 0.80, info_box_text, fontsize=8.6, color=COLOR_TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.25", fc="#FFFBEB", ec="#F59E0B", lw=0.8), linespacing=1.35)

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
    card_ax = fig.add_axes([0.08, 0.025, 0.84, 0.14])
    card_ax.axis('off')
    card_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.03",
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
