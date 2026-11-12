"""
H-GEAR STUDIO Blog Part 1 Academic Diagram Generator (Regular Typography & Slim Lines)
Generates high-precision, publication-quality SVG and PNG diagrams:
  1. Fig 1: Friction Drive vs Involute Conjugate Toothed Drive (fig1_friction_vs_gear)
  2. Fig 2: The Fundamental Law of Gearing (Willis' Law) (fig2_willis_law_geometry)
  3. Fig 3: Contact Point Kinematics & Velocity Decomposition (fig3_contact_velocity_vectors)

Applied Engineering Design Standards:
  - 100% Regular font weights (no bold fonts whatsoever, clean academic typography)
  - Strict line-weight hierarchy:
      * Max line weight: 1.4 ~ 1.5 pt (core profile/normal only, never heavy or suffocating)
      * Secondary lines: 1.0 ~ 1.2 pt
      * Fine reference/hairlines: 0.6 ~ 0.8 pt (pitch circles, base circles, projections, centerlines)
  - Sharp, slim arrowheads (head_length=0.45, head_width=0.22) instead of bulky blocky heads
  - Zero-overlap label layout: leader lines and generous radial offsets keep the central geometry uncluttered
  - Lossless vector SVG (svg.fonttype='path') and publication 300 DPI PNG
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np

# Ensure backend profile_service is importable
BACKEND_DIR = Path(__file__).resolve().parents[2] / "prototype2" / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from profile_service import generate_gear_pair_profile
except ImportError:
    from profile_service import generate_gear_pair_profile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Arc
from matplotlib.path import Path as MplPath

# ---------------------------------------------------------------------------
# Global Typography & Vector Graphics Configuration (100% Regular Weight)
# ---------------------------------------------------------------------------
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['font.weight'] = 'normal'
plt.rcParams['axes.labelweight'] = 'normal'
plt.rcParams['axes.titleweight'] = 'normal'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'dejavusans'
plt.rcParams['svg.fonttype'] = 'path'

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "images" / "part1"

# ---------------------------------------------------------------------------
# Refined High-Contrast Academic Palette
# ---------------------------------------------------------------------------
COLOR_BG = "#FFFFFF"
COLOR_PINION = "#1D4ED8"       # Royal Deep Blue (Pinion / Profile 1)
COLOR_GEAR = "#0F766E"         # Forest Teal (Gear / Profile 2)
COLOR_NORMAL = "#E11D48"       # Vivid Crimson (Line of action / common normal)
COLOR_TANGENT = "#7C3AED"      # Slate Violet (Pitch line / contact tangent)
COLOR_VELOCITY_1 = "#1D4ED8"   # Royal Blue (Velocity v1)
COLOR_VELOCITY_2 = "#0F766E"   # Forest Teal (Velocity v2)
COLOR_SLIP = "#DC2626"         # Warning Red (Sliding velocity vs)
COLOR_CONTACT = "#D97706"      # Amber Gold (Contact point K)
COLOR_PITCH = "#E11D48"        # Vivid Crimson (Pitch point P)
COLOR_TEXT_MAIN = "#0F172A"    # Dark Slate 900
COLOR_TEXT_MUTED = "#64748B"   # Muted Slate
COLOR_GRID = "#E2E8F0"         # Light Gray border
COLOR_AXIS = "#94A3B8"         # Neutral Slate centerline / reference

# ---------------------------------------------------------------------------
# Precise, Slim Vector & Arrow Helper Functions
# ---------------------------------------------------------------------------
def draw_vector(ax, start, end, color=COLOR_TEXT_MAIN, lw=1.3, mutation_scale=12,
                linestyle='-', zorder=6):
    """Draws a sharp, slim triangular vector arrow with zero gap at endpoints."""
    arrow = FancyArrowPatch(
        posA=start, posB=end,
        arrowstyle='-|>,head_length=0.48,head_width=0.24',
        shrinkA=0, shrinkB=0,
        mutation_scale=mutation_scale,
        color=color, linewidth=lw, linestyle=linestyle,
        joinstyle='round', capstyle='round',
        zorder=zorder
    )
    ax.add_patch(arrow)
    return arrow


def draw_circular_arrow(ax, center, radius, theta_start_deg, theta_end_deg,
                        color=COLOR_PINION, lw=1.1, mutation_scale=11, zorder=6):
    """Draws a slim circular arc arrow tangentially aligned with circular trajectory."""
    n_pts = 60
    thetas = np.linspace(np.radians(theta_start_deg), np.radians(theta_end_deg), n_pts)
    verts = np.column_stack([center[0] + radius * np.cos(thetas),
                             center[1] + radius * np.sin(thetas)])
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * (n_pts - 1)
    path = MplPath(verts, codes)
    arrow = FancyArrowPatch(
        path=path,
        arrowstyle='-|>,head_length=0.45,head_width=0.22',
        shrinkA=0, shrinkB=0,
        mutation_scale=mutation_scale,
        color=color, linewidth=lw,
        joinstyle='round', capstyle='round',
        zorder=zorder
    )
    ax.add_patch(arrow)
    return arrow


def draw_right_angle(ax, vertex, v1, v2, size=0.20, color=COLOR_TEXT_MUTED, lw=0.8):
    """Draws a clean, slim orthogonal right-angle marker."""
    u1 = v1 / np.linalg.norm(v1) * size
    u2 = v2 / np.linalg.norm(v2) * size
    corner = vertex + u1 + u2
    ax.plot([vertex[0] + u1[0], corner[0], vertex[0] + u2[0]],
            [vertex[1] + u1[1], corner[1], vertex[1] + u2[1]],
            color=color, lw=lw, zorder=5)


def draw_leader_annotation(ax, pt, text_pos, text, color=COLOR_TEXT_MAIN,
                           fontweight='normal', fontsize=10.5, box_ec="none",
                           box_fc="white", box_alpha=0.92, lw=0.7, ha='center', va='center'):
    """Draws an elegant, slim leader line from point to annotation text box."""
    ax.annotate(
        text, xy=pt, xytext=text_pos,
        ha=ha, va=va,
        fontsize=fontsize, fontweight=fontweight, color=color,
        arrowprops=dict(
            arrowstyle="-",
            color=COLOR_TEXT_MUTED,
            lw=lw,
            shrinkA=2, shrinkB=2
        ),
        bbox=dict(
            boxstyle="round,pad=0.22",
            fc=box_fc, ec=box_ec, lw=0.8,
            alpha=box_alpha
        ),
        zorder=8
    )


# ---------------------------------------------------------------------------
# Save Diagram Helper
# ---------------------------------------------------------------------------
def save_diagram(fig, base_name, output_dir, dpi, formats):
    """Saves figure in requested formats with tight bounds and white background."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    if formats in ('all', 'svg'):
        svg_path = output_dir / f"{base_name}.svg"
        fig.savefig(svg_path, format='svg', bbox_inches='tight', pad_inches=0.08,
                    facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(svg_path)
    if formats in ('all', 'png'):
        png_path = output_dir / f"{base_name}.png"
        fig.savefig(png_path, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0.08,
                    facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(png_path)
    
    plt.close(fig)
    for p in saved_paths:
        size_kb = p.stat().st_size / 1024
        print(f"  [SAVED] {p.name:<34} ({size_kb:6.1f} KB) -> {p.parent}")


# ---------------------------------------------------------------------------
# Diagram 1: Friction Drive vs Involute Conjugate Toothed Drive
# ---------------------------------------------------------------------------
def create_diagram_1(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all'):
    """
    Fig 1: Friction Wheel (Slip & Normal Force) vs Involute Gear (Conjugate Positive Mesh).
    Slim lines and clean regular typography.
    """
    print("\nGenerating Fig 1: fig1_friction_vs_gear (Regular Font & Slim)...")
    fig = plt.figure(figsize=(15.5, 8.2), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    
    # Left Column: (A) Friction Wheel Mechanism
    ax1 = fig.add_axes([0.05, 0.08, 0.42, 0.84])
    ax1.set_facecolor(COLOR_BG)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    r1 = 2.0
    r2 = 3.2
    O1 = np.array([0.0, -r1])
    O2 = np.array([0.0, r2])
    P = np.array([0.0, 0.0])
    
    # Friction Cylinders (Slim 1.3 pt outlines)
    circle1 = plt.Circle(O1, r1, facecolor=COLOR_PINION, fill=True, alpha=0.06,
                         linewidth=1.3, edgecolor=COLOR_PINION, zorder=2)
    circle2 = plt.Circle(O2, r2, facecolor=COLOR_GEAR, fill=True, alpha=0.06,
                         linewidth=1.3, edgecolor=COLOR_GEAR, zorder=2)
    ax1.add_patch(circle1)
    ax1.add_patch(circle2)
    
    # Line of centers (Slim 0.8 pt centerline)
    ax1.plot([0, 0], [O1[1] - 0.7, O2[1] + 0.7], color=COLOR_AXIS, linestyle="-.",
             linewidth=0.8, zorder=1)
    ax1.scatter([O1[0], O2[0]], [O1[1], O2[1]], color=[COLOR_PINION, COLOR_GEAR],
                s=50, zorder=5, edgecolors=COLOR_TEXT_MAIN, linewidths=0.8)
    
    ax1.text(O1[0] - 0.35, O1[1], r"$O_1$", fontsize=12, fontweight='normal',
             color=COLOR_PINION, va='center', ha='right')
    ax1.text(O2[0] - 0.35, O2[1], r"$O_2$", fontsize=12, fontweight='normal',
             color=COLOR_GEAR, va='center', ha='right')
    
    # Rotation Arrows (Slim 1.1 pt)
    draw_circular_arrow(ax1, O1, 1.25, 140, 40, color=COLOR_PINION, lw=1.2, mutation_scale=11)
    ax1.text(0.95, O1[1] + 0.45, r"$\omega_1$ (구동, CW)", fontsize=10.5, fontweight='normal',
             color=COLOR_PINION)
    
    draw_circular_arrow(ax1, O2, 1.6, 220, 320, color=COLOR_GEAR, lw=1.2, mutation_scale=11)
    ax1.text(1.15, O2[1] - 0.45, r"$\omega_2$ (종동, CCW)", fontsize=10.5, fontweight='normal',
             color=COLOR_GEAR)
    
    # Contact point P
    ax1.scatter([P[0]], [P[1]], color=COLOR_NORMAL, s=70, zorder=7,
                edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    ax1.text(P[0] - 0.30, P[1] + 0.25, r"$P$ (접촉점)", fontsize=11, fontweight='normal',
             color=COLOR_NORMAL, ha='right',
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.9))
    
    # Compression Normal Force FN (Slim 1.3 pt vector)
    draw_vector(ax1, (0.0, 1.6), (0.0, 0.4), color=COLOR_TEXT_MAIN, lw=1.3, mutation_scale=12)
    ax1.text(0.22, 1.05, r"압축 수직항력 $F_N$", fontsize=10, fontweight='normal',
             color=COLOR_TEXT_MAIN,
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    
    # Traction Force Ft (Slim 1.4 pt vector)
    draw_vector(ax1, (0.1, 0.0), (1.5, 0.0), color=COLOR_SLIP, lw=1.4, mutation_scale=13)
    ax1.text(0.35, 0.28, r"마찰 구동력 $F_t \leq \mu F_N$", fontsize=10.5, fontweight='normal',
             color=COLOR_SLIP,
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    
    # Warning Box: Friction Wheel Limitations
    slip_box = patches.FancyBboxPatch((-3.6, -4.7), 7.2, 1.8, boxstyle="round,pad=0.3",
                                      fc="#FEF2F2", ec="#FCA5A5", lw=1.0, zorder=3)
    ax1.add_patch(slip_box)
    ax1.text(0, -3.95, "[마찰차의 역학적 한계: 필연적 슬립(Slip) 발생]", fontsize=11,
             fontweight='normal', color="#991B1B", ha='center')
    ax1.text(0, -4.55,
             "전달 토크 급증 또는 표면 오염/마찰계수 저하 시 필연적 미끄러짐 발생\n"
             r"$\Delta v = v_1 - v_2 \neq 0 \;\longrightarrow\;$ 회전각 위상 동기화 상실 & 발열/마모",
             fontsize=9.5, color="#7F1D1D", ha='center', va='center')
    
    ax1.set_xlim(-4.0, 4.0)
    ax1.set_ylim(-5.2, 4.6)
    ax1.set_title("(A) 평찰차(Friction Wheel)의 구동 메커니즘", fontsize=13.5,
                  fontweight='normal', pad=15, color=COLOR_TEXT_MAIN)
    
    # -------------------------------------------------------------
    # Right Column: (B) Involute Conjugate Toothed Drive
    # -------------------------------------------------------------
    ax2_top = fig.add_axes([0.53, 0.46, 0.44, 0.45])
    ax2_top.set_facecolor(COLOR_BG)
    ax2_top.set_aspect('equal')
    ax2_top.axis('off')
    
    # Generate exact gear profiles
    gear_data = generate_gear_pair_profile(
        module=2.0, z1=17, z2=33, alpha_n_deg=20.0,
        backlash_jn_mm=0.0, num_involute_pts=80, num_fillet_pts=50
    )
    
    px = np.array(gear_data['pinion_outline']['x'])
    py = np.array(gear_data['pinion_outline']['y'])
    gx = np.array(gear_data['gear_outline']['x'])
    gy = np.array(gear_data['gear_outline']['y'])
    
    Xp, Yp = -py, px - 17.0
    Xg, Yg = -gy, gx - 17.0
    
    # Plot true conjugate closed-form gear outlines (Slim 1.4 pt)
    ax2_top.plot(Xp, Yp, color=COLOR_PINION, lw=1.4, zorder=4)
    ax2_top.fill(Xp, Yp, color=COLOR_PINION, alpha=0.08, zorder=3)
    ax2_top.plot(Xg, Yg, color=COLOR_GEAR, lw=1.4, zorder=4)
    ax2_top.fill(Xg, Yg, color=COLOR_GEAR, alpha=0.08, zorder=3)
    
    # Line of centers (Slim 0.8 pt)
    ax2_top.plot([0, 0], [-4.4, 4.4], color=COLOR_AXIS, linestyle="-.", lw=0.8, zorder=2)
    
    # Pitch circles (Slim 0.8 pt dashed)
    theta_pc = np.linspace(-np.pi/6, np.pi/6, 120)
    pc1_x = 17.0 * np.sin(theta_pc)
    pc1_y = -17.0 + 17.0 * np.cos(theta_pc)
    pc2_x = 33.0 * np.sin(theta_pc)
    pc2_y = 33.0 - 33.0 * np.cos(theta_pc)
    ax2_top.plot(pc1_x, pc1_y, color=COLOR_AXIS, linestyle="--", lw=0.8, zorder=2)
    ax2_top.plot(pc2_x, pc2_y, color=COLOR_AXIS, linestyle="--", lw=0.8, zorder=2)
    
    # Pitch tangent line (Slim 0.8 pt)
    ax2_top.plot([-5.5, 5.5], [0, 0], color=COLOR_TANGENT, linestyle="--", lw=0.8, zorder=2)
    
    # Line of Action (1.3 pt)
    alpha_rad = np.radians(20.0)
    loa_len = 5.2
    loa_x = np.array([-np.cos(alpha_rad), np.cos(alpha_rad)]) * loa_len
    loa_y = np.array([np.sin(alpha_rad), -np.sin(alpha_rad)]) * loa_len
    ax2_top.plot(loa_x, loa_y, color=COLOR_NORMAL, lw=1.3, linestyle="-", zorder=3,
                 label=r"작용선(Line of Action, $n-n$)")
    
    # Pitch point P
    ax2_top.scatter([0.0], [0.0], color=COLOR_PITCH, s=70, zorder=8,
                    edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    ax2_top.text(0.35, -0.42, r"$P$ (피치점)", fontsize=10.5, fontweight='normal',
                 color=COLOR_PITCH,
                 bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PITCH, lw=0.8, alpha=0.9))
    
    # Annotations with slim leader lines
    ax2_top.text(-5.4, 3.6,
                 r"★ 정규 인볼류트 형상 맞물림 (공액 접촉, 오버랩 $0.000\;\mathrm{mm}$)" "\n"
                 r"   모듈 $m=2.0,\; z_1=17,\; z_2=33,\; \alpha_n=20^\circ,\; j_n=0.0$",
                 fontsize=10, fontweight='normal', color=COLOR_TEXT_MAIN,
                 bbox=dict(boxstyle="round,pad=0.25", fc="#F8FAFC", ec=COLOR_AXIS, lw=0.8))
    
    ax2_top.annotate("이뿌리 틈새(Clearance)\n" r"$c = 0.25m = 0.50\;\mathrm{mm}$",
                     xy=(0.0, 2.5), xytext=(2.2, 2.8),
                     arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22",
                                     color=COLOR_GEAR, lw=1.0),
                     fontsize=9.0, fontweight='normal', color=COLOR_GEAR,
                     bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8))
    
    ax2_top.annotate("이끝 평탄면(Top Land)\n" r"$s_a \geq 0.25m$",
                     xy=(1.40, 1.94), xytext=(-1.70, 2.70),
                     ha='center', va='center',
                     arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22",
                                     color=COLOR_PINION, lw=1.0, shrinkA=0, shrinkB=0),
                     fontsize=9.0, fontweight='normal', color=COLOR_PINION,
                     bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PINION, lw=0.8))
    
    ax2_top.set_xlim(-5.8, 5.8)
    ax2_top.set_ylim(-4.5, 4.4)
    
    # Bottom View: High-Clarity Engineering Comparison Table
    ax2_bot = fig.add_axes([0.53, 0.08, 0.44, 0.36])
    ax2_bot.set_facecolor(COLOR_BG)
    ax2_bot.axis('off')
    ax2_bot.set_xlim(0, 1)
    ax2_bot.set_ylim(0, 1)
    
    # Outer Card Boundary (Slim 1.0 pt)
    card_box = patches.FancyBboxPatch((0.01, 0.01), 0.98, 0.98, boxstyle="round,pad=0.015",
                                      fc="#FFFFFF", ec="#CBD5E1", lw=1.0, zorder=1)
    ax2_bot.add_patch(card_box)
    
    # Top Banner
    banner_box = patches.FancyBboxPatch((0.02, 0.77), 0.96, 0.20, boxstyle="round,pad=0.01",
                                        fc="#F0FDF4", ec="#86EFAC", lw=1.0, zorder=2)
    ax2_bot.add_patch(banner_box)
    ax2_bot.text(0.50, 0.90, "★ 기어 전동의 제1원리: 불변의 상수 각속도비 (Constant Ratio)",
                 fontsize=11, fontweight='normal', color="#166534", ha='center', va='center', zorder=3)
    ax2_bot.text(0.50, 0.81,
                 r"$u = \frac{\omega_1}{\omega_2} = \frac{z_2}{z_1} = \frac{33}{17} \approx 1.9412 = \mathrm{Constant} \quad (\Delta u \equiv 0.000000)$",
                 fontsize=11.5, fontweight='normal', color="#14532D", ha='center', va='center', zorder=3)
    
    # Table Header Row
    header_box = patches.FancyBboxPatch((0.02, 0.61), 0.96, 0.13, boxstyle="square,pad=0.0",
                                        fc="#F8FAFC", ec="#E2E8F0", lw=0.8, zorder=2)
    ax2_bot.add_patch(header_box)
    col1_x = 0.13
    col2_x = 0.46
    col3_x = 0.81

    ax2_bot.text(col1_x, 0.675, "비교 항목 (Criteria)", fontsize=9.0, fontweight='normal',
                 color=COLOR_TEXT_MAIN, ha='center', va='center', zorder=3)
    ax2_bot.text(col2_x, 0.675, "평찰차 (Friction Wheel)", fontsize=9.0, fontweight='normal',
                 color="#B91C1C", ha='center', va='center', zorder=3)
    ax2_bot.text(col3_x, 0.675, "정규 인볼류트 기어 (Involute)", fontsize=9.0, fontweight='normal',
                 color="#15803D", ha='center', va='center', zorder=3)
    
    # Table Data Rows
    rows = [
        ("동력 전달 원리",
         "접촉면 마찰력 의존\n" r"$(F_t \leq \mu F_N)$",
         "치면 형상 맞물림\n(Positive Mechanical Mesh)", False),
        ("속도비 동기화",
         "미끄러짐 발생\n" r"$(\Delta v \neq 0,$ $u$ 변동)",
         "이론적 완전 동기화\n" r"$(u = z_2/z_1 = \mathrm{const})$", True),
        ("베어링 축 하중",
         r"거대 압축 하중 $F_N$ 필수" "\n(베어링 피로 가중)",
         "전달 토크에만 비례하는\n정상 맞물림 하중", False),
        ("고부하 신뢰성",
         "과부하 시 헛돎 슬립\n(급격한 마모 및 손상)",
         r"$0.000\;\mathrm{mm}$ 간섭 없는" "\n무슬립 동력 전달", True)
    ]
    
    y_starts = [0.46, 0.31, 0.16, 0.02]
    row_h = 0.14
    for i, (crit, fric, gear, is_alt) in enumerate(rows):
        y_pos = y_starts[i]
        rbox = patches.FancyBboxPatch((0.02, y_pos), 0.96, row_h, boxstyle="square,pad=0.0",
                                      fc="#F8FAFC" if is_alt else "#FFFFFF",
                                      ec="#E2E8F0", lw=0.5, zorder=2)
        ax2_bot.add_patch(rbox)
        
        ax2_bot.text(col1_x, y_pos + row_h/2, crit, fontsize=8.5, fontweight='normal',
                     color=COLOR_TEXT_MAIN, ha='center', va='center', zorder=3)
        ax2_bot.text(col2_x, y_pos + row_h/2, fric, fontsize=8.2, fontweight='normal',
                     color="#7F1D1D", ha='center', va='center', zorder=3)
        ax2_bot.text(col3_x, y_pos + row_h/2, gear, fontsize=8.2, fontweight='normal',
                     color="#14532D", ha='center', va='center', zorder=3)
    
    ax2_top.set_title("(B) 정규 인볼류트 기어의 형상 맞물림(Positive Conjugate Mesh)",
                      fontsize=13.5, fontweight='normal', pad=15, color=COLOR_TEXT_MAIN)
    
    save_diagram(fig, "fig1_friction_vs_gear", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 2: The Fundamental Law of Gearing (Willis' Law) - Regular Typography
# ---------------------------------------------------------------------------
def create_diagram_2(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all'):
    """
    Fig 2: Willis' Law of Gearing.
    100% Regular font weights, slim lines, generous uncrowded layout.
    """
    print("\nGenerating Fig 2: fig2_willis_law_geometry (Regular Font & Slim)...")
    fig, ax = plt.subplots(figsize=(12.5, 11.2), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Centers and Pitch Point
    r1 = 2.6
    r2 = 3.4
    O1 = np.array([0.0, -r1])
    O2 = np.array([0.0, r2])
    P = np.array([0.0, 0.0])
    
    # 1. Line of Centers (Slim 0.8 pt)
    ax.plot([0, 0], [-3.8, 4.6], color=COLOR_AXIS, linestyle="-.", lw=0.8,
            zorder=1, label="중심선 (Line of Centers)")
    
    # Pressure Angle and Line of Action Unit Vectors
    alpha = np.radians(22.0)
    n_dir = np.array([np.cos(alpha), np.sin(alpha)])    # Line of Action direction
    t_dir = np.array([-np.sin(alpha), np.cos(alpha)])   # Perpendicular direction
    
    # 2. Pitch Circles (Slim 0.7 pt dashed)
    circle_p1 = plt.Circle(O1, r1, color=COLOR_AXIS, fill=False, linestyle="--",
                           lw=0.7, zorder=2)
    circle_p2 = plt.Circle(O2, r2, color=COLOR_AXIS, fill=False, linestyle="--",
                           lw=0.7, zorder=2)
    ax.add_patch(circle_p1)
    ax.add_patch(circle_p2)
    
    # 3. Base Circles (Slim 0.7 pt dotted)
    rb1 = r1 * np.cos(alpha)
    rb2 = r2 * np.cos(alpha)
    circle_b1 = plt.Circle(O1, rb1, color=COLOR_PINION, fill=False, linestyle=":",
                           lw=0.7, alpha=0.6, zorder=2)
    circle_b2 = plt.Circle(O2, rb2, color=COLOR_GEAR, fill=False, linestyle=":",
                           lw=0.7, alpha=0.6, zorder=2)
    ax.add_patch(circle_b1)
    ax.add_patch(circle_b2)
    
    # 4. Common Normal / Line of Action n-n (1.4 pt)
    L_norm = 5.2
    n_start = P - n_dir * L_norm
    n_end = P + n_dir * L_norm
    ax.plot([n_start[0], n_end[0]], [n_start[1], n_end[1]],
            color=COLOR_NORMAL, lw=1.4, zorder=3,
            label=r"공통 법선 $n-n$ (작용선, Line of Action)")
    
    # 5. Horizontal Pitch Line Tangent (Slim 0.8 pt dashed)
    L_tan_pitch = 3.4
    ax.plot([-L_tan_pitch, L_tan_pitch], [0, 0], color=COLOR_TANGENT,
            linestyle="--", lw=0.8, zorder=3,
            label=r"피치점 공통 접선 ($t_P - t_P$)")
    
    # Position pitch tangent label far to the left
    ax.text(-2.6, 0.18, r"피치 접선 ($t_P - t_P$)", fontsize=9.5, fontweight='normal',
            color=COLOR_TANGENT, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    
    # 6. Perpendicular Points N1, N2 (Feet of Perpendiculars from O1, O2)
    proj_1 = np.dot(O1 - P, n_dir)
    proj_2 = np.dot(O2 - P, n_dir)
    N1 = P + n_dir * proj_1
    N2 = P + n_dir * proj_2
    
    # Shaded Similar Right Triangles
    tri1_pts = np.array([O1, N1, P])
    tri2_pts = np.array([O2, N2, P])
    ax.fill(tri1_pts[:, 0], tri1_pts[:, 1], color=COLOR_PINION, alpha=0.06, zorder=2)
    ax.fill(tri2_pts[:, 0], tri2_pts[:, 1], color=COLOR_GEAR, alpha=0.06, zorder=2)
    
    # Perpendicular lines O1-N1 and O2-N2 (Slim 0.9 pt dashed)
    ax.plot([O1[0], N1[0]], [O1[1], N1[1]], color=COLOR_PINION, lw=0.9, linestyle="--", zorder=4)
    ax.plot([O2[0], N2[0]], [O2[1], N2[1]], color=COLOR_GEAR, lw=0.9, linestyle="--", zorder=4)
    
    # Right-Angle Symbols (Slim 0.8 pt)
    draw_right_angle(ax, N1, O1 - N1, P - N1, size=0.20, color=COLOR_PINION, lw=0.8)
    draw_right_angle(ax, N2, O2 - N2, P - N2, size=0.20, color=COLOR_GEAR, lw=0.8)
    
    # 7. Contact Point K
    K = P + n_dir * 0.55
    
    # Common Tangent at Contact Point K (Slim 0.8 pt dotted)
    L_tan_K = 1.9
    t_start = K - t_dir * L_tan_K
    t_end = K + t_dir * L_tan_K
    ax.plot([t_start[0], t_end[0]], [t_start[1], t_end[1]],
            color=COLOR_TANGENT, lw=0.8, linestyle=":", zorder=4,
            label=r"접점 공통 접선 ($t_K - t_K$)")
    draw_right_angle(ax, K, t_dir, n_dir, size=0.18, color=COLOR_NORMAL, lw=0.8)
    
    # 8. Tooth Profiles Sigma_1, Sigma_2 (Maximum emphasis line: 1.5 pt only!)
    s = np.linspace(-1.15, 1.15, 120)
    curve1 = K[:, None] + t_dir[:, None] * s + n_dir[:, None] * (-0.18 * s**2 + 0.01 * s**3)
    curve2 = K[:, None] + t_dir[:, None] * s + n_dir[:, None] * (0.22 * s**2 + 0.01 * s**3)
    ax.plot(curve1[0], curve1[1], color=COLOR_PINION, lw=1.5, zorder=5,
            label=r"치형 곡선 1 ($\Sigma_1$)")
    ax.plot(curve2[0], curve2[1], color=COLOR_GEAR, lw=1.5, zorder=5,
            label=r"치형 곡선 2 ($\Sigma_2$)")
    
    # 9. Precise point scatter markers
    ax.scatter([O1[0], O2[0]], [O1[1], O2[1]], color=[COLOR_PINION, COLOR_GEAR],
                s=45, zorder=7, edgecolors=COLOR_TEXT_MAIN, linewidths=0.8)
    ax.scatter([N1[0], N2[0]], [N1[1], N2[1]], color=[COLOR_PINION, COLOR_GEAR],
                s=40, zorder=7, edgecolors=COLOR_TEXT_MAIN, linewidths=0.8)
    ax.scatter([P[0]], [P[1]], color=COLOR_PITCH, s=65, zorder=8,
                edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    ax.scatter([K[0]], [K[1]], color=COLOR_CONTACT, s=60, zorder=8,
                edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    
    # -----------------------------------------------------------------------
    # UNCLUTTERED ANNOTATIONS VIA ELEGANT LEADER LINES (All Regular Font)
    # -----------------------------------------------------------------------
    
    # O1, O2 Labels
    ax.text(O1[0] + 0.35, O1[1], r"$O_1$ (피니언 중심)", fontsize=11, fontweight='normal',
             color=COLOR_PINION, va='center', ha='left',
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))
    ax.text(O2[0] + 0.35, O2[1], r"$O_2$ (대기어 중심)", fontsize=11, fontweight='normal',
             color=COLOR_GEAR, va='center', ha='left',
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))
    
    # Pitch Point P: Leader line to Upper-Left (-1.8, 0.7)
    draw_leader_annotation(ax, pt=P, text_pos=(-1.8, 0.7),
                           text=r"$P$ (고정된 피치점)", color=COLOR_PITCH,
                           box_ec=COLOR_PITCH, fontsize=11, fontweight='normal',
                           ha='right', va='center')
    
    # Contact Point K: Leader line to Lower-Right (2.2, -0.4)
    draw_leader_annotation(ax, pt=K, text_pos=(2.2, -0.4),
                           text=r"$K$ (임의의 치면 접촉점)", color="#B45309",
                           box_ec=COLOR_CONTACT, fontsize=11, fontweight='normal',
                           ha='left', va='center')
    
    # N1: Leader line to Lower-Left (-1.8, -0.8)
    draw_leader_annotation(ax, pt=N1, text_pos=(-1.8, -0.8),
                           text=r"$N_1$ (기초원 접점)", color=COLOR_PINION,
                           box_ec=COLOR_PINION, fontsize=10.5, fontweight='normal',
                           ha='right', va='center')
    
    # N2: Leader line to Upper-Right (2.2, 1.1)
    draw_leader_annotation(ax, pt=N2, text_pos=(2.2, 1.1),
                           text=r"$N_2$ (기초원 접점)", color=COLOR_GEAR,
                           box_ec=COLOR_GEAR, fontsize=10.5, fontweight='normal',
                           ha='left', va='center')
    
    # Pressure Angle Arc
    arc_alpha = Arc(P, 2.6, 2.6, angle=0, theta1=0, theta2=np.degrees(alpha),
                    color=COLOR_NORMAL, lw=1.1, zorder=5)
    ax.add_patch(arc_alpha)
    ax.text(1.45, 0.26, r"$\alpha$ (압력각)", fontsize=10.5, fontweight='normal',
             color=COLOR_NORMAL, va='center', ha='left',
             bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))
    
    # Base Circle Radii Labels
    ax.text(O1[0] - 1.1, O1[1] + 1.4, r"$r_{b1} = r_1 \cos\alpha$", fontsize=9.5,
             fontweight='normal', color=COLOR_PINION, ha='center',
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.text(O2[0] + 1.2, O2[1] - 1.6, r"$r_{b2} = r_2 \cos\alpha$", fontsize=9.5,
             fontweight='normal', color=COLOR_GEAR, ha='center',
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    
    # Slim Circular Arc Rotation Arrows (1.1 pt)
    draw_circular_arrow(ax, O1, 1.45, 20, 110, color=COLOR_PINION, lw=1.1, mutation_scale=11)
    ax.text(0.95, O1[1] + 0.5, r"$\omega_1$", fontsize=12, fontweight='normal', color=COLOR_PINION)
    
    draw_circular_arrow(ax, O2, 1.85, 240, 330, color=COLOR_GEAR, lw=1.1, mutation_scale=11)
    ax.text(1.15, O2[1] - 0.5, r"$\omega_2$", fontsize=12, fontweight='normal', color=COLOR_GEAR)
    
    # Proof Box: Slim 1.0 pt border, clear regular typography
    proof_box = patches.FancyBboxPatch((-5.6, -5.6), 11.2, 2.0, boxstyle="round,pad=0.35",
                                       fc="#F0FDF4", ec="#86EFAC", lw=1.0, zorder=4)
    ax.add_patch(proof_box)
    ax.text(0, -3.95, "★ 윌리스(Willis) 맞물림 기본 법칙의 기하학적 닫힌 해 수식",
            fontsize=12, fontweight='normal', color="#166534", ha='center', zorder=6)
    ax.text(0, -4.55,
            r"$\Delta O_1 N_1 P \sim \Delta O_2 N_2 P$ (닮은꼴 직각삼각형)"
            r" $\;\Longrightarrow\; \frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \frac{r_2}{r_1} = \frac{O_2 N_2}{O_1 N_1} = \frac{r_{b2}}{r_{b1}} = \mathrm{Constant}$",
            fontsize=12.5, fontweight='normal', color="#14532D", ha='center', zorder=6)
    ax.text(0, -5.15,
            "치면 접촉점 K의 이동과 무관하게, 공통 법선(Line of Action)이 중심선상의 고정된 피치점 P를 관통해야만 일정한 속도비가 보존된다.",
            fontsize=10, fontweight='normal', color="#15803D", ha='center', zorder=6)
    
    ax.set_xlim(-6.0, 6.0)
    ax.set_ylim(-6.05, 4.8)
    ax.set_title("기어 기구학의 제1헌법: 공액 맞물림의 법칙 (Willis' Law)",
                 fontsize=15, fontweight='normal', pad=22, color=COLOR_TEXT_MAIN)
    ax.legend(loc="upper left", fontsize=9.5, framealpha=0.95, edgecolor=COLOR_AXIS)
    
    save_diagram(fig, "fig2_willis_law_geometry", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 3: Contact Point Kinematics & Velocity Decomposition (Regular Font)
# ---------------------------------------------------------------------------
def create_diagram_3(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all'):
    """
    Fig 3: Contact Point Kinematics & Velocity Decomposition.
    100% Regular font weights, slim lines, clean uncrowded layout.
    """
    print("\nGenerating Fig 3: fig3_contact_velocity_vectors (Regular Font & Slim)...")
    fig, ax = plt.subplots(figsize=(13.2, 9.4), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Coordinate Axes: Normal theta_n = 30 deg
    theta_n = np.radians(30.0)
    e_n = np.array([np.cos(theta_n), np.sin(theta_n)])   # (0.866, 0.500)
    e_t = np.array([-np.sin(theta_n), np.cos(theta_n)])  # (-0.500, 0.866)
    
    # Common Tangent (t-t): Slim 0.8 pt dashed
    ax.plot([-e_t[0]*1.8, e_t[0]*3.2], [-e_t[1]*1.8, e_t[1]*3.2],
            color=COLOR_TANGENT, lw=0.8, linestyle="--", zorder=2,
            label=r"공통 접선 ($t-t$)")
    
    # Common Normal (n-n): Slim 1.3 pt solid
    ax.plot([-e_n[0]*1.6, e_n[0]*3.6], [-e_n[1]*1.6, e_n[1]*3.6],
            color=COLOR_NORMAL, lw=1.3, linestyle="-", zorder=2,
            label=r"공통 법선 ($\vec{n}$)")
    
    # Right-Angle Symbol at Contact Point K (0.8 pt)
    draw_right_angle(ax, np.array([0.0, 0.0]), e_t, e_n, size=0.20, color=COLOR_NORMAL, lw=0.8)
    
    # Curved Tooth Profiles at K(0, 0): Slim 1.4 pt
    s = np.linspace(-1.5, 2.2, 160)
    c1 = e_t[:, None] * s + e_n[:, None] * (-0.14 * s**2)
    c2 = e_t[:, None] * s + e_n[:, None] * (0.16 * s**2)
    ax.plot(c1[0], c1[1], color=COLOR_PINION, lw=1.4, alpha=0.7, zorder=3,
            label=r"치형 1 치면 ($\Sigma_1$)")
    ax.plot(c2[0], c2[1], color=COLOR_GEAR, lw=1.4, alpha=0.7, zorder=3,
            label=r"치형 2 치면 ($\Sigma_2$)")
    
    # Velocity Component Values
    v_n = 2.0      # Normal velocity (Identical for both teeth!)
    v_t1 = 2.6     # Tangential velocity of Tooth 1
    v_t2 = 0.9     # Tangential velocity of Tooth 2
    
    v1 = v_t1 * e_t + v_n * e_n
    v2 = v_t2 * e_t + v_n * e_n
    vn_vec = v_n * e_n
    vt1_vec = v_t1 * e_t
    vt2_vec = v_t2 * e_t
    
    # Full Velocity Vectors v1 and v2 (Slim 1.3 pt)
    draw_vector(ax, (0, 0), v1, color=COLOR_VELOCITY_1, lw=1.3, mutation_scale=12, zorder=6)
    ax.text(v1[0] + 0.15, v1[1] + 0.10, r"$\vec{v}_1$ (치형 1 선속도)", fontsize=11.5,
            fontweight='normal', color=COLOR_VELOCITY_1,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    
    draw_vector(ax, (0, 0), v2, color=COLOR_VELOCITY_2, lw=1.3, mutation_scale=12, zorder=6)
    ax.text(v2[0] - 0.18, v2[1] + 0.22, r"$\vec{v}_2$ (치형 2 선속도)", fontsize=11.5,
            fontweight='normal', color=COLOR_VELOCITY_2,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    
    # Identical Normal Velocity Vector vn (1.5 pt)
    draw_vector(ax, (0, 0), vn_vec, color=COLOR_NORMAL, lw=1.5, mutation_scale=14, zorder=7)
    ax.text(vn_vec[0] + 0.20, vn_vec[1] - 0.18,
            r"$\vec{v}_{n1} = \vec{v}_{n2}$ (법선 속도 완전 일치!)",
            fontsize=11, fontweight='normal', color=COLOR_NORMAL,
            bbox=dict(boxstyle="round,pad=0.2", fc="#FEF2F2", ec=COLOR_NORMAL, lw=0.9, alpha=0.95))
    
    # Orthogonal Projections (Slim 0.7 pt dotted)
    ax.plot([v1[0], vn_vec[0]], [v1[1], vn_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    ax.plot([v2[0], vn_vec[0]], [v2[1], vn_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    ax.plot([v1[0], vt1_vec[0]], [v1[1], vt1_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    ax.plot([v2[0], vt2_vec[0]], [v2[1], vt2_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    
    # Tangential Velocity Components (Slim 0.9 pt dash-dot)
    draw_vector(ax, (0, 0), vt1_vec, color=COLOR_VELOCITY_1, lw=0.9, mutation_scale=10,
                linestyle="-.", zorder=5)
    ax.text(vt1_vec[0] - 0.40, vt1_vec[1] + 0.10, r"$\vec{v}_{t1}$", fontsize=10.5,
            fontweight='normal', color=COLOR_VELOCITY_1)
    
    draw_vector(ax, (0, 0), vt2_vec, color=COLOR_VELOCITY_2, lw=0.9, mutation_scale=10,
                linestyle="-.", zorder=5)
    ax.text(vt2_vec[0] - 0.38, vt2_vec[1] - 0.20, r"$\vec{v}_{t2}$", fontsize=10.5,
            fontweight='normal', color=COLOR_VELOCITY_2)
    
    # Relative Sliding Velocity Vector (1.3 pt)
    draw_vector(ax, vt2_vec, vt1_vec, color=COLOR_SLIP, lw=1.3, mutation_scale=12, zorder=6)
    
    # Label positioned cleanly to the upper-left of vs
    ax.text(-1.55, 1.95,
            r"$\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2}$" "\n(상대 미끄럼 속도, Sliding)",
            fontsize=10.5, fontweight='normal', color=COLOR_SLIP, ha='right', va='center',
            bbox=dict(boxstyle="round,pad=0.2", fc="#FEF2F2", ec=COLOR_SLIP, lw=0.9, alpha=0.95))
    
    # Contact Point K Marker (Small 60 size)
    ax.scatter([0], [0], color=COLOR_CONTACT, s=60, edgecolor=COLOR_TEXT_MAIN, lw=1.0, zorder=10)
    ax.text(0.12, -0.32, r"$K$ (치면 접촉점)", fontsize=11, fontweight='normal', color=COLOR_TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    
    # Summary Box: Slim 1.0 pt border, regular font
    summary_box = patches.FancyBboxPatch((-4.6, -4.2), 9.2, 1.65, boxstyle="round,pad=0.2",
                                        fc="#F8FAFC", ec=COLOR_AXIS, lw=1.0, zorder=3)
    ax.add_patch(summary_box)
    ax.text(0, -2.85, "★ 접촉점(K) 기구학의 2대 절대 물리 법칙",
            fontsize=12, fontweight='normal', color=COLOR_TEXT_MAIN, ha='center')
    ax.text(0, -3.35,
            r"1. 법선 방향 연속 접촉 조건: $v_{n1} = v_{n2}$ $\;\longrightarrow\;$ 파고듦(Interpenetration) 및 들뜸(Separation) 방지",
            fontsize=10, fontweight='normal', color="#1E293B", ha='center')
    ax.text(0, -3.75,
            r"2. 접선 방향 상대 미끄럼 발생: $\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2} \neq \vec{0}$ $\;\longrightarrow\;$ 치면 마찰열, 스커핑(Scuffing), EHL 마모의 근원",
            fontsize=10, fontweight='normal', color="#B91C1C", ha='center')
    
    ax.set_xlim(-5.0, 5.0)
    ax.set_ylim(-4.6, 4.0)
    ax.set_title("접촉점(K)의 기구학적 속도 분해: 법선 연속성 vs 상대 미끄럼",
                 fontsize=15, fontweight='normal', pad=22, color=COLOR_TEXT_MAIN)
    ax.legend(loc="upper left", fontsize=9.5, framealpha=0.95, edgecolor=COLOR_AXIS)
    
    save_diagram(fig, "fig3_contact_velocity_vectors", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate publication-grade engineering diagrams for H-GEAR STUDIO Blog Part 1."
    )
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help="Output directory for generated SVG/PNG files")
    parser.add_argument("--dpi", type=int, default=300,
                        help="DPI resolution for PNG output (default: 300)")
    parser.add_argument("--fig", type=str, choices=['all', 'fig1', 'fig2', 'fig3'], default='all',
                        help="Specific figure to generate (default: all)")
    parser.add_argument("--format", type=str, choices=['all', 'svg', 'png'], default='all',
                        help="Export format (default: all)")
    
    args = parser.parse_args()
    
    out_dir = Path(args.output_dir)
    print("=" * 72)
    print(" H-GEAR STUDIO Blog Part 1 Academic Diagram Generator (100% Regular Font & Slim)")
    print(f" Target Directory : {out_dir}")
    print(f" Resolution       : {args.dpi} DPI")
    print(f" Target Figures   : {args.fig}")
    print(f" Output Formats   : {args.format}")
    print("=" * 72)
    
    if args.fig in ('all', 'fig1'):
        create_diagram_1(out_dir, args.dpi, args.format)
    if args.fig in ('all', 'fig2'):
        create_diagram_2(out_dir, args.dpi, args.format)
    if args.fig in ('all', 'fig3'):
        create_diagram_3(out_dir, args.dpi, args.format)
        
    print("\n" + "=" * 72)
    print(" All regular-font & slim diagrams generated successfully!")
    print("=" * 72)


if __name__ == "__main__":
    main()
