"""
H-GEAR STUDIO Blog Part 3 Academic Diagram Generator (Multilingual & High-Precision)
=====================================================================================
Generates high-precision, publication-quality SVG and PNG diagrams for Chapter 3:
  1. Fig 1: Line of Action Five Singular Points & Meshing Geometry (fig1_line_of_action_five_points)
  2. Fig 2: Tooth Load Sharing Profile & HPSTC Critical Bending (fig2_tooth_load_sharing)
  3. Fig 3: Contact Kinematics, Curvature Radii & Sliding Velocities (fig3_contact_kinematics_velocities)
  4. Fig 4: Specific Sliding Curves & Wear/Scuffing Hazard Zones (fig4_specific_sliding_curves)

Applied Engineering Design Standards:
  - 100% Regular font weights (no bold fonts)
  - Mathematical font scaling for web container (~720px~768px):
      * Title: 15.0 ~ 15.5 pt
      * Card Header: 12.5 ~ 13.0 pt
      * Body Label / Dimension: 11.5 ~ 12.0 pt (>= 11.2 pt threshold)
      * Formula / Sub-details: 10.5 ~ 11.0 pt
      * Footnote / Annotation: 8.3 ~ 9.0 pt
  - Strict line-weight hierarchy:
      * Core curve / Line of action: 1.4 ~ 1.5 pt
      * Fundamental circles: 1.0 ~ 1.2 pt
      * Dimension & leader lines: 0.8 ~ 1.0 pt
      * Centerlines & reference: 0.6 ~ 0.8 pt
      * Contact path highlight band: 3.6 ~ 4.8 pt
  - Zero-overlap layout: radial offsets, leader lines, isolated callout cards
  - Dynamic multilingual typography (ko, en, de, ja)
  - Lossless vector SVG (svg.fonttype='path') and publication 300 DPI PNG (W>=2400, H>=2400)
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

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "images" / "part3"

# ---------------------------------------------------------------------------
# Refined High-Contrast Academic Palette
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
        # Fig 1
        'fig1_title': "그림 1: 작용선(Line of Action) 5대 특이점과 맞물림 궤적 기하학",
        'fig1_point_a': r"점 $A$ (SAP, 물림 시작점)",
        'fig1_point_b': r"점 $B$ (LPSTC, 최하위 단일 접촉점)",
        'fig1_point_p': r"점 $P$ (피치점, 순수 구름 $v_g=0$)",
        'fig1_point_d': r"점 $D$ (HPSTC, 최상위 단일 접촉점)",
        'fig1_point_e': r"점 $E$ (EAP, 물림 종료점)",
        'fig1_point_n1': r"$T_1$ (피니언 기초원 접점)",
        'fig1_point_n2': r"$T_2$ (대기어 기초원 접점)",
        'fig1_loa': r"작용선 (Line of Action, $\alpha_0=20^\circ$)",
        'fig1_pitch_line': "피치선 (Pitch Tangent)",
        'fig1_pinion_tip': r"피니언 이끝원 ($r_{a1}=30.0\text{ mm}$)",
        'fig1_gear_tip': r"대기어 이끝원 ($r_{a2}=84.0\text{ mm}$)",
        'fig1_dim_gf': r"접근 물림길이 $g_f = 7.828\text{ mm}$",
        'fig1_dim_ga': r"후퇴 물림길이 $g_a = 6.774\text{ mm}$",
        'fig1_dim_g_alpha': r"총 유효 물림길이 $g_\alpha = 14.602\text{ mm}$",
        'fig1_dim_pb': r"법선 피치 $p_b = 8.856\text{ mm}$",
        'fig1_dim_bd': r"단일 접촉 구간 $\overline{BD} = 3.111\text{ mm}$",
        'fig1_card_title': "[작용선 5대 특이점과 맞물림 궤적 기하학적 정밀 요약]",
        'fig1_card_body': (
            "1. 5대 특이점: 점 A (SAP) -> 점 B (LPSTC) -> 점 P (피치점) -> 점 D (HPSTC) -> 점 E (EAP)\n"
            r"2. 물림길이 및 법선 피치: $g_f = 7.828\text{ mm}$, $g_a = 6.774\text{ mm} \rightarrow g_\alpha = 14.602\text{ mm}$, $p_b = 8.856\text{ mm}$" + "\n"
            r"3. 정면 물림률: $\epsilon_\alpha = g_\alpha / p_b = 1.649 \geq 1.200$ (단일 접촉 21.3%, 이중 접촉 78.7% 분할 보존)"
        ),

        # Fig 2
        'fig2_title': "그림 2: 작용선 상 하중 분담률 및 HPSTC(점 D) 치근 굽힘 하중 집중 메커니즘",
        'fig2_panel1_title': "작용선 접촉 위치에 따른 정규 하중 분담 프로파일 (Load Sharing)",
        'fig2_panel2_title': "피니언 치아 외팔보 모델 및 HPSTC(점 D) 치근 굽힘 모멘트 지배성",
        'fig2_load_ratio': "하중 분담률 (%)",
        'fig2_double_contact': "이중 접촉 (50%)",
        'fig2_single_contact': "단일 접촉 (100%)",
        'fig2_hpstc_callout': "HPSTC (점 D)\n100% 하중 작용 최상단 (최대 굽힘)",
        'fig2_lpstc_callout': "LPSTC (점 B)\n100% 하중 진입점 (피팅 핵 생성)",
        'fig2_moment_d': r"$M_{b,D} = 1.0 \cdot F_n \cdot h_D$ (최대 굽힘)",
        'fig2_moment_e': r"$M_{b,E} = 0.5 \cdot F_n \cdot h_E \approx 0.60 M_{b,D}$",
        'fig2_lever_arm_d': r"$h_D = 4.25\text{ mm}$",
        'fig2_lever_arm_e': r"$h_E = 5.10\text{ mm}$",
        'fig2_fillet_critical': r"위험 단면 (ISO 6336 $30^\circ$ 접선)",
        'fig2_cantilever_fixed': "치근 고정단",
        'fig2_tooth_tip': "이끝 (Point E)",
        'fig2_tooth_hpstc': "HPSTC (Point D)",
        'fig2_card_title': "[하중 분담률 및 HPSTC 치근 굽힘 집중 핵심 요약]",
        'fig2_card_body': (
            r"1. 단일 치 접촉 구간 ($\overline{BD} = 3.111\text{ mm}$): 전 하중 $100\% F_n$이 단 1쌍의 치에 집중 작용" + "\n"
            r"2. HPSTC (점 D, $r_D = 27.369\text{ mm}$): $100\%$ 하중이 작용하는 최외곽 위치로 최대 굽힘 모멘트 $M_{b,D}$ 발생" + "\n"
            r"3. ISO 6336 파손 기준: 이끝(점 E)은 하중 분담($50\%$)으로 굽힘 모멘트가 $M_{b,D}$의 약 60%에 불과하여 치근 피로는 항상 HPSTC가 지배"
        ),

        # Fig 3
        'fig3_title': "그림 3: 접촉점 기구학, 곡률반경 및 접선·상대 미끄럼 속도 벡터선도",
        'fig3_panel1_title': "접촉점 K에서의 치형 곡률반경 및 순간 접선 속도 기구학",
        'fig3_panel2_title': "작용선 상 접선 속도($v_{t1}, v_{t2}$) 및 상대 미끄럼 속도($v_g$) 분포",
        'fig3_rho1': r"$\rho_1(s) = 5.20\text{ mm}$",
        'fig3_rho2': r"$\rho_2(s) = 31.74\text{ mm}$",
        'fig3_vt1': r"피니언 속도 $v_{t1} = \omega_1 \rho_1$",
        'fig3_vt2': r"대기어 속도 $v_{t2} = \omega_2 \rho_2$",
        'fig3_vg': r"미끄럼 속도 $v_g = v_{t1} - v_{t2}$",
        'fig3_pure_rolling': r"피치점 $P$: $v_g = 0$ (순수 구름)",
        'fig3_pinion_dedendum_neg': "피니언 이뿌리: 음의 미끄럼 ($v_g < 0$)",
        'fig3_pinion_addendum_pos': "피니언 이끝: 양의 미끄럼 ($v_g > 0$)",
        'fig3_velocity_axis': "속도 (정규화)",
        'fig3_pos_axis': "작용선 접촉 위치 s (mm)",
        'fig3_card_title': "[접촉 기구학 및 상대 미끄럼 속도 해석 요약]",
        'fig3_card_body': (
            r"1. 곡률반경 보존 법칙: $\rho_1(s) + \rho_2(s) = a \sin\alpha_0 = 36.938\text{ mm}$ (접촉 전 구간 불변)" + "\n"
            r"2. 접선 속도 일치: 피치점 P ($s=0$)에서 $v_{t1} = v_{t2} \rightarrow$ 상대 미끄럼 속도 $v_g = 0$ (순수 구름)" + "\n"
            r"3. 미끄럼 속도 부호 반전: $v_g(s) = (\omega_1 + \omega_2) s$로 피치점을 기점으로 이뿌리($-$)와 이끝($+$)의 미끄럼 방향이 반전"
        ),

        # Fig 4
        'fig4_title': "그림 4: 치면 상대 미끄럼률(Specific Sliding) 곡선 및 마모·소착 위험 구역",
        'fig4_k1_label': r"피니언 $k_1(s) = 1 - \frac{\rho_2}{u \rho_1}$",
        'fig4_k2_label': r"대기어 $k_2(s) = 1 - \frac{u \rho_1}{\rho_2}$",
        'fig4_asymptote_t1': r"$T_1$ 점근선 ($\rho_1 \to 0$)",
        'fig4_danger_zone_pinion': "피니언 이뿌리 고위험 지대 (소착/스코어링, k1 < -1)",
        'fig4_danger_zone_gear': "대기어 이뿌리 주의 지대 (k2 < -1)",
        'fig4_pure_rolling_point': "피치점 $P$: $k_1 = k_2 = 0$\n(순수 구름, 피팅 위험)",
        'fig4_pt_a_annot': r"점 $A$: $k_1 = -7.420$ (극대 음의 미끄럼)",
        'fig4_pt_b_annot': r"점 $B$: $k_1 = -0.388$",
        'fig4_pt_d_annot': r"점 $D$: $k_2 = -0.154$",
        'fig4_pt_e_annot': r"점 $E$: $k_2 = -1.295$",
        'fig4_identity_box': r"항등식: $(1 - k_1)(1 - k_2) \equiv 1.0$",
        'fig4_asymmetry_box': "미끄럼률 비대칭: |k1,A|=7.42 >> |k2,E|=1.29\n(u=3 -> 정전위 x1 > 0 설계 필요)",
        'fig4_y_axis': "상대 미끄럼률 k (Specific Sliding)",
        'fig4_x_axis': "작용선 상 접촉 위치 s (mm, 피치점 P 기준)",
        'fig4_card_title': "[치면 상대 미끄럼률(Specific Sliding) 및 마모 역학 핵심 요약]",
        'fig4_card_body': (
            r"1. 미끄럼률 정의: $k_1 = 1 - \rho_2 / (u \rho_1)$, $k_2 = 1 - (u \rho_1) / \rho_2$ (전 구간 항등식 $(1-k_1)(1-k_2) \equiv 1$ 성립)" + "\n"
            r"2. 피치점 $P$: $k_1 = k_2 = 0$ (순수 구름 접촉, 반복 전동 압축에 의한 피팅 발생 구역)" + "\n"
            r"3. 비대칭성: 점 A에서 피니언 $k_1 = -7.420$으로 유막 파괴 및 스코어링 위험 집중 $\rightarrow$ 정전위 ($x_1 > 0$) 설계 필요"
        ),
    },

    'en': {
        # Fig 1
        'fig1_title': "Fig 1: Line of Action Five Singular Points and Meshing Path Geometry",
        'fig1_point_a': r"Point $A$ (SAP, Start of Active Profile)",
        'fig1_point_b': r"Point $B$ (LPSTC, Lowest Single Contact)",
        'fig1_point_p': r"Point $P$ (Pitch Point, Pure Rolling $v_g=0$)",
        'fig1_point_d': r"Point $D$ (HPSTC, Highest Single Contact)",
        'fig1_point_e': r"Point $E$ (EAP, End of Active Profile)",
        'fig1_point_n1': r"$T_1$ (Pinion Base Circle)",
        'fig1_point_n2': r"$T_2$ (Gear Base Circle)",
        'fig1_loa': r"Line of Action ($\alpha_0=20^\circ$)",
        'fig1_pitch_line': "Pitch Tangent",
        'fig1_pinion_tip': r"Pinion Tip Circle ($r_{a1}=30.0\text{ mm}$)",
        'fig1_gear_tip': r"Gear Tip Circle ($r_{a2}=84.0\text{ mm}$)",
        'fig1_dim_gf': r"Approach Path $g_f = 7.828\text{ mm}$",
        'fig1_dim_ga': r"Recess Path $g_a = 6.774\text{ mm}$",
        'fig1_dim_g_alpha': r"Total Active Path $g_\alpha = 14.602\text{ mm}$",
        'fig1_dim_pb': r"Base Pitch $p_b = 8.856\text{ mm}$",
        'fig1_dim_bd': r"Single Contact Zone $\overline{BD} = 3.111\text{ mm}$",
        'fig1_card_title': "[Summary: Line of Action Five Singular Points & Contact Ratio]",
        'fig1_card_body': (
            "1. Sequential Points: Point A (SAP) -> Point B (LPSTC) -> Point P (Pitch) -> Point D (HPSTC) -> Point E (EAP)\n"
            r"2. Path Lengths: $g_f = 7.828\text{ mm}$, $g_a = 6.774\text{ mm} \rightarrow g_\alpha = 14.602\text{ mm}$, $p_b = 8.856\text{ mm}$" + "\n"
            r"3. Transverse Contact Ratio: $\epsilon_\alpha = g_\alpha / p_b = 1.649 \geq 1.200$ (Single 21.3%, Double 78.7% partition)"
        ),

        # Fig 2
        'fig2_title': "Fig 2: Tooth Load Sharing Profile along LOA and HPSTC (Point D) Critical Bending Stress",
        'fig2_panel1_title': "Normal Load Sharing Profile along Line of Action",
        'fig2_panel2_title': "Pinion Tooth Cantilever Model & HPSTC (Point D) Bending Dominance",
        'fig2_load_ratio': "Load Sharing Ratio (%)",
        'fig2_double_contact': "Double Contact (50%)",
        'fig2_single_contact': "Single Contact (100%)",
        'fig2_hpstc_callout': "HPSTC (Point D)\n100% Load at Max Lever Arm",
        'fig2_lpstc_callout': "LPSTC (Point B)\n100% Load Inception (Pitting)",
        'fig2_moment_d': r"$M_{b,D} = 1.0 \cdot F_n \cdot h_D$ (Max Bending)",
        'fig2_moment_e': r"$M_{b,E} = 0.5 \cdot F_n \cdot h_E \approx 0.60 M_{b,D}$",
        'fig2_lever_arm_d': r"$h_D = 4.25\text{ mm}$",
        'fig2_lever_arm_e': r"$h_E = 5.10\text{ mm}$",
        'fig2_fillet_critical': r"Critical Section (ISO 6336 $30^\circ$ Tangent)",
        'fig2_cantilever_fixed': "Root Fixed End",
        'fig2_tooth_tip': "Tooth Tip (Point E)",
        'fig2_tooth_hpstc': "HPSTC (Point D)",
        'fig2_card_title': "[Summary: Tooth Load Sharing & HPSTC Bending Mechanics]",
        'fig2_card_body': (
            r"1. Single-Tooth Zone ($\overline{BD} = 3.111\text{ mm}$): Full $100\% F_n$ load transmitted by a single tooth pair" + "\n"
            r"2. HPSTC (Point D, $r_D = 27.369\text{ mm}$): Outermost position carrying $100\%$ load, maximizing bending moment $M_{b,D}$" + "\n"
            r"3. ISO 6336 Rating: Tip loading (Point E) carries only $50\%$ load ($M_{b,E} \approx 0.6 M_{b,D}$); HPSTC always governs"
        ),

        # Fig 3
        'fig3_title': "Fig 3: Contact Kinematics, Radii of Curvature, Tangential & Sliding Velocities",
        'fig3_panel1_title': "Profile Radii of Curvature and Tangential Velocities at Contact Point K",
        'fig3_panel2_title': "Distribution of Tangential ($v_{t1}, v_{t2}$) and Sliding ($v_g$) Velocities",
        'fig3_rho1': r"$\rho_1(s) = 5.20\text{ mm}$",
        'fig3_rho2': r"$\rho_2(s) = 31.74\text{ mm}$",
        'fig3_vt1': r"Pinion Velocity $v_{t1} = \omega_1 \rho_1$",
        'fig3_vt2': r"Gear Velocity $v_{t2} = \omega_2 \rho_2$",
        'fig3_vg': r"Sliding Velocity $v_g = v_{t1} - v_{t2}$",
        'fig3_pure_rolling': r"Pitch Point $P$: $v_g = 0$ (Pure Rolling)",
        'fig3_pinion_dedendum_neg': "Pinion Dedendum: Negative Sliding ($v_g < 0$)",
        'fig3_pinion_addendum_pos': "Pinion Addendum: Positive Sliding ($v_g > 0$)",
        'fig3_velocity_axis': "Velocity (norm)",
        'fig3_pos_axis': "Position s along Line of Action (mm)",
        'fig3_card_title': "[Summary: Contact Kinematics & Sliding Velocity Analysis]",
        'fig3_card_body': (
            r"1. Conservation of Curvature: $\rho_1(s) + \rho_2(s) = a \sin\alpha_0 = 36.938\text{ mm}$ (Invariant along path)" + "\n"
            r"2. Velocity Matching: At pitch point P ($s=0$), $v_{t1} = v_{t2} \rightarrow v_g = 0$ (Pure rolling, zero sliding friction)" + "\n"
            r"3. Sliding Sign Reversal: $v_g(s) = (\omega_1 + \omega_2) s$ reverses direction across P (negative at dedendum, positive at tip)"
        ),

        # Fig 4
        'fig4_title': "Fig 4: Specific Sliding Curves and Wear/Scuffing Risk Zones along Active Profile",
        'fig4_k1_label': r"Pinion $k_1(s) = 1 - \frac{\rho_2}{u \rho_1}$",
        'fig4_k2_label': r"Gear $k_2(s) = 1 - \frac{u \rho_1}{\rho_2}$",
        'fig4_asymptote_t1': r"$T_1$ Asymptote ($\rho_1 \to 0$)",
        'fig4_danger_zone_pinion': "Pinion Dedendum Severe Zone (Scuffing, k1 < -1)",
        'fig4_danger_zone_gear': "Gear Dedendum Caution Zone (k2 < -1)",
        'fig4_pure_rolling_point': "Pitch Point $P$: $k_1 = k_2 = 0$\n(Pure Rolling, Pitting)",
        'fig4_pt_a_annot': r"Point $A$: $k_1 = -7.420$ (Extreme Sliding)",
        'fig4_pt_b_annot': r"Point $B$: $k_1 = -0.388$",
        'fig4_pt_d_annot': r"Point $D$: $k_2 = -0.154$",
        'fig4_pt_e_annot': r"Point $E$: $k_2 = -1.295$",
        'fig4_identity_box': r"Identity: $(1 - k_1)(1 - k_2) \equiv 1.0$",
        'fig4_asymmetry_box': "Sliding Asymmetry: |k1,A|=7.42 >> |k2,E|=1.29\n(u=3 -> profile shift x1 > 0 required)",
        'fig4_y_axis': "Specific Sliding k",
        'fig4_x_axis': "Position s along LOA (mm, from Pitch Point P)",
        'fig4_card_title': "[Summary: Specific Sliding Distribution & Wear Mechanics]",
        'fig4_card_body': (
            r"1. Formulation: $k_1 = 1 - \rho_2 / (u \rho_1)$, $k_2 = 1 - (u \rho_1) / \rho_2$ (Satisfies $(1-k_1)(1-k_2) \equiv 1$ everywhere)" + "\n"
            r"2. Pitch Point: $k_1 = k_2 = 0$ (Pure rolling contact, prone to subsurface shear fatigue and micropitting)" + "\n"
            r"3. Asymmetry: Pinion dedendum suffers $k_1 = -7.420$, justifying positive profile shift ($x_1 > 0$) for balance"
        ),
    },

    'de': {
        # Fig 1
        'fig1_title': "Abb. 1: Fünf singuläre Punkte der Eingriffslinie und Geometrie der Eingriffsstrecke",
        'fig1_point_a': r"Punkt $A$ (SAP, Eingriffsbeginn)",
        'fig1_point_b': r"Punkt $B$ (LPSTC, Unterer Einzeleingriff)",
        'fig1_point_p': r"Punkt $P$ (Wälzpunkt, Reines Rollen $v_g=0$)",
        'fig1_point_d': r"Punkt $D$ (HPSTC, Oberer Einzeleingriff)",
        'fig1_point_e': r"Punkt $E$ (EAP, Eingriffsende)",
        'fig1_point_n1': r"$T_1$ (Grundkreis Ritzel)",
        'fig1_point_n2': r"$T_2$ (Grundkreis Rad)",
        'fig1_loa': r"Eingriffslinie ($\alpha_0=20^\circ$)",
        'fig1_pitch_line': "Wälztangente",
        'fig1_pinion_tip': r"Ritzel-Kopfkreis ($r_{a1}=30.0\text{ mm}$)",
        'fig1_gear_tip': r"Rad-Kopfkreis ($r_{a2}=84.0\text{ mm}$)",
        'fig1_dim_gf': r"Eingriffsvorlauf $g_f = 7.828\text{ mm}$",
        'fig1_dim_ga': r"Eingriffsnachlauf $g_a = 6.774\text{ mm}$",
        'fig1_dim_g_alpha': r"Gesamteingriffsstrecke $g_\alpha = 14.602\text{ mm}$",
        'fig1_dim_pb': r"Eingriffsteilung $p_b = 8.856\text{ mm}$",
        'fig1_dim_bd': r"Einzeleingriff $\overline{BD} = 3.111\text{ mm}$",
        'fig1_card_title': "[Zusammenfassung: Fünf singuläre Eingriffspunkte & Profilüberdeckung]",
        'fig1_card_body': (
            "1. Punkte: Punkt A (SAP) -> Punkt B (LPSTC) -> Punkt P (Wälzpunkt) -> Punkt D (HPSTC) -> Punkt E (EAP)\n"
            r"2. Strecken: $g_f = 7.828\text{ mm}$, $g_a = 6.774\text{ mm} \rightarrow g_\alpha = 14.602\text{ mm}$, $p_b = 8.856\text{ mm}$" + "\n"
            r"3. Profilüberdeckung: $\epsilon_\alpha = g_\alpha / p_b = 1.649 \geq 1.200$ (Einzeleingriff 21.3%, Doppeleingriff 78.7%)"
        ),

        # Fig 2
        'fig2_title': "Abb. 2: Lastaufteilungsprofil entlang der Eingriffslinie und Biegebeanspruchung am HPSTC",
        'fig2_panel1_title': "Normallast-Aufteilungsprofil entlang der Eingriffsstrecke",
        'fig2_panel2_title': "Kragträgermodell des Ritzelzahns und Biegemomenten-Dominanz am HPSTC (Punkt D)",
        'fig2_load_ratio': "Lastaufteilung (%)",
        'fig2_double_contact': "Doppeleingriff (50%)",
        'fig2_single_contact': "Einzeleingriff (100%)",
        'fig2_hpstc_callout': "HPSTC (Punkt D)\n100% Last am Hebelarm (Max. Biegung)",
        'fig2_lpstc_callout': "LPSTC (Punkt B)\n100% Last (Grübchengefahr)",
        'fig2_moment_d': r"$M_{b,D} = 1.0 \cdot F_n \cdot h_D$ (Max. Biegung)",
        'fig2_moment_e': r"$M_{b,E} = 0.5 \cdot F_n \cdot h_E \approx 0.60 M_{b,D}$",
        'fig2_lever_arm_d': r"$h_D = 4.25\text{ mm}$",
        'fig2_lever_arm_e': r"$h_E = 5.10\text{ mm}$",
        'fig2_fillet_critical': r"Kritischer Querschnitt (ISO 6336 $30^\circ$)",
        'fig2_cantilever_fixed': "Zahnfuß-Einspannung",
        'fig2_tooth_tip': "Zahnkopf (Punkt E)",
        'fig2_tooth_hpstc': "HPSTC (Punkt D)",
        'fig2_card_title': "[Zusammenfassung: Lastaufteilung & Zahnfußbiegung am HPSTC]",
        'fig2_card_body': (
            r"1. Einzeleingriff ($\overline{BD} = 3.111\text{ mm}$): Volle $100\% F_n$ Last wird von einem einzigen Zahnpaar getragen" + "\n"
            r"2. HPSTC (Punkt D, $r_D = 27.369\text{ mm}$): Äußerster Punkt mit $100\%$ Last, erzeugt maximales Biegemoment $M_{b,D}$" + "\n"
            r"3. ISO 6336 Bemessung: Am Zahnkopf (Punkt E) nur $50\%$ Last ($M_{b,E} \approx 0.6 M_{b,D}$); HPSTC stets maßgebend"
        ),

        # Fig 3
        'fig3_title': "Abb. 3: Eingriffskinematik, Krümmungsradien, Tangential- und Gleitgeschwindigkeiten",
        'fig3_panel1_title': "Zahnflanken-Krümmungsradien und Tangentialgeschwindigkeiten am Kontaktpunkt K",
        'fig3_panel2_title': "Verteilung von Tangential- ($v_{t1}, v_{t2}$) und Gleitgeschwindigkeit ($v_g$)",
        'fig3_rho1': r"$\rho_1(s) = 5.20\text{ mm}$",
        'fig3_rho2': r"$\rho_2(s) = 31.74\text{ mm}$",
        'fig3_vt1': r"Ritzel-Geschwindigkeit $v_{t1} = \omega_1 \rho_1$",
        'fig3_vt2': r"Rad-Geschwindigkeit $v_{t2} = \omega_2 \rho_2$",
        'fig3_vg': r"Gleitgeschwindigkeit $v_g = v_{t1} - v_{t2}$",
        'fig3_pure_rolling': r"Wälzpunkt $P$: $v_g = 0$ (Reines Rollen)",
        'fig3_pinion_dedendum_neg': "Ritzel-Zahnfuß: Negatives Gleiten ($v_g < 0$)",
        'fig3_pinion_addendum_pos': "Ritzel-Zahnkopf: Positives Gleiten ($v_g > 0$)",
        'fig3_velocity_axis': "Geschwindigkeit (norm)",
        'fig3_pos_axis': "Position s auf der Eingriffslinie (mm)",
        'fig3_card_title': "[Zusammenfassung: Eingriffskinematik & Gleitgeschwindigkeitsanalyse]",
        'fig3_card_body': (
            r"1. Krümmungssumme: $\rho_1(s) + \rho_2(s) = a \sin\alpha_0 = 36.938\text{ mm}$ (Konstant über gesamte Eingriffsstrecke)" + "\n"
            r"2. Geschwindigkeitsgleichheit: Im Wälzpunkt P ($s=0$) gilt $v_{t1} = v_{t2} \rightarrow v_g = 0$ (Reines Rollen)" + "\n"
            r"3. Vorzeichenwechsel: $v_g(s) = (\omega_1 + \omega_2) s$ wechselt im Wälzpunkt das Vorzeichen (negativ am Fuß, positiv am Kopf)"
        ),

        # Fig 4
        'fig4_title': "Abb. 4: Spezifische Gleitkurven und Verschleiß-/Fressrisikozonen entlang des Profils",
        'fig4_k1_label': r"Ritzel $k_1(s) = 1 - \frac{\rho_2}{u \rho_1}$",
        'fig4_k2_label': r"Rad $k_2(s) = 1 - \frac{u \rho_1}{\rho_2}$",
        'fig4_asymptote_t1': r"$T_1$ Asymptote ($\rho_1 \to 0$)",
        'fig4_danger_zone_pinion': "Ritzel-Zahnfuß Gefahrenzone (Fressen, k1 < -1)",
        'fig4_danger_zone_gear': "Rad-Zahnfuß Verschleißzone (k2 < -1)",
        'fig4_pure_rolling_point': "Wälzpunkt $P$: $k_1 = k_2 = 0$\n(Reines Rollen)",
        'fig4_pt_a_annot': r"Punkt $A$: $k_1 = -7.420$ (Extremes Gleiten)",
        'fig4_pt_b_annot': r"Punkt $B$: $k_1 = -0.388$",
        'fig4_pt_d_annot': r"Punkt $D$: $k_2 = -0.154$",
        'fig4_pt_e_annot': r"Punkt $E$: $k_2 = -1.295$",
        'fig4_identity_box': r"Identität: $(1 - k_1)(1 - k_2) \equiv 1.0$",
        'fig4_asymmetry_box': "Gleit-Asymmetrie: |k1,A|=7.42 >> |k2,E|=1.29\n(u=3 -> Profilverschiebung x1 > 0 nötig)",
        'fig4_y_axis': "Spezifisches Gleiten k",
        'fig4_x_axis': "Position s auf der Eingriffslinie (mm, ab Wälzpunkt P)",
        'fig4_card_title': "[Zusammenfassung: Spezifisches Gleiten & Verschleißmechanismen]",
        'fig4_card_body': (
            r"1. Definition: $k_1 = 1 - \rho_2 / (u \rho_1)$, $k_2 = 1 - (u \rho_1) / \rho_2$ (Erfüllt $(1-k_1)(1-k_2) \equiv 1$ überall)" + "\n"
            r"2. Wälzpunkt: $k_1 = k_2 = 0$ (Reiner Rollkontakt, anfällig für Grübchenbildung durch Scherspannungen)" + "\n"
            r"3. Asymmetrie: Am Punkt A erfährt das Ritzel $k_1 = -7.420 \rightarrow$ Begründung für positive Profilverschiebung ($x_1 > 0$)"
        ),
    },

    'ja': {
        # Fig 1
        'fig1_title': "図 1: 作用線上の5大特異点と噛合い軌跡幾何学",
        'fig1_point_a': r"点 $A$ (SAP, 噛合い開始点)",
        'fig1_point_b': r"点 $B$ (LPSTC, 単一歯接触最下点)",
        'fig1_point_p': r"点 $P$ (ピッチ点, 純粋転がり $v_g=0$)",
        'fig1_point_d': r"点 $D$ (HPSTC, 単一歯接触最上点)",
        'fig1_point_e': r"点 $E$ (EAP, 噛合い終了点)",
        'fig1_point_n1': r"$T_1$ (ピニオン基礎円)",
        'fig1_point_n2': r"$T_2$ (大歯車基礎円)",
        'fig1_loa': r"作用線 (Line of Action, $\alpha_0=20^\circ$)",
        'fig1_pitch_line': "ピッチ線 (Pitch Tangent)",
        'fig1_pinion_tip': r"ピニオン歯先円 ($r_{a1}=30.0\text{ mm}$)",
        'fig1_gear_tip': r"大歯車歯先円 ($r_{a2}=84.0\text{ mm}$)",
        'fig1_dim_gf': r"接近噛合い長さ $g_f = 7.828\text{ mm}$",
        'fig1_dim_ga': r"後退噛合い長さ $g_a = 6.774\text{ mm}$",
        'fig1_dim_g_alpha': r"全作用噛合い長さ $g_\alpha = 14.602\text{ mm}$",
        'fig1_dim_pb': r"法線ピッチ $p_b = 8.856\text{ mm}$",
        'fig1_dim_bd': r"単一歯接触区間 $\overline{BD} = 3.111\text{ mm}$",
        'fig1_card_title': "[作用線5大特異点と噛合い率の幾何学的精密要約]",
        'fig1_card_body': (
            "1. 5大特異点: 点 A (SAP) -> 点 B (LPSTC) -> 点 P (ピッチ点) -> 点 D (HPSTC) -> 点 E (EAP)\n"
            r"2. 噛合い長さ・法線ピッチ: $g_f = 7.828\text{ mm}$, $g_a = 6.774\text{ mm} \rightarrow g_\alpha = 14.602\text{ mm}$, $p_b = 8.856\text{ mm}$" + "\n"
            r"3. 正面噛合い率: $\epsilon_\alpha = g_\alpha / p_b = 1.649 \geq 1.200$ (単一接触 21.3%、2歯接触 78.7% 分担)"
        ),

        # Fig 2
        'fig2_title': "図 2: 作用線上の荷重分担率とHPSTC（点D）歯元曲げ応力集中機構",
        'fig2_panel1_title': "作用線接触位置に応じた法線荷重分担プロファイル",
        'fig2_panel2_title': "ピニオン歯の片持ち梁モデルとHPSTC（点D）曲げモーメント支配性",
        'fig2_load_ratio': "荷重分担率 (%)",
        'fig2_double_contact': "2歯接触 (50%)",
        'fig2_single_contact': "単一歯接触 (100%)",
        'fig2_hpstc_callout': "HPSTC (点D)\n100%荷重作用最外端 (最大曲げ)",
        'fig2_lpstc_callout': "LPSTC (点B)\n100%荷重突入点 (ピッチング起点)",
        'fig2_moment_d': r"$M_{b,D} = 1.0 \cdot F_n \cdot h_D$ (最大曲げ)",
        'fig2_moment_e': r"$M_{b,E} = 0.5 \cdot F_n \cdot h_E \approx 0.60 M_{b,D}$",
        'fig2_lever_arm_d': r"$h_D = 4.25\text{ mm}$",
        'fig2_lever_arm_e': r"$h_E = 5.10\text{ mm}$",
        'fig2_fillet_critical': r"危険断面 (ISO 6336 $30^\circ$ 接線)",
        'fig2_cantilever_fixed': "歯元固定端",
        'fig2_tooth_tip': "歯先 (Point E)",
        'fig2_tooth_hpstc': "HPSTC (Point D)",
        'fig2_card_title': "[荷重分担率およびHPSTC歯元曲げ集中要約]",
        'fig2_card_body': (
            r"1. 単一歯接触区間 ($\overline{BD} = 3.111\text{ mm}$): 全荷重 $100\% F_n$ が単一の歯の対に集中作用" + "\n"
            r"2. HPSTC (点D, $r_D = 27.369\text{ mm}$): $100\%$荷重が作用する最外径位置であり最大曲げモーメント $M_{b,D}$ を発生" + "\n"
            r"3. ISO 6336 評価基準: 歯先(点E)は荷重分担($50\%$)により $M_{b,E} \approx 0.6 M_{b,D}$ に留まり、歯元疲労は常にHPSTCが支配"
        ),

        # Fig 3
        'fig3_title': "図 3: 接触点機構学、曲率半径および接線・相対すべり速度線図",
        'fig3_panel1_title': "接触点Kにおける歯形曲率半径および瞬間接線速度機構学",
        'fig3_panel2_title': "作用線上の接線速度($v_{t1}, v_{t2}$)と相対すべり速度($v_g$)分布",
        'fig3_rho1': r"$\rho_1(s) = 5.20\text{ mm}$",
        'fig3_rho2': r"$\rho_2(s) = 31.74\text{ mm}$",
        'fig3_vt1': r"ピニオン速度 $v_{t1} = \omega_1 \rho_1$",
        'fig3_vt2': r"大歯車速度 $v_{t2} = \omega_2 \rho_2$",
        'fig3_vg': r"相対すべり速度 $v_g = v_{t1} - v_{t2}$",
        'fig3_pure_rolling': r"ピッチ点 $P$: $v_g = 0$ (純粋転がり)",
        'fig3_pinion_dedendum_neg': "ピニオン歯元: 負のすべり ($v_g < 0$)",
        'fig3_pinion_addendum_pos': "ピニオン歯先: 正のすべり ($v_g > 0$)",
        'fig3_velocity_axis': "速度 (正規化)",
        'fig3_pos_axis': "作用線上の接触位置 s (mm)",
        'fig3_card_title': "[接触機構学および相対すべり速度解析要約]",
        'fig3_card_body': (
            r"1. 曲率半径保存則: $\rho_1(s) + \rho_2(s) = a \sin\alpha_0 = 36.938\text{ mm}$ (噛合い全区間で一定不変)" + "\n"
            r"2. 接線速度一致: ピッチ点 P ($s=0$) で $v_{t1} = v_{t2} \rightarrow$ 相対すべり速度 $v_g = 0$ (純粋転がり接触)" + "\n"
            r"3. すべり速度反転: $v_g(s) = (\omega_1 + \omega_2) s$ によりピッチ点を境に歯元($-$)と歯先($+$)ですべり方向が逆転"
        ),

        # Fig 4
        'fig4_title': "図 4: 歯面相対すべり率（Specific Sliding）曲線と摩耗・焼付き危険ゾーン",
        'fig4_k1_label': r"ピニオン $k_1(s) = 1 - \frac{\rho_2}{u \rho_1}$",
        'fig4_k2_label': r"大歯車 $k_2(s) = 1 - \frac{u \rho_1}{\rho_2}$",
        'fig4_asymptote_t1': r"$T_1$ 漸近線 ($\rho_1 \to 0$)",
        'fig4_danger_zone_pinion': "ピニオン歯元危険域 (焼付き・スコアリング, k1 < -1)",
        'fig4_danger_zone_gear': "大歯車歯元注意域 (k2 < -1)",
        'fig4_pure_rolling_point': "ピッチ点 $P$: $k_1 = k_2 = 0$\n(純粋転がり, ピッチング)",
        'fig4_pt_a_annot': r"点 $A$: $k_1 = -7.420$ (極大負のすべり)",
        'fig4_pt_b_annot': r"点 $B$: $k_1 = -0.388$",
        'fig4_pt_d_annot': r"点 $D$: $k_2 = -0.154$",
        'fig4_pt_e_annot': r"点 $E$: $k_2 = -1.295$",
        'fig4_identity_box': r"恒等式: $(1 - k_1)(1 - k_2) \equiv 1.0$",
        'fig4_asymmetry_box': "比すべり非対称性: |k1,A|=7.42 >> |k2,E|=1.29\n(u=3 -> 転位係数 x1 > 0 補正必要)",
        'fig4_y_axis': "相対すべり率 k (Specific Sliding)",
        'fig4_x_axis': "作用線上の接触位置 s (mm, ピッチ点P基準)",
        'fig4_card_title': "[歯面相対すべり率（比すべり）および摩耗力学要約]",
        'fig4_card_body': (
            r"1. 定義式: $k_1 = 1 - \rho_2 / (u \rho_1)$, $k_2 = 1 - (u \rho_1) / \rho_2$ (全域で $(1-k_1)(1-k_2) \equiv 1$ 成立)" + "\n"
            r"2. ピッチ点 $P$: $k_1 = k_2 = 0$ (純粋転がり接触、繰返し圧縮せん断によるピッチング発生危険域)" + "\n"
            r"3. 非対称性: 点 A でピニオン $k_1 = -7.420$ となり油膜破断・スコアリング危険集中 $\rightarrow$ 正転位 ($x_1 > 0$) 必要"
        ),
    }
}


def get_tr(lang: str):
    """Returns translation helper function for given language."""
    d = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    def tr(key: str) -> str:
        return d.get(key, TRANSLATIONS['en'].get(key, key))
    return tr


# ---------------------------------------------------------------------------
# Drawing Helpers
# ---------------------------------------------------------------------------
def draw_right_angle(ax, vertex, v1, v2, size=0.8, color=COLOR_TEXT_MUTED, lw=0.8):
    """Draws a clean, slim orthogonal right-angle marker."""
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-9 or n2 < 1e-9:
        return
    u1 = v1 / n1 * size
    u2 = v2 / n2 * size
    corner = vertex + u1 + u2
    ax.plot([vertex[0] + u1[0], corner[0], vertex[0] + u2[0]],
            [vertex[1] + u1[1], corner[1], vertex[1] + u2[1]],
            color=color, lw=lw, zorder=5)


def save_diagram(fig, base_name, output_dir, dpi, formats):
    """Saves figure in requested formats with exact canvas dimensions."""
    output_dir = Path(output_dir)
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
        print(f"  [SAVED] {p.name:<42} ({size_kb:6.1f} KB) -> {p.parent}")


# ---------------------------------------------------------------------------
# Diagram 1: Line of Action Five Singular Points (fig1_line_of_action_five_points)
# ---------------------------------------------------------------------------
def create_diagram_1(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 1: Line of Action Five Singular Points and Meshing Path Geometry.
    Standard Gear Pair: m=3, z1=18, z2=54, alpha_0=20 deg, a=108 mm.
    """
    apply_language_typography(lang)
    tr = get_tr(lang)

    m = 3.0
    z1, z2 = 18, 54
    alpha_deg = 20.0
    alpha_rad = np.radians(alpha_deg)

    r1 = 0.5 * m * z1       # 27.0 mm
    r2 = 0.5 * m * z2       # 81.0 mm
    rb1 = r1 * np.cos(alpha_rad)  # 25.371701 mm
    rb2 = r2 * np.cos(alpha_rad)  # 76.115102 mm
    ra1 = r1 + m                  # 30.0 mm
    ra2 = r2 + m                  # 84.0 mm
    pb = np.pi * m * np.cos(alpha_rad)  # 8.856394 mm

    gf = np.sqrt(ra2**2 - rb2**2) - r2 * np.sin(alpha_rad)  # 7.827921 mm
    ga = np.sqrt(ra1**2 - rb1**2) - r1 * np.sin(alpha_rad)  # 6.774104 mm

    t_A = -gf               # -7.827921 mm
    t_B = ga - pb           # -2.082290 mm
    t_P = 0.0               #  0.000000 mm
    t_D = -gf + pb          # +1.028474 mm
    t_E = ga                # +6.774104 mm

    t_N1 = -r1 * np.sin(alpha_rad)  # -9.234544 mm
    t_N2 = r2 * np.sin(alpha_rad)   # +27.703632 mm

    u_loa = np.array([np.cos(alpha_rad), -np.sin(alpha_rad)])
    norm_loa = np.array([np.sin(alpha_rad), np.cos(alpha_rad)])

    O1 = np.array([0.0, r1])
    O2 = np.array([0.0, -r2])
    P = np.array([0.0, 0.0])

    A = t_A * u_loa
    B = t_B * u_loa
    D = t_D * u_loa
    E = t_E * u_loa
    N1 = t_N1 * u_loa
    N2 = t_N2 * u_loa

    # Setup figure canvas (8.5 x 8.8 in -> 2550 x 2640 px at 300 DPI)
    fig, ax = plt.subplots(figsize=(8.5, 8.8))
    ax.set_aspect('equal')
    ax.axis('off')

    # Line of centers
    ax.plot([0, 0], [-6.5, 9.5], color=COLOR_AXIS, linestyle="-.", lw=0.7, zorder=1)

    # Pitch Tangent line
    ax.plot([-32.0, 42.0], [0, 0], color=COLOR_TANGENT, linestyle="--", lw=0.8, zorder=1)
    ax.text(26.0, 1.5, tr('fig1_pitch_line'), fontsize=8.8, color=COLOR_TANGENT,
            va='bottom', ha='left',
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=1.0), zorder=6)

    # Circular Arcs around Pitch Point (bounded within central clearance zone)
    thetas_p = np.linspace(np.radians(-90 - 20), np.radians(-90 + 20), 160)
    thetas_g = np.linspace(np.radians(90 - 10), np.radians(90 + 10), 160)

    # Pitch circles
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

    # Full Line of Action N1 -> N2
    loa_ext_start = (t_N1 - 2.5) * u_loa
    loa_ext_end = (t_N2 + 2.5) * u_loa
    ax.plot([loa_ext_start[0], loa_ext_end[0]], [loa_ext_start[1], loa_ext_end[1]],
            color=COLOR_NORMAL, lw=1.2, linestyle="-", zorder=3)

    # 3 Contact Zones
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLOR_DOUBLE, lw=3.6, alpha=0.85, zorder=4)
    ax.plot([B[0], D[0]], [B[1], D[1]], color=COLOR_HIGHLIGHT, lw=4.8, alpha=0.95, zorder=5)
    ax.plot([D[0], E[0]], [D[1], E[1]], color=COLOR_DOUBLE, lw=3.6, alpha=0.85, zorder=4)

    # Tangent rays
    ray1_dir = (O1 - N1) / np.linalg.norm(O1 - N1)
    ray1_start = N1 + ray1_dir * 8.0
    ax.plot([ray1_start[0], N1[0]], [ray1_start[1], N1[1]], color=COLOR_AXIS, linestyle=":", lw=0.8, zorder=2)

    ray2_dir = (O2 - N2) / np.linalg.norm(O2 - N2)
    ray2_start = N2 + ray2_dir * 5.0
    ax.plot([ray2_start[0], N2[0]], [ray2_start[1], N2[1]], color=COLOR_AXIS, linestyle=":", lw=0.8, zorder=2)

    draw_right_angle(ax, N1, O1 - N1, u_loa, size=0.8, color=COLOR_TEXT_MUTED, lw=0.8)
    draw_right_angle(ax, N2, O2 - N2, -u_loa, size=0.8, color=COLOR_TEXT_MUTED, lw=0.8)

    # Scatter markers
    ax.scatter([N1[0], N2[0]], [N1[1], N2[1]], color=COLOR_PINION, s=42, zorder=7)
    ax.scatter([A[0], E[0]], [A[1], E[1]], color=COLOR_NORMAL, s=55, zorder=8, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([B[0], D[0]], [B[1], D[1]], color='#7C3AED', s=52, zorder=8, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.scatter([P[0]], [P[1]], color=COLOR_NORMAL, s=62, zorder=9, edgecolors=COLOR_TEXT_MAIN, lw=1.0)

    # -------------------------------------------------------------------------
    # Point Annotations with Elbow Leader Lines (Outer Canvas Distribution)
    # Zero Overlap & 100% Visual Clearance Zone Guaranteed
    # -------------------------------------------------------------------------
    # Point P: High North Tier (y=21.0, x=0.0, explicit elbow to avoid Point D)
    ax.annotate(tr('fig1_point_p'),
                xy=(P[0], P[1]), xytext=(0.0, 21.0),
                fontsize=8.5, color=COLOR_NORMAL, ha='center', va='bottom',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=1.0),
                zorder=7)

    # Point B: North-West Tier (y=17.2, x=-16.0, ha='center', clear of Point P and Layer +1 text)
    ax.annotate(tr('fig1_point_b'),
                xy=(B[0], B[1]), xytext=(-16.0, 17.2),
                fontsize=8.5, color='#7C3AED', ha='center', va='bottom',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color='#7C3AED', lw=0.8),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec='#7C3AED', lw=0.8, alpha=1.0),
                zorder=7)

    # Point D: North-East Margin raised to y=18.0 (>=2.5 mm clearance from Layer +2 pb text)
    ax.annotate(tr('fig1_point_d'),
                xy=(D[0], D[1]), xytext=(22.0, 18.0),
                fontsize=8.5, color='#7C3AED', ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color='#7C3AED', lw=0.8),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec='#7C3AED', lw=0.8, alpha=1.0),
                zorder=7)

    # Point A: Outer West Margin (y=-0.5, clear of gear pitch arc)
    ax.annotate(tr('fig1_point_a'),
                xy=(A[0], A[1]), xytext=(-24.0, -0.5),
                fontsize=8.5, color=COLOR_NORMAL, ha='right', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=1.0),
                zorder=7)

    # Point E: Outer East Margin (y=-3.5, x=26.0, clear of pitch arc and Layer -1 BD)
    ax.annotate(tr('fig1_point_e'),
                xy=(E[0], E[1]), xytext=(26.0, -3.5),
                fontsize=8.5, color=COLOR_NORMAL, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=1.0),
                zorder=7)

    # N1 on Pinion base circle (Outer West Margin raised to y=10.0 to prevent cross with ra2)
    ax.annotate(tr('fig1_point_n1'),
                xy=(N1[0], N1[1]), xytext=(-24.0, 10.0),
                fontsize=8.5, color=COLOR_PINION, ha='right', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_PINION, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_PINION, lw=0.7, alpha=1.0),
                zorder=7)

    # N2 on Gear base circle (Outer East Margin: y=-12.0, x=30.0, ha='left')
    ax.annotate(tr('fig1_point_n2'),
                xy=(N2[0], N2[1]), xytext=(30.0, -12.0),
                fontsize=8.5, color=COLOR_PINION, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_PINION, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_PINION, lw=0.7, alpha=1.0),
                zorder=7)

    # Line of action label (Top-Left: y=21.0, x=-39.5)
    ax.text(-39.5, 21.0, tr('fig1_loa'),
            fontsize=9.0, color=COLOR_NORMAL, ha='left', va='bottom',
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=1.0),
            zorder=7)

    # Gear tip circle label (West Margin lowered to y=4.5 to prevent cross with N1)
    ra2_pt_x = -20.0
    ra2_pt_y = -r2 + np.sqrt(ra2**2 - ra2_pt_x**2)
    ax.annotate(tr('fig1_gear_tip'),
                xy=(ra2_pt_x, ra2_pt_y), xytext=(-24.0, 4.5),
                fontsize=8.3, color=COLOR_GEAR, ha='right', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_GEAR, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_GEAR, lw=0.7, alpha=1.0),
                zorder=7)

    # Pinion tip circle label (East Margin: y=8.5, x=22.0, ha='left')
    ra1_pt_x = 15.5
    ra1_pt_y = r1 - np.sqrt(ra1**2 - ra1_pt_x**2)
    ax.annotate(tr('fig1_pinion_tip'),
                xy=(ra1_pt_x, ra1_pt_y), xytext=(22.0, 8.5),
                fontsize=8.3, color=COLOR_GEAR, ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>", connectionstyle="angle,angleA=0,angleB=90,rad=0", color=COLOR_GEAR, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=COLOR_GEAR, lw=0.7, alpha=1.0),
                zorder=7)

    # Dimensions
    # Layer +1: Base pitch pb = segment AD (Offset +10.5 mm)
    bar1_offset = norm_loa * 10.5
    bar_A1 = A + bar1_offset
    bar_D1 = D + bar1_offset
    ax.annotate('', xy=bar_D1, xytext=bar_A1,
                arrowprops=dict(arrowstyle='<->', color='#7C3AED', lw=0.9), zorder=6)
    mid_AD = bar_A1 - u_loa * 0.5 + norm_loa * 0.7
    ax.text(mid_AD[0], mid_AD[1], tr('fig1_dim_pb'),
            fontsize=8.5, color='#7C3AED', ha='right', va='bottom',
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.95), zorder=7)

    # Layer +2: Base pitch pb = segment BE (Offset +15.5 mm)
    bar2_offset = norm_loa * 15.5
    bar_B2 = B + bar2_offset
    bar_E2 = E + bar2_offset
    ax.annotate('', xy=bar_E2, xytext=bar_B2,
                arrowprops=dict(arrowstyle='<->', color='#7C3AED', lw=0.9), zorder=6)
    mid_BE = (bar_B2 + bar_E2) * 0.5 + norm_loa * 0.7 + u_loa * 6.0
    ax.text(mid_BE[0], mid_BE[1], tr('fig1_dim_pb'),
            fontsize=8.5, color='#7C3AED', ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.95), zorder=7)

    # Extension lines
    ax.plot([A[0], bar_A1[0] + norm_loa[0] * 0.5], [A[1], bar_A1[1] + norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([D[0], bar_D1[0] + norm_loa[0] * 0.5], [D[1], bar_D1[1] + norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([B[0], bar_B2[0] + norm_loa[0] * 0.5], [B[1], bar_B2[1] + norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([E[0], bar_E2[0] + norm_loa[0] * 0.5], [E[1], bar_E2[1] + norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)

    # Downward Dimension Layer -1: BD (Offset -5.5 mm)
    bar_sub_offset = -norm_loa * 5.5
    bar_B_sub = B + bar_sub_offset
    bar_D_sub = D + bar_sub_offset
    ax.annotate('', xy=bar_D_sub, xytext=bar_B_sub,
                arrowprops=dict(arrowstyle='<->', color='#EA580C', lw=1.0), zorder=6)
    mid_BD_sub = (bar_B_sub + bar_D_sub) * 0.5 - norm_loa * 0.5
    ax.text(mid_BD_sub[0], mid_BD_sub[1], tr('fig1_dim_bd'),
            fontsize=8.3, color='#EA580C', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none", alpha=0.95), zorder=7)

    # Downward Dimension Layer -2: gf and ga (Offset -9.5 mm)
    bar3_offset = -norm_loa * 9.5
    bar_A3 = A + bar3_offset
    bar_P3 = P + bar3_offset
    bar_E3 = E + bar3_offset
    ax.annotate('', xy=bar_P3, xytext=bar_A3,
                arrowprops=dict(arrowstyle='<->', color=COLOR_NORMAL, lw=0.9), zorder=6)
    mid_AP = (bar_A3 + bar_P3) * 0.5 - norm_loa * 0.5
    ax.text(mid_AP[0], mid_AP[1], tr('fig1_dim_gf'),
            fontsize=8.3, color=COLOR_NORMAL, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none", alpha=0.95), zorder=7)

    ax.annotate('', xy=bar_E3, xytext=bar_P3,
                arrowprops=dict(arrowstyle='<->', color=COLOR_NORMAL, lw=0.9), zorder=6)
    mid_PE = (bar_P3 + bar_E3) * 0.5 - norm_loa * 0.5
    ax.text(mid_PE[0], mid_PE[1], tr('fig1_dim_ga'),
            fontsize=8.3, color=COLOR_NORMAL, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none", alpha=0.95), zorder=7)

    # Downward Dimension Layer -3: g_alpha (Offset -14.0 mm)
    bar4_offset = -norm_loa * 14.0
    bar_A4 = A + bar4_offset
    bar_E4 = E + bar4_offset
    ax.annotate('', xy=bar_E4, xytext=bar_A4,
                arrowprops=dict(arrowstyle='<->', color=COLOR_NORMAL, lw=1.0), zorder=6)
    mid_AE = (bar_A4 + bar_E4) * 0.5 - norm_loa * 0.5
    ax.text(mid_AE[0], mid_AE[1], tr('fig1_dim_g_alpha'),
            fontsize=8.5, color=COLOR_NORMAL, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.95), zorder=7)

    # Downward extension lines
    ax.plot([A[0], bar_A4[0] - norm_loa[0] * 0.5], [A[1], bar_A4[1] - norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([E[0], bar_E4[0] - norm_loa[0] * 0.5], [E[1], bar_E4[1] - norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([B[0], bar_B_sub[0] - norm_loa[0] * 0.5], [B[1], bar_B_sub[1] - norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([D[0], bar_D_sub[0] - norm_loa[0] * 0.5], [D[1], bar_D_sub[1] - norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)
    ax.plot([P[0], bar_P3[0] - norm_loa[0] * 0.5], [P[1], bar_P3[1] - norm_loa[1] * 0.5],
            color=COLOR_AXIS, lw=0.65, linestyle=":", zorder=2)

    # Bottom Contact Ratio Summary Card (Completely Clear of Dimensions)
    card_x, card_y, card_w, card_h = -39.0, -34.5, 78.0, 16.5
    card_patch = patches.FancyBboxPatch((card_x, card_y), card_w, card_h, boxstyle="round,pad=0.35",
                                        fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0, zorder=2)
    ax.add_patch(card_patch)
    card_full_text = f"{tr('fig1_card_title')}\n\n{tr('fig1_card_body')}"
    ax.text(card_x + card_w * 0.5, card_y + card_h * 0.5, card_full_text,
            fontsize=8.3, color=COLOR_TEXT_MAIN, ha='center', va='center',
            linespacing=1.30, zorder=4)

    ax.set_xlim(-42.0, 46.0)
    ax.set_ylim(-36.5, 24.5)
    ax.set_title(tr('fig1_title'), fontsize=15.0, fontweight='normal', pad=16, color=COLOR_TEXT_MAIN)

    save_diagram(fig, "fig1_line_of_action_five_points", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 2: Tooth Load Sharing & HPSTC Critical Bending (fig2_tooth_load_sharing)
# ---------------------------------------------------------------------------
def create_diagram_2(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 2: Tooth Load Sharing Profile along LOA & HPSTC Critical Bending Stress.
    """
    apply_language_typography(lang)
    tr = get_tr(lang)

    # Setup figure canvas (8.5 x 8.8 in -> 2550 x 2640 px at 300 DPI)
    fig = plt.figure(figsize=(8.5, 8.8))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.25], hspace=0.38,
                           left=0.12, right=0.90, top=0.88, bottom=0.22)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # -----------------------------------------------------------------------
    # Upper Panel: Load Sharing Profile along LOA
    # -----------------------------------------------------------------------
    s_A = -7.828
    s_B = -2.082
    s_P = 0.000
    s_D = 1.028
    s_E = 6.774

    s_pts = np.array([-10.0, s_A, s_A, s_B, s_B, s_D, s_D, s_E, s_E, 9.0])
    load_pts = np.array([0.0, 0.0, 50.0, 50.0, 100.0, 100.0, 50.0, 50.0, 0.0, 0.0])

    ax1.plot(s_pts, load_pts, color=COLOR_PINION, lw=1.8, zorder=4)

    # Shaded Zones
    ax1.fill_between([s_A, s_B], [0, 0], [50, 50], color=COLOR_DOUBLE, alpha=0.18, zorder=2)
    ax1.fill_between([s_B, s_D], [0, 0], [100, 100], color=COLOR_HIGHLIGHT, alpha=0.25, zorder=2)
    ax1.fill_between([s_D, s_E], [0, 0], [50, 50], color=COLOR_DOUBLE, alpha=0.18, zorder=2)

    for s_val, col in [(s_A, COLOR_NORMAL), (s_B, '#7C3AED'), (s_P, COLOR_TANGENT),
                       (s_D, '#7C3AED'), (s_E, COLOR_NORMAL)]:
        ax1.axvline(s_val, color=col, linestyle=":", lw=0.8, alpha=0.75, zorder=1)

    ax1.text(0.5 * (s_A + s_B), 25.0, tr('fig2_double_contact'),
             fontsize=8.8, color=COLOR_DOUBLE, ha='center', va='center', fontweight='normal')
    ax1.text(0.5 * (s_B + s_D), 55.0, tr('fig2_single_contact'),
             fontsize=9.2, color=COLOR_HIGHLIGHT, ha='center', va='center', fontweight='normal')
    ax1.text(0.5 * (s_D + s_E), 25.0, tr('fig2_double_contact'),
             fontsize=8.8, color=COLOR_DOUBLE, ha='center', va='center', fontweight='normal')

    # HPSTC Point D Callout (Centered to prevent canvas bleed)
    ax1.annotate(tr('fig2_hpstc_callout'),
                 xy=(s_D, 100.0), xytext=(s_D + 0.5, 108.0),
                 fontsize=8.3, color=COLOR_HIGHLIGHT, ha='center', va='bottom',
                 arrowprops=dict(arrowstyle="-|>", color=COLOR_HIGHLIGHT, lw=0.8),
                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=COLOR_HIGHLIGHT, lw=0.7),
                 zorder=6)

    # LPSTC Point B Callout
    ax1.annotate(tr('fig2_lpstc_callout'),
                 xy=(s_B, 100.0), xytext=(s_B - 2.5, 108.0),
                 fontsize=8.3, color='#7C3AED', ha='center', va='bottom',
                 arrowprops=dict(arrowstyle="-|>", color='#7C3AED', lw=0.8),
                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec='#7C3AED', lw=0.7),
                 zorder=6)

    ax1.set_xticks([s_A, s_B, s_P, s_D, s_E])
    ax1.set_xticklabels([f"A\n({s_A:.2f})", f"B\n({s_B:.2f})", f"P\n({s_P:.1f})",
                         f"D\n(+{s_D:.2f})", f"E\n(+{s_E:.2f})"], fontsize=8.5)
    ax1.set_xlim(-10.5, 9.5)
    ax1.set_ylim(-5.0, 138.0)
    ax1.set_ylabel(tr('fig2_load_ratio'), fontsize=9.0, color=COLOR_TEXT_MAIN)
    ax1.set_title(tr('fig2_panel1_title'), fontsize=11.5, color=COLOR_TEXT_MAIN, pad=8)
    ax1.grid(True, linestyle="--", alpha=0.5, color=COLOR_GRID)

    # -----------------------------------------------------------------------
    # Lower Panel: Pinion Tooth Cantilever Bending Mechanics
    # -----------------------------------------------------------------------
    tooth_x = np.array([0.0, 0.4, 1.0, 2.0, 3.2, 4.25, 5.10, 6.75,
                        6.75, 5.10, 4.25, 3.2, 2.0, 1.0, 0.4, 0.0])
    tooth_y = np.array([2.8, 2.65, 2.50, 2.35, 2.20, 2.00, 1.80, 1.02,
                        -1.02, -1.80, -2.00, -2.20, -2.35, -2.50, -2.65, -2.8])

    ax2.plot(tooth_x, tooth_y, color=COLOR_PINION, lw=1.5, zorder=3)
    ax2.fill(tooth_x, tooth_y, color='#EFF6FF', alpha=0.6, zorder=2)

    # Clamped root wall
    ax2.plot([0, 0], [-3.8, 3.8], color=COLOR_TEXT_MAIN, lw=2.0, zorder=4)
    for hy in np.linspace(-3.6, 3.6, 15):
        ax2.plot([-0.35, 0], [hy - 0.25, hy], color=COLOR_AXIS, lw=0.9, zorder=3)
    ax2.text(-0.5, 0.0, tr('fig2_cantilever_fixed'), fontsize=8.5, color=COLOR_TEXT_MUTED,
             ha='right', va='center', rotation=90)

    # Critical Root Section
    x_crit = 0.55
    ax2.plot([x_crit, x_crit], [-2.60, 2.60], color=COLOR_NORMAL, linestyle="--", lw=1.0, zorder=4)
    ax2.text(x_crit + 0.15, -2.85, tr('fig2_fillet_critical'), fontsize=8.3, color=COLOR_NORMAL,
             ha='left', va='top')

    # HPSTC Loading Point (x_D = 4.25 mm)
    xD = 4.25
    yD = 2.00
    ax2.scatter([xD], [yD], color=COLOR_HIGHLIGHT, s=48, zorder=5, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax2.text(xD, yD + 0.25, tr('fig2_tooth_hpstc'), fontsize=8.3, color=COLOR_HIGHLIGHT, ha='center', va='bottom')

    ax2.annotate('', xy=(xD, yD), xytext=(xD + 0.8, yD + 1.8),
                arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.20",
                                color=COLOR_HIGHLIGHT, lw=1.8), zorder=6)
    ax2.text(xD + 0.9, yD + 1.9, r"$F_n$ (100%)", fontsize=8.8, color=COLOR_HIGHLIGHT,
             ha='left', va='bottom', fontweight='normal')

    # Tip Loading Point (Point E, x_E = 6.75 mm)
    xE = 6.75
    yE = 1.02
    ax2.scatter([xE], [yE], color=COLOR_DOUBLE, s=45, zorder=5, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax2.text(xE - 0.2, yE + 0.25, tr('fig2_tooth_tip'), fontsize=8.3, color=COLOR_DOUBLE, ha='right', va='bottom')

    ax2.annotate('', xy=(xE, yE), xytext=(xE + 0.40, yE + 1.6),
                arrowprops=dict(arrowstyle="-|>,head_length=0.40,head_width=0.18",
                                color=COLOR_DOUBLE, lw=1.3), zorder=6)
    ax2.text(xE + 0.45, yE + 1.70, r"$0.5 F_n$ (50%)", fontsize=8.5, color=COLOR_DOUBLE,
             ha='left', va='bottom', fontweight='normal', zorder=7)

    # Moment arm dimensions
    ax2.annotate('', xy=(xD, -0.6), xytext=(x_crit, -0.6),
                arrowprops=dict(arrowstyle='<->', color=COLOR_HIGHLIGHT, lw=0.9), zorder=5)
    ax2.text(0.5 * (x_crit + xD), -0.75, tr('fig2_lever_arm_d'), fontsize=8.3,
             color=COLOR_HIGHLIGHT, ha='center', va='top')

    ax2.annotate('', xy=(xE, -1.75), xytext=(x_crit, -1.75),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DOUBLE, lw=0.9), zorder=5)
    ax2.text(5.05, -1.55, tr('fig2_lever_arm_e'), fontsize=8.3,
             color=COLOR_DOUBLE, ha='center', va='bottom', zorder=6)

    ax2.plot([x_crit, x_crit], [-2.2, 0], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=2)
    ax2.plot([xD, xD], [-1.0, yD], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=2)
    ax2.plot([xE, xE], [-2.2, yE], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=2)

    # Bending moment comparison callout box (Enlarged to guarantee Gate 3 padding >= 15 px)
    box_x, box_y, box_w, box_h = 9.8, -0.95, 5.5, 3.7
    comp_box = patches.FancyBboxPatch((box_x, box_y), box_w, box_h, boxstyle="round,pad=0.25",
                                      fc="#FFFBEB", ec="#F59E0B", lw=1.0, zorder=5)
    ax2.add_patch(comp_box)
    comp_text = (
        f"{tr('fig2_moment_d')}\n"
        f"{tr('fig2_moment_e')}\n"
        r"$M_{b,D} / M_{b,E} \approx 1.67$"
    )
    ax2.text(box_x + box_w * 0.5, box_y + box_h * 0.5, comp_text,
             fontsize=7.5, color=COLOR_TEXT_MAIN, ha='center', va='center', linespacing=1.28, zorder=6)

    ax2.set_xlim(-1.6, 16.0)
    ax2.set_ylim(-3.8, 4.6)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title(tr('fig2_panel2_title'), fontsize=11.5, color=COLOR_TEXT_MAIN, pad=8)

    # Bottom Summary Card on Figure (Completely clear of ax2)
    card_ax = fig.add_axes([0.11, 0.02, 0.80, 0.15])
    card_ax.axis('off')
    summary_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.04",
                                          fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0, zorder=1)
    card_ax.add_patch(summary_patch)
    full_card_text = f"{tr('fig2_card_title')}\n\n{tr('fig2_card_body')}"
    card_ax.text(0.5, 0.5, full_card_text, fontsize=8.3, color=COLOR_TEXT_MAIN,
                 ha='center', va='center', linespacing=1.30, zorder=2)

    fig.suptitle(tr('fig2_title'), fontsize=15.0, color=COLOR_TEXT_MAIN, y=0.96)

    save_diagram(fig, "fig2_tooth_load_sharing", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 3: Contact Kinematics & Velocities (fig3_contact_kinematics_velocities)
# ---------------------------------------------------------------------------
def create_diagram_3(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 3: Contact Kinematics, Radii of Curvature, Tangential & Sliding Velocities.
    """
    apply_language_typography(lang)
    tr = get_tr(lang)

    # Setup figure canvas (8.5 x 9.0 in -> 2550 x 2700 px at 300 DPI)
    fig = plt.figure(figsize=(8.5, 9.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.15, 1.0], hspace=0.38,
                           left=0.12, right=0.90, top=0.88, bottom=0.245)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # -----------------------------------------------------------------------
    # Upper Panel: Kinematics at Contact Point K
    # -----------------------------------------------------------------------
    T1_x = 0.0
    T2_x = 36.938
    P_x = 9.235
    K_x = 5.200

    ax1.plot([T1_x - 3.0, T2_x + 3.0], [0, 0], color=COLOR_NORMAL, lw=1.2, linestyle="-", zorder=2)
    ax1.text(T2_x + 3.5, 0.0, r"$\mathrm{LOA}$", fontsize=9.0, color=COLOR_NORMAL,
             ha='left', va='center', zorder=3)

    ax1.scatter([T1_x, T2_x], [0, 0], color=COLOR_PINION, s=45, zorder=5)
    ax1.text(T1_x, -0.65, r"$T_1$", fontsize=8.8, color=COLOR_PINION, ha='center', va='top')
    ax1.text(T2_x, -0.65, r"$T_2$", fontsize=8.8, color=COLOR_PINION, ha='center', va='top')

    ax1.scatter([P_x], [0], color=COLOR_TANGENT, s=55, zorder=5)
    ax1.text(P_x, -0.65, r"$P$", fontsize=9.0, color=COLOR_TANGENT, ha='center', va='top')

    ax1.scatter([K_x], [0], color=COLOR_NORMAL, s=60, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.9)
    ax1.text(K_x, -0.65, r"$K$", fontsize=9.2, color=COLOR_NORMAL, ha='center', va='top', fontweight='normal')

    # Curvature radii arrows
    ax1.annotate('', xy=(K_x, 1.15), xytext=(T1_x, 1.15),
                arrowprops=dict(arrowstyle='<->', color=COLOR_PINION, lw=1.0), zorder=4)
    ax1.text(0.5 * (T1_x + K_x) - 0.5, 1.30, tr('fig3_rho1'),
             fontsize=8.5, color=COLOR_PINION, ha='center', va='bottom')

    ax1.annotate('', xy=(T2_x, 1.15), xytext=(K_x, 1.15),
                arrowprops=dict(arrowstyle='<->', color=COLOR_GEAR, lw=1.0), zorder=4)
    ax1.text(0.5 * (K_x + T2_x), 1.30, tr('fig3_rho2'),
             fontsize=8.5, color=COLOR_GEAR, ha='center', va='bottom')

    # Curvature sum badge (Enlarged to guarantee Gate 3 padding >= 15 px)
    sum_badge = patches.FancyBboxPatch((9.0, 2.7), 20.0, 2.2, boxstyle="round,pad=0.25",
                                       fc="#F8FAFC", ec=COLOR_AXIS, lw=0.8, zorder=4)
    ax1.add_patch(sum_badge)
    ax1.text(19.0, 3.8, r"$\rho_1 + \rho_2 = T_1 T_2 = a \sin\alpha_0 = 36.938\text{ mm}$",
             fontsize=8.5, color=COLOR_TEXT_MAIN, ha='center', va='center', zorder=5)

    # Tangential Velocity Vectors at Point K
    ax1.annotate('', xy=(K_x, 3.6), xytext=(K_x, 0.0),
                arrowprops=dict(arrowstyle="-|>,head_length=0.40,head_width=0.18",
                                color=COLOR_PINION, lw=1.5), zorder=7)
    ax1.text(K_x - 0.5, 3.3, r"$v_{t1}$", fontsize=9.0, color=COLOR_PINION, ha='right', va='center')

    ax1.annotate('', xy=(K_x + 0.8, 5.2), xytext=(K_x + 0.8, 0.0),
                arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.20",
                                color=COLOR_GEAR, lw=1.6), zorder=7)
    ax1.text(K_x + 1.2, 4.0, r"$v_{t2}$", fontsize=9.0, color=COLOR_GEAR, ha='left', va='center')

    ax1.annotate('', xy=(K_x - 0.8, -2.4), xytext=(K_x - 0.8, 0.0),
                arrowprops=dict(arrowstyle="-|>,head_length=0.40,head_width=0.18",
                                color=COLOR_NORMAL, lw=1.5), zorder=7)
    ax1.text(K_x - 1.2, -1.5, r"$v_g < 0$", fontsize=9.0, color=COLOR_NORMAL, ha='right', va='center')

    ax1.set_xlim(-4.5, 41.5)
    ax1.set_ylim(-3.5, 6.2)
    ax1.axis('off')
    ax1.set_title(tr('fig3_panel1_title'), fontsize=11.5, color=COLOR_TEXT_MAIN, pad=8)

    # -----------------------------------------------------------------------
    # Lower Panel: Velocity Distributions along Active Path
    # -----------------------------------------------------------------------
    s_vals = np.linspace(-7.828, 6.774, 180)
    vt1_vals = 9.235 + s_vals
    vt2_vals = (27.704 - s_vals) / 3.0
    vg_vals = vt1_vals - vt2_vals

    ax2.plot(s_vals, vt1_vals, color=COLOR_PINION, lw=1.8, label=tr('fig3_vt1'), zorder=4)
    ax2.plot(s_vals, vt2_vals, color=COLOR_GEAR, lw=1.8, label=tr('fig3_vt2'), zorder=4)
    ax2.plot(s_vals, vg_vals, color=COLOR_NORMAL, lw=1.8, linestyle="--", label=tr('fig3_vg'), zorder=4)

    ax2.axhline(0, color=COLOR_AXIS, linestyle="-", lw=0.7, zorder=2)
    ax2.axvline(0, color=COLOR_TANGENT, linestyle=":", lw=0.9, zorder=2)

    ax2.scatter([0], [0], color=COLOR_NORMAL, s=55, zorder=5)
    ax2.scatter([0], [9.235], color=COLOR_TANGENT, s=55, zorder=5)
    ax2.text(0.3, 0.5, tr('fig3_pure_rolling'), fontsize=8.5, color=COLOR_NORMAL, ha='left', va='bottom')

    ax2.fill_between(s_vals[s_vals <= 0], vg_vals[s_vals <= 0], 0,
                     color='#FEE2E2', alpha=0.45, zorder=2)
    ax2.fill_between(s_vals[s_vals >= 0], 0, vg_vals[s_vals >= 0],
                     color='#E0F2FE', alpha=0.45, zorder=2)

    ax2.text(-4.5, -4.5, tr('fig3_pinion_dedendum_neg'),
             fontsize=8.3, color=COLOR_NORMAL, ha='center', va='center')
    ax2.text(4.0, 4.5, tr('fig3_pinion_addendum_pos'),
             fontsize=8.3, color=COLOR_PINION, ha='center', va='center')

    ax2.set_xticks([-7.828, -2.082, 0.0, 1.028, 6.774])
    ax2.set_xticklabels(["A\n(-7.83)", "B\n(-2.08)", "P\n(0.0)", "D\n(+1.03)", "E\n(+6.77)"], fontsize=8.5)
    ax2.set_xlim(-8.5, 7.5)
    ax2.set_ylim(-11.5, 17.5)
    ax2.set_xlabel(tr('fig3_pos_axis'), fontsize=9.0, color=COLOR_TEXT_MAIN)
    ax2.set_ylabel(tr('fig3_velocity_axis'), fontsize=9.0, color=COLOR_TEXT_MAIN)
    ax2.grid(True, linestyle="--", alpha=0.5, color=COLOR_GRID)
    ax2.legend(loc="upper left", fontsize=8.3, framealpha=0.95)
    ax2.set_title(tr('fig3_panel2_title'), fontsize=11.5, color=COLOR_TEXT_MAIN, pad=8)

    # Bottom Summary Card on Figure (Completely clear of ax2)
    card_ax = fig.add_axes([0.105, 0.018, 0.81, 0.144])
    card_ax.axis('off')
    summary_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.04",
                                          fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0, zorder=1)
    card_ax.add_patch(summary_patch)
    full_card_text = f"{tr('fig3_card_title')}\n\n{tr('fig3_card_body')}"
    card_ax.text(0.5, 0.5, full_card_text, fontsize=8.2, color=COLOR_TEXT_MAIN,
                 ha='center', va='center', linespacing=1.26, zorder=2)

    fig.suptitle(tr('fig3_title'), fontsize=15.0, color=COLOR_TEXT_MAIN, y=0.96)

    save_diagram(fig, "fig3_contact_kinematics_velocities", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 4: Specific Sliding Curves (fig4_specific_sliding_curves)
# ---------------------------------------------------------------------------
def create_diagram_4(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 4: Specific Sliding Curves and Wear/Scuffing Risk Zones along Active Profile.
    """
    apply_language_typography(lang)
    tr = get_tr(lang)

    # Setup figure canvas (8.5 x 9.0 in -> 2550 x 2700 px at 300 DPI)
    fig, ax = plt.subplots(figsize=(8.5, 9.0))
    plt.subplots_adjust(left=0.12, right=0.90, top=0.90, bottom=0.245)

    s_vals = np.linspace(-7.828, 6.774, 300)
    rho1_vals = 9.234544 + s_vals
    rho2_vals = 27.703632 - s_vals
    u = 3.0

    k1_vals = 1.0 - rho2_vals / (u * rho1_vals)
    k2_vals = 1.0 - (u * rho1_vals) / rho2_vals

    s_ext = np.linspace(-8.5, -7.828, 60)
    rho1_ext = 9.234544 + s_ext
    rho2_ext = 27.703632 - s_ext
    k1_ext = 1.0 - rho2_ext / (u * rho1_ext)

    ax.plot(s_vals, k1_vals, color=COLOR_PINION, lw=2.0, label=tr('fig4_k1_label'), zorder=4)
    ax.plot(s_ext, k1_ext, color=COLOR_PINION, lw=1.2, linestyle=":", zorder=3)

    ax.plot(s_vals, k2_vals, color=COLOR_GEAR, lw=2.0, label=tr('fig4_k2_label'), zorder=4)

    ax.axhline(0, color=COLOR_TEXT_MAIN, linestyle="-", lw=0.8, zorder=2)
    ax.axvline(0, color=COLOR_TANGENT, linestyle=":", lw=0.9, zorder=2)

    # Asymptote T1 line
    ax.axvline(-9.235, color=COLOR_NORMAL, linestyle="--", lw=1.0, alpha=0.7, zorder=2)
    ax.text(-9.35, -3.8, tr('fig4_asymptote_t1'), fontsize=8.3, color=COLOR_NORMAL,
            rotation=90, va='center', ha='right')

    # Hazard Zones (Shaded)
    mask_danger = s_vals <= -3.85
    ax.fill_between(s_vals[mask_danger], k1_vals[mask_danger], -1.0,
                    color='#FEE2E2', alpha=0.50, zorder=2)
    ax.text(-5.8, -5.8, tr('fig4_danger_zone_pinion'), fontsize=8.3, color=COLOR_NORMAL,
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=COLOR_NORMAL, lw=0.6))

    mask_gear = s_vals >= 5.54
    ax.fill_between(s_vals[mask_gear], k2_vals[mask_gear], -1.0,
                    color='#CCFBF1', alpha=0.50, zorder=2)
    ax.text(6.1, -1.8, tr('fig4_danger_zone_gear'), fontsize=8.3, color=COLOR_GEAR,
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=COLOR_GEAR, lw=0.6))

    # Key Singular Points (Isolated to prevent any text overlaps)
    # Point A: Callout below A
    ax.scatter([-7.828], [-7.420], color=COLOR_NORMAL, s=55, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.annotate(tr('fig4_pt_a_annot'),
                xy=(-7.828, -7.420), xytext=(-7.0, -7.80),
                fontsize=8.3, color=COLOR_NORMAL, ha='left', va='top',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_NORMAL, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=COLOR_NORMAL, lw=0.8), zorder=7)

    # Point B: Callout left-below
    ax.scatter([-2.082], [-0.388], color='#7C3AED', s=45, zorder=6)
    ax.annotate(tr('fig4_pt_b_annot'),
                xy=(-2.082, -0.388), xytext=(-3.2, -1.6),
                fontsize=8.3, color='#7C3AED', ha='right', va='top',
                arrowprops=dict(arrowstyle="-|>", color='#7C3AED', lw=0.7),
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec='#7C3AED', lw=0.7), zorder=7)

    # Point P: Callout top-left above P
    ax.scatter([0.0], [0.0], color=COLOR_CONTACT, s=60, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=1.0)
    ax.annotate(tr('fig4_pure_rolling_point'),
                xy=(0.0, 0.0), xytext=(-0.3, 0.65),
                fontsize=8.0, color=COLOR_CONTACT, ha='right', va='bottom',
                linespacing=1.20,
                arrowprops=dict(arrowstyle="-|>", color=COLOR_CONTACT, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=COLOR_CONTACT, lw=0.8), zorder=7)

    # Point D: Callout right-below
    ax.scatter([1.028], [-0.154], color='#7C3AED', s=45, zorder=6)
    ax.annotate(tr('fig4_pt_d_annot'),
                xy=(1.028, -0.154), xytext=(2.2, -0.65),
                fontsize=8.3, color='#7C3AED', ha='left', va='top',
                arrowprops=dict(arrowstyle="-|>", color='#7C3AED', lw=0.7),
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec='#7C3AED', lw=0.7), zorder=7)

    # Point E: Callout right-below
    ax.scatter([6.774], [-1.295], color=COLOR_GEAR, s=52, zorder=6, edgecolors=COLOR_TEXT_MAIN, lw=0.8)
    ax.annotate(tr('fig4_pt_e_annot'),
                xy=(6.774, -1.295), xytext=(5.6, -2.5),
                fontsize=8.3, color=COLOR_GEAR, ha='right', va='top',
                arrowprops=dict(arrowstyle="-|>", color=COLOR_GEAR, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=COLOR_GEAR, lw=0.8), zorder=7)

    # Top Right Box: Kinematic Identity (Enlarged for Gate 3 padding >= 15 px)
    id_box = patches.FancyBboxPatch((1.0, 0.75), 6.2, 0.80, boxstyle="round,pad=0.20",
                                   fc="#F8FAFC", ec=COLOR_AXIS, lw=0.8, zorder=5)
    ax.add_patch(id_box)
    ax.text(4.1, 1.15, tr('fig4_identity_box'), fontsize=8.3, color=COLOR_TEXT_MAIN,
            ha='center', va='center', zorder=6)

    # Asymmetry callout (Enlarged for Gate 3 padding >= 15 px)
    asym_box = patches.FancyBboxPatch((-8.6, -3.8), 7.2, 1.7, boxstyle="round,pad=0.25",
                                      fc="#FFFBEB", ec="#F59E0B", lw=0.8, zorder=5)
    ax.add_patch(asym_box)
    ax.text(-5.0, -2.95, tr('fig4_asymmetry_box'), fontsize=7.8, color=COLOR_TEXT_MAIN,
            ha='center', va='center', linespacing=1.25, zorder=6)

    ax.set_xticks([-7.828, -2.082, 0.0, 1.028, 6.774])
    ax.set_xticklabels(["A\n(-7.83)", "B\n(-2.08)", "P\n(0.0)", "D\n(+1.03)", "E\n(+6.77)"], fontsize=8.5)
    ax.set_xlim(-9.8, 7.6)
    ax.set_ylim(-8.6, 1.8)
    ax.set_xlabel(tr('fig4_x_axis'), fontsize=9.0, color=COLOR_TEXT_MAIN)
    ax.set_ylabel(tr('fig4_y_axis'), fontsize=9.0, color=COLOR_TEXT_MAIN)
    ax.grid(True, linestyle="--", alpha=0.5, color=COLOR_GRID)
    ax.legend(loc="upper left", fontsize=8.3, framealpha=0.95)
    ax.set_title(tr('fig4_title'), fontsize=15.0, color=COLOR_TEXT_MAIN, pad=14)

    # Bottom Summary Card on Figure (Completely clear of ax)
    card_ax = fig.add_axes([0.105, 0.018, 0.81, 0.144])
    card_ax.axis('off')
    summary_patch = patches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0, boxstyle="round,pad=0.04",
                                          fc=COLOR_CARD_BG, ec=COLOR_CARD_BORDER, lw=1.0, zorder=1)
    card_ax.add_patch(summary_patch)
    full_card_text = f"{tr('fig4_card_title')}\n\n{tr('fig4_card_body')}"
    card_ax.text(0.5, 0.5, full_card_text, fontsize=8.2, color=COLOR_TEXT_MAIN,
                 ha='center', va='center', linespacing=1.26, zorder=2)

    save_diagram(fig, "fig4_specific_sliding_curves", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Aliases and Dispatch Table
# ---------------------------------------------------------------------------
create_diagram_fig1 = create_diagram_1
create_diagram_fig2 = create_diagram_2
create_diagram_fig3 = create_diagram_3
create_diagram_fig4 = create_diagram_4

DIAGRAM_DISPATCH = {
    'fig1': create_diagram_1,
    'fig2': create_diagram_2,
    'fig3': create_diagram_3,
    'fig4': create_diagram_4,
}


def main():
    parser = argparse.ArgumentParser(
        description="H-GEAR STUDIO Blog Part 3 Academic Diagram Generator (32 Assets, Multilingual, 300 DPI)"
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
    print("H-GEAR STUDIO Part 3 Academic Diagram Generation Pipeline")
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
