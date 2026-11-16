"""
blog/scripts/export_part4_locales.py
================================================================================
H-GEAR STUDIO: Blog Series 1 Part A Chapter 4 Semantic Locales Generator
Produces 4-language localization dictionaries (KO, EN, DE, JA) for:
  - Fig 1: Rack Cutter Profile Shift & Undercut Elimination
  - Fig 2: Operating Mesh Geometry (Working Center Distance a' & Pressure Angle alpha_w)
  - Fig 3: Specific Sliding Balancing Curves (k1, k2 Along Path of Contact)
  - Benchmark Table: 38 Parameters Closed-Form Precision Table
Standards: ISO 21771, DIN 3960, DIN 3992, AGMA 901-A92, JIS B 1701, KS B 0102
Precision Standard: Authentic native engineering terminology across all 4 locales.
================================================================================
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOCALES_DIR = REPO_ROOT / "blog" / "data" / "locales"

LABELS: Dict[str, Dict[str, str]] = {
    "ko": {
        # --- Fig 1: Rack Cutter Profile Shift & Undercut Elimination ---
        "fig1_title": "그림 1: 랙 커터 전위(Profile Shift)와 언더컷(Undercut) 해소 기하학",
        "fig1_panel_a_title": "부전위 (x = -0.30): 심각한 언더컷 발생 (치근 잘림)",
        "fig1_panel_b_title": "표준 무전위 (x = 0.00): 한계 언더컷 (z1=14 < 17.1)",
        "fig1_panel_c_title": "정전위 (x = +0.35): 언더컷 완전 해소 및 치근 강화",
        "fig1_pitch_point": "피치점 P (순수 구름)",
        "fig1_interference_point": "간섭 한계점 T1 (기초원 접점)",
        "fig1_rack_datum_line": "랙 기준선 (Rack Datum Line)",
        "fig1_pitch_line": "피치선 (Pitch Line)",
        "fig1_undercut_trochoid": "트로코이드 절삭 궤적 (언더컷 노치)",
        "fig1_critical_root_thickness": "치근 위험단면 두께 sF",
        "fig1_base_circle": "기초원 (rb = 19.734 mm)",
        "fig1_tip_circle": "이끝원 (ra)",
        "fig1_root_circle": "이뿌리원 (rf)",
        "fig1_shift_amount": "전위량 x·m",
        "fig1_min_teeth_limit": "언더컷 한계 잇수 z_min = 17.097 ≈ 17",
        "fig1_min_shift_limit": "최소 필요 전위계수 x_min = +0.181",
        "fig1_undercut_depth": "언더컷 침투 깊이 Δh",
        "fig1_summary_title": "[랙 커터 전위와 언더컷 해소 공학 요약]",
        "fig1_summary_1": "(1) 한계 잇수: z_min = 2ha* / sin²(α0) = 17.097 (z1=14 < 17.1 언더컷 필연)",
        "fig1_summary_2": "(2) 최소 전위계수: x_min = 1 - z1·sin²(α0)/2 = +0.181156",
        "fig1_summary_3": "(3) 벤치마크 설계: x1 = +0.350 > +0.181 (언더컷 완전 배제, 치근두께 +44.8% 증대)",
        "fig1_summary_note": "[공학적 의의] 공구를 반경 외측으로 후퇴시켜 치근 절손을 방지하고 굽힘 피로강도를 대폭 향상",

        # --- Fig 2: Operating Mesh Geometry (38 Parameters) ---
        "fig2_title": "그림 2: 전위 기어 쌍의 운전 맞물림 기하학 (중심거리 증가 a' 및 물림 압력각 αw)",
        "fig2_point_t1": "T1 (피니언 기초원 접점)",
        "fig2_point_a": "A (접촉 시작점, SAP)",
        "fig2_point_b": "B (단일 접촉 하한점, LPSTC)",
        "fig2_point_p": "P (운전 피치점, Working Pitch Point)",
        "fig2_point_d": "D (단일 접촉 상한점, HPSTC)",
        "fig2_point_e": "E (접촉 종료점, EAP)",
        "fig2_point_t2": "T2 (대기어 기초원 접점)",
        "fig2_loa_operating": "운전 작용선 (Working Line of Action, αw = 22.463°)",
        "fig2_pitch_tangent": "운전 피치 접선 (Working Pitch Tangent)",
        "fig2_std_pitch_pinion": "피니언 기준 피치원 (d1 = 42.000 mm)",
        "fig2_std_pitch_gear": "대기어 기준 피치원 (d2 = 126.000 mm)",
        "fig2_op_pitch_pinion": "피니언 운전 피치원 (dw1 = 42.707 mm)",
        "fig2_op_pitch_gear": "대기어 운전 피치원 (dw2 = 128.122 mm)",
        "fig2_base_pinion": "피니언 기초원 (db1 = 39.467 mm)",
        "fig2_base_gear": "대기어 기초원 (db2 = 118.401 mm)",
        "fig2_tip_pinion": "피니언 이끝원 (da1 = 49.930 mm)",
        "fig2_tip_gear": "대기어 이끝원 (da2 = 132.730 mm)",
        "fig2_root_pinion": "피니언 이뿌리원 (df1 = 36.600 mm)",
        "fig2_root_gear": "대기어 이뿌리원 (df2 = 119.400 mm)",
        "fig2_dim_ga": "후퇴 물림길이 ga = 7.133 mm",
        "fig2_dim_gf": "접근 물림길이 gf = 5.516 mm",
        "fig2_dim_g_alpha": "실제 접촉 궤적 gα = ga + gf = 12.649 mm",
        "fig2_dim_pb": "기초원 피치 pb = π·m·cos α0 = 8.856 mm",
        "fig2_dim_bd": "단일 치 접촉 구간 BD (g1 = 5.064 mm)",
        "fig2_dim_clearance": "이끝틈새 c = 0.750 mm (엄격 보존, k = 0.028365)",
        "fig2_dim_center_distance": "운전 중심거리 a' = 85.415 mm (Δa = +1.415 mm)",
        "fig2_summary_title": "[전위 기어 쌍 운전 맞물림 기하학 정밀 요약]",
        "fig2_summary_1": "(1) 물림 압력각: inv(αw) = inv(α0) + 2(Σx/Σz)tan(α0) = 0.021404 ➔ αw = 22.462989°",
        "fig2_summary_2": "(2) 중심거리 및 변경계수: a' = 85.415 mm, y = 0.471635, k = 0.028365 (c ≡ 0.750 mm 보존)",
        "fig2_summary_3": "(3) 물림률 및 접촉 비율: εα = 1.428213 ≥ 1.200 (단일 40.0%, 이중 60.0%)",
        "fig2_summary_note": "[공학적 의의] 이끝높이 변경계수 k 적용으로 표준 이끝틈새 c=0.75 mm를 0.000 mm 오차 없이 엄격 보존",

        # --- Fig 3: Specific Sliding Balancing Curves ---
        "fig3_title": "그림 3: 전위계수 배분에 따른 치면 상대 미끄럼률(Specific Sliding) 밸런싱 곡선",
        "fig3_curve_k1": "피니언 미끄럼률 k1 (전위 후: k1A = -2.783, k1E = +0.622)",
        "fig3_curve_k2": "대기어 미끄럼률 k2 (전위 후: k2A = +0.736, k2E = -1.645)",
        "fig3_curve_k1_std": "무전위 피니언 k1 (언더컷 발산: sA < 0)",
        "fig3_point_a": "A (SAP): k1 = -2.783, k2 = +0.736",
        "fig3_point_b": "B (LPSTC): k1 = -0.357, k2 = +0.263",
        "fig3_point_p": "P (피치점): k1 = 0.000, k2 = 0.000 (순수 구름)",
        "fig3_point_d": "D (HPSTC): k1 = +0.387, k2 = -0.632",
        "fig3_point_e": "E (EAP): k1 = +0.622, k2 = -1.645",
        "fig3_axis_s": "작용선 접촉 좌표 s (mm, T1 기준)",
        "fig3_axis_k": "치면 상대 미끄럼률 (Specific Sliding, k)",
        "fig3_pure_rolling": "순수 구름 기준선 (k = 0)",
        "fig3_balancing_ratio": "미끄럼률 밸런싱 비율 |k1A| / |k2E| = 1.692",
        "fig3_summary_title": "[치면 상대 미끄럼률 밸런싱 공학 요약]",
        "fig3_summary_1": "(1) 특이점 미끄럼률: SAP(A) k1=-2.783, EAP(E) k2=-1.645 (양 치근 마모 밸런싱)",
        "fig3_summary_2": "(2) 대칭 항등식: 전 구간 (1 - k1)(1 - k2) ≡ 1.000000 성립 확인",
        "fig3_summary_3": "(3) 무전위 대비 개선: 무전위 시 sA < 0 침범 발산 ➔ 전위 후 건전 구간 안착",
        "fig3_summary_note": "[공학적 의의] 잇수비 3:1 기어 쌍에서 피니언에 전위를 집중 배분하여 국부 치면 소착 및 마모 균일화",

        # --- Benchmark Proportions Table Headers ---
        "table_title": "표 1: 전위 평치차 쌍 38개 파라미터 폐쇄형 정밀 계산표",
        "col_no": "번호",
        "col_name": "파라미터 명칭",
        "col_symbol": "기호",
        "col_formula": "산출 공식",
        "col_value": "계산값 (6자리)",
        "col_unit": "단위",
        "table_summary_note": "[검증 완료] 38개 파라미터 전수 미분기하학 닫힌 해 수식 0.000000 mm 무결함 입증"
    },

    "en": {
        # --- Fig 1: Rack Cutter Profile Shift & Undercut Elimination ---
        "fig1_title": "Fig 1: Rack Cutter Profile Shift and Undercut Elimination Geometry",
        "fig1_panel_a_title": "Negative Shift (x = -0.30): Severe Undercut (Root Weakened)",
        "fig1_panel_b_title": "Standard Zero Shift (x = 0.00): Incipient Undercut (z1=14 < 17.1)",
        "fig1_panel_c_title": "Positive Shift (x = +0.35): Undercut Eliminated & Root Strengthened",
        "fig1_pitch_point": "Pitch Point P (Pure Rolling)",
        "fig1_interference_point": "Interference Limit Point T1 (Base Circle Tangency)",
        "fig1_rack_datum_line": "Rack Datum Line",
        "fig1_pitch_line": "Pitch Line",
        "fig1_undercut_trochoid": "Trochoidal Root Trajectory (Undercut Notch)",
        "fig1_critical_root_thickness": "Critical Tooth Root Thickness sF",
        "fig1_base_circle": "Base Circle (rb = 19.734 mm)",
        "fig1_tip_circle": "Tip Circle (ra)",
        "fig1_root_circle": "Root Circle (rf)",
        "fig1_shift_amount": "Shift Amount x·m",
        "fig1_min_teeth_limit": "Undercut Limit Teeth z_min = 17.097 ≈ 17",
        "fig1_min_shift_limit": "Min Required Shift Coefficient x_min = +0.181",
        "fig1_undercut_depth": "Undercut Interference Depth Δh",
        "fig1_summary_title": "[Summary: Rack Cutter Shift & Undercut Elimination Mechanics]",
        "fig1_summary_1": "(1) Limit Teeth: z_min = 2ha* / sin²(α0) = 17.097 (z1=14 < 17.1 undercut inevitable)",
        "fig1_summary_2": "(2) Min Shift Coefficient: x_min = 1 - z1·sin²(α0)/2 = +0.181156",
        "fig1_summary_3": "(3) Benchmark Design: x1 = +0.350 > +0.181 (Undercut eliminated, root thickness +44.8%)",
        "fig1_summary_note": "[Engineering Significance] Retracting the cutter radially outward prevents root cutting and enhances bending fatigue strength",

        # --- Fig 2: Operating Mesh Geometry (38 Parameters) ---
        "fig2_title": "Fig 2: Operating Mesh Geometry of Profile-Shifted Gear Pair (Working Center Distance a' & Pressure Angle αw)",
        "fig2_point_t1": "T1 (Pinion Base Circle Tangency)",
        "fig2_point_a": "A (Start of Active Profile, SAP)",
        "fig2_point_b": "B (Lowest Point Single Contact, LPSTC)",
        "fig2_point_p": "P (Operating Pitch Point, Pure Rolling)",
        "fig2_point_d": "D (Highest Point Single Contact, HPSTC)",
        "fig2_point_e": "E (End of Active Profile, EAP)",
        "fig2_point_t2": "T2 (Gear Base Circle Tangency)",
        "fig2_loa_operating": "Operating Line of Action (Working LOA, αw = 22.463°)",
        "fig2_pitch_tangent": "Working Pitch Tangent",
        "fig2_std_pitch_pinion": "Pinion Standard Pitch Circle (d1 = 42.000 mm)",
        "fig2_std_pitch_gear": "Gear Standard Pitch Circle (d2 = 126.000 mm)",
        "fig2_op_pitch_pinion": "Pinion Operating Pitch Circle (dw1 = 42.707 mm)",
        "fig2_op_pitch_gear": "Gear Operating Pitch Circle (dw2 = 128.122 mm)",
        "fig2_base_pinion": "Pinion Base Circle (db1 = 39.467 mm)",
        "fig2_base_gear": "Gear Base Circle (db2 = 118.401 mm)",
        "fig2_tip_pinion": "Pinion Tip Circle (da1 = 49.930 mm)",
        "fig2_tip_gear": "Gear Tip Circle (da2 = 132.730 mm)",
        "fig2_root_pinion": "Pinion Root Circle (df1 = 36.600 mm)",
        "fig2_root_gear": "Gear Root Circle (df2 = 119.400 mm)",
        "fig2_dim_ga": "Recess Path ga = 7.133 mm",
        "fig2_dim_gf": "Approach Path gf = 5.516 mm",
        "fig2_dim_g_alpha": "Total Active Contact Path gα = ga + gf = 12.649 mm",
        "fig2_dim_pb": "Base Pitch pb = π·m·cos α0 = 8.856 mm",
        "fig2_dim_bd": "Single Contact Zone BD (g1 = 5.064 mm)",
        "fig2_dim_clearance": "Bottom Clearance c = 0.750 mm (Strictly Preserved, k = 0.028365)",
        "fig2_dim_center_distance": "Operating Center Distance a' = 85.415 mm (Δa = +1.415 mm)",
        "fig2_summary_title": "[Summary: Operating Mesh Geometry & Contact Mechanics]",
        "fig2_summary_1": "(1) Working Pressure Angle: inv(αw) = inv(α0) + 2(Σx/Σz)tan(α0) = 0.021404 ➔ αw = 22.462989°",
        "fig2_summary_2": "(2) Center Distance & Modification: a' = 85.415 mm, y = 0.471635, k = 0.028365 (c ≡ 0.750 mm preserved)",
        "fig2_summary_3": "(3) Contact Ratio & Zones: εα = 1.428213 ≥ 1.200 (Single 40.0%, Double 60.0%)",
        "fig2_summary_note": "[Engineering Significance] Applying addendum modification factor k preserves nominal bottom clearance c=0.75 mm with zero error",

        # --- Fig 3: Specific Sliding Balancing Curves ---
        "fig3_title": "Fig 3: Specific Sliding Balancing Curves Along Path of Contact",
        "fig3_curve_k1": "Pinion Specific Sliding k1 (Shifted: k1A = -2.783, k1E = +0.622)",
        "fig3_curve_k2": "Gear Specific Sliding k2 (Shifted: k2A = +0.736, k2E = -1.645)",
        "fig3_curve_k1_std": "Unshifted Pinion k1 (Diverges in Undercut: sA < 0)",
        "fig3_point_a": "A (SAP): k1 = -2.783, k2 = +0.736",
        "fig3_point_b": "B (LPSTC): k1 = -0.357, k2 = +0.263",
        "fig3_point_p": "P (Pitch Point): k1 = 0.000, k2 = 0.000 (Pure Rolling)",
        "fig3_point_d": "D (HPSTC): k1 = +0.387, k2 = -0.632",
        "fig3_point_e": "E (EAP): k1 = +0.622, k2 = -1.645",
        "fig3_axis_s": "Contact Path Coordinate s (mm, from T1)",
        "fig3_axis_k": "Specific Sliding (k)",
        "fig3_pure_rolling": "Pure Rolling Baseline (k = 0)",
        "fig3_balancing_ratio": "Specific Sliding Balancing Ratio |k1A| / |k2E| = 1.692",
        "fig3_summary_title": "[Summary: Specific Sliding Balancing & Wear Equalization]",
        "fig3_summary_1": "(1) Singular Sliding Values: SAP(A) k1=-2.783, EAP(E) k2=-1.645 (Balanced root sliding wear)",
        "fig3_summary_2": "(2) Complementary Identity: (1 - k1)(1 - k2) ≡ 1.000000 strictly maintained everywhere",
        "fig3_summary_3": "(3) Improvement Over Standard: Unshifted sA < 0 divergence eliminated, safely seated on sound profile",
        "fig3_summary_note": "[Engineering Significance] Strategic shift allocation for 3:1 ratio equalizes scuffing risk and achieves uniform flank wear",

        # --- Benchmark Proportions Table Headers ---
        "table_title": "Table 1: 38 Parameters Closed-Form Precision Table for Profile-Shifted Spur Gear Pair",
        "col_no": "No.",
        "col_name": "Parameter Name",
        "col_symbol": "Symbol",
        "col_formula": "Derivation Formula",
        "col_value": "Calculated Value (6 Digits)",
        "col_unit": "Unit",
        "table_summary_note": "[Verified] All 38 parameters proven exact to 0.000000 mm via differential geometry closed-form equations"
    },

    "de": {
        # --- Fig 1: Rack Cutter Profile Shift & Undercut Elimination ---
        "fig1_title": "Abb. 1: Profilverschiebung des Bezugsprofils und Geometrie der Unterschnittvermeidung",
        "fig1_panel_a_title": "Negative Profilverschiebung (x = -0.30): Schwerer Unterschnitt (Zahnfuß geschwächt)",
        "fig1_panel_b_title": "Ohne Profilverschiebung (x = 0.00): Grenzunterschnitt (z1=14 < 17.1)",
        "fig1_panel_c_title": "Positive Profilverschiebung (x = +0.35): Unterschnittfrei & Zahnfuß verstärkt",
        "fig1_pitch_point": "Wälzpunkt P (Reines Rollen)",
        "fig1_interference_point": "Eingriffsgrenzpunkt T1 (Grundkreisberührung)",
        "fig1_rack_datum_line": "Werkzeug-Bezugslinie (Datum Line)",
        "fig1_pitch_line": "Wälzlinie (Pitch Line)",
        "fig1_undercut_trochoid": "Trochoidale Fußrundung (Unterschnittkerbe)",
        "fig1_critical_root_thickness": "Kritische Zahnfußdicke sF",
        "fig1_base_circle": "Grundkreis (rb = 19.734 mm)",
        "fig1_tip_circle": "Kopfkreis (ra)",
        "fig1_root_circle": "Fußkreis (rf)",
        "fig1_shift_amount": "Profilverschiebungsbetrag x·m",
        "fig1_min_teeth_limit": "Grenzzähnezahl z_min = 17.097 ≈ 17",
        "fig1_min_shift_limit": "Mindestprofilverschiebung x_min = +0.181",
        "fig1_undercut_depth": "Unterschnitt-Eingriffstiefe Δh",
        "fig1_summary_title": "[Zusammenfassung: Profilverschiebung & Unterschnittmechanik]",
        "fig1_summary_1": "(1) Grenzzähnezahl: z_min = 2ha* / sin²(α0) = 17.097 (z1=14 < 17.1 Unterschnitt unvermeidlich)",
        "fig1_summary_2": "(2) Mindestverschiebung: x_min = 1 - z1·sin²(α0)/2 = +0.181156",
        "fig1_summary_3": "(3) Benchmark-Auslegung: x1 = +0.350 > +0.181 (Vollständig unterschnittfrei, Fußdicke +44.8%)",
        "fig1_summary_note": "[Ingenieurmäßige Bedeutung] Radiales Zurückziehen des Werkzeugs verhindert Fußunterhöhlung und steigert die Biegefestigkeit",

        # --- Fig 2: Operating Mesh Geometry (38 Parameters) ---
        "fig2_title": "Abb. 2: Eingriffsgeometrie des profilverschobenen Stirnradpaares (Betriebsachsabstand a' & Betriebseingriffswinkel αw)",
        "fig2_point_t1": "T1 (Grundkreis Ritzel Berührung)",
        "fig2_point_a": "A (Eingriffsbeginn, SAP)",
        "fig2_point_b": "B (Unterer Einzeleingriffspunkt, LPSTC)",
        "fig2_point_p": "P (Betriebswälzpunkt, Reines Rollen)",
        "fig2_point_d": "D (Oberer Einzeleingriffspunkt, HPSTC)",
        "fig2_point_e": "E (Eingriffsende, EAP)",
        "fig2_point_t2": "T2 (Grundkreis Rad Berührung)",
        "fig2_loa_operating": "Betriebseingriffslinie (αw = 22.463°)",
        "fig2_pitch_tangent": "Betriebswälztangente",
        "fig2_std_pitch_pinion": "Ritzel Teilkreis (d1 = 42.000 mm)",
        "fig2_std_pitch_gear": "Rad Teilkreis (d2 = 126.000 mm)",
        "fig2_op_pitch_pinion": "Ritzel Betriebswälzkreis (dw1 = 42.707 mm)",
        "fig2_op_pitch_gear": "Rad Betriebswälzkreis (dw2 = 128.122 mm)",
        "fig2_base_pinion": "Ritzel Grundkreis (db1 = 39.467 mm)",
        "fig2_base_gear": "Rad Grundkreis (db2 = 118.401 mm)",
        "fig2_tip_pinion": "Ritzel Kopfkreis (da1 = 49.930 mm)",
        "fig2_tip_gear": "Rad Kopfkreis (da2 = 132.730 mm)",
        "fig2_root_pinion": "Ritzel Fußkreis (df1 = 36.600 mm)",
        "fig2_root_gear": "Rad Fußkreis (df2 = 119.400 mm)",
        "fig2_dim_ga": "Rückwegeingriffsstrecke ga = 7.133 mm",
        "fig2_dim_gf": "Vorwegeingriffsstrecke gf = 5.516 mm",
        "fig2_dim_g_alpha": "Gesamte Eingriffsstrecke gα = ga + gf = 12.649 mm",
        "fig2_dim_pb": "Grundkreisteilung pb = π·m·cos α0 = 8.856 mm",
        "fig2_dim_bd": "Einzeleingriffsstrecke BD (g1 = 5.064 mm)",
        "fig2_dim_clearance": "Kopfspiel c = 0.750 mm (Exakt erhalten, k = 0.028365)",
        "fig2_dim_center_distance": "Betriebsachsabstand a' = 85.415 mm (Δa = +1.415 mm)",
        "fig2_summary_title": "[Zusammenfassung: Eingriffsgeometrie & Kontaktmechanik]",
        "fig2_summary_1": "(1) Betriebseingriffswinkel: inv(αw) = inv(α0) + 2(Σx/Σz)tan(α0) = 0.021404 ➔ αw = 22.462989°",
        "fig2_summary_2": "(2) Achsabstand & Kopfkürzung: a' = 85.415 mm, y = 0.471635, k = 0.028365 (c ≡ 0.750 mm erhalten)",
        "fig2_summary_3": "(3) Profilüberdeckung: εα = 1.428213 ≥ 1.200 (Einzeleingriff 40.0%, Doppeleingriff 60.0%)",
        "fig2_summary_note": "[Ingenieurmäßige Bedeutung] Anwendung des Kopfkürzungsfaktors k bewahrt das Nenn-Kopfspiel c=0.75 mm ohne Abweichung",

        # --- Fig 3: Specific Sliding Balancing Curves ---
        "fig3_title": "Abb. 3: Ausgleich des spezifischen Gleitens entlang der Eingriffsstrecke durch Profilverschiebung",
        "fig3_curve_k1": "Spezifisches Gleiten Ritzel k1 (Verschoben: k1A = -2.783, k1E = +0.622)",
        "fig3_curve_k2": "Spezifisches Gleiten Rad k2 (Verschoben: k2A = +0.736, k2E = -1.645)",
        "fig3_curve_k1_std": "Unverschobenes Ritzel k1 (Divergiert im Unterschnitt: sA < 0)",
        "fig3_point_a": "A (SAP): k1 = -2.783, k2 = +0.736",
        "fig3_point_b": "B (LPSTC): k1 = -0.357, k2 = +0.263",
        "fig3_point_p": "P (Wälzpunkt): k1 = 0.000, k2 = 0.000 (Reines Rollen)",
        "fig3_point_d": "D (HPSTC): k1 = +0.387, k2 = -0.632",
        "fig3_point_e": "E (EAP): k1 = +0.622, k2 = -1.645",
        "fig3_axis_s": "Eingriffsstreckenkoordinate s (mm, ab T1)",
        "fig3_axis_k": "Spezifisches Gleiten (k)",
        "fig3_pure_rolling": "Nulllinie des reinen Rollens (k = 0)",
        "fig3_balancing_ratio": "Ausgleichsverhältnis des Gleitens |k1A| / |k2E| = 1.692",
        "fig3_summary_title": "[Zusammenfassung: Gleitausgleich & Verschleißharmonisierung]",
        "fig3_summary_1": "(1) Singuläre Gleitwerte: SAP(A) k1=-2.783, EAP(E) k2=-1.645 (Harmonisierter Fußgleitverschleiß)",
        "fig3_summary_2": "(2) Komplementäre Identität: (1 - k1)(1 - k2) ≡ 1.000000 im gesamten Verlauf exakt erfüllt",
        "fig3_summary_3": "(3) Verbesserung gegenüber Standard: Unterschnittbedingte Divergenz eliminiert, sichere Lage auf der Flanke",
        "fig3_summary_note": "[Ingenieurmäßige Bedeutung] Gezielte Profilverschiebungsaufteilung bei 3:1 Übersetzung minimiert Fressneigung",

        # --- Benchmark Proportions Table Headers ---
        "table_title": "Tabelle 1: 38 Parameter geschlossene Präzisionsberechnungstabelle für profilverschobene Stirnradpaarung",
        "col_no": "Nr.",
        "col_name": "Parameterbezeichnung",
        "col_symbol": "Symbol",
        "col_formula": "Berechnungsformel",
        "col_value": "Berechneter Wert (6 Dezimalstellen)",
        "col_unit": "Einheit",
        "table_summary_note": "[Geprüft] Alle 38 Parameter analytisch geschlossen mit 0.000000 mm Fehlerfreiheit nachgewiesen"
    },

    "ja": {
        # --- Fig 1: Rack Cutter Profile Shift & Undercut Elimination ---
        "fig1_title": "図1: ラックカッタ転位(Profile Shift)とアンダーカット(Undercut)解消の幾何学",
        "fig1_panel_a_title": "負転位 (x = -0.30): 深刻なアンダーカット発生 (歯元強度低下)",
        "fig1_panel_b_title": "標準無転位 (x = 0.00): 限界アンダーカット (z1=14 < 17.1)",
        "fig1_panel_c_title": "正転位 (x = +0.35): アンダーカット完全解消および歯元強化",
        "fig1_pitch_point": "ピッチ点 P (純粋転がり)",
        "fig1_interference_point": "干渉限界点 T1 (基礎円接点)",
        "fig1_rack_datum_line": "ラック基準線 (Datum Line)",
        "fig1_pitch_line": "ピッチ線 (Pitch Line)",
        "fig1_undercut_trochoid": "トロコイド切削軌跡 (アンダーカットノッチ)",
        "fig1_critical_root_thickness": "歯元危険断面厚さ sF",
        "fig1_base_circle": "基礎円 (rb = 19.734 mm)",
        "fig1_tip_circle": "歯先円 (ra)",
        "fig1_root_circle": "歯底円 (rf)",
        "fig1_shift_amount": "転位量 x·m",
        "fig1_min_teeth_limit": "アンダーカット限界歯数 z_min = 17.097 ≈ 17",
        "fig1_min_shift_limit": "最小必要転位係数 x_min = +0.181",
        "fig1_undercut_depth": "干渉切込み深さ Δh",
        "fig1_summary_title": "[ラックカッタ転位とアンダーカット解消工学要約]",
        "fig1_summary_1": "(1) 限界歯数: z_min = 2ha* / sin²(α0) = 17.097 (z1=14 < 17.1 でアンダーカット必然)",
        "fig1_summary_2": "(2) 最小転位係数: x_min = 1 - z1·sin²(α0)/2 = +0.181156",
        "fig1_summary_3": "(3) ベンチマーク設計: x1 = +0.350 > +0.181 (アンダーカット完全排除、歯元厚さ +44.8% 増大)",
        "fig1_summary_note": "[工学的意義] 工具を半径方向外側に後退させ歯元の切り欠きを防止、曲げ疲労強度を大幅向上",

        # --- Fig 2: Operating Mesh Geometry (38 Parameters) ---
        "fig2_title": "図2: 転位歯車対の運転噛み合い幾何学 (中心距離増加 a' および噛み合い圧力角 αw)",
        "fig2_point_t1": "T1 (ピニオン基礎円接点)",
        "fig2_point_a": "A (噛み合い開始点, SAP)",
        "fig2_point_b": "B (単一接触下限点, LPSTC)",
        "fig2_point_p": "P (運転ピッチ点, Working Pitch Point)",
        "fig2_point_d": "D (単一接触上限点, HPSTC)",
        "fig2_point_e": "E (噛み合い終了点, EAP)",
        "fig2_point_t2": "T2 (大歯車基礎円接点)",
        "fig2_loa_operating": "運転作用線 (Working Line of Action, αw = 22.463°)",
        "fig2_pitch_tangent": "運転ピッチ接線 (Working Pitch Tangent)",
        "fig2_std_pitch_pinion": "ピニオン基準ピッチ円 (d1 = 42.000 mm)",
        "fig2_std_pitch_gear": "大歯車基準ピッチ円 (d2 = 126.000 mm)",
        "fig2_op_pitch_pinion": "ピニオン運転ピッチ円 (dw1 = 42.707 mm)",
        "fig2_op_pitch_gear": "大歯車運転ピッチ円 (dw2 = 128.122 mm)",
        "fig2_base_pinion": "ピニオン基礎円 (db1 = 39.467 mm)",
        "fig2_base_gear": "大歯車基礎円 (db2 = 118.401 mm)",
        "fig2_tip_pinion": "ピニオン歯先円 (da1 = 49.930 mm)",
        "fig2_tip_gear": "大歯車歯先円 (da2 = 132.730 mm)",
        "fig2_root_pinion": "ピニオン歯底円 (df1 = 36.600 mm)",
        "fig2_root_gear": "大歯車歯底円 (df2 = 119.400 mm)",
        "fig2_dim_ga": "後退噛み合い長さ ga = 7.133 mm",
        "fig2_dim_gf": "接近噛み合い長さ gf = 5.516 mm",
        "fig2_dim_g_alpha": "全有効噛み合い長さ gα = ga + gf = 12.649 mm",
        "fig2_dim_pb": "基礎円ピッチ pb = π·m·cos α0 = 8.856 mm",
        "fig2_dim_bd": "単一歯接触区間 BD (g1 = 5.064 mm)",
        "fig2_dim_clearance": "頂隙 c = 0.750 mm (厳格保持, k = 0.028365)",
        "fig2_dim_center_distance": "運転中心距離 a' = 85.415 mm (Δa = +1.415 mm)",
        "fig2_summary_title": "[転位歯車対運転噛み合い幾何学精密要約]",
        "fig2_summary_1": "(1) 噛み合い圧力角: inv(αw) = inv(α0) + 2(Σx/Σz)tan(α0) = 0.021404 ➔ αw = 22.462989°",
        "fig2_summary_2": "(2) 中心距離と変更係数: a' = 85.415 mm, y = 0.471635, k = 0.028365 (c ≡ 0.750 mm保持)",
        "fig2_summary_3": "(3) 全かみ合い率: εα = 1.428213 ≥ 1.200 (単一接触 40.0%, 複接触 60.0%)",
        "fig2_summary_note": "[工学的意義] 歯先短縮係数 k の適用により標準頂隙 c=0.75 mm を誤差 0.000 mm で厳格保持",

        # --- Fig 3: Specific Sliding Balancing Curves ---
        "fig3_title": "図3: 転位係数配分に伴う歯面比滑り(Specific Sliding)バランシング曲線",
        "fig3_curve_k1": "ピニオン比滑り k1 (転位後: k1A = -2.783, k1E = +0.622)",
        "fig3_curve_k2": "大歯車比滑り k2 (転位後: k2A = +0.736, k2E = -1.645)",
        "fig3_curve_k1_std": "無転位ピニオン k1 (アンダーカット発散: sA < 0)",
        "fig3_point_a": "A (SAP): k1 = -2.783, k2 = +0.736",
        "fig3_point_b": "B (LPSTC): k1 = -0.357, k2 = +0.263",
        "fig3_point_p": "P (ピッチ点): k1 = 0.000, k2 = 0.000 (純粋転がり)",
        "fig3_point_d": "D (HPSTC): k1 = +0.387, k2 = -0.632",
        "fig3_point_e": "E (EAP): k1 = +0.622, k2 = -1.645",
        "fig3_axis_s": "作用線接触座標 s (mm, T1基準)",
        "fig3_axis_k": "歯面比滑り (Specific Sliding, k)",
        "fig3_pure_rolling": "純粋転がり基準線 (k = 0)",
        "fig3_balancing_ratio": "比滑りバランス比率 |k1A| / |k2E| = 1.692",
        "fig3_summary_title": "[歯面比滑りバランシング工学要約]",
        "fig3_summary_1": "(1) 特異点比滑り: SAP(A) k1=-2.783, EAP(E) k2=-1.645 (歯元摩耗の均等化)",
        "fig3_summary_2": "(2) 相補恒等式: 全区間で (1 - k1)(1 - k2) ≡ 1.000000 が成立",
        "fig3_summary_3": "(3) 標準無転位対比改善: 無転位時の sA < 0 侵入発散を排除、健全歯面に完全着座",
        "fig3_summary_note": "[工学的意義] 歯数比 3:1 歯車対でピニオンに転位を集中配分し耐スコーリング性向上と均一摩耗を達成",

        # --- Benchmark Proportions Table Headers ---
        "table_title": "表1: 転位平歯車対38個パラメータ閉形式精密計算表",
        "col_no": "番号",
        "col_name": "パラメータ名称",
        "col_symbol": "記号",
        "col_formula": "算出公式",
        "col_value": "計算値 (6桁)",
        "col_unit": "単位",
        "table_summary_note": "[検証完了] 全38個パラメータが微分幾何学閉形式数式により0.000000 mm無欠陥であることを立証"
    }
}


def export_all_locales(locales_dir: Path, lang_choice: str = "all", indent: int = 2) -> None:
    """Exports Part 4 localized dictionary JSON files."""
    langs = ["ko", "en", "de", "ja"] if lang_choice == "all" else [lang_choice]

    for lang in langs:
        lang_dir = locales_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        dict_data = LABELS[lang]

        # 1. Unified part4_labels.json
        unified_path = lang_dir / "part4_labels.json"
        with open(unified_path, "w", encoding="utf-8") as f:
            json.dump(dict_data, f, indent=indent, ensure_ascii=False)
        print(f"  [SAVED] {unified_path} ({len(dict_data)} keys, {unified_path.stat().st_size:,} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Export Part 4 Semantic Locales Dictionaries")
    parser.add_argument("--lang", choices=["all", "ko", "en", "de", "ja"], default="all",
                        help="Specify language to export")
    parser.add_argument("--indent", type=int, default=2, help="JSON formatting indentation")
    args = parser.parse_args()

    print("=" * 80)
    print("  H-GEAR STUDIO: Exporting Part 4 Multi-Language Semantic Dictionaries")
    print("=" * 80)
    export_all_locales(LOCALES_DIR, lang_choice=args.lang, indent=args.indent)
    print("=" * 80)
    print("  100% LOCALES EXPORT COMPLETE.")
    print("=" * 80)


if __name__ == "__main__":
    main()
