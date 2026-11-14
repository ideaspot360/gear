"""
H-GEAR STUDIO Blog Part 2 Academic Diagram Generator (Multilingual & High-Precision)
=====================================================================================
Generates high-precision, publication-quality SVG and PNG diagrams for Chapter 2:
  1. Fig 1: Involute Generation Principle & Taut String Geometry (fig1_involute_generation)
  2. Fig 2: Involute Function Geometry & Closed-Form Derivation (fig2_involute_function_geometry)
  3. Fig 3: Spur Gear Four Fundamental Circles & ISO 53 Proportions (fig3_spur_gear_four_circles)
  4. Fig 4: Line of Action, Path of Contact & Contact Ratio (fig4_line_of_action_contact_path)

Applied Engineering Design Standards:
  - 100% Regular font weights (no bold fonts)
  - Mathematical font scaling for web container (~720px~768px):
      * Title: 15.0 ~ 15.5 pt
      * Card Header: 12.5 ~ 13.0 pt
      * Body Label / Dimension: 11.5 ~ 12.0 pt (>= 14px threshold)
      * Formula / Sub-details: 10.5 ~ 11.0 pt
      * Footnote / Annotation: 9.5 ~ 10.0 pt
  - Strict line-weight hierarchy:
      * Core curve / Line of action: 1.4 ~ 1.5 pt
      * Fundamental circles: 1.0 ~ 1.2 pt
      * Dimension & leader lines: 0.8 ~ 1.0 pt
      * Centerlines & reference: 0.6 ~ 0.8 pt
      * Contact path highlight band: 3.0 ~ 3.2 pt (alpha=0.6)
  - Zero-overlap layout: radial offsets, leader lines, isolated callout cards
  - Dynamic multilingual typography (ko, en, de, ja)
  - Lossless vector SVG (svg.fonttype='path') and publication 300 DPI PNG
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Arc
from matplotlib.path import Path as MplPath

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "images" / "part2"

# ---------------------------------------------------------------------------
# Refined High-Contrast Academic Palette
# ---------------------------------------------------------------------------
COLOR_BG = "#FFFFFF"
COLOR_PINION = "#1D4ED8"       # Royal Deep Blue (Involute curve / Base circle)
COLOR_GEAR = "#0F766E"         # Forest Teal (Tip circle / Arc highlight)
COLOR_NORMAL = "#E11D48"       # Vivid Crimson (Line of action / Root circle)
COLOR_TANGENT = "#7C3AED"      # Slate Violet (Pitch circle / Tangents)
COLOR_CONTACT = "#D97706"      # Amber Gold (Contact point / Taut string)
COLOR_HIGHLIGHT = "#F59E0B"    # Gold Highlight (Contact path band)
COLOR_TEXT_MAIN = "#0F172A"    # Dark Slate 900
COLOR_TEXT_MUTED = "#64748B"   # Muted Slate 500
COLOR_GRID = "#E2E8F0"         # Light Gray border
COLOR_AXIS = "#94A3B8"         # Neutral Slate centerline / reference

# ---------------------------------------------------------------------------
# Dynamic Typography & Font Profiles per Language
# ---------------------------------------------------------------------------
LANGUAGE_FONT_PROFILES = {
    'ko': ['Malgun Gothic', 'Noto Sans KR', 'Segoe UI', 'DejaVu Sans', 'Arial'],
    'ja': ['Yu Gothic', 'MS Gothic', 'Segoe UI', 'DejaVu Sans', 'Arial'],
    'de': ['Segoe UI', 'Segoe UI Symbol', 'DejaVu Sans', 'Arial'],
    'en': ['Segoe UI', 'Segoe UI Symbol', 'DejaVu Sans', 'Arial'],
}


def apply_language_typography(lang: str):
    """
    Dynamically configure Matplotlib typography profile per language.
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


# ---------------------------------------------------------------------------
# Comprehensive Multilingual Translation Dictionary (ko, en, de, ja)
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    'ko': {
        # Titles
        'fig1_title': "그림 1: 인볼류트 곡선의 발생 원리와 실타래 기하학",
        'fig2_title': "그림 2: 인볼류트 함수 inv α의 기하학적 유도와 폐곡선 관계",
        'fig3_title': "그림 3: 스퍼 기어의 4대 기본 원 및 치형 기본 치수",
        'fig4_title': "그림 4: 물림선(Line of Action)과 접촉 궤적 및 정면 물림률",

        # Fig 1 Labels
        'fig1_origin': r"$O$ (기초원 중심)",
        'fig1_a0': r"$A_0$ (인볼류트 시작점, $\theta=0$)",
        'fig1_tangent_n': r"$N$ (기초원 접점)",
        'fig1_point_k': r"$K$ (인볼류트 점, $\rho_K=r_b \theta$)",
        'fig1_base_circle': r"기초원 (Base Circle, $r_b$)",
        'fig1_involute_curve': "인볼류트 치형 곡선",
        'fig1_taut_string': r"팽팽한 실타래 선분 $\overline{NK}$",
        'fig1_ghost_string': "실 풀림 중간 궤적 (Ghost String)",
        'fig1_roll_angle': r"전개각 $\theta$ (Roll Angle)",
        'fig1_pressure_angle': r"압력각 $\alpha_K$",
        'fig1_radius_k': r"반경 $r_K = r_b / \cos\alpha_K$",
        'fig1_rho_label': r"곡률반경 $\rho_K = r_b \theta = r_b \tan\alpha_K$",
        'fig1_card_title': "[인볼류트 곡선의 3대 기하학적 불변 법칙]",
        'fig1_card_body': (
            "(1) 실의 길이 = 기초원 호의 길이 :  $L = \\overline{NK} = \\mathrm{Arc}(A_0 N) = r_b \\theta$\n"
            "(2) 치형의 법선 = 기초원의 접선 :  $\\angle ONK = 90^\\circ$ (임의 점 $K$의 법선은 항상 기초원에 접함)\n"
            "(3) 전개각과 압력각의 대수적 관계 :  $\\theta = \\tan\\alpha_K \\Leftrightarrow \\rho_K = r_b \\tan\\alpha_K$"
        ),

        # Fig 2 Labels
        'fig2_triangle_title': r"직각삼각형 $\Delta ONK$ ($\angle ONK = 90^\circ$)",
        'fig2_arc_len': r"기초원 호 길이 $\mathrm{Arc}(A_0 N) = r_b \theta$",
        'fig2_tangent_len': r"접선 선분 길이 $|\overline{NK}| = r_b \tan\alpha$",
        'fig2_equality': r"$\mathrm{Arc}(A_0 N) = |\overline{NK}| \;\Rightarrow\; \theta = \tan\alpha$",
        'fig2_inv_angle': r"인볼류트 각 $\phi_K = \mathrm{inv}\,\alpha = \tan\alpha - \alpha$",
        'fig2_roll_angle_theta': r"전개각 $\theta = \tan\alpha$",
        'fig2_pressure_angle_alpha': r"압력각 $\alpha$",
        'fig2_card_title': "[인볼류트 함수 inv α의 기하학적 정의 및 폐곡선 유도]",
        'fig2_card_body': (
            "(1) 직각삼각형 $\\Delta ONK$ 대변 길이:  $|\\overline{NK}| = r_b \\tan\\alpha$\n"
            "(2) 실타래 무미끄럼 신개 원리:  $\\mathrm{Arc}(A_0 N) = r_b \\theta = |\\overline{NK}| \\;\\rightarrow\\; \\theta = \\tan\\alpha$\n"
            "(3) 극각 기하 차분 유도:  $\\phi_K = \\angle A_0 O N - \\angle N O K = \\theta - \\alpha = \\tan\\alpha - \\alpha \\equiv \\mathrm{inv}\\,\\alpha$\n"
            "[주의] 삼각함수 연산 시 각도 $\\alpha$는 반드시 라디안(rad) 단위로 대입해야 함"
        ),

        # Fig 3 Labels
        'fig3_tip_circle': r"이끝원 (Tip Circle) $d_a = d + 2h_a = m(z+2)$",
        'fig3_pitch_circle': r"피치원 (Pitch Circle) $d = m \cdot z$",
        'fig3_base_circle': r"기초원 (Base Circle) $d_b = d \cos\alpha$",
        'fig3_root_circle': r"이뿌리원 (Root Circle) $d_f = d - 2h_f = m(z-2.5)$",
        'fig3_ha': r"$h_a = 1.0 m$ (이끝높이)",
        'fig3_hf': r"$h_f = 1.25 m$ (이뿌리높이)",
        'fig3_c': r"$c = 0.25 m$ (틈새)",
        'fig3_h': r"$h = 2.25 m$ (전이높이)",
        'fig3_pitch_p': r"원주피치 $p = \pi m$",
        'fig3_thick_s': r"치두께 $s = \pi m / 2$",
        'fig3_space_e': r"치홈너비 $e = \pi m / 2$",
        'fig3_base_pitch': r"기초원 피치 $p_b = \pi m \cos\alpha$",
        'fig3_topland': r"이끝 두께 $s_a \geq 0.25m$",
        'fig3_card_title': "[ISO 53 / KS B 0053 표준 랙 기본 치형 계수 체계]",
        'fig3_card_body': (
            "- 모듈 $m$, 표준 압력각 $\\alpha = 20^\\circ$, 잇수 $z$\n"
            "- 치형 계수:  $h_a^* = 1.000, \\; h_f^* = 1.250, \\; c^* = 0.250, \\; h^* = 2.250$\n"
            "- 원주 제원:  $p = \\pi m = s + e, \\; s = e = \\pi m / 2, \\; p_b = \\pi m \\cos\\alpha$\n"
            "- 안전 기준:  이끝 평탄면 $s_a \\geq 0.25m$ 유지 (열처리 시 전경화 취성 파손 방지)"
        ),

        # Fig 4 Labels
        'fig4_loa': r"물림 작용선 (Line of Action, $n-n$)",
        'fig4_pitch_line': r"피치 접선 ($t_P - t_P$)",
        'fig4_centerline': "중심선 (Line of Centers)",
        'fig4_point_p': r"$P$ (피치점)",
        'fig4_point_a': r"$A$ (접촉 시작점, SAP)",
        'fig4_point_e': r"$E$ (접촉 종료점, EAP)",
        'fig4_point_b': r"$B$ (단일 접촉 하한점)",
        'fig4_point_d': r"$D$ (단일 접촉 상한점)",
        'fig4_point_n1': r"$N_1$ (피니언 기초원 접점)",
        'fig4_point_n2': r"$N_2$ (기어 기초원 접점)",
        'fig4_pinion_tip': r"피니언 이끝원 ($r_{a1}$)",
        'fig4_gear_tip': r"기어 이끝원 ($r_{a2}$)",
        'fig4_active_path': r"실제 접촉 궤적 $\overline{AE}$ ($g_\alpha = g_a + g_f$)",
        'fig4_ga_gf': r"$g_f = \overline{AP}$ (접근 물림길이),  $g_a = \overline{PE}$ (후퇴 물림길이)",
        'fig4_base_pitch_bar': r"기초원 피치 $p_b = \pi m \cos\alpha$",
        'fig4_single_pair': "단일 접촉 (100% 하중)",
        'fig4_double_pair': "이중 접촉 (50% 분담)",
        'fig4_card_title': "[물림선 접촉 궤적 및 정면 물림률 닫힌 해 수식]",
        'fig4_card_body': (
            "(1) 물림길이 닫힌 해:  $g_\\alpha = \\sqrt{r_{a1}^2 - r_{b1}^2} + \\sqrt{r_{a2}^2 - r_{b2}^2} - a \\sin\\alpha = 14.558\\;\\mathrm{mm}$\n"
            "(2) 정면 물림률:  $\\epsilon_\\alpha = \\frac{g_\\alpha}{p_b} = \\frac{14.558}{8.856} = 1.644 \\geq 1.20$ (설계 합격)\n"
            "(3) 접촉 구간 분담:  단일 치 접촉 $g_1 = 3.155\\;\\mathrm{mm}$ (21.7%),  이중 치 접촉 $g_2 = 11.403\\;\\mathrm{mm}$ (78.3%)\n"
            "[공학적 의의] $\\epsilon_\\alpha \\geq 1.20$ 확보로 전달 오차 완충 및 무충격 연속 동력 전달 보장"
        ),
    },

    'en': {
        # Titles
        'fig1_title': "Figure 1: Generation Principle of the Involute Curve from Base Circle",
        'fig2_title': "Figure 2: Geometric Interpretation and Derivation of Involute Function inv α",
        'fig3_title': "Figure 3: Four Fundamental Circles and Standard Proportions of Spur Gear",
        'fig4_title': "Figure 4: Line of Action, Path of Contact, and Transverse Contact Ratio",

        # Fig 1 Labels
        'fig1_origin': r"$O$ (Base Circle Center)",
        'fig1_a0': r"$A_0$ (Involute Origin, $\theta=0$)",
        'fig1_tangent_n': r"$N$ (Base Tangent Point)",
        'fig1_point_k': r"$K$ (Involute Point, $\rho_K=r_b \theta$)",
        'fig1_base_circle': r"Base Circle ($r_b$)",
        'fig1_involute_curve': "Involute Tooth Flank Curve",
        'fig1_taut_string': r"Taut String Segment $\overline{NK}$",
        'fig1_ghost_string': "Unwinding Trajectory (Ghost String)",
        'fig1_roll_angle': r"Roll Angle $\theta$",
        'fig1_pressure_angle': r"Pressure Angle $\alpha_K$",
        'fig1_radius_k': r"Radius $r_K = r_b / \cos\alpha_K$",
        'fig1_rho_label': r"Radius of Curvature $\rho_K = r_b \theta = r_b \tan\alpha_K$",
        'fig1_card_title': "[Three Fundamental Geometric Laws of the Involute Curve]",
        'fig1_card_body': (
            "(1) String Length = Base Circle Arc:  $L = \\overline{NK} = \\mathrm{Arc}(A_0 N) = r_b \\theta$\n"
            "(2) Profile Normal = Base Circle Tangent:  $\\angle ONK = 90^\\circ$ (Normal always tangent to base circle)\n"
            "(3) Algebraic Relation of Roll & Pressure Angles:  $\\theta = \\tan\\alpha_K \\Leftrightarrow \\rho_K = r_b \\tan\\alpha_K$"
        ),

        # Fig 2 Labels
        'fig2_triangle_title': r"Right Triangle $\Delta ONK$ ($\angle ONK = 90^\circ$)",
        'fig2_arc_len': r"Base Circle Arc $\mathrm{Arc}(A_0 N) = r_b \theta$",
        'fig2_tangent_len': r"Tangent Segment $|\overline{NK}| = r_b \tan\alpha$",
        'fig2_equality': r"$\mathrm{Arc}(A_0 N) = |\overline{NK}| \;\Rightarrow\; \theta = \tan\alpha$",
        'fig2_inv_angle': r"Involute Polar Angle $\phi_K = \mathrm{inv}\,\alpha = \tan\alpha - \alpha$",
        'fig2_roll_angle_theta': r"Roll Angle $\theta = \tan\alpha$",
        'fig2_pressure_angle_alpha': r"Pressure Angle $\alpha$",
        'fig2_card_title': "[Geometric Derivation of the Involute Function inv α]",
        'fig2_card_body': (
            "(1) Opposite Side of Right Triangle $\\Delta ONK$:  $|\\overline{NK}| = r_b \\tan\\alpha$\n"
            "(2) Non-slip Unwinding Condition:  $\\mathrm{Arc}(A_0 N) = r_b \\theta = |\\overline{NK}| \\;\\rightarrow\\; \\theta = \\tan\\alpha$\n"
            "(3) Polar Angle Subtraction:  $\\phi_K = \\angle A_0 O N - \\angle N O K = \\theta - \\alpha = \\tan\\alpha - \\alpha \\equiv \\mathrm{inv}\\,\\alpha$\n"
            "[Note] In trigonometric calculations, the angle $\\alpha$ must be expressed in radians (rad)."
        ),

        # Fig 3 Labels
        'fig3_tip_circle': r"Tip Circle $d_a = d + 2h_a = m(z+2)$",
        'fig3_pitch_circle': r"Pitch Circle $d = m \cdot z$",
        'fig3_base_circle': r"Base Circle $d_b = d \cos\alpha$",
        'fig3_root_circle': r"Root Circle $d_f = d - 2h_f = m(z-2.5)$",
        'fig3_ha': r"$h_a = 1.0 m$ (Addendum)",
        'fig3_hf': r"$h_f = 1.25 m$ (Dedendum)",
        'fig3_c': r"$c = 0.25 m$ (Clearance)",
        'fig3_h': r"$h = 2.25 m$ (Whole Depth)",
        'fig3_pitch_p': r"Circular Pitch $p = \pi m$",
        'fig3_thick_s': r"Tooth Thickness $s = \pi m / 2$",
        'fig3_space_e': r"Space Width $e = \pi m / 2$",
        'fig3_base_pitch': r"Base Pitch $p_b = \pi m \cos\alpha$",
        'fig3_topland': r"Top Land $s_a \geq 0.25m$",
        'fig3_card_title': "[ISO 53 Standard Basic Rack Tooth Profile Proportions]",
        'fig3_card_body': (
            "- Module $m$, Standard Pressure Angle $\\alpha = 20^\\circ$, Number of Teeth $z$\n"
            "- Standard Factors:  $h_a^* = 1.000, \\; h_f^* = 1.250, \\; c^* = 0.250, \\; h^* = 2.250$\n"
            "- Circular Dimensions:  $p = \\pi m = s + e, \\; s = e = \\pi m / 2, \\; p_b = \\pi m \\cos\\alpha$\n"
            "- Design Invariant:  Top land $s_a \\geq 0.25m$ prevents through-hardening brittleness in heat treatment."
        ),

        # Fig 4 Labels
        'fig4_loa': r"Line of Action ($n-n$)",
        'fig4_pitch_line': r"Pitch Tangent ($t_P - t_P$)",
        'fig4_centerline': "Line of Centers",
        'fig4_point_p': r"$P$ (Pitch Point)",
        'fig4_point_a': r"$A$ (Start of Contact, SAP)",
        'fig4_point_e': r"$E$ (End of Contact, EAP)",
        'fig4_point_b': r"$B$ (Lower Single Contact)",
        'fig4_point_d': r"$D$ (Upper Single Contact)",
        'fig4_point_n1': r"$N_1$ (Pinion Base Tangent)",
        'fig4_point_n2': r"$N_2$ (Gear Base Tangent)",
        'fig4_pinion_tip': r"Pinion Tip Circle ($r_{a1}$)",
        'fig4_gear_tip': r"Gear Tip Circle ($r_{a2}$)",
        'fig4_active_path': r"Path of Contact $\overline{AE}$ ($g_\alpha = g_a + g_f$)",
        'fig4_ga_gf': r"$g_f = \overline{AP}$ (Approach Path),  $g_a = \overline{PE}$ (Recess Path)",
        'fig4_base_pitch_bar': r"Base Pitch $p_b = \pi m \cos\alpha$",
        'fig4_single_pair': "Single Pair (100% Load)",
        'fig4_double_pair': "Double Pair (50% Shared)",
        'fig4_card_title': "[Closed-Form Formulation of Path of Contact & Contact Ratio]",
        'fig4_card_body': (
            "(1) Path of Contact:  $g_\\alpha = \\sqrt{r_{a1}^2 - r_{b1}^2} + \\sqrt{r_{a2}^2 - r_{b2}^2} - a \\sin\\alpha = 14.558\\;\\mathrm{mm}$\n"
            "(2) Transverse Contact Ratio:  $\\epsilon_\\alpha = \\frac{g_\\alpha}{p_b} = \\frac{14.558}{8.856} = 1.644 \\geq 1.20$ (PASS)\n"
            "(3) Load Sharing:  Single contact $g_1 = 3.155\\;\\mathrm{mm}$ (21.7%),  Double contact $g_2 = 11.403\\;\\mathrm{mm}$ (78.3%)\n"
            "[Significance] $\\epsilon_\\alpha \\geq 1.20$ guarantees smooth, shockless continuous power transfer."
        ),
    },

    'de': {
        # Titles
        'fig1_title': "Abbildung 1: Erzeugungsprinzip der Evolventenkurve am Grundkreis",
        'fig2_title': "Abbildung 2: Geometrische Interpretation der Evolventenfunktion inv α",
        'fig3_title': "Abbildung 3: Vier Grundkreise und Verzahnungs-Hauptabmessungen",
        'fig4_title': "Abbildung 4: Eingriffslinie, Eingriffsstrecke und Profilüberdeckung",

        # Fig 1 Labels
        'fig1_origin': r"$O$ (Grundkreismittelpunkt)",
        'fig1_a0': r"$A_0$ (Evolventen-Ursprung, $\theta=0$)",
        'fig1_tangent_n': r"$N$ (Grundkreis-Berührungspunkt)",
        'fig1_point_k': r"$K$ (Evolventenpunkt, $\rho_K=r_b \theta$)",
        'fig1_base_circle': r"Grundkreis ($r_b$)",
        'fig1_involute_curve': "Evolventen-Zahnflankenkurve",
        'fig1_taut_string': r"Gespannte Schnur $\overline{NK}$",
        'fig1_ghost_string': "Abwälz-Zwischenkurve (Faden)",
        'fig1_roll_angle': r"Abwälzwinkel $\theta$",
        'fig1_pressure_angle': r"Eingriffswinkel $\alpha_K$",
        'fig1_radius_k': r"Radius $r_K = r_b / \cos\alpha_K$",
        'fig1_rho_label': r"Krümmungsradius $\rho_K = r_b \theta = r_b \tan\alpha_K$",
        'fig1_card_title': "[Drei Grundgesetze der Evolventengeometrie]",
        'fig1_card_body': (
            "(1) Fadenlänge = Grundkreisbogen:  $L = \\overline{NK} = \\mathrm{Arc}(A_0 N) = r_b \\theta$\n"
            "(2) Profilnormale = Grundkreistangente:  $\\angle ONK = 90^\\circ$ (Normale tangiert stets den Grundkreis)\n"
            "(3) Zusammenhang Abwälz- & Eingriffswinkel:  $\\theta = \\tan\\alpha_K \\Leftrightarrow \\rho_K = r_b \\tan\\alpha_K$"
        ),

        # Fig 2 Labels
        'fig2_triangle_title': r"Rechtwinkliges Dreieck $\Delta ONK$ ($\angle ONK = 90^\circ$)",
        'fig2_arc_len': r"Grundkreisbogen $\mathrm{Arc}(A_0 N) = r_b \theta$",
        'fig2_tangent_len': r"Tangentenstrecke $|\overline{NK}| = r_b \tan\alpha$",
        'fig2_equality': r"$\mathrm{Arc}(A_0 N) = |\overline{NK}| \;\Rightarrow\; \theta = \tan\alpha$",
        'fig2_inv_angle': r"Evolventenwinkel $\phi_K = \mathrm{inv}\,\alpha = \tan\alpha - \alpha$",
        'fig2_roll_angle_theta': r"Abwälzwinkel $\theta = \tan\alpha$",
        'fig2_pressure_angle_alpha': r"Eingriffswinkel $\alpha$",
        'fig2_card_title': "[Geometrische Herleitung der Evolventenfunktion inv α]",
        'fig2_card_body': (
            "(1) Gegenkathete des Dreiecks $\\Delta ONK$:  $|\\overline{NK}| = r_b \\tan\\alpha$\n"
            "(2) Schlupffreie Abwälzbedingung:  $\\mathrm{Arc}(A_0 N) = r_b \\theta = |\\overline{NK}| \\;\\rightarrow\\; \\theta = \\tan\\alpha$\n"
            "(3) Polarwinkelsubtraktion:  $\\phi_K = \\angle A_0 O N - \\angle N O K = \\theta - \\alpha = \\tan\\alpha - \\alpha \\equiv \\mathrm{inv}\\,\\alpha$\n"
            "[Hinweis] Bei trigonometrischen Berechnungen muss $\\alpha$ im Bogenmaß (rad) eingesetzt werden."
        ),

        # Fig 3 Labels
        'fig3_tip_circle': r"Kopfkreis $d_a = d + 2h_a = m(z+2)$",
        'fig3_pitch_circle': r"Teilkreis $d = m \cdot z$",
        'fig3_base_circle': r"Grundkreis $d_b = d \cos\alpha$",
        'fig3_root_circle': r"Fußkreis $d_f = d - 2h_f = m(z-2.5)$",
        'fig3_ha': r"$h_a = 1.0 m$ (Kopfhöhe)",
        'fig3_hf': r"$h_f = 1.25 m$ (Fußhöhe)",
        'fig3_c': r"$c = 0.25 m$ (Kopfspiel)",
        'fig3_h': r"$h = 2.25 m$ (Gesamtzahnhöhe)",
        'fig3_pitch_p': r"Teilung $p = \pi m$",
        'fig3_thick_s': r"Zahndicke $s = \pi m / 2$",
        'fig3_space_e': r"Zahnlückenweite $e = \pi m / 2$",
        'fig3_base_pitch': r"Eingriffsteilung $p_b = \pi m \cos\alpha$",
        'fig3_topland': r"Kopfbreite $s_a \geq 0.25m$",
        'fig3_card_title': "[Norm-Bezugsprofil nach ISO 53 / DIN 867]",
        'fig3_card_body': (
            "- Modul $m$, Normaleingriffswinkel $\\alpha = 20^\\circ$, Zähnezahl $z$\n"
            "- Profilfaktoren:  $h_a^* = 1.000, \\; h_f^* = 1.250, \\; c^* = 0.250, \\; h^* = 2.250$\n"
            "- Umfangsmaße:  $p = \\pi m = s + e, \\; s = e = \\pi m / 2, \\; p_b = \\pi m \\cos\\alpha$\n"
            "- Kriterium:  Kopfbreite $s_a \\geq 0.25m$ verhindert Durchhärtungsversprödung beim Härten."
        ),

        # Fig 4 Labels
        'fig4_loa': r"Eingriffslinie ($n-n$)",
        'fig4_pitch_line': r"Wälztangente ($t_P - t_P$)",
        'fig4_centerline': "Zentrallinie (Achsabstand)",
        'fig4_point_p': r"$P$ (Wälzpunkt)",
        'fig4_point_a': r"$A$ (Eingriffsbeginn)",
        'fig4_point_e': r"$E$ (Eingriffsende)",
        'fig4_point_b': r"$B$ (Beginn Einzeleingriff)",
        'fig4_point_d': r"$D$ (Ende Einzeleingriff)",
        'fig4_point_n1': r"$N_1$ (Ritzel-Grundkreistangente)",
        'fig4_point_n2': r"$N_2$ (Rad-Grundkreistangente)",
        'fig4_pinion_tip': r"Ritzel-Kopfkreis ($r_{a1}$)",
        'fig4_gear_tip': r"Rad-Kopfkreis ($r_{a2}$)",
        'fig4_active_path': r"Eingriffsstrecke $\overline{AE}$ ($g_\alpha = g_a + g_f$)",
        'fig4_ga_gf': r"$g_f = \overline{AP}$ (Vor-Eingriffsstrecke),  $g_a = \overline{PE}$ (Nach-Eingriffsstrecke)",
        'fig4_base_pitch_bar': r"Eingriffsteilung $p_b = \pi m \cos\alpha$",
        'fig4_single_pair': "Einzeleingriff (100% Last)",
        'fig4_double_pair': "Doppeleingriff (50% Lastteilung)",
        'fig4_card_title': "[Geschlossene Formulierung der Eingriffsstrecke & Profilüberdeckung]",
        'fig4_card_body': (
            "(1) Eingriffsstrecke:  $g_\\alpha = \\sqrt{r_{a1}^2 - r_{b1}^2} + \\sqrt{r_{a2}^2 - r_{b2}^2} - a \\sin\\alpha = 14.558\\;\\mathrm{mm}$\n"
            "(2) Profilüberdeckung:  $\\epsilon_\\alpha = \\frac{g_\\alpha}{p_b} = \\frac{14.558}{8.856} = 1.644 \\geq 1.20$ (Bestanden)\n"
            "(3) Lastaufteilung:  Einzeleingriff $g_1 = 3.155\\;\\mathrm{mm}$ (21.7%),  Doppeleingriff $g_2 = 11.403\\;\\mathrm{mm}$ (78.3%)\n"
            "[Bedeutung] $\\epsilon_\\alpha \\geq 1.20$ sichert stoßfreie, kontinuierliche Leistungsübertragung."
        ),
    },

    'ja': {
        # Titles
        'fig1_title': "図 1: インボリュート曲線の創成原理と伸開線幾何学",
        'fig2_title': "図 2: インボリュート関数 inv α の幾何学的解釈と閉曲線関係",
        'fig3_title': "図 3: 平歯車の4大基準円と基本諸元寸法体系",
        'fig4_title': "図 4: かみ合い線(作用線)と接触軌跡および正面かみ合い率",

        # Fig 1 Labels
        'fig1_origin': r"$O$ (基礎円中心)",
        'fig1_a0': r"$A_0$ (インボリュート開始点, $\theta=0$)",
        'fig1_tangent_n': r"$N$ (基礎円接点)",
        'fig1_point_k': r"$K$ (インボリュート点, $\rho_K=r_b \theta$)",
        'fig1_base_circle': r"基礎円 (Base Circle, $r_b$)",
        'fig1_involute_curve': "インボリュート歯形曲線",
        'fig1_taut_string': r"張った糸の線分 $\overline{NK}$",
        'fig1_ghost_string': "糸の展開中間軌跡 (Ghost String)",
        'fig1_roll_angle': r"展開角 $\theta$ (ロール角)",
        'fig1_pressure_angle': r"圧力角 $\alpha_K$",
        'fig1_radius_k': r"半径 $r_K = r_b / \cos\alpha_K$",
        'fig1_rho_label': r"曲率半径 $\rho_K = r_b \theta = r_b \tan\alpha_K$",
        'fig1_card_title': "[インボリュート曲線の3大幾何学的普遍法則]",
        'fig1_card_body': (
            "(1) 糸の長さ = 基礎円の円弧長 :  $L = \\overline{NK} = \\mathrm{Arc}(A_0 N) = r_b \\theta$\n"
            "(2) 歯形法線 = 基礎円の接線 :  $\\angle ONK = 90^\\circ$ (任意の点 $K$ の法線は常に基礎円に接する)\n"
            "(3) 展開角と圧力角の代数関係 :  $\\theta = \\tan\\alpha_K \\Leftrightarrow \\rho_K = r_b \\tan\\alpha_K$"
        ),

        # Fig 2 Labels
        'fig2_triangle_title': r"直角三角形 $\Delta ONK$ ($\angle ONK = 90^\circ$)",
        'fig2_arc_len': r"基礎円弧長 $\mathrm{Arc}(A_0 N) = r_b \theta$",
        'fig2_tangent_len': r"接線線分長 $|\overline{NK}| = r_b \tan\alpha$",
        'fig2_equality': r"$\mathrm{Arc}(A_0 N) = |\overline{NK}| \;\Rightarrow\; \theta = \tan\alpha$",
        'fig2_inv_angle': r"インボリュート角 $\phi_K = \mathrm{inv}\,\alpha = \tan\alpha - \alpha$",
        'fig2_roll_angle_theta': r"展開角 $\theta = \tan\alpha$",
        'fig2_pressure_angle_alpha': r"圧力角 $\alpha$",
        'fig2_card_title': "[インボリュート関数 inv α の幾何学的導出体系]",
        'fig2_card_body': (
            "(1) 直角三角形 $\\Delta ONK$ 対辺長:  $|\\overline{NK}| = r_b \\tan\\alpha$\n"
            "(2) すべりなき伸開線原理:  $\\mathrm{Arc}(A_0 N) = r_b \\theta = |\\overline{NK}| \\;\\rightarrow\\; \\theta = \\tan\\alpha$\n"
            "(3) 極角の幾何的差分:  $\\phi_K = \\angle A_0 O N - \\angle N O K = \\theta - \\alpha = \\tan\\alpha - \\alpha \\equiv \\mathrm{inv}\\,\\alpha$\n"
            "[注意] 三角関数計算時、角度 $\\alpha$ は必ずラジアン(rad)単位で代入すること"
        ),

        # Fig 3 Labels
        'fig3_tip_circle': r"歯先円 (Tip Circle) $d_a = d + 2h_a = m(z+2)$",
        'fig3_pitch_circle': r"基準ピッチ円 $d = m \cdot z$",
        'fig3_base_circle': r"基礎円 $d_b = d \cos\alpha$",
        'fig3_root_circle': r"歯底円 $d_f = d - 2h_f = m(z-2.5)$",
        'fig3_ha': r"$h_a = 1.0 m$ (歯先たけ)",
        'fig3_hf': r"$h_f = 1.25 m$ (歯底たけ)",
        'fig3_c': r"$c = 0.25 m$ (頂げき)",
        'fig3_h': r"$h = 2.25 m$ (全歯たけ)",
        'fig3_pitch_p': r"円周ピッチ $p = \pi m$",
        'fig3_thick_s': r"歯厚 $s = \pi m / 2$",
        'fig3_space_e': r"歯溝の幅 $e = \pi m / 2$",
        'fig3_base_pitch': r"基礎円ピッチ $p_b = \pi m \cos\alpha$",
        'fig3_topland': r"歯先頂幅 $s_a \geq 0.25m$",
        'fig3_card_title': "[JIS B 01701 / ISO 53 標準基本ラック歯形体系]",
        'fig3_card_body': (
            "- モジュール $m$, 基準圧力角 $\\alpha = 20^\\circ$, 歯数 $z$\n"
            "- 諸元係数:  $h_a^* = 1.000, \\; h_f^* = 1.250, \\; c^* = 0.250, \\; h^* = 2.250$\n"
            "- 円周諸元:  $p = \\pi m = s + e, \\; s = e = \\pi m / 2, \\; p_b = \\pi m \\cos\\alpha$\n"
            "- 安全基準:  歯先頂幅 $s_a \\geq 0.25m$ 維持 (熱処理時の全硬化脆性破壊を防止)"
        ),

        # Fig 4 Labels
        'fig4_loa': r"かみ合い線 (作用線, $n-n$)",
        'fig4_pitch_line': r"ピッチ点共通接線 ($t_P - t_P$)",
        'fig4_centerline': "中心線 (Line of Centers)",
        'fig4_point_p': r"$P$ (ピッチ点)",
        'fig4_point_a': r"$A$ (かみ合い開始点, SAP)",
        'fig4_point_e': r"$E$ (かみ合い終了点, EAP)",
        'fig4_point_b': r"$B$ (単一接触下限点)",
        'fig4_point_d': r"$D$ (単一接触上限点)",
        'fig4_point_n1': r"$N_1$ (ピニオン基礎円接点)",
        'fig4_point_n2': r"$N_2$ (ギヤ基礎円接点)",
        'fig4_pinion_tip': r"ピニオン歯先円 ($r_{a1}$)",
        'fig4_gear_tip': r"ギヤ歯先円 ($r_{a2}$)",
        'fig4_active_path': r"実かみ合い長さ $\overline{AE}$ ($g_\alpha = g_a + g_f$)",
        'fig4_ga_gf': r"$g_f = \overline{AP}$ (接近かみ合い長さ),  $g_a = \overline{PE}$ (遠退かみ合い長さ)",
        'fig4_base_pitch_bar': r"基礎円ピッチ $p_b = \pi m \cos\alpha$",
        'fig4_single_pair': "単一歯接触 (100% 負荷)",
        'fig4_double_pair': "2歯接触 (50% 分担)",
        'fig4_card_title': "[かみ合い長さ及び正面かみ合い率の厳密閉形式]",
        'fig4_card_body': (
            "(1) かみ合い長さ閉形式:  $g_\\alpha = \\sqrt{r_{a1}^2 - r_{b1}^2} + \\sqrt{r_{a2}^2 - r_{b2}^2} - a \\sin\\alpha = 14.558\\;\\mathrm{mm}$\n"
            "(2) 正面かみ合い率:  $\\epsilon_\\alpha = \\frac{g_\\alpha}{p_b} = \\frac{14.558}{8.856} = 1.644 \\geq 1.20$ (設計合格)\n"
            "(3) 接触区間分担:  単一歯接触 $g_1 = 3.155\\;\\mathrm{mm}$ (21.7%),  2歯接触 $g_2 = 11.403\\;\\mathrm{mm}$ (78.3%)\n"
            "[工学的意義] $\\epsilon_\\alpha \\geq 1.20$ 確保により伝達誤差緩衝と無衝撃連続動力を実現"
        ),
    }
}


def get_tr(key: str, lang: str) -> str:
    """Retrieve localized string with English fallback."""
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    return TRANSLATIONS['en'].get(key, key)


# ---------------------------------------------------------------------------
# Drawing Utility Helpers
# ---------------------------------------------------------------------------
def draw_vector(ax, start, end, color=COLOR_TEXT_MAIN, lw=1.2,
                mutation_scale=11, zorder=6, linestyle='-'):
    """Draws a clean, slim vector arrow."""
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle='-|>,head_length=0.42,head_width=0.20',
        mutation_scale=mutation_scale,
        color=color, linewidth=lw,
        linestyle=linestyle,
        shrinkA=0, shrinkB=0,
        zorder=zorder
    )
    ax.add_patch(arrow)
    return arrow


def draw_circular_arrow(ax, center, radius, theta_start_deg, theta_end_deg,
                        color=COLOR_TEXT_MAIN, lw=1.0, mutation_scale=10, zorder=6):
    """Draws an arc arrow tangentially aligned with circular trajectory."""
    n_pts = 45
    thetas = np.linspace(np.radians(theta_start_deg), np.radians(theta_end_deg), n_pts)
    verts = np.column_stack([center[0] + radius * np.cos(thetas),
                             center[1] + radius * np.sin(thetas)])
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * (n_pts - 1)
    path = MplPath(verts, codes)
    arrow = FancyArrowPatch(
        path=path,
        arrowstyle='-|>,head_length=0.40,head_width=0.18',
        shrinkA=0, shrinkB=0,
        mutation_scale=mutation_scale,
        color=color, linewidth=lw,
        zorder=zorder
    )
    ax.add_patch(arrow)
    return arrow


def draw_right_angle(ax, vertex, v1, v2, size=0.25, color=COLOR_TEXT_MUTED, lw=0.8):
    """Draws a clean, slim orthogonal right-angle marker."""
    u1 = v1 / np.linalg.norm(v1) * size
    u2 = v2 / np.linalg.norm(v2) * size
    corner = vertex + u1 + u2
    ax.plot([vertex[0] + u1[0], corner[0], vertex[0] + u2[0]],
            [vertex[1] + u1[1], corner[1], vertex[1] + u2[1]],
            color=color, lw=lw, zorder=5)


def draw_leader_annotation(ax, pt, text_pos, text, color=COLOR_TEXT_MAIN,
                           fontsize=11.5, lw=0.7, ha='center', va='center',
                           box_fc="white", box_ec="none", box_alpha=0.92):
    """Draws a slim leader line from point to text box."""
    ax.annotate(
        text, xy=pt, xytext=text_pos,
        ha=ha, va=va,
        fontsize=fontsize, fontweight='normal', color=color,
        arrowprops=dict(
            arrowstyle="-",
            color=COLOR_TEXT_MUTED,
            lw=lw,
            shrinkA=2, shrinkB=2
        ),
        bbox=dict(
            boxstyle="round,pad=0.20",
            fc=box_fc, ec=box_ec, lw=0.8,
            alpha=box_alpha
        ),
        zorder=8
    )


# ---------------------------------------------------------------------------
# Save Diagram Helper
# ---------------------------------------------------------------------------
def save_diagram(fig, base_name, output_dir, dpi, formats):
    """Saves figure in requested formats with tight bounds and pure white background."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    if formats in ('all', 'svg'):
        svg_path = output_dir / f"{base_name}.svg"
        fig.savefig(svg_path, format='svg', bbox_inches='tight', pad_inches=0.18,
                    facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(svg_path)
    if formats in ('all', 'png'):
        png_path = output_dir / f"{base_name}.png"
        fig.savefig(png_path, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0.18,
                    facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(png_path)
    
    plt.close(fig)
    for p in saved_paths:
        size_kb = p.stat().st_size / 1024
        print(f"  [SAVED] {p.name:<38} ({size_kb:6.1f} KB) -> {p.parent}")


# ---------------------------------------------------------------------------
# Diagram 1: Involute Generation Principle (fig1_involute_generation)
# ---------------------------------------------------------------------------
def create_diagram_1(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 1: Generation Principle of the Involute Curve from Base Circle.
    Shows unwinding taut string, roll angle theta, pressure angle alpha_K,
    curvature radius rho_K = r_b * theta, and 3 invariance laws.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 1: fig1_involute_generation [{lang.upper()}] (8.0 x 9.5 in, 300 DPI)...")

    fig = plt.figure(figsize=(8.0, 9.5), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)

    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')

    rb = 3.3
    O = np.array([0.0, 0.0])
    A0 = np.array([rb, 0.0])

    # Reference centerlines (Slim 0.7 pt)
    ax.plot([-1.2, 5.4], [0, 0], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)
    ax.plot([0, 0], [-1.0, 4.8], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)

    # Base Circle arc (theta from -15 deg to 95 deg)
    phi_bc = np.linspace(np.radians(-15), np.radians(95), 180)
    bc_x = rb * np.cos(phi_bc)
    bc_y = rb * np.sin(phi_bc)
    ax.plot(bc_x, bc_y, color=COLOR_PINION, linestyle="--", lw=1.1, zorder=2)
    ax.fill_between(bc_x, 0, bc_y, where=(bc_x >= 0) & (bc_y >= 0),
                    color=COLOR_PINION, alpha=0.04, zorder=1)

    # Involute Curve parametric generation (theta from 0 to 1.05 rad ~ 60.16 deg)
    theta_arr = np.linspace(0.0, 1.05, 200)
    inv_x = rb * (np.cos(theta_arr) + theta_arr * np.sin(theta_arr))
    inv_y = rb * (np.sin(theta_arr) - theta_arr * np.cos(theta_arr))
    ax.plot(inv_x, inv_y, color=COLOR_PINION, lw=1.5, zorder=4)

    # Active Demonstration Point K at theta_0 = 0.82 rad (~47.0 deg)
    th0 = 0.82
    N = np.array([rb * np.cos(th0), rb * np.sin(th0)])
    # Tangent vector from N towards K: length is rho = rb * th0
    u_tan = np.array([np.sin(th0), -np.cos(th0)])
    rho = rb * th0
    K = N + rho * u_tan

    # Ghost unwinding strings (Intermediate steps: th1=0.32, th2=0.58)
    for th_g, ls, alp in [(0.32, ':', 0.45), (0.58, '--', 0.60)]:
        Ng = np.array([rb * np.cos(th_g), rb * np.sin(th_g)])
        Kg = np.array([rb * (np.cos(th_g) + th_g * np.sin(th_g)),
                       rb * (np.sin(th_g) - th_g * np.cos(th_g))])
        ax.plot([Ng[0], Kg[0]], [Ng[1], Kg[1]], color=COLOR_CONTACT,
                linestyle=ls, lw=1.0, alpha=alp, zorder=3)
        ax.scatter([Kg[0]], [Kg[1]], color=COLOR_CONTACT, s=25, alpha=alp, zorder=4)

    # Current Taut String line segment N -> K (Thick amber line, lw=1.4)
    ax.plot([N[0], K[0]], [N[1], K[1]], color=COLOR_CONTACT, lw=1.4, zorder=5)

    # Radius ray ON and OK
    ax.plot([0, N[0]], [0, N[1]], color=COLOR_AXIS, lw=1.0, zorder=2)
    ax.plot([0, K[0]], [0, K[1]], color=COLOR_TEXT_MUTED, linestyle="--", lw=0.9, zorder=2)

    # Right angle marker at N: ON perpendicular to NK
    draw_right_angle(ax, N, -N, K - N, size=0.25, color=COLOR_TEXT_MUTED, lw=0.8)

    # Roll Angle Arc (from x-axis (0 deg) to ray ON (th0)) at radius r=1.35
    draw_circular_arrow(ax, O, 1.35, 0, np.degrees(th0), color=COLOR_TEXT_MAIN, lw=0.9, mutation_scale=10)
    ax.text(1.50 * np.cos(th0 * 0.5), 1.50 * np.sin(th0 * 0.5), tr('fig1_roll_angle'),
            fontsize=11.5, color=COLOR_TEXT_MAIN, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # Pressure Angle Arc (from ray OK to ray ON) at radius r=2.25
    ang_K_deg = np.degrees(np.arctan2(K[1], K[0]))
    ang_N_deg = np.degrees(th0)
    draw_circular_arrow(ax, O, 2.25, ang_K_deg, ang_N_deg, color=COLOR_NORMAL, lw=0.9, mutation_scale=10)
    ax.text(2.45 * np.cos(np.radians((ang_K_deg + ang_N_deg) * 0.5)),
            2.45 * np.sin(np.radians((ang_K_deg + ang_N_deg) * 0.5)),
            tr('fig1_pressure_angle'), fontsize=11.5, color=COLOR_NORMAL,
            va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # Curvature Radius Dimension (offset parallel to NK)
    n_offset = np.array([np.cos(th0), np.sin(th0)]) * 0.28
    p1 = N + n_offset
    p2 = K + n_offset
    ax.annotate('', xy=p1, xytext=p2,
                arrowprops=dict(arrowstyle='<->,head_length=0.35,head_width=0.18',
                                color=COLOR_CONTACT, lw=0.9))
    mid_nk = (p1 + p2) * 0.5
    ax.text(mid_nk[0] + 0.15, mid_nk[1] + 0.15, tr('fig1_rho_label'),
            fontsize=11.5, color=COLOR_CONTACT, va='bottom', ha='left',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # Critical Key Points & Markers
    ax.scatter([O[0]], [O[1]], color=COLOR_TEXT_MAIN, s=45, zorder=6)
    ax.scatter([A0[0]], [A0[1]], color=COLOR_PINION, s=55, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([N[0]], [N[1]], color=COLOR_PINION, s=55, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([K[0]], [K[1]], color=COLOR_CONTACT, s=70, zorder=7, edgecolors=COLOR_TEXT_MAIN, lw=1.0)

    # Annotations with leader lines or radial placement
    ax.text(-0.25, -0.28, tr('fig1_origin'), fontsize=11.5, color=COLOR_TEXT_MAIN, ha='right', va='top')
    ax.text(A0[0] + 0.20, -0.32, tr('fig1_a0'), fontsize=11.5, color=COLOR_PINION, ha='left', va='top',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))
    ax.text(N[0] - 0.25, N[1] + 0.25, tr('fig1_tangent_n'), fontsize=11.5, color=COLOR_PINION, ha='right', va='bottom',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))
    ax.text(K[0] + 0.15, K[1] - 0.15, tr('fig1_point_k'), fontsize=11.0, color=COLOR_CONTACT, ha='left', va='top',
            bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=COLOR_CONTACT, lw=0.8, alpha=0.92))

    # Curve label at upper tip of involute
    ax.text(inv_x[-1] - 0.20, inv_y[-1] + 0.25, tr('fig1_involute_curve'),
            fontsize=12.0, color=COLOR_PINION, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PINION, lw=0.8, alpha=0.90))

    # Base Circle Label
    ax.text(-0.35, 3.45, tr('fig1_base_circle'), fontsize=11.5, color=COLOR_PINION, ha='right', va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # Bottom Invariance Laws Callout Card
    card_x, card_y, card_w, card_h = -1.6, -4.9, 7.8, 1.85
    card_patch = patches.FancyBboxPatch((card_x, card_y), card_w, card_h, boxstyle="round,pad=0.25",
                                        fc="#F8FAFC", ec=COLOR_AXIS, lw=1.0, zorder=2)
    ax.add_patch(card_patch)
    card_full_text = f"{tr('fig1_card_title')}\n\n{tr('fig1_card_body')}"
    ax.text(card_x + card_w * 0.5, card_y + card_h * 0.5, card_full_text,
            fontsize=9.8, color=COLOR_TEXT_MAIN, ha='center', va='center',
            linespacing=1.30, zorder=4)

    ax.set_xlim(-2.0, 6.7)
    ax.set_ylim(-5.35, 5.25)
    ax.set_title(tr('fig1_title'), fontsize=15.0, fontweight='normal', pad=16, color=COLOR_TEXT_MAIN)

    save_diagram(fig, "fig1_involute_generation", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 2: Involute Function Geometry (fig2_involute_function_geometry)
# ---------------------------------------------------------------------------
def create_diagram_2(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 2: Geometric Interpretation and Derivation of Involute Function inv alpha.
    Focuses on right triangle Delta ONK and circular sector O A0 N.
    Proves theta = tan alpha and inv alpha = tan alpha - alpha.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 2: fig2_involute_function_geometry [{lang.upper()}] (8.0 x 9.5 in, 300 DPI)...")

    fig = plt.figure(figsize=(8.0, 9.5), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)

    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')

    rb = 4.0
    O = np.array([0.0, 0.0])
    A0 = np.array([rb, 0.0])

    # Choose clear, representative pressure angle for diagram visualization (alpha = 36 deg)
    alpha_rad = np.radians(36.0)
    theta_rad = np.tan(alpha_rad)       # tan(36 deg) ~ 0.7265 rad ~ 41.63 deg
    phi_inv = theta_rad - alpha_rad     # inv(alpha) ~ 0.7265 - 0.6283 = 0.0982 rad ~ 5.63 deg

    N = np.array([rb * np.cos(theta_rad), rb * np.sin(theta_rad)])
    r_k = rb / np.cos(alpha_rad)
    K = np.array([r_k * np.cos(phi_inv), r_k * np.sin(phi_inv)])

    # Reference axes
    ax.plot([-0.8, 5.8], [0, 0], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)
    ax.plot([0, 0], [-0.8, 4.6], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)

    # Base Circle Arc (phi from -5 deg to 55 deg)
    phi_bc = np.linspace(np.radians(-5), np.radians(55), 150)
    ax.plot(rb * np.cos(phi_bc), rb * np.sin(phi_bc), color=COLOR_PINION, linestyle="--", lw=1.1, zorder=2)

    # Shaded Right Triangle Delta ONK (Soft Blue tint)
    triangle_pts = np.array([O, N, K])
    tri_patch = patches.Polygon(triangle_pts, closed=True,
                                facecolor="#EFF6FF", edgecolor=COLOR_PINION, lw=1.2, alpha=0.45, zorder=2)
    ax.add_patch(tri_patch)

    # Highlight Base Circle Arc A0 -> N (Vibrant Forest Teal, lw=2.4)
    phi_arc = np.linspace(0.0, theta_rad, 80)
    ax.plot(rb * np.cos(phi_arc), rb * np.sin(phi_arc), color=COLOR_GEAR, lw=2.4, zorder=4)

    # Highlight Tangent Segment N -> K (Vibrant Forest Teal, lw=2.2)
    ax.plot([N[0], K[0]], [N[1], K[1]], color=COLOR_GEAR, lw=2.2, zorder=4)

    # Involute curve passing through A0 and K
    th_inv = np.linspace(0.0, theta_rad * 1.25, 120)
    ix = rb * (np.cos(th_inv) + th_inv * np.sin(th_inv))
    iy = rb * (np.sin(th_inv) - th_inv * np.cos(th_inv))
    ax.plot(ix, iy, color=COLOR_PINION, lw=1.4, linestyle="-", zorder=3)

    # Right angle marker at N
    draw_right_angle(ax, N, -N, K - N, size=0.28, color=COLOR_TEXT_MUTED, lw=0.8)

    # Angle Arcs from origin:
    # 1. Roll angle theta (from x-axis 0 deg to ray ON theta_rad) at r=1.25
    r_roll = 1.25
    draw_circular_arrow(ax, O, r_roll, 0, np.degrees(theta_rad), color=COLOR_TEXT_MAIN, lw=0.9, mutation_scale=10)
    ax.text((r_roll + 0.15) * np.cos(theta_rad * 0.55), (r_roll + 0.15) * np.sin(theta_rad * 0.55),
            tr('fig2_roll_angle_theta'), fontsize=11.0, color=COLOR_TEXT_MAIN,
            va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # 2. Pressure angle alpha (from ray OK phi_inv to ray ON theta_rad) at r=2.65
    r_alpha = 2.65
    draw_circular_arrow(ax, O, r_alpha, np.degrees(phi_inv), np.degrees(theta_rad),
                        color=COLOR_NORMAL, lw=0.9, mutation_scale=10)
    mid_alpha = (phi_inv + theta_rad) * 0.5
    ax.text((r_alpha + 0.20) * np.cos(mid_alpha), (r_alpha + 0.20) * np.sin(mid_alpha),
            tr('fig2_pressure_angle_alpha'), fontsize=11.0, color=COLOR_NORMAL,
            va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # 3. Involute polar angle phi_K = inv alpha (from x-axis 0 deg to ray OK phi_inv) at r=3.65
    r_inv = 3.65
    draw_circular_arrow(ax, O, r_inv, 0, np.degrees(phi_inv), color=COLOR_TANGENT, lw=0.9, mutation_scale=10)
    ax.text((r_inv + 0.17) * np.cos(phi_inv * 0.5), (r_inv + 0.17) * np.sin(phi_inv * 0.5) - 0.22,
            tr('fig2_inv_angle'), fontsize=10.5, color=COLOR_TANGENT,
            va='top', ha='left',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))

    # Segment Length Callout: Arc(A0 N) and Segment NK equality
    ax.text(rb * np.cos(theta_rad * 0.45) - 0.45, rb * np.sin(theta_rad * 0.45) + 0.35,
            tr('fig2_arc_len'), fontsize=10.5, color=COLOR_GEAR, ha='right', va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8, alpha=0.90))

    mid_nk = (N + K) * 0.5
    ax.text(mid_nk[0] + 0.35, mid_nk[1] + 0.25,
            tr('fig2_tangent_len'), fontsize=10.5, color=COLOR_GEAR, ha='left', va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8, alpha=0.90))

    # Equality Badge
    ax.text(3.4, 3.8, tr('fig2_equality'), fontsize=11.5, color=COLOR_GEAR, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.22", fc="#F0FDF4", ec=COLOR_GEAR, lw=0.9))

    # Key Point Markers
    ax.scatter([O[0]], [O[1]], color=COLOR_TEXT_MAIN, s=45, zorder=6)
    ax.scatter([A0[0]], [A0[1]], color=COLOR_PINION, s=55, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([N[0]], [N[1]], color=COLOR_PINION, s=55, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([K[0]], [K[1]], color=COLOR_CONTACT, s=70, zorder=7, edgecolors=COLOR_TEXT_MAIN, lw=1.0)

    # Point labels
    ax.text(-0.25, -0.28, r"$O$", fontsize=12.0, color=COLOR_TEXT_MAIN, ha='right', va='top')
    ax.text(A0[0] + 0.15, -0.28, r"$A_0$", fontsize=12.0, color=COLOR_PINION, ha='left', va='top')
    ax.text(N[0] - 0.25, N[1] + 0.22, r"$N$", fontsize=12.0, color=COLOR_PINION, ha='right', va='bottom')
    ax.text(K[0] + 0.20, K[1] + 0.15, r"$K$", fontsize=12.5, color=COLOR_CONTACT, ha='left', va='bottom')

    # Bottom Involute Function Callout Card
    card_x, card_y, card_w, card_h = -1.2, -4.8, 7.5, 1.95
    card_patch = patches.FancyBboxPatch((card_x, card_y), card_w, card_h, boxstyle="round,pad=0.25",
                                        fc="#F8FAFC", ec=COLOR_AXIS, lw=1.0, zorder=2)
    ax.add_patch(card_patch)
    card_full_text = f"{tr('fig2_card_title')}\n\n{tr('fig2_card_body')}"
    ax.text(card_x + card_w * 0.5, card_y + card_h * 0.5, card_full_text,
            fontsize=9.6, color=COLOR_TEXT_MAIN, ha='center', va='center',
            linespacing=1.30, zorder=4)

    ax.set_xlim(-1.6, 7.0)
    ax.set_ylim(-5.25, 4.8)
    ax.set_title(tr('fig2_title'), fontsize=15.0, fontweight='normal', pad=16, color=COLOR_TEXT_MAIN)

    save_diagram(fig, "fig2_involute_function_geometry", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 3: Spur Gear Four Fundamental Circles (fig3_spur_gear_four_circles)
# ---------------------------------------------------------------------------
def create_diagram_3(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 3: Four Fundamental Circles and Standard Proportions of Spur Gear.
    Displays Tip Circle (da), Pitch Circle (d), Base Circle (db), Root Circle (df)
    along with ISO 53 / KS B 0053 basic rack proportions (ha, hf, c, h, p, s, e, pb).
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 3: fig3_spur_gear_four_circles [{lang.upper()}] (8.0 x 9.5 in, 300 DPI)...")

    fig = plt.figure(figsize=(8.0, 9.5), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)

    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')

    # Gear Proportions (Module m=6.0, z=19, alpha=20 deg)
    m = 6.0
    z = 19
    alpha_deg = 20.0
    alpha_rad = np.radians(alpha_deg)

    r = (m * z) * 0.5            # 57.0 mm (Pitch radius)
    rb = r * np.cos(alpha_rad)   # 53.562 mm (Base radius)
    ha = 1.0 * m                 # 6.0 mm (Addendum)
    hf = 1.25 * m                # 7.5 mm (Dedendum)
    c = 0.25 * m                 # 1.5 mm (Clearance)
    ra = r + ha                  # 63.0 mm (Tip radius)
    rf = r - hf                  # 49.5 mm (Root radius)
    p = np.pi * m                # 18.850 mm (Circular pitch)
    s = p * 0.5                  # 9.425 mm (Tooth thickness)
    pb = p * np.cos(alpha_rad)   # 17.713 mm (Base pitch)

    # Place gear center below canvas so pitch point is at (0, 0)
    O_gear = np.array([0.0, -r])

    # Plot 4 Concentric Circle Arcs across angular span (-28 deg to +28 deg)
    span_deg = 28.0
    thetas = np.linspace(np.radians(90 - span_deg), np.radians(90 + span_deg), 240)

    # Tip Circle da (Teal, solid, lw=1.3)
    ax.plot(O_gear[0] + ra * np.cos(thetas), O_gear[1] + ra * np.sin(thetas),
            color=COLOR_GEAR, lw=1.3, linestyle="-", zorder=3)

    # Pitch Circle d (Slate Violet, dashdot, lw=1.3)
    ax.plot(O_gear[0] + r * np.cos(thetas), O_gear[1] + r * np.sin(thetas),
            color=COLOR_TANGENT, lw=1.3, linestyle="-.", zorder=3)

    # Base Circle db (Royal Blue, dashed, lw=1.1)
    ax.plot(O_gear[0] + rb * np.cos(thetas), O_gear[1] + rb * np.sin(thetas),
            color=COLOR_PINION, lw=1.1, linestyle="--", zorder=3)

    # Root Circle df (Crimson, dashed, lw=1.1)
    ax.plot(O_gear[0] + rf * np.cos(thetas), O_gear[1] + rf * np.sin(thetas),
            color=COLOR_NORMAL, lw=1.1, linestyle="--", zorder=3)

    # Centerline
    ax.plot([0, 0], [-10.5, 9.5], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)

    # Generate exact involute tooth profiles for 2 adjacent teeth and 1 tooth space
    # Pitch angular pitch is 2*pi / z
    pitch_ang = 2.0 * np.pi / z
    tooth_half_ang = (s / (2.0 * r))

    def get_tooth_contour(center_ang):
        """Generates profile coordinates of a tooth centered at center_ang."""
        r_eval = np.linspace(rb, ra, 60)
        alpha_eval = np.arccos(rb / r_eval)
        inv_eval = np.tan(alpha_eval) - alpha_eval
        inv_alpha = np.tan(alpha_rad) - alpha_rad
        psi = tooth_half_ang + inv_alpha - inv_eval

        # Left flank (from rb to ra)
        left_ang = center_ang - psi
        lx = O_gear[0] + r_eval * np.sin(left_ang)
        ly = O_gear[1] + r_eval * np.cos(left_ang)

        # Right flank (from ra down to rb)
        right_ang = center_ang + psi[::-1]
        rx = O_gear[0] + r_eval[::-1] * np.sin(right_ang)
        ry = O_gear[1] + r_eval[::-1] * np.cos(right_ang)

        # Tip land arc at ra
        tip_ang = np.linspace(center_ang - psi[-1], center_ang + psi[-1], 20)
        tx = O_gear[0] + ra * np.sin(tip_ang)
        ty = O_gear[1] + ra * np.cos(tip_ang)

        # Root fillet extension down to rf
        root_lx = [O_gear[0] + rf * np.sin(center_ang - psi[0] - 0.02), lx[0]]
        root_ly = [O_gear[1] + rf * np.cos(center_ang - psi[0] - 0.02), ly[0]]
        root_rx = [rx[-1], O_gear[0] + rf * np.sin(center_ang + psi[0] + 0.02)]
        root_ry = [ry[-1], O_gear[1] + rf * np.cos(center_ang + psi[0] + 0.02)]

        all_x = np.concatenate([root_lx, lx, tx, rx, root_rx])
        all_y = np.concatenate([root_ly, ly, ty, ry, root_ry])
        return all_x, all_y

    # Tooth 1 (Left, centered at -pitch_ang / 2)
    t1_x, t1_y = get_tooth_contour(-pitch_ang * 0.5)
    ax.plot(t1_x, t1_y, color=COLOR_TEXT_MAIN, lw=1.3, zorder=4)
    ax.fill(t1_x, t1_y, color=COLOR_PINION, alpha=0.08, zorder=2)

    # Tooth 2 (Right, centered at +pitch_ang / 2)
    t2_x, t2_y = get_tooth_contour(pitch_ang * 0.5)
    ax.plot(t2_x, t2_y, color=COLOR_TEXT_MAIN, lw=1.3, zorder=4)
    ax.fill(t2_x, t2_y, color=COLOR_PINION, alpha=0.08, zorder=2)

    # Pitch point P
    ax.scatter([0.0], [0.0], color=COLOR_NORMAL, s=55, zorder=7)
    ax.annotate(r"$P$", xy=(0.0, 0.0), xytext=(1.5, 1.2),
                fontsize=12.0, color=COLOR_NORMAL, ha='left', va='bottom',
                arrowprops=dict(arrowstyle="-", color=COLOR_NORMAL, lw=0.6),
                bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec=COLOR_NORMAL, lw=0.7, alpha=0.92))

    # Left Leader Annotations for the 4 Fundamental Circles (Monotonic Stack outside tooth profile)
    ax.annotate(tr('fig3_tip_circle'),
                xy=(-21.5, -r + ra * np.cos(np.radians(22))), xytext=(-38.5, 8.5),
                fontsize=10.0, color=COLOR_GEAR, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8, alpha=0.90))

    ax.annotate(tr('fig3_pitch_circle'),
                xy=(-23.5, -r + r * np.cos(np.radians(24))), xytext=(-38.5, 3.2),
                fontsize=10.0, color=COLOR_TANGENT, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_TANGENT, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_TANGENT, lw=0.8, alpha=0.90))

    ax.annotate(tr('fig3_base_circle'),
                xy=(-22.5, -r + rb * np.cos(np.radians(25))), xytext=(-38.5, -2.2),
                fontsize=10.0, color=COLOR_PINION, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_PINION, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PINION, lw=0.8, alpha=0.90))

    ax.annotate(tr('fig3_root_circle'),
                xy=(-20.0, -r + rf * np.cos(np.radians(26))), xytext=(-38.5, -7.8),
                fontsize=10.0, color=COLOR_NORMAL, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.90))

    # Right Radial Dimension Bars (ha, hf, c, h) - Clean offset from tooth profile
    dim_x = 16.5
    y_tip = ra - r
    y_pitch = 0.0
    y_root = rf - r

    # Addendum ha: pitch to tip
    ax.plot([dim_x, dim_x], [y_pitch, y_tip], color=COLOR_GEAR, lw=1.2, zorder=5)
    ax.scatter([dim_x, dim_x], [y_pitch, y_tip], marker='_', color=COLOR_GEAR, s=60, zorder=5)
    ax.text(dim_x + 0.5, (y_pitch + y_tip) * 0.5, tr('fig3_ha'),
            fontsize=9.8, color=COLOR_GEAR, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))

    # Dedendum hf: root to pitch
    ax.plot([dim_x, dim_x], [y_root, y_pitch], color=COLOR_NORMAL, lw=1.2, zorder=5)
    ax.scatter([dim_x, dim_x], [y_root, y_pitch], marker='_', color=COLOR_NORMAL, s=60, zorder=5)
    ax.text(dim_x + 0.5, (y_root + y_pitch) * 0.5, tr('fig3_hf'),
            fontsize=9.8, color=COLOR_NORMAL, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))

    # Whole depth h: root to tip (further right at dim_x2)
    dim_x2 = 22.8
    ax.plot([dim_x2, dim_x2], [y_root, y_tip], color=COLOR_TEXT_MAIN, lw=1.2, zorder=5)
    ax.scatter([dim_x2, dim_x2], [y_root, y_tip], marker='_', color=COLOR_TEXT_MAIN, s=60, zorder=5)
    ax.text(dim_x2 + 0.5, (y_root + y_tip) * 0.5, tr('fig3_h'),
            fontsize=9.8, color=COLOR_TEXT_MAIN, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))

    # Tooth thickness s on Tooth 1 (Dimension arc + Leader to clear top margin!)
    ang_t1_c = -pitch_ang * 0.5
    th_s_span = np.linspace(np.radians(90 - np.degrees(ang_t1_c + tooth_half_ang)),
                            np.radians(90 - np.degrees(ang_t1_c - tooth_half_ang)), 30)
    ax.plot(O_gear[0] + r * np.cos(th_s_span), O_gear[1] + r * np.sin(th_s_span),
            color=COLOR_TANGENT, lw=2.2, zorder=5)

    t1_mid_x = O_gear[0] + r * np.sin(ang_t1_c)
    t1_mid_y = O_gear[1] + r * np.cos(ang_t1_c)
    ax.annotate(tr('fig3_thick_s'),
                xy=(t1_mid_x, t1_mid_y), xytext=(t1_mid_x, 11.2),
                fontsize=10.0, color=COLOR_TANGENT, ha='center', va='bottom',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_TANGENT, lw=0.9),
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=COLOR_TANGENT, lw=0.8, alpha=0.95))

    # Tooth space width e (Dimension arc + Leader to bottom margin!)
    th_e_span = np.linspace(np.radians(90 - np.degrees(pitch_ang * 0.5 - tooth_half_ang)),
                            np.radians(90 - np.degrees(-pitch_ang * 0.5 + tooth_half_ang)), 30)
    ax.plot(O_gear[0] + r * np.cos(th_e_span), O_gear[1] + r * np.sin(th_e_span),
            color=COLOR_TANGENT, lw=2.2, zorder=5)

    ax.annotate(tr('fig3_space_e'),
                xy=(0.0, 0.0), xytext=(0.0, -11.5),
                fontsize=10.0, color=COLOR_TANGENT, ha='center', va='top',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_TANGENT, lw=0.9),
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=COLOR_TANGENT, lw=0.8, alpha=0.95))

    # Bottom Standard Rack Proportions Callout Card
    card_x, card_y, card_w, card_h = -37.5, -32.0, 75.0, 16.5
    card_patch = patches.FancyBboxPatch((card_x, card_y), card_w, card_h, boxstyle="round,pad=0.25",
                                        fc="#F8FAFC", ec=COLOR_AXIS, lw=1.0, zorder=2)
    ax.add_patch(card_patch)
    card_full_text = f"{tr('fig3_card_title')}\n\n{tr('fig3_card_body')}"
    ax.text(card_x + card_w * 0.5, card_y + card_h * 0.5, card_full_text,
            fontsize=9.5, color=COLOR_TEXT_MAIN, ha='center', va='center',
            linespacing=1.30, zorder=4)

    ax.set_xlim(-41.0, 41.0)
    ax.set_ylim(-34.0, 15.5)
    ax.set_title(tr('fig3_title'), fontsize=15.0, fontweight='normal', pad=16, color=COLOR_TEXT_MAIN)

    save_diagram(fig, "fig3_spur_gear_four_circles", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 4: Line of Action and Contact Path (fig4_line_of_action_contact_path)
# ---------------------------------------------------------------------------
def create_diagram_4(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 4: Line of Action, Path of Contact (AE), and Transverse Contact Ratio (eps_alpha).
    Exact closed-form benchmark: m=3, z1=19, z2=47, alpha=20 deg, a=99 mm.
    Shows SAP (A), Pitch Point (P), EAP (E), Single/Double contact sub-zones,
    and rigorous derivation of eps_alpha >= 1.20.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 4: fig4_line_of_action_contact_path [{lang.upper()}] (8.0 x 9.5 in, 300 DPI)...")

    fig = plt.figure(figsize=(8.0, 9.5), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)

    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')

    # Benchmark closed-form dimensions
    m = 3.0
    z1, z2 = 19, 47
    alpha_deg = 20.0
    alpha_rad = np.radians(alpha_deg)

    r1 = 0.5 * m * z1            # 28.5 mm (Pinion pitch radius)
    r2 = 0.5 * m * z2            # 70.5 mm (Gear pitch radius)
    a = r1 + r2                  # 99.0 mm (Center distance)
    rb1 = r1 * np.cos(alpha_rad) # 26.781 mm
    rb2 = r2 * np.cos(alpha_rad) # 66.248 mm
    ra1 = r1 + 1.0 * m           # 31.5 mm
    ra2 = r2 + 1.0 * m           # 73.5 mm

    # Closed-form contact lengths
    gf = np.sqrt(ra2**2 - rb2**2) - rb2 * np.tan(alpha_rad)  # 7.721662 mm (AP)
    ga = np.sqrt(ra1**2 - rb1**2) - rb1 * np.tan(alpha_rad)  # 6.836008 mm (PE)
    g_alpha = gf + ga                                        # 14.557670 mm (AE)
    pb = np.pi * m * np.cos(alpha_rad)                       # 8.856394 mm
    eps_alpha = g_alpha / pb                                 # 1.643747

    # Center coordinates: Pitch point P at (0, 0)
    O1 = np.array([0.0, -r1])
    O2 = np.array([0.0, r2])
    P = np.array([0.0, 0.0])

    # Line of centers (Slim 0.7 pt dashdot)
    ax.plot([0, 0], [-13.0, 13.0], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)

    # Pitch Tangent line (t_P - t_P)
    ax.plot([-28.0, 28.0], [0, 0], color=COLOR_TANGENT, linestyle="--", lw=0.8, zorder=1)
    ax.text(26.0, -2.0, tr('fig4_pitch_line'), fontsize=10.0, color=COLOR_TANGENT,
            va='top', ha='center',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))

    # Circular Arcs around Pitch Point:
    thetas_p = np.linspace(np.radians(90 - 24), np.radians(90 + 24), 140)
    thetas_g = np.linspace(np.radians(-90 - 15), np.radians(-90 + 15), 140)

    # Pitch circles (tangent at P)
    ax.plot(O1[0] + r1 * np.cos(thetas_p), O1[1] + r1 * np.sin(thetas_p),
            color=COLOR_TANGENT, linestyle="-.", lw=1.0, zorder=2)
    ax.plot(O2[0] + r2 * np.cos(thetas_g), O2[1] + r2 * np.sin(thetas_g),
            color=COLOR_TANGENT, linestyle="-.", lw=1.0, zorder=2)

    # Base circles
    ax.plot(O1[0] + rb1 * np.cos(thetas_p), O1[1] + rb1 * np.sin(thetas_p),
            color=COLOR_PINION, linestyle="--", lw=0.9, zorder=2)
    ax.plot(O2[0] + rb2 * np.cos(thetas_g), O2[1] + rb2 * np.sin(thetas_g),
            color=COLOR_PINION, linestyle="--", lw=0.9, zorder=2)

    # Tip circles
    ax.plot(O1[0] + ra1 * np.cos(thetas_p), O1[1] + ra1 * np.sin(thetas_p),
            color=COLOR_GEAR, linestyle="-", lw=1.1, zorder=2)
    ax.plot(O2[0] + ra2 * np.cos(thetas_g), O2[1] + ra2 * np.sin(thetas_g),
            color=COLOR_GEAR, linestyle="-", lw=1.1, zorder=2)

    # Line of Action Unit Vector: tilted by -alpha from horizontal
    u_loa = np.array([np.cos(alpha_rad), -np.sin(alpha_rad)])

    # Tangency Points on Base Circles:
    t_N2 = -r2 * np.sin(alpha_rad)
    t_N1 = r1 * np.sin(alpha_rad)
    N2 = t_N2 * u_loa
    N1 = t_N1 * u_loa

    # Contact Intersections:
    # Point A (SAP): Gear 2 tip circle intersection, t_A = -gf
    # Point E (EAP): Pinion 1 tip circle intersection, t_E = +ga
    t_A = -gf
    t_E = ga
    A = t_A * u_loa
    E = t_E * u_loa

    # Single-tooth contact limits B and D:
    # Point B: ga - pb
    # Point D: -gf + pb
    t_B = ga - pb
    t_D = -gf + pb
    B = t_B * u_loa
    D = t_D * u_loa

    # Draw Full Line of Action N2 -> N1 (Crimson, lw=1.2)
    loa_ext_start = (t_N2 - 1.5) * u_loa
    loa_ext_end = (t_N1 + 2.0) * u_loa
    ax.plot([loa_ext_start[0], loa_ext_end[0]], [loa_ext_start[1], loa_ext_end[1]],
            color=COLOR_NORMAL, lw=1.2, linestyle="-", zorder=3)

    # Highlight Active Path of Contact AE with Glowing Amber Band (lw=3.2, alpha=0.6)
    ax.plot([A[0], E[0]], [A[1], E[1]], color=COLOR_HIGHLIGHT, lw=3.2, alpha=0.65, zorder=4)
    ax.plot([A[0], E[0]], [A[1], E[1]], color=COLOR_CONTACT, lw=1.5, zorder=5)

    # Tangent rays from O1 to N1 and O2 to N2
    ax.plot([O1[0], N1[0]], [O1[1], N1[1]], color=COLOR_AXIS, linestyle=":", lw=0.8, zorder=2)
    ax.plot([O2[0], N2[0]], [O2[1], N2[1]], color=COLOR_AXIS, linestyle=":", lw=0.8, zorder=2)
    draw_right_angle(ax, N1, O1 - N1, -u_loa, size=0.8, color=COLOR_TEXT_MUTED, lw=0.8)
    draw_right_angle(ax, N2, O2 - N2, u_loa, size=0.8, color=COLOR_TEXT_MUTED, lw=0.8)

    # Markers for Critical Contact Points
    ax.scatter([N1[0], N2[0]], [N1[1], N2[1]], color=COLOR_PINION, s=45, zorder=6)
    ax.scatter([A[0], E[0]], [A[1], E[1]], color=COLOR_NORMAL, s=65, zorder=7, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([B[0], D[0]], [B[1], D[1]], color=COLOR_TEXT_MUTED, s=45, zorder=6)
    ax.scatter([P[0]], [P[1]], color=COLOR_NORMAL, s=70, zorder=8, edgecolors=COLOR_TEXT_MAIN, lw=1.0)

    # Text Annotations for Points (Smart Leader Annotations, 0 Collision with LOA!)
    # Point P: North-West leader to top clear space between LOA and Centerline
    ax.annotate(tr('fig4_point_p'),
                xy=(P[0], P[1]), xytext=(-3.5, 4.5),
                fontsize=11.0, color=COLOR_NORMAL, ha='right', va='bottom',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_NORMAL, lw=0.9),
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.95))

    # Point A: South-West leader
    ax.annotate(tr('fig4_point_a'),
                xy=(A[0], A[1]), xytext=(A[0] - 4.5, A[1] - 4.5),
                fontsize=10.5, color=COLOR_NORMAL, ha='right', va='top',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_NORMAL, lw=0.9),
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.95))

    # Point E: North-East leader into clear space above LOA
    ax.annotate(tr('fig4_point_e'),
                xy=(E[0], E[1]), xytext=(E[0] + 3.5, E[1] + 3.2),
                fontsize=10.5, color=COLOR_NORMAL, ha='left', va='bottom',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_NORMAL, lw=0.9),
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.95))

    # N2 (North-West, well clear of LOA text)
    ax.annotate(tr('fig4_point_n2'),
                xy=(N2[0], N2[1]), xytext=(N2[0] - 1.5, N2[1] + 2.8),
                fontsize=10.0, color=COLOR_PINION, ha='right', va='bottom',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_PINION, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PINION, lw=0.7, alpha=0.92))

    # N1 (Far East / North-East of N1)
    ax.annotate(tr('fig4_point_n1'),
                xy=(N1[0], N1[1]), xytext=(N1[0] + 3.2, N1[1] + 1.8),
                fontsize=10.0, color=COLOR_PINION, ha='left', va='bottom',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_PINION, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PINION, lw=0.7, alpha=0.92))

    # Line of action label (Top-Left clear margin, isolated from pb bar)
    ax.text(-36.0, 17.5, tr('fig4_loa'),
            fontsize=10.5, color=COLOR_NORMAL, ha='left', va='bottom',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.90))

    # Tip Circle identification labels (Outside active contact zone!)
    ax.annotate(tr('fig4_gear_tip'),
                xy=(-16.5, -2.2), xytext=(-26.0, 2.5),
                fontsize=10.0, color=COLOR_GEAR, ha='right', va='center',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8, alpha=0.92))

    ax.annotate(tr('fig4_pinion_tip'),
                xy=(14.0, -5.2), xytext=(18.0, -9.5),
                fontsize=10.0, color=COLOR_GEAR, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8, alpha=0.92))

    # Path of Contact Dimension Bar (Layer 1 Offset: 8.5 mm)
    norm_loa = np.array([np.sin(alpha_rad), np.cos(alpha_rad)])
    bar_offset = norm_loa * 8.5
    bar_A = A + bar_offset
    bar_E = E + bar_offset
    ax.annotate('', xy=bar_A, xytext=bar_E,
                arrowprops=dict(arrowstyle='<->,head_length=0.35,head_width=0.18',
                                color=COLOR_CONTACT, lw=1.1))
    mid_bar = (bar_A + bar_E) * 0.5
    ax.text(mid_bar[0] - 0.5, mid_bar[1] + 0.45, tr('fig4_active_path'),
            fontsize=10.2, color=COLOR_CONTACT, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92))

    # Base pitch pb indicator bar (Layer 2 Offset: 14.0 mm)
    bar2_offset = norm_loa * 14.0
    bar_p1 = A + bar2_offset
    bar_p2 = (t_A + pb) * u_loa + bar2_offset
    ax.annotate('', xy=bar_p1, xytext=bar_p2,
                arrowprops=dict(arrowstyle='<->,head_length=0.35,head_width=0.18',
                                color=COLOR_PINION, lw=1.0))
    mid_p = (bar_p1 + bar_p2) * 0.5
    ax.text(mid_p[0] + 3.0, mid_p[1] + 0.45, tr('fig4_base_pitch_bar'),
            fontsize=10.0, color=COLOR_PINION, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92))

    # Bottom Contact Ratio Summary Card
    card_x, card_y, card_w, card_h = -37.5, -31.5, 75.0, 17.5
    card_patch = patches.FancyBboxPatch((card_x, card_y), card_w, card_h, boxstyle="round,pad=0.35",
                                        fc="#F8FAFC", ec=COLOR_AXIS, lw=1.0, zorder=2)
    ax.add_patch(card_patch)
    card_full_text = f"{tr('fig4_card_title')}\n\n{tr('fig4_card_body')}"
    ax.text(card_x + card_w * 0.5, card_y + card_h * 0.5, card_full_text,
            fontsize=8.8, color=COLOR_TEXT_MAIN, ha='center', va='center',
            linespacing=1.30, zorder=4)

    ax.set_xlim(-41.0, 41.0)
    ax.set_ylim(-33.5, 21.5)
    ax.set_title(tr('fig4_title'), fontsize=15.0, fontweight='normal', pad=16, color=COLOR_TEXT_MAIN)

    save_diagram(fig, "fig4_line_of_action_contact_path", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# CLI Argument Dispatcher
# ---------------------------------------------------------------------------
DIAGRAM_DISPATCH = {
    'fig1': create_diagram_1,
    'fig2': create_diagram_2,
    'fig3': create_diagram_3,
    'fig4': create_diagram_4,
}


def main():
    parser = argparse.ArgumentParser(
        description="H-GEAR STUDIO Blog Part 2 Academic Diagram Generator (32 Assets, Multilingual, 300 DPI)"
    )
    parser.add_argument('--lang', choices=['all', 'ko', 'en', 'de', 'ja'], default='all',
                        help="Language profile to generate (default: all)")
    parser.add_argument('--fig', choices=['all', 'fig1', 'fig2', 'fig3', 'fig4'], default='all',
                        help="Specific diagram to generate (default: all)")
    parser.add_argument('--format', choices=['all', 'png', 'svg'], default='all',
                        help="Output image format (default: all)")
    parser.add_argument('--dpi', type=int, default=300,
                        help="Raster resolution DPI for PNG (default: 300)")
    parser.add_argument('--output-dir', type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help="Root output directory for generated assets")
    args = parser.parse_args()

    languages = ['ko', 'en', 'de', 'ja'] if args.lang == 'all' else [args.lang]
    figs = ['fig1', 'fig2', 'fig3', 'fig4'] if args.fig == 'all' else [args.fig]

    print("=" * 80)
    print("H-GEAR STUDIO Part 2 Academic Diagram Generation Pipeline")
    print(f"  Languages: {languages}")
    print(f"  Diagrams:  {figs}")
    print(f"  Formats:   {args.format}")
    print(f"  DPI:       {args.dpi}")
    print(f"  Output:    {args.output_dir}")
    print("=" * 80)

    total_generated = 0
    base_out = Path(args.output_dir)

    for lang in languages:
        lang_out = base_out / lang
        lang_out.mkdir(parents=True, exist_ok=True)
        print(f"\n--- Processing Language: [{lang.upper()}] ---")
        for fig_key in figs:
            generator_fn = DIAGRAM_DISPATCH[fig_key]
            generator_fn(output_dir=lang_out, dpi=args.dpi, formats=args.format, lang=lang)
            total_generated += (2 if args.format == 'all' else 1)

    print("\n" + "=" * 80)
    print(f"Pipeline Completed Successfully! Total Assets Generated: {total_generated}")
    print("=" * 80)


if __name__ == '__main__':
    main()
