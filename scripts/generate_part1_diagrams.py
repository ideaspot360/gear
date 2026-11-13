"""
H-GEAR STUDIO Blog Part 1 Academic Diagram Generator (Multilingual & High-Precision)
Generates high-precision, publication-quality SVG and PNG diagrams:
  1. Fig 1A: Friction Drive Mechanism (fig1a_friction_drive)
  2. Fig 1B: Involute Conjugate Toothed Drive (fig1b_gear_drive)
  3. Fig 2: The Fundamental Law of Gearing (Willis' Law) (fig2_willis_law_geometry)
  4. Fig 3: Contact Point Kinematics & Velocity Decomposition (fig3_contact_velocity_vectors)

Applied Engineering Design Standards:
  - 100% Regular font weights (clean academic typography)
  - Mathematical font scaling for web content container (~720px~768px):
      * Title: 16.0 pt (screen: 18.8 ~ 20.0 px)
      * Subtitle / Section Header: 13.0 pt (screen: 15.3 ~ 16.3 px, matches 16px body font)
      * Body Label / Dimension: 12.0 pt (screen: 14.1 ~ 15.0 px >= 14px threshold)
      * Caption / Annotation / Legend: 10.5 pt (screen: 12.4 ~ 13.1 px)
  - Strict line-weight hierarchy:
      * Core profile / normal: 1.4 ~ 1.5 pt
      * Secondary lines: 1.0 ~ 1.2 pt
      * Fine reference / hairlines: 0.7 ~ 0.8 pt (pitch circles, base circles, projections, centerlines)
  - Slim arrowheads (head_length=0.45, head_width=0.22)
  - Zero-overlap layout: radial offsets, leader lines, separated callout cards
  - Multilingual pipeline for 4 languages: ko (Korean), en (English), de (German), ja (Japanese)
  - Dynamic font profile switching (Malgun Gothic, Yu Gothic, Segoe UI)
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
        # Fig 1A
        'fig1a_title': "(A) 마찰차(Friction Wheel)의 구동 메커니즘",
        'o1_label': r"$O_1$",
        'o2_label': r"$O_2$",
        'omega1_label': r"$\omega_1$ (구동, CW)",
        'omega2_label': r"$\omega_2$ (종동, CCW)",
        'p_contact': r"$P$ (접촉점)",
        'fn_force': "압축 수직항력 $F_N$\n(외부 가압 필수)",
        'ft_force': r"마찰 구동력 $F_t \leq \mu_s F_N$",
        'slip_box_title': "[마찰차의 역학적 한계: 필연적 슬립(Slip) 발생]",
        'slip_box_body': "전달 토크 급증 또는 마찰계수 저하 시 필연적 미끄러짐 발생\n"
                         r"$\Delta v = v_1 - v_2 \neq 0 \;\longrightarrow\;$ 각속도비($u$) 변동 및 위상 동기화 상실",
        # Fig 1B
        'fig1b_title': "(B) 정규 인벌류트 기어의 형상 맞물림(Positive Conjugate Mesh)",
        'spec_badge': "★ 정규 인볼류트 치형 맞물림 (등속 맞물림, 간섭 0.000 mm)\n"
                      r"   모듈 $m=2.0,\; z_1=17,\; z_2=33,\; \alpha_n=20^\circ,\; j_n=0.0$",
        'clearance_label': "이뿌리 틈새 (Clearance)\n" r"$c = 0.25m = 0.50\;\mathrm{mm}$",
        'topland_label': "이끝 평탄면 (Top Land)\n" r"$s_a \geq 0.25m$",
        'loa_label': r"작용선 (Line of Action, $n-n$)",
        'pitch_tangent': r"피치 접선 ($t_P - t_P$)",
        'p_pitch': r"$P$ (피치점)",
        'banner_title': "★ 기어 전동의 제1원리: 불변의 상수 각속도비 (Constant Velocity Ratio)",
        'banner_formula': r"$u = \frac{\omega_1}{\omega_2} = \frac{z_2}{z_1} = \frac{33}{17} \approx 1.9412 = \mathrm{Constant} \quad (\Delta u \equiv 0.000000)$",
        'banner_desc': "① 치면 형상 맞물림(Positive Mesh): 외부 예압(FN) 없이 전달 토크에만 비례하는 정상 하중 발생\n"
                       r"② 닫힌 해 접촉 기하: 간섭 0.000 mm 무슬립 롤링-슬라이딩으로 98~99.5% 초고효율 동력 전달",
        # Fig 2
        'fig2_title': "기어 기구학의 제1법칙: 기어 맞물림의 법칙 (Willis' Law)",
        'fig2_centerline': "중심선 (Line of Centers)",
        'fig2_common_normal': r"공통 법선 $n-n$ (작용선, Line of Action)",
        'fig2_pitch_tangent': r"피치점 공통 접선 ($t_P - t_P$)",
        'fig2_contact_tangent': r"접점 공통 접선 ($t_K - t_K$)",
        'fig2_profile_1': r"치형 곡선 1 ($\Sigma_1$)",
        'fig2_profile_2': r"치형 곡선 2 ($\Sigma_2$)",
        'fig2_o1': r"$O_1$ (피니언 중심)",
        'fig2_o2': r"$O_2$ (대기어 중심)",
        'fig2_p': r"$P$ (고정된 피치점)",
        'fig2_k': r"$K$ (임의의 치면 접촉점)",
        'fig2_n1': r"$N_1$ (기초원 접점)",
        'fig2_n2': r"$N_2$ (기초원 접점)",
        'fig2_alpha': r"$\alpha$ (압력각)",
        'fig2_rb1': r"$r_{b1} = r_1 \cos\alpha$",
        'fig2_rb2': r"$r_{b2} = r_2 \cos\alpha$",
        'fig2_omega1': r"$\omega_1$",
        'fig2_omega2': r"$\omega_2$",
        'fig2_proof_title': "★ 윌리스(Willis) 맞물림 기본 법칙의 기하학적 닫힌 해 수식",
        'fig2_proof_formula': r"$\Delta O_1 N_1 P \sim \Delta O_2 N_2 P$ (닮은꼴 직각삼각형)"
                              r" $\;\Longrightarrow\; \frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \frac{r_2}{r_1} = \frac{O_2 N_2}{O_1 N_1} = \frac{r_{b2}}{r_{b1}} = \mathrm{Constant}$",
        'fig2_proof_desc': "치면 접촉점 K의 이동과 무관하게, 공통 법선(Line of Action)이\n중심선상의 고정된 피치점 P를 관통해야만 일정한 속도비가 보존된다.",
        # Fig 3
        'fig3_title': "접촉점(K)의 기구학적 속도 분해: 법선 연속성 vs 상대 미끄럼",
        'fig3_tangent': r"공통 접선 ($t-t$)",
        'fig3_normal': r"공통 법선 ($\vec{n}$)",
        'fig3_profile_1': r"치형 1 치면 ($\Sigma_1$)",
        'fig3_profile_2': r"치형 2 치면 ($\Sigma_2$)",
        'fig3_v1': r"$\vec{v}_1$ (치형 1 선속도)",
        'fig3_v2': r"$\vec{v}_2$ (치형 2 선속도)",
        'fig3_vn': r"$\vec{v}_{n1} = \vec{v}_{n2}$ (법선 속도 완전 일치!)",
        'fig3_vt1': r"$\vec{v}_{t1}$",
        'fig3_vt2': r"$\vec{v}_{t2}$",
        'fig3_vs': r"$\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2}$" "\n(상대 미끄럼 속도, Sliding)",
        'fig3_k': r"$K$ (치면 접촉점)",
        'fig3_summary_title': "★ 접촉점(K) 기구학의 2대 절대 물리 법칙",
        'fig3_rule1': "1. 법선 방향 연속 접촉 조건: $v_{n1} = v_{n2}$\n   " r"$\longrightarrow$ 치면 파고듦(Interpenetration) 및 들뜸(Separation) 방지",
        'fig3_rule2': r"2. 접선 방향 상대 미끄럼 발생: $\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2} \neq \vec{0}$" "\n   " r"$\longrightarrow$ 치면 마찰열, 스커핑(Scuffing), EHL 마모의 근원",
    },
    'en': {
        # Fig 1A
        'fig1a_title': "(A) Friction Wheel Drive Mechanism",
        'o1_label': r"$O_1$",
        'o2_label': r"$O_2$",
        'omega1_label': r"$\omega_1$ (Driver, CW)",
        'omega2_label': r"$\omega_2$ (Driven, CCW)",
        'p_contact': r"$P$ (Contact Point)",
        'fn_force': "Normal Clamping Force $F_N$\n(External Preload Required)",
        'ft_force': r"Friction Traction $F_t \leq \mu_s F_N$",
        'slip_box_title': "[Mechanical Limits of Friction Drive: Inevitable Slip]",
        'slip_box_body': "Inevitable contact slip occurs when torque exceeds traction limit\n"
                         r"$\Delta v = v_1 - v_2 \neq 0 \;\longrightarrow\;$ Velocity ratio fluctuation & phase desynchronization",
        # Fig 1B
        'fig1b_title': "(B) Positive Conjugate Involute Gear Drive",
        'spec_badge': "[Standard Involute Conjugate Mesh (Zero Overlap 0.000 mm)]\n"
                      r"   Module $m=2.0,\; z_1=17,\; z_2=33,\; \alpha_n=20^\circ,\; j_n=0.0$",
        'clearance_label': "Bottom Clearance\n" r"$c = 0.25m = 0.50\;\mathrm{mm}$",
        'topland_label': "Top Land Width\n" r"$s_a \geq 0.25m$",
        'loa_label': r"Line of Action ($n-n$)",
        'pitch_tangent': r"Pitch Tangent ($t_P - t_P$)",
        'p_pitch': r"$P$ (Pitch Point)",
        'banner_title': "[First Principle of Gearing: Constant Angular Velocity Ratio]",
        'banner_formula': r"$u = \frac{\omega_1}{\omega_2} = \frac{z_2}{z_1} = \frac{33}{17} \approx 1.9412 = \mathrm{Constant} \quad (\Delta u \equiv 0.000000)$",
        'banner_desc': "1. Positive Mechanical Interlock: Mesh load proportional to torque without preload\n"
                       r"2. Closed-form Contact: Pure rolling-sliding with zero interference (0.000 mm)",
        # Fig 2
        'fig2_title': "Fundamental Law of Gearing: Willis' Law of Conjugate Action",
        'fig2_centerline': "Line of Centers",
        'fig2_common_normal': r"Common Normal $n-n$ (Line of Action)",
        'fig2_pitch_tangent': r"Pitch Tangent ($t_P - t_P$)",
        'fig2_contact_tangent': r"Contact Tangent ($t_K - t_K$)",
        'fig2_profile_1': r"Tooth Profile 1 ($\Sigma_1$)",
        'fig2_profile_2': r"Tooth Profile 2 ($\Sigma_2$)",
        'fig2_o1': r"$O_1$ (Pinion Center)",
        'fig2_o2': r"$O_2$ (Gear Center)",
        'fig2_p': r"$P$ (Fixed Pitch Point)",
        'fig2_k': r"$K$ (Arbitrary Contact Point)",
        'fig2_n1': r"$N_1$ (Base Circle Tangent Point)",
        'fig2_n2': r"$N_2$ (Base Circle Tangent Point)",
        'fig2_alpha': r"$\alpha$ (Pressure Angle)",
        'fig2_rb1': r"$r_{b1} = r_1 \cos\alpha$",
        'fig2_rb2': r"$r_{b2} = r_2 \cos\alpha$",
        'fig2_omega1': r"$\omega_1$",
        'fig2_omega2': r"$\omega_2$",
        'fig2_proof_title': "[Geometric Closed-Form Formulation of Willis' Law of Gearing]",
        'fig2_proof_formula': r"$\Delta O_1 N_1 P \sim \Delta O_2 N_2 P$ (Similar Right Triangles)"
                              r" $\;\Longrightarrow\; \frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \frac{r_2}{r_1} = \frac{O_2 N_2}{O_1 N_1} = \frac{r_{b2}}{r_{b1}} = \mathrm{Constant}$",
        'fig2_proof_desc': "Constant velocity ratio is maintained if and only if the common normal\npasses through the fixed pitch point P along the line of centers.",
        # Fig 3
        'fig3_title': "Kinematic Velocity Decomposition at Contact Point K: Normal Continuity vs Relative Sliding",
        'fig3_tangent': r"Common Tangent ($t-t$)",
        'fig3_normal': r"Common Normal ($\vec{n}$)",
        'fig3_profile_1': r"Tooth 1 Profile ($\Sigma_1$)",
        'fig3_profile_2': r"Tooth 2 Profile ($\Sigma_2$)",
        'fig3_v1': r"$\vec{v}_1$ (Tooth 1 Velocity)",
        'fig3_v2': r"$\vec{v}_2$ (Tooth 2 Velocity)",
        'fig3_vn': r"$\vec{v}_{n1} = \vec{v}_{n2}$ (Strict Normal Continuity)",
        'fig3_vt1': r"$\vec{v}_{t1}$",
        'fig3_vt2': r"$\vec{v}_{t2}$",
        'fig3_vs': r"$\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2}$" "\n(Relative Sliding Velocity)",
        'fig3_k': r"$K$ (Contact Point)",
        'fig3_summary_title': "[Two Fundamental Kinematic Laws at Contact Point K]",
        'fig3_rule1': "1. Normal Continuity Condition: $v_{n1} = v_{n2}$\n   " r"$\longrightarrow$ Prevents interpenetration and contact loss",
        'fig3_rule2': r"2. Tangential Relative Sliding: $\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2} \neq \vec{0}$" "\n   " r"$\longrightarrow$ Source of frictional heat, scuffing, and EHL wear",
    },
    'de': {
        # Fig 1A
        'fig1a_title': "(A) Reibradgetriebe-Mechanismus",
        'o1_label': r"$O_1$",
        'o2_label': r"$O_2$",
        'omega1_label': r"$\omega_1$ (Treiber, CW)",
        'omega2_label': r"$\omega_2$ (Abtrieb, CCW)",
        'p_contact': r"$P$ (Berührungspunkt)",
        'fn_force': "Normalkraft $F_N$\n(Anpressung erforderlich)",
        'ft_force': r"Reibkraft $F_t \leq \mu_s F_N$",
        'slip_box_title': "[Grenzen des Reibradgetriebes: Unvermeidlicher Schlupf]",
        'slip_box_body': "Schlupf tritt unvermeidlich bei Drehmomentspitzen oder Reibwertabfall auf\n"
                         r"$\Delta v = v_1 - v_2 \neq 0 \;\longrightarrow\;$ Übersetzungsänderung & Synchronisationsverlust",
        # Fig 1B
        'fig1b_title': "(B) Formschlüssige Evolventenverzahnung",
        'spec_badge': "[Norm-Evolventeneingriff (Konjugiert, Überlappung 0.000 mm)]\n"
                      r"   Modul $m=2.0,\; z_1=17,\; z_2=33,\; \alpha_n=20^\circ,\; j_n=0.0$",
        'clearance_label': "Kopfspiel (Clearance)\n" r"$c = 0.25m = 0.50\;\mathrm{mm}$",
        'topland_label': "Kopfdicke (Top Land)\n" r"$s_a \geq 0.25m$",
        'loa_label': r"Eingriffslinie ($n-n$)",
        'pitch_tangent': r"Wälztangente ($t_P - t_P$)",
        'p_pitch': r"$P$ (Wälzpunkt)",
        'banner_title': "[Erstes Grundgesetz der Verzahnung: Konstantes Übersetzungsverhältnis]",
        'banner_formula': r"$u = \frac{\omega_1}{\omega_2} = \frac{z_2}{z_1} = \frac{33}{17} \approx 1.9412 = \mathrm{Constant} \quad (\Delta u \equiv 0.000000)$",
        'banner_desc': "1. Formschluss: Zahnkraft rein proportional zum Drehmoment ohne radiale Vorlast\n"
                       r"2. Exakte Geometrie: Schlupffreies Abwälzen ohne Klemmen (0.000 mm) mit 98-99.5% Wirkungsgrad",
        # Fig 2
        'fig2_title': "Erstes Grundgesetz der Getriebekinematik: Verzahnungsgesetz (Willis)",
        'fig2_centerline': "Zentrallinie",
        'fig2_common_normal': r"Gemeinsame Normale $n-n$ (Eingriffslinie)",
        'fig2_pitch_tangent': r"Wälztangente ($t_P - t_P$)",
        'fig2_contact_tangent': r"Berührtangente ($t_K - t_K$)",
        'fig2_profile_1': r"Zahnprofil 1 ($\Sigma_1$)",
        'fig2_profile_2': r"Zahnprofil 2 ($\Sigma_2$)",
        'fig2_o1': r"$O_1$ (Ritzel-Zentrum)",
        'fig2_o2': r"$O_2$ (Rad-Zentrum)",
        'fig2_p': r"$P$ (Fester Wälzpunkt)",
        'fig2_k': r"$K$ (Zahnkontaktpunkt)",
        'fig2_n1': r"$N_1$ (Grundkreis-Berührungspunkt)",
        'fig2_n2': r"$N_2$ (Grundkreis-Berührungspunkt)",
        'fig2_alpha': r"$\alpha$ (Eingriffswinkel)",
        'fig2_rb1': r"$r_{b1} = r_1 \cos\alpha$",
        'fig2_rb2': r"$r_{b2} = r_2 \cos\alpha$",
        'fig2_omega1': r"$\omega_1$",
        'fig2_omega2': r"$\omega_2$",
        'fig2_proof_title': "[Geometrische geschlossene Formulierung des Verzahnungsgesetzes (Willis)]",
        'fig2_proof_formula': r"$\Delta O_1 N_1 P \sim \Delta O_2 N_2 P$"
                              r" $\;\Longrightarrow\; \frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \frac{r_2}{r_1} = \frac{O_2 N_2}{O_1 N_1} = \frac{r_{b2}}{r_{b1}} = \mathrm{Constant}$",
        'fig2_proof_desc': "Das Übersetzungsverhältnis ist genau dann konstant, wenn die gemeinsame Normale\nstets den festen Wälzpunkt P auf der Zentrallinie schneidet.",
        # Fig 3
        'fig3_title': "Kinematische Geschwindigkeitszerlegung im Kontaktpunkt K: Normalkontinuität vs. Relativgleiten",
        'fig3_tangent': r"Gemeinsame Tangente ($t-t$)",
        'fig3_normal': r"Gemeinsame Normale ($\vec{n}$)",
        'fig3_profile_1': r"Zahnflanke 1 ($\Sigma_1$)",
        'fig3_profile_2': r"Zahnflanke 2 ($\Sigma_2$)",
        'fig3_v1': r"$\vec{v}_1$ (Zahn 1 Geschwindigkeit)",
        'fig3_v2': r"$\vec{v}_2$ (Zahn 2 Geschwindigkeit)",
        'fig3_vn': r"$\vec{v}_{n1} = \vec{v}_{n2}$ (Identische Normalkomponente)",
        'fig3_vt1': r"$\vec{v}_{t1}$",
        'fig3_vt2': r"$\vec{v}_{t2}$",
        'fig3_vs': r"$\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2}$" "\n(Relativ-Gleitgeschwindigkeit)",
        'fig3_k': r"$K$ (Zahnkontaktpunkt)",
        'fig3_summary_title': "[Zwei fundamentale kinematische Gesetzmässigkeiten im Kontaktpunkt K]",
        'fig3_rule1': "1. Kontaktbedingung in Normalenrichtung: $v_{n1} = v_{n2}$\n   " r"$\longrightarrow$ Verhindert Eindringen und Abheben der Zahnflanken",
        'fig3_rule2': r"2. Relativgleiten in Tangentialrichtung: $\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2} \neq \vec{0}$" "\n   " r"$\longrightarrow$ Ursache für Reibungswärme, Fressen und EHL-Verschleiss",
    },
    'ja': {
        # Fig 1A
        'fig1a_title': "(A) 摩擦車 (Friction Wheel) の伝動機構",
        'o1_label': r"$O_1$",
        'o2_label': r"$O_2$",
        'omega1_label': r"$\omega_1$ (駆動, CW)",
        'omega2_label': r"$\omega_2$ (従動, CCW)",
        'p_contact': r"$P$ (接触点)",
        'fn_force': "圧縮垂直抗力 $F_N$\n(外部加圧が必須)",
        'ft_force': r"摩擦駆動力 $F_t \leq \mu_s F_N$",
        'slip_box_title': "[摩擦車の力学的限界: 必然的すべり (Slip) の発生]",
        'slip_box_body': "伝達トルク急増やすべり摩擦低下時に必然的すべりが発生\n"
                         r"$\Delta v = v_1 - v_2 \neq 0 \;\longrightarrow\;$ 角速度比 ($u$) 変動および位相同期の喪失",
        # Fig 1B
        'fig1b_title': "(B) 正準インボリュート歯車の形状かみ合い (Positive Mesh)",
        'spec_badge': "★ 正準インボリュート歯車かみ合い (等速接触, 干渉 0.000 mm)\n"
                      r"   モジュール $m=2.0,\; z_1=17,\; z_2=33,\; \alpha_n=20^\circ,\; j_n=0.0$",
        'clearance_label': "頂げき (Clearance)\n" r"$c = 0.25m = 0.50\;\mathrm{mm}$",
        'topland_label': "歯先円筒面幅 (Top Land)\n" r"$s_a \geq 0.25m$",
        'loa_label': r"作用線 (かみ合い線, $n-n$)",
        'pitch_tangent': r"ピッチ点共通接線 ($t_P - t_P$)",
        'p_pitch': r"$P$ (ピッチ点)",
        'banner_title': "★ 歯車伝動の第1原理: 不変の一定角速度比 (Constant Velocity Ratio)",
        'banner_formula': r"$u = \frac{\omega_1}{\omega_2} = \frac{z_2}{z_1} = \frac{33}{17} \approx 1.9412 = \mathrm{Constant} \quad (\Delta u \equiv 0.000000)$",
        'banner_desc': "① 歯面形状拘束: 外部予圧なしに伝達トルクにのみ比例する正常かみ合い荷重\n"
                       r"② 厳密解接触幾何: 干渉 0.000 mm 無すべり転がり-滑りで 98〜99.5% 超高効率伝動",
        # Fig 2
        'fig2_title': "歯車機構学の第1法則: 歯車かみ合いの法則 (Willis' Law)",
        'fig2_centerline': "中心線 (Line of Centers)",
        'fig2_common_normal': r"共通法線 $n-n$ (作用線, Line of Action)",
        'fig2_pitch_tangent': r"ピッチ点共通接線 ($t_P - t_P$)",
        'fig2_contact_tangent': r"接触点共通接線 ($t_K - t_K$)",
        'fig2_profile_1': r"歯形曲線 1 ($\Sigma_1$)",
        'fig2_profile_2': r"歯形曲線 2 ($\Sigma_2$)",
        'fig2_o1': r"$O_1$ (小歯車中心)",
        'fig2_o2': r"$O_2$ (大歯車中心)",
        'fig2_p': r"$P$ (固定ピッチ点)",
        'fig2_k': r"$K$ (歯面接触点)",
        'fig2_n1': r"$N_1$ (基礎円接点)",
        'fig2_n2': r"$N_2$ (基礎円接点)",
        'fig2_alpha': r"$\alpha$ (圧力角)",
        'fig2_rb1': r"$r_{b1} = r_1 \cos\alpha$",
        'fig2_rb2': r"$r_{b2} = r_2 \cos\alpha$",
        'fig2_omega1': r"$\omega_1$",
        'fig2_omega2': r"$\omega_2$",
        'fig2_proof_title': "★ ウィリス (Willis) のかみ合い基本法則の幾何学的厳密解",
        'fig2_proof_formula': r"$\Delta O_1 N_1 P \sim \Delta O_2 N_2 P$ (相似な直角三角形)"
                              r" $\;\Longrightarrow\; \frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \frac{r_2}{r_1} = \frac{O_2 N_2}{O_1 N_1} = \frac{r_{b2}}{r_{b1}} = \mathrm{Constant}$",
        'fig2_proof_desc': "歯面接触点 K の移動にかかわらず、共通法線がかみ合い中心線上の\n固定ピッチ点 P を常に通過して初めて一定の速度比が維持される。",
        # Fig 3
        'fig3_title': "接触点 (K) における機構学的速度分解: 法線方向連続性 vs 相対すべり",
        'fig3_tangent': r"共通接線 ($t-t$)",
        'fig3_normal': r"共通法線 ($\vec{n}$)",
        'fig3_profile_1': r"歯形 1 歯面 ($\Sigma_1$)",
        'fig3_profile_2': r"歯形 2 歯面 ($\Sigma_2$)",
        'fig3_v1': r"$\vec{v}_1$ (歯形 1 線速度)",
        'fig3_v2': r"$\vec{v}_2$ (歯形 2 線速度)",
        'fig3_vn': r"$\vec{v}_{n1} = \vec{v}_{n2}$ (法線速度の完全一致!)",
        'fig3_vt1': r"$\vec{v}_{t1}$",
        'fig3_vt2': r"$\vec{v}_{t2}$",
        'fig3_vs': r"$\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2}$" "\n(相対すべり速度, Sliding)",
        'fig3_k': r"$K$ (歯面接触点)",
        'fig3_summary_title': "★ 接触点 (K) における機構学の2大絶対物理法則",
        'fig3_rule1': "1. 法線方向連続接触条件: $v_{n1} = v_{n2}$\n   " r"$\longrightarrow$ 食い込み (Interpenetration) および離脱 (Separation) の防止",
        'fig3_rule2': r"2. 接線方向相対すべり発生: $\vec{v}_s = \vec{v}_{t1} - \vec{v}_{t2} \neq \vec{0}$" "\n   " r"$\longrightarrow$ 歯面摩擦熱, スカッフィング (Scuffing), EHL 摩耗の根源",
    }
}


def get_tr(key: str, lang: str = 'ko') -> str:
    """Safely retrieves translated string for a given key and language with fallback."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS.get('en', {}))
    if key in lang_dict:
        return lang_dict[key]
    return TRANSLATIONS.get('en', {}).get(key, TRANSLATIONS.get('ko', {}).get(key, key))


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
        fig.savefig(svg_path, format='svg', bbox_inches='tight', pad_inches=0.15,
                    facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(svg_path)
    if formats in ('all', 'png'):
        png_path = output_dir / f"{base_name}.png"
        fig.savefig(png_path, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0.15,
                    facecolor=COLOR_BG, edgecolor='none')
        saved_paths.append(png_path)
    
    plt.close(fig)
    for p in saved_paths:
        size_kb = p.stat().st_size / 1024
        print(f"  [SAVED] {p.name:<34} ({size_kb:6.1f} KB) -> {p.parent}")


# ---------------------------------------------------------------------------
# Diagram 1A: Friction Wheel Drive Mechanism (Single-Column Vertical Layout)
# ---------------------------------------------------------------------------
def create_diagram_1a(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 1A: Friction Wheel Drive Mechanism (Mechanics, Forces & Slip Limit).
    Single-column vertical layout optimized for web containers (~720px~768px).
    Zero-overlap layout between friction wheels and bottom slip warning card.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 1A: fig1a_friction_drive [{lang.upper()}] (8.0 x 9.5 in, 300 DPI)...")
    
    fig = plt.figure(figsize=(8.0, 9.5), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Kinematic Centers and Radii (Normalized Zero-Overlap Geometry)
    r1 = 1.85
    r2 = 2.95
    O1 = np.array([0.0, -r1])      # (0, -1.85), bottom at y = -3.70
    O2 = np.array([0.0, r2])       # (0, 2.95)
    P = np.array([0.0, 0.0])       # Instantaneous pitch contact point
    
    # Friction Cylinders (Slim 1.4 pt outlines, subtle filled tint)
    circle1 = plt.Circle(O1, r1, facecolor=COLOR_PINION, fill=True, alpha=0.07,
                         linewidth=1.4, edgecolor=COLOR_PINION, zorder=2)
    circle2 = plt.Circle(O2, r2, facecolor=COLOR_GEAR, fill=True, alpha=0.07,
                         linewidth=1.4, edgecolor=COLOR_GEAR, zorder=2)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    
    # Line of centers (Slim 0.8 pt centerline)
    ax.plot([0, 0], [-3.75, 4.2], color=COLOR_AXIS, linestyle="-.", linewidth=0.8, zorder=1)
    ax.scatter([O1[0], O2[0]], [O1[1], O2[1]], color=[COLOR_PINION, COLOR_GEAR],
               s=55, zorder=5, edgecolors=COLOR_TEXT_MAIN, linewidths=0.8)
    
    # Center Labels (13.0 pt Regular)
    ax.text(O1[0] - 0.35, O1[1], tr('o1_label'), fontsize=13.0, fontweight='normal',
            color=COLOR_PINION, va='center', ha='right')
    ax.text(O2[0] - 0.35, O2[1], tr('o2_label'), fontsize=13.0, fontweight='normal',
            color=COLOR_GEAR, va='center', ha='right')
    
    # Angular Velocity Rotation Arrows (Slim 1.2 pt, fontsize 12.0 pt)
    draw_circular_arrow(ax, O1, 1.15, 140, 40, color=COLOR_PINION, lw=1.2, mutation_scale=12)
    ax.text(0.95, O1[1] + 0.45, tr('omega1_label'), fontsize=12.0, fontweight='normal',
            color=COLOR_PINION, va='center')
    
    draw_circular_arrow(ax, O2, 1.50, 220, 320, color=COLOR_GEAR, lw=1.2, mutation_scale=12)
    ax.text(1.15, O2[1] - 0.45, tr('omega2_label'), fontsize=12.0, fontweight='normal',
            color=COLOR_GEAR, va='center')
    
    # Instantaneous Contact Point P (70 marker, fontsize 12.0 pt)
    ax.scatter([P[0]], [P[1]], color=COLOR_NORMAL, s=70, zorder=7,
               edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    ax.text(P[0] - 0.35, P[1] + 0.28, tr('p_contact'), fontsize=12.0, fontweight='normal',
            color=COLOR_NORMAL, ha='right', va='center',
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=COLOR_NORMAL, lw=0.8, alpha=0.92))
    
    # Normal Clamping Force FN (Downward vector, fontsize 12.0 pt)
    draw_vector(ax, (0.0, 1.70), (0.0, 0.35), color=COLOR_TEXT_MAIN, lw=1.4, mutation_scale=13)
    ax.text(0.25, 1.05, tr('fn_force'), fontsize=12.0, fontweight='normal',
            color=COLOR_TEXT_MAIN, va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))
    
    # Friction Traction Force Ft (Horizontal vector, fontsize 12.0 pt)
    draw_vector(ax, (0.10, 0.0), (1.60, 0.0), color=COLOR_SLIP, lw=1.4, mutation_scale=13)
    ax.text(0.35, -0.32, tr('ft_force'), fontsize=12.0, fontweight='normal',
            color=COLOR_SLIP, va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.90))
    
    # Engineering Callout Card: Friction Wheel Physical Limitations (Zero-Overlap at y in [-5.2, -3.85])
    slip_box = patches.FancyBboxPatch((-3.8, -5.2), 7.6, 1.35, boxstyle="round,pad=0.2",
                                      fc="#FEF2F2", ec="#FCA5A5", lw=1.1, zorder=3)
    ax.add_patch(slip_box)
    ax.text(0, -4.15, tr('slip_box_title'), fontsize=13.0,
            fontweight='normal', color="#991B1B", ha='center', va='center', zorder=4)
    ax.text(0, -4.70, tr('slip_box_body'), fontsize=10.5,
            fontweight='normal', color="#7F1D1D", ha='center', va='center', zorder=4)
    
    ax.set_xlim(-4.3, 4.3)
    ax.set_ylim(-5.75, 4.65)
    ax.set_title(tr('fig1a_title'), fontsize=16.0, fontweight='normal', pad=14, color=COLOR_TEXT_MAIN)
    
    save_diagram(fig, "fig1a_friction_drive", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 1B: Involute Conjugate Toothed Drive (Single-Column Vertical Layout)
# ---------------------------------------------------------------------------
def create_diagram_1b(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 1B: Positive Involute Conjugate Toothed Drive (Exact Closed-form Profile Mesh).
    Single-column vertical layout with Willis First Principle closed-form math banner.
    Connects directly to backend profile_service for true zero-overlap conjugate profiles.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 1B: fig1b_gear_drive [{lang.upper()}] (8.0 x 9.5 in, 300 DPI)...")
    
    fig = plt.figure(figsize=(8.0, 9.5), dpi=dpi)
    fig.patch.set_facecolor(COLOR_BG)
    
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.set_facecolor(COLOR_BG)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Generate exact gear pair profile from backend kernel (module=2.0, z1=17, z2=33)
    gear_data = generate_gear_pair_profile(
        module=2.0, z1=17, z2=33, alpha_n_deg=20.0,
        backlash_jn_mm=0.0, num_involute_pts=80, num_fillet_pts=50
    )
    
    px = np.array(gear_data['pinion_outline']['x'])
    py = np.array(gear_data['pinion_outline']['y'])
    gx = np.array(gear_data['gear_outline']['x'])
    gy = np.array(gear_data['gear_outline']['y'])
    
    # Transform to vertical centerline coordinate system (Pitch point P at origin (0, 0))
    Xp, Yp = -py, px - 17.0
    Xg, Yg = -gy, gx - 17.0
    
    # Plot true conjugate closed-form gear outlines (Slim 1.4 pt)
    ax.plot(Xp, Yp, color=COLOR_PINION, lw=1.4, zorder=4)
    ax.fill(Xp, Yp, color=COLOR_PINION, alpha=0.08, zorder=3)
    ax.plot(Xg, Yg, color=COLOR_GEAR, lw=1.4, zorder=4)
    ax.fill(Xg, Yg, color=COLOR_GEAR, alpha=0.08, zorder=3)
    
    # Line of centers (Slim 0.8 pt)
    ax.plot([0, 0], [-4.2, 4.2], color=COLOR_AXIS, linestyle="-.", lw=0.8, zorder=2)
    
    # Pitch circles (Slim 0.8 pt dashed)
    theta_pc = np.linspace(-np.pi/6, np.pi/6, 120)
    pc1_x = 17.0 * np.sin(theta_pc)
    pc1_y = -17.0 + 17.0 * np.cos(theta_pc)
    pc2_x = 33.0 * np.sin(theta_pc)
    pc2_y = 33.0 - 33.0 * np.cos(theta_pc)
    ax.plot(pc1_x, pc1_y, color=COLOR_AXIS, linestyle="--", lw=0.8, zorder=2)
    ax.plot(pc2_x, pc2_y, color=COLOR_AXIS, linestyle="--", lw=0.8, zorder=2)
    
    # Pitch tangent line (Slim 0.8 pt dashed)
    ax.plot([-5.5, 5.5], [0, 0], color=COLOR_TANGENT, linestyle="--", lw=0.8, zorder=2)
    ax.text(-3.4, 0.18, tr('pitch_tangent'), fontsize=11.0, fontweight='normal',
            color=COLOR_TANGENT, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))
    
    # Line of Action (Crimson solid line, lw=1.3 pt, alpha=20 deg)
    alpha_rad = np.radians(20.0)
    loa_len = 5.2
    loa_x = np.array([-np.cos(alpha_rad), np.cos(alpha_rad)]) * loa_len
    loa_y = np.array([np.sin(alpha_rad), -np.sin(alpha_rad)]) * loa_len
    ax.plot(loa_x, loa_y, color=COLOR_NORMAL, lw=1.3, linestyle="-", zorder=3)
    ax.text(2.0, -1.60, tr('loa_label'), fontsize=11.5, fontweight='normal',
            color=COLOR_NORMAL, ha='left', va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92))
    
    # Pitch point P
    ax.scatter([0.0], [0.0], color=COLOR_PITCH, s=70, zorder=8,
               edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    ax.text(0.35, -0.42, tr('p_pitch'), fontsize=12.0, fontweight='normal',
            color=COLOR_PITCH, va='center',
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PITCH, lw=0.8, alpha=0.90))
    
    # Top-Left Engineering Specification Badge (10.5 pt)
    ax.text(-5.4, 3.90, tr('spec_badge'), fontsize=10.5, fontweight='normal',
            color=COLOR_TEXT_MAIN, va='top',
            bbox=dict(boxstyle="round,pad=0.25", fc="#F8FAFC", ec=COLOR_AXIS, lw=0.8))
    
    # Clearance and Top Land Leader Annotations (10.5 pt)
    ax.annotate(tr('clearance_label'),
                xy=(0.0, 2.5), xytext=(2.5, 3.0), ha='left', va='center',
                arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22",
                                color=COLOR_GEAR, lw=1.0),
                fontsize=10.5, fontweight='normal', color=COLOR_GEAR,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_GEAR, lw=0.8))
    
    ax.annotate(tr('topland_label'),
                xy=(1.40, 1.94), xytext=(-2.0, 2.05),
                ha='right', va='center',
                arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.22",
                                color=COLOR_PINION, lw=1.0, shrinkA=0, shrinkB=0),
                fontsize=10.5, fontweight='normal', color=COLOR_PINION,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=COLOR_PINION, lw=0.8))
    
    # Bottom Callout Card: Willis First Principle & Constant Velocity Ratio Banner (y in [-6.35, -4.15])
    banner_box = patches.FancyBboxPatch((-5.5, -6.35), 11.0, 2.20, boxstyle="round,pad=0.2",
                                        fc="#F0FDF4", ec="#86EFAC", lw=1.1, zorder=5)
    ax.add_patch(banner_box)
    ax.text(0.0, -4.40, tr('banner_title'),
            fontsize=13.0, fontweight='normal', color="#166534", ha='center', va='center', zorder=6)
    ax.text(0.0, -5.00, tr('banner_formula'),
            fontsize=13.0, fontweight='normal', color="#14532D", ha='center', va='center', zorder=6)
    ax.text(0.0, -5.75, tr('banner_desc'),
            fontsize=10.5, fontweight='normal', color="#166534", ha='center', va='center', zorder=6)
    
    ax.set_xlim(-5.9, 5.9)
    ax.set_ylim(-6.95, 4.45)
    ax.set_title(tr('fig1b_title'), fontsize=16.0, fontweight='normal', pad=14, color=COLOR_TEXT_MAIN)
    
    save_diagram(fig, "fig1b_gear_drive", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Backward Compatibility Wrapper for Fig 1
# ---------------------------------------------------------------------------
def create_diagram_1(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Backward-compatibility wrapper: sequentially creates Fig 1A and Fig 1B.
    Ensures existing tests and CLI invocation (--fig fig1) work seamlessly.
    """
    print(f"\n[COMPAT] Invoking Fig 1 split pipeline: fig1a & fig1b (fig1_friction_vs_gear wrapper) [{lang.upper()}]...")
    create_diagram_1a(output_dir=output_dir, dpi=dpi, formats=formats, lang=lang)
    create_diagram_1b(output_dir=output_dir, dpi=dpi, formats=formats, lang=lang)


# ---------------------------------------------------------------------------
# Diagram 2: The Fundamental Law of Gearing (Willis' Law)
# ---------------------------------------------------------------------------
def create_diagram_2(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 2: Willis' Law of Gearing.
    Canvas: (8.5, 9.0) in. Mathematical font scaling: Title 16pt, Subtitle 13pt, Body 12pt, Caption 10.5pt.
    100% Regular font weights, slim lines, generous uncrowded layout.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 2: fig2_willis_law_geometry [{lang.upper()}] (8.5 x 9.0 in, 300 DPI)...")
    
    fig, ax = plt.subplots(figsize=(8.5, 9.0), dpi=dpi)
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
            zorder=1, label=tr('fig2_centerline'))
    
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
            label=tr('fig2_common_normal'))
    
    # 5. Horizontal Pitch Line Tangent (Slim 0.8 pt dashed)
    L_tan_pitch = 3.4
    ax.plot([-L_tan_pitch, L_tan_pitch], [0, 0], color=COLOR_TANGENT,
            linestyle="--", lw=0.8, zorder=3,
            label=tr('fig2_pitch_tangent'))
    
    # Position pitch tangent label
    ax.text(-2.5, 0.18, tr('fig2_pitch_tangent'), fontsize=11.0, fontweight='normal',
            color=COLOR_TANGENT, ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))
    
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
            label=tr('fig2_contact_tangent'))
    draw_right_angle(ax, K, t_dir, n_dir, size=0.18, color=COLOR_NORMAL, lw=0.8)
    
    # 8. Tooth Profiles Sigma_1, Sigma_2 (Maximum emphasis line: 1.5 pt only)
    s = np.linspace(-1.15, 1.15, 120)
    curve1 = K[:, None] + t_dir[:, None] * s + n_dir[:, None] * (-0.18 * s**2 + 0.01 * s**3)
    curve2 = K[:, None] + t_dir[:, None] * s + n_dir[:, None] * (0.22 * s**2 + 0.01 * s**3)
    ax.plot(curve1[0], curve1[1], color=COLOR_PINION, lw=1.5, zorder=5,
            label=tr('fig2_profile_1'))
    ax.plot(curve2[0], curve2[1], color=COLOR_GEAR, lw=1.5, zorder=5,
            label=tr('fig2_profile_2'))
    
    # 9. Precise point scatter markers
    ax.scatter([O1[0], O2[0]], [O1[1], O2[1]], color=[COLOR_PINION, COLOR_GEAR],
               s=50, zorder=7, edgecolors=COLOR_TEXT_MAIN, linewidths=0.8)
    ax.scatter([N1[0], N2[0]], [N1[1], N2[1]], color=[COLOR_PINION, COLOR_GEAR],
               s=45, zorder=7, edgecolors=COLOR_TEXT_MAIN, linewidths=0.8)
    ax.scatter([P[0]], [P[1]], color=COLOR_PITCH, s=70, zorder=8,
               edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    ax.scatter([K[0]], [K[1]], color=COLOR_CONTACT, s=65, zorder=8,
               edgecolors=COLOR_TEXT_MAIN, linewidths=1.0)
    
    # Center Labels (12.0 pt)
    ax.text(O1[0] + 0.35, O1[1], tr('fig2_o1'), fontsize=12.0, fontweight='normal',
            color=COLOR_PINION, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.90))
    ax.text(O2[0] + 0.35, O2[1], tr('fig2_o2'), fontsize=12.0, fontweight='normal',
            color=COLOR_GEAR, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.90))
    
    # Pitch Point P: Leader line to Upper-Left (-1.6, 1.40) - Safe vertical separation from pitch tangent text
    draw_leader_annotation(ax, pt=P, text_pos=(-1.6, 1.40),
                           text=tr('fig2_p'), color=COLOR_PITCH,
                           box_ec=COLOR_PITCH, fontsize=12.0, fontweight='normal',
                           ha='right', va='center')
    
    # Contact Point K: Leader line to Lower-Right (2.4, -0.4)
    draw_leader_annotation(ax, pt=K, text_pos=(2.4, -0.4),
                           text=tr('fig2_k'), color="#B45309",
                           box_ec=COLOR_CONTACT, fontsize=12.0, fontweight='normal',
                           ha='left', va='center')
    
    # N1: Leader line to Lower-Left (-1.8, -0.8)
    draw_leader_annotation(ax, pt=N1, text_pos=(-1.8, -0.8),
                           text=tr('fig2_n1'), color=COLOR_PINION,
                           box_ec=COLOR_PINION, fontsize=11.0, fontweight='normal',
                           ha='right', va='center')
    
    # N2: Leader line to Upper-Right (2.2, 1.1)
    draw_leader_annotation(ax, pt=N2, text_pos=(2.2, 1.1),
                           text=tr('fig2_n2'), color=COLOR_GEAR,
                           box_ec=COLOR_GEAR, fontsize=11.0, fontweight='normal',
                           ha='left', va='center')
    
    # Pressure Angle Arc (11.0 pt)
    arc_alpha = Arc(P, 2.6, 2.6, angle=0, theta1=0, theta2=np.degrees(alpha),
                    color=COLOR_NORMAL, lw=1.1, zorder=5)
    ax.add_patch(arc_alpha)
    ax.text(1.45, 0.26, tr('fig2_alpha'), fontsize=11.0, fontweight='normal',
            color=COLOR_NORMAL, va='center', ha='left',
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.90))
    
    # Base Circle Radii Labels (10.5 pt)
    ax.text(O1[0] - 1.1, O1[1] + 1.4, tr('fig2_rb1'), fontsize=10.5,
            fontweight='normal', color=COLOR_PINION, ha='center',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.text(O2[0] + 1.2, O2[1] - 1.6, tr('fig2_rb2'), fontsize=10.5,
            fontweight='normal', color=COLOR_GEAR, ha='center',
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    
    # Rotation Arrows (12.0 pt)
    draw_circular_arrow(ax, O1, 1.45, 20, 110, color=COLOR_PINION, lw=1.1, mutation_scale=11)
    ax.text(0.95, O1[1] + 0.5, tr('fig2_omega1'), fontsize=12.0, fontweight='normal', color=COLOR_PINION)
    
    draw_circular_arrow(ax, O2, 1.85, 240, 330, color=COLOR_GEAR, lw=1.1, mutation_scale=11)
    ax.text(1.15, O2[1] - 0.5, tr('fig2_omega2'), fontsize=12.0, fontweight='normal', color=COLOR_GEAR)
    
    # Proof Box: Scaled Typography (Header 13pt, Formula 11.4pt, Desc 10.5pt, Box expanded to 11.4 x 2.35)
    proof_box = patches.FancyBboxPatch((-5.7, -6.05), 11.4, 2.35, boxstyle="round,pad=0.22",
                                       fc="#F0FDF4", ec="#86EFAC", lw=1.0, zorder=4)
    ax.add_patch(proof_box)
    ax.text(0, -3.95, tr('fig2_proof_title'),
            fontsize=13.0, fontweight='normal', color="#166534", ha='center', va='center', zorder=6)
    ax.text(0, -4.63, tr('fig2_proof_formula'),
            fontsize=11.4, fontweight='normal', color="#14532D", ha='center', va='center', zorder=6)
    ax.text(0, -5.40, tr('fig2_proof_desc'),
            fontsize=10.5, fontweight='normal', color="#15803D", ha='center', va='center', zorder=6)
    
    ax.set_xlim(-6.2, 6.2)
    ax.set_ylim(-6.65, 4.75)
    ax.set_title(tr('fig2_title'), fontsize=16.0, fontweight='normal', pad=18, color=COLOR_TEXT_MAIN)
    ax.legend(loc="upper left", fontsize=10.5, framealpha=0.95, edgecolor=COLOR_AXIS)
    
    save_diagram(fig, "fig2_willis_law_geometry", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# Diagram 3: Contact Point Kinematics & Velocity Decomposition
# ---------------------------------------------------------------------------
def create_diagram_3(output_dir=DEFAULT_OUTPUT_DIR, dpi=300, formats='all', lang='ko'):
    """
    Fig 3: Contact Point Kinematics & Velocity Decomposition.
    Canvas: (8.5, 7.5) in. Mathematical font scaling: Title 16pt, Subtitle 13pt, Body 12pt, Caption 10.5pt.
    100% Regular font weights, slim lines, clean uncrowded layout.
    """
    apply_language_typography(lang)
    tr = lambda k: get_tr(k, lang)
    print(f"\nGenerating Fig 3: fig3_contact_velocity_vectors [{lang.upper()}] (8.5 x 7.5 in, 300 DPI)...")
    
    fig, ax = plt.subplots(figsize=(8.5, 7.8), dpi=dpi)
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
            label=tr('fig3_tangent'))
    
    # Common Normal (n-n): Slim 1.3 pt solid
    ax.plot([-e_n[0]*1.6, e_n[0]*3.6], [-e_n[1]*1.6, e_n[1]*3.6],
            color=COLOR_NORMAL, lw=1.3, linestyle="-", zorder=2,
            label=tr('fig3_normal'))
    
    # Right-Angle Symbol at Contact Point K (0.8 pt)
    draw_right_angle(ax, np.array([0.0, 0.0]), e_t, e_n, size=0.20, color=COLOR_NORMAL, lw=0.8)
    
    # Curved Tooth Profiles at K(0, 0): Slim 1.4 pt
    s = np.linspace(-1.5, 2.2, 160)
    c1 = e_t[:, None] * s + e_n[:, None] * (-0.14 * s**2)
    c2 = e_t[:, None] * s + e_n[:, None] * (0.16 * s**2)
    ax.plot(c1[0], c1[1], color=COLOR_PINION, lw=1.4, alpha=0.7, zorder=3,
            label=tr('fig3_profile_1'))
    ax.plot(c2[0], c2[1], color=COLOR_GEAR, lw=1.4, alpha=0.7, zorder=3,
            label=tr('fig3_profile_2'))
    
    # Velocity Component Values
    v_n = 2.0      # Normal velocity (Identical for both teeth)
    v_t1 = 2.6     # Tangential velocity of Tooth 1
    v_t2 = 0.9     # Tangential velocity of Tooth 2
    
    v1 = v_t1 * e_t + v_n * e_n
    v2 = v_t2 * e_t + v_n * e_n
    vn_vec = v_n * e_n
    vt1_vec = v_t1 * e_t
    vt2_vec = v_t2 * e_t
    
    # Full Velocity Vectors v1 and v2 (Slim 1.3 pt, fontsize 12.0 pt)
    draw_vector(ax, (0, 0), v1, color=COLOR_VELOCITY_1, lw=1.3, mutation_scale=12, zorder=6)
    ax.text(v1[0] + 0.15, v1[1] + 0.10, tr('fig3_v1'), fontsize=12.0,
            fontweight='normal', color=COLOR_VELOCITY_1,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))
    
    draw_vector(ax, (0, 0), v2, color=COLOR_VELOCITY_2, lw=1.3, mutation_scale=12, zorder=6)
    ax.text(v2[0] - 0.18, v2[1] + 0.22, tr('fig3_v2'), fontsize=12.0,
            fontweight='normal', color=COLOR_VELOCITY_2,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.90))
    
    # Identical Normal Velocity Vector vn (1.5 pt, fontsize 11.0 pt, 2-line clean placement)
    draw_vector(ax, (0, 0), vn_vec, color=COLOR_NORMAL, lw=1.5, mutation_scale=14, zorder=7)
    vn_multiline = {
        'ko': r"$\vec{v}_{n1} = \vec{v}_{n2}$" "\n(법선 속도 완전 일치!)",
        'en': r"$\vec{v}_{n1} = \vec{v}_{n2}$" "\n(Strict Normal Continuity)",
        'de': r"$\vec{v}_{n1} = \vec{v}_{n2}$" "\n(Identische Normalkomponente)",
        'ja': r"$\vec{v}_{n1} = \vec{v}_{n2}$" "\n(法線速度の完全一致!)"
    }
    ax.text(vn_vec[0] + 0.15, vn_vec[1] - 0.05, vn_multiline.get(lang, vn_multiline['en']),
            fontsize=11.0, fontweight='normal', color=COLOR_NORMAL, ha='left', va='center',
            bbox=dict(boxstyle="round,pad=0.20", fc="#FEF2F2", ec=COLOR_NORMAL, lw=0.9, alpha=0.95))
    
    # Orthogonal Projections (Slim 0.7 pt dotted)
    ax.plot([v1[0], vn_vec[0]], [v1[1], vn_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    ax.plot([v2[0], vn_vec[0]], [v2[1], vn_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    ax.plot([v1[0], vt1_vec[0]], [v1[1], vt1_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    ax.plot([v2[0], vt2_vec[0]], [v2[1], vt2_vec[1]], color=COLOR_AXIS, linestyle=":", lw=0.7, zorder=4)
    
    # Tangential Velocity Components (Slim 0.9 pt dash-dot, fontsize 11.0 pt, protective bbox)
    draw_vector(ax, (0, 0), vt1_vec, color=COLOR_VELOCITY_1, lw=0.9, mutation_scale=10,
                linestyle="-.", zorder=5)
    ax.text(vt1_vec[0] - 0.40, vt1_vec[1] + 0.10, tr('fig3_vt1'), fontsize=11.0,
            fontweight='normal', color=COLOR_VELOCITY_1,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.90))
    
    draw_vector(ax, (0, 0), vt2_vec, color=COLOR_VELOCITY_2, lw=0.9, mutation_scale=10,
                linestyle="-.", zorder=5)
    ax.text(vt2_vec[0] - 0.38, vt2_vec[1] - 0.20, tr('fig3_vt2'), fontsize=11.0,
            fontweight='normal', color=COLOR_VELOCITY_2,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.90))
    
    # Relative Sliding Velocity Vector (1.3 pt, fontsize 11.0 pt)
    draw_vector(ax, vt2_vec, vt1_vec, color=COLOR_SLIP, lw=1.3, mutation_scale=12, zorder=6)
    ax.text(-1.55, 1.95, tr('fig3_vs'),
            fontsize=11.0, fontweight='normal', color=COLOR_SLIP, ha='right', va='center',
            bbox=dict(boxstyle="round,pad=0.2", fc="#FEF2F2", ec=COLOR_SLIP, lw=0.9, alpha=0.95))
    
    # Contact Point K Marker (65 size, fontsize 12.0 pt)
    ax.scatter([0], [0], color=COLOR_CONTACT, s=65, edgecolor=COLOR_TEXT_MAIN, lw=1.0, zorder=10)
    ax.text(0.12, -0.32, tr('fig3_k'), fontsize=12.0, fontweight='normal', color=COLOR_TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    
    # Summary Box: Header 13pt, Structured 4-line rules (10.2pt, 66.9 px margin guaranteed)
    summary_box = patches.FancyBboxPatch((-4.6, -4.75), 9.2, 2.05, boxstyle="round,pad=0.22",
                                         fc="#F8FAFC", ec=COLOR_AXIS, lw=1.0, zorder=3)
    ax.add_patch(summary_box)
    ax.text(0, -2.95, tr('fig3_summary_title'),
            fontsize=13.0, fontweight='normal', color=COLOR_TEXT_MAIN, ha='center', va='center', zorder=4)
    ax.text(0, -3.55, tr('fig3_rule1'),
            fontsize=10.2, fontweight='normal', color="#1E293B", ha='center', va='center', zorder=4)
    ax.text(0, -4.25, tr('fig3_rule2'),
            fontsize=10.2, fontweight='normal', color="#B91C1C", ha='center', va='center', zorder=4)
    
    ax.set_xlim(-5.0, 5.0)
    ax.set_ylim(-5.35, 3.85)
    title_text = tr('fig3_title')
    if lang in ['de', 'en']:
        title_text = title_text.replace(": ", ":\n")
    ax.set_title(title_text, fontsize=14.5, fontweight='normal', pad=14, color=COLOR_TEXT_MAIN)
    ax.legend(loc="upper left", fontsize=10.5, framealpha=0.95, edgecolor=COLOR_AXIS)
    
    save_diagram(fig, "fig3_contact_velocity_vectors", output_dir, dpi, formats)


# ---------------------------------------------------------------------------
# CLI & Dispatch Pipeline
# ---------------------------------------------------------------------------
FIGURE_DISPATCH_MAP = {
    'all':   ['fig1a', 'fig1b', 'fig2', 'fig3'],
    'fig1':  ['fig1a', 'fig1b'],   # Backward-compatibility alias
    'fig1a': ['fig1a'],
    'fig1b': ['fig1b'],
    'fig2':  ['fig2'],
    'fig3':  ['fig3'],
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate publication-grade engineering diagrams for H-GEAR STUDIO Blog Part 1."
    )
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help="Base output directory for generated SVG/PNG files")
    parser.add_argument("--dpi", type=int, default=300,
                        help="DPI resolution for PNG output (default: 300)")
    parser.add_argument("--lang", type=str, choices=['all', 'ko', 'en', 'de', 'ja'], default='all',
                        help="Language for diagram text (default: all)")
    parser.add_argument("--fig", type=str,
                        choices=['all', 'fig1a', 'fig1b', 'fig2', 'fig3', 'fig1'], default='all',
                        help="Specific figure to generate (fig1 generates both 1a and 1b, default: all)")
    parser.add_argument("--format", type=str, choices=['all', 'png', 'svg'], default='all',
                        help="Export format (default: all)")
    return parser.parse_args()


def main():
    args = parse_args()
    
    target_langs = ['ko', 'en', 'de', 'ja'] if args.lang == 'all' else [args.lang]
    target_figs = FIGURE_DISPATCH_MAP[args.fig]
    base_out_dir = Path(args.output_dir)
    
    print("=" * 76)
    print(" H-GEAR STUDIO Blog Part 1 Multilingual Diagram Pipeline")
    print(f" Target Languages : {target_langs}")
    print(f" Target Figures   : {target_figs} (from arg: {args.fig})")
    print(f" Base Output Dir  : {base_out_dir}")
    print(f" Resolution & Fmt : {args.dpi} DPI, {args.format}")
    print("=" * 76)
    
    total_saved = 0
    for lang in target_langs:
        print(f"\n>>> Applying Typography Profile for [{lang.upper()}]...")
        apply_language_typography(lang)
        
        # Decide output directory per language
        lang_dir = base_out_dir if base_out_dir.name == lang else base_out_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        for fig_key in target_figs:
            if fig_key == 'fig1a':
                create_diagram_1a(lang_dir, dpi=args.dpi, formats=args.format, lang=lang)
                total_saved += 2 if args.format == 'all' else 1
            elif fig_key == 'fig1b':
                create_diagram_1b(lang_dir, dpi=args.dpi, formats=args.format, lang=lang)
                total_saved += 2 if args.format == 'all' else 1
            elif fig_key == 'fig2':
                create_diagram_2(lang_dir, dpi=args.dpi, formats=args.format, lang=lang)
                total_saved += 2 if args.format == 'all' else 1
            elif fig_key == 'fig3':
                create_diagram_3(lang_dir, dpi=args.dpi, formats=args.format, lang=lang)
                total_saved += 2 if args.format == 'all' else 1
            
    print("\n" + "=" * 76)
    print(f" Pipeline execution completed successfully! Generated {total_saved} assets.")
    print("=" * 76)


if __name__ == "__main__":
    main()
