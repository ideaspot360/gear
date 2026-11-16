"""
Export Geometry Specification for Gear Technical Diagrams (Phase 1: Fig 4 Pilot).
Computes exact closed-form benchmark geometry (0.000000 mm precision)
and serializes to JSON according to gear_diagram_spec.schema.json.
"""

import json
import math
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "blog" / "data"
SPECS_DIR = DATA_DIR / "specs"
LOCALES_DIR = DATA_DIR / "locales"


def compute_fig4_spec():
    """
    Computes exact geometry for Fig 4: Line of Action, Path of Contact & Contact Ratio.
    Standard spur gear pair: m=3.0, z1=19, z2=47, alpha=20 deg, a=99.0 mm.
    """
    m = 3.0
    z1 = 19
    z2 = 47
    alpha_deg = 20.0
    alpha_rad = math.radians(alpha_deg)

    # Standard pitch and base radii
    r1 = 0.5 * m * z1            # 28.5 mm (Pinion pitch radius)
    r2 = 0.5 * m * z2            # 70.5 mm (Gear pitch radius)
    a = r1 + r2                  # 99.0 mm (Center distance)
    rb1 = r1 * math.cos(alpha_rad) # 26.781216 mm
    rb2 = r2 * math.cos(alpha_rad) # 66.248261 mm
    ra1 = r1 + 1.0 * m           # 31.5 mm (Pinion tip radius)
    ra2 = r2 + 1.0 * m           # 73.5 mm (Gear tip radius)
    rf1 = r1 - 1.25 * m          # 24.75 mm
    rf2 = r2 - 1.25 * m          # 66.75 mm

    # Closed-form contact lengths
    gf = math.sqrt(ra2**2 - rb2**2) - rb2 * math.tan(alpha_rad)  # 7.721662 mm (AP, approach)
    ga = math.sqrt(ra1**2 - rb1**2) - rb1 * math.tan(alpha_rad)  # 6.836008 mm (PE, recess)
    g_alpha = gf + ga                                            # 14.557670 mm (AE, total active path)
    pb = math.pi * m * math.cos(alpha_rad)                       # 8.856394 mm (Base pitch)
    eps_alpha = g_alpha / pb                                     # 1.643747 (Transverse contact ratio)

    # Unit vectors for line of action (LOA)
    # Pitch point P is at origin (0, 0)
    # LOA runs downwards from top-left (Pinion side) to bottom-right (Gear side)
    cos_a = math.cos(alpha_rad)
    sin_a = math.sin(alpha_rad)
    u_loa = [cos_a, -sin_a]      # Along line of action
    norm_loa = [sin_a, cos_a]    # Perpendicular to line of action (upwards-left)

    # Tangency points on base circles (N1 on pinion base circle, N2 on gear base circle)
    t_N1 = -r1 * sin_a           # -9.747594 mm
    t_N2 = r2 * sin_a            # +24.112469 mm
    N1 = [t_N1 * u_loa[0], t_N1 * u_loa[1]]
    N2 = [t_N2 * u_loa[0], t_N2 * u_loa[1]]

    # Contact limits on LOA (t parameter where point = t * u_loa)
    t_A = -gf                    # -7.721662 mm (SAP: Gear 2 tip circle intersection)
    t_E = ga                     # +6.836008 mm (EAP: Pinion 1 tip circle intersection)
    A = [t_A * u_loa[0], t_A * u_loa[1]]
    E = [t_E * u_loa[0], t_E * u_loa[1]]

    # Single-tooth contact limits (LPSTC: B, HPSTC: D)
    t_B = ga - pb                # -2.020386 mm (Point B: LPSTC)
    t_D = -gf + pb               # +1.134732 mm (Point D: HPSTC)
    B = [t_B * u_loa[0], t_B * u_loa[1]]
    D = [t_D * u_loa[0], t_D * u_loa[1]]
    P = [0.0, 0.0]

    # Contact length segments
    g1 = t_D - t_B               # 3.155118 mm (Single contact BD)
    g2_approach = t_B - t_A      # 5.701276 mm (Double contact AB)
    g2_recess = t_E - t_D        # 5.701276 mm (Double contact DE)
    g2_total = g2_approach + g2_recess # 11.402552 mm

    # Gear centers (P is at (0, 0))
    # Pinion 1 is at (0, +r1), Gear 2 is at (0, -r2)
    O1 = [0.0, r1]
    O2 = [0.0, -r2]

    spec = {
        "schema_version": "1.0.0",
        "diagram_id": "fig4_line_of_action_contact_path",
        "title_key": "fig4_title",
        "parameters": {
            "module": m,
            "z1": z1,
            "z2": z2,
            "alpha_deg": alpha_deg,
            "center_distance": a,
            "r1": r1,
            "r2": r2,
            "rb1": round(rb1, 6),
            "rb2": round(rb2, 6),
            "ra1": ra1,
            "ra2": ra2,
            "rf1": rf1,
            "rf2": rf2,
            "gf": round(gf, 6),
            "ga": round(ga, 6),
            "g_alpha": round(g_alpha, 6),
            "pb": round(pb, 6),
            "g1": round(g1, 6),
            "g2_total": round(g2_total, 6),
            "contact_ratio_transverse": round(eps_alpha, 6),
            "ratio_single_percent": round((g1 / g_alpha) * 100.0, 1),
            "ratio_double_percent": round((g2_total / g_alpha) * 100.0, 1)
        },
        "viewport": {
            "x_min": -32.0,
            "x_max": 34.0,
            "y_min": -22.0,
            "y_max": 24.0,
            "aspect_ratio": "equal"
        },
        "landmarks": {
            "N1": {
                "coord": [round(N1[0], 6), round(N1[1], 6)],
                "t": round(t_N1, 6),
                "label_key": "fig4_point_n1",
                "preferred_side": "west",
                "marker_style": "square",
                "color_role": "base_circle"
            },
            "ra2_arc": {
                "coord": [-14.0, round(-r2 + math.sqrt(ra2**2 - (-14.0)**2), 6)],
                "label_key": "fig4_gear_tip",
                "preferred_side": "west",
                "marker_style": "arrow_to_curve",
                "target_curve": "tip_circle_gear",
                "color_role": "gear"
            },
            "A": {
                "coord": [round(A[0], 6), round(A[1], 6)],
                "t": round(t_A, 6),
                "label_key": "fig4_point_a",
                "preferred_side": "west",
                "marker_style": "circle",
                "color_role": "contact_point"
            },
            "loa_label": {
                "coord": [-24.0, 12.0],
                "label_key": "fig4_loa",
                "preferred_side": "west",
                "marker_style": "none",
                "color_role": "action_line"
            },
            "B": {
                "coord": [round(B[0], 6), round(B[1], 6)],
                "t": round(t_B, 6),
                "label_key": "fig4_point_b",
                "preferred_side": "north_west",
                "marker_style": "circle",
                "color_role": "contact_limit"
            },
            "P": {
                "coord": [0.0, 0.0],
                "t": 0.0,
                "label_key": "fig4_point_p",
                "preferred_side": "south",
                "marker_style": "circle",
                "color_role": "pitch_point"
            },
            "D": {
                "coord": [round(D[0], 6), round(D[1], 6)],
                "t": round(t_D, 6),
                "label_key": "fig4_point_d",
                "preferred_side": "north_east",
                "marker_style": "circle",
                "color_role": "contact_limit"
            },
            "ra1_arc": {
                "coord": [14.0, round(r1 - math.sqrt(ra1**2 - 14.0**2), 6)],
                "label_key": "fig4_pinion_tip",
                "preferred_side": "east",
                "marker_style": "arrow_to_curve",
                "target_curve": "tip_circle_pinion",
                "color_role": "pinion"
            },
            "pitch_tangent_label": {
                "coord": [28.0, 0.5],
                "label_key": "fig4_pitch_line",
                "preferred_side": "east",
                "marker_style": "none",
                "color_role": "pitch_line"
            },
            "E": {
                "coord": [round(E[0], 6), round(E[1], 6)],
                "t": round(t_E, 6),
                "label_key": "fig4_point_e",
                "preferred_side": "east",
                "marker_style": "circle",
                "color_role": "contact_point"
            },
            "N2": {
                "coord": [round(N2[0], 6), round(N2[1], 6)],
                "t": round(t_N2, 6),
                "label_key": "fig4_point_n2",
                "preferred_side": "east",
                "marker_style": "square",
                "color_role": "base_circle"
            }
        },
        "curves": {
            "line_of_action": {
                "type": "segment",
                "start": [round((t_N1 - 2.5) * u_loa[0], 6), round((t_N1 - 2.5) * u_loa[1], 6)],
                "end": [round((t_N2 + 2.5) * u_loa[0], 6), round((t_N2 + 2.5) * u_loa[1], 6)],
                "style": "solid",
                "color_role": "action_line",
                "stroke_width": 1.4
            },
            "pitch_tangent": {
                "type": "segment",
                "start": [-28.0, 0.0],
                "end": [30.0, 0.0],
                "style": "dashed",
                "color_role": "pitch_line",
                "stroke_width": 0.9
            },
            "line_of_centers": {
                "type": "segment",
                "start": [0.0, -8.0],
                "end": [0.0, 8.0],
                "style": "dashdot",
                "color_role": "axis_line",
                "stroke_width": 0.8
            },
            "tip_circle_gear": {
                "type": "arc",
                "center": O2,
                "radius": ra2,
                "start_angle_deg": 75.0,
                "end_angle_deg": 105.0,
                "style": "solid",
                "color_role": "gear_body",
                "stroke_width": 1.2
            },
            "tip_circle_pinion": {
                "type": "arc",
                "center": O1,
                "radius": ra1,
                "start_angle_deg": 255.0,
                "end_angle_deg": 305.0,
                "style": "solid",
                "color_role": "pinion_body",
                "stroke_width": 1.2
            },
            "pitch_circle_pinion": {
                "type": "arc",
                "center": O1,
                "radius": r1,
                "start_angle_deg": 255.0,
                "end_angle_deg": 285.0,
                "style": "dashdot",
                "color_role": "reference_circle",
                "stroke_width": 0.8
            },
            "pitch_circle_gear": {
                "type": "arc",
                "center": O2,
                "radius": r2,
                "start_angle_deg": 75.0,
                "end_angle_deg": 105.0,
                "style": "dashdot",
                "color_role": "reference_circle",
                "stroke_width": 0.8
            },
            "active_contact_band": {
                "type": "segment",
                "start": [round(A[0], 6), round(A[1], 6)],
                "end": [round(E[0], 6), round(E[1], 6)],
                "style": "solid",
                "color_role": "active_band",
                "stroke_width": 4.5
            },
            "single_contact_band": {
                "type": "segment",
                "start": [round(B[0], 6), round(B[1], 6)],
                "end": [round(D[0], 6), round(D[1], 6)],
                "style": "solid",
                "color_role": "single_contact_band",
                "stroke_width": 4.5
            }
        },
        "dimensions": [
            {
                "id": "dim_pb_ad",
                "type": "linear_aligned",
                "start_point": A,
                "end_point": D,
                "direction": u_loa,
                "normal": norm_loa,
                "layer": 1,
                "offset_normal": 8.0,
                "label_key": "fig4_dim_pb",
                "color_role": "dimension_pb",
                "value_mm": round(pb, 3)
            },
            {
                "id": "dim_g_alpha",
                "type": "linear_aligned",
                "start_point": A,
                "end_point": E,
                "direction": u_loa,
                "normal": norm_loa,
                "layer": 2,
                "offset_normal": 14.5,
                "label_key": "fig4_dim_ga",
                "color_role": "dimension_ga",
                "value_mm": round(g_alpha, 3)
            },
            {
                "id": "dim_g1_bd",
                "type": "linear_aligned",
                "start_point": B,
                "end_point": D,
                "direction": u_loa,
                "normal": [-norm_loa[0], -norm_loa[1]],
                "layer": 1,
                "offset_normal": 7.5,
                "label_key": "fig4_dim_bd",
                "color_role": "dimension_bd",
                "value_mm": round(g1, 3)
            }
        ]
    }

    return spec


def get_i18n_dictionaries():
    """Generates standard translations for KO, EN, DE, JA."""
    dicts = {
        "ko": {
            "fig4_title": "그림 4: 물림선(Line of Action)과 접촉 궤적 및 정면 물림률",
            "fig4_loa": "물림 작용선 (Line of Action, n-n)",
            "fig4_pitch_line": "피치 접선 (tP - tP)",
            "fig4_centerline": "중심선 (Line of Centers)",
            "fig4_point_p": "P (피치점)",
            "fig4_point_a": "A (접촉 시작점, SAP)",
            "fig4_point_e": "E (접촉 종료점, EAP)",
            "fig4_point_b": "B (단일 접촉 하한점)",
            "fig4_point_d": "D (단일 접촉 상한점)",
            "fig4_point_n1": "N1 (피니언 기초원 접점)",
            "fig4_point_n2": "N2 (기어 기초원 접점)",
            "fig4_gear_tip": "기어 이끝원 (ra2 = 73.5 mm)",
            "fig4_pinion_tip": "피니언 이끝원 (ra1 = 31.5 mm)",
            "fig4_dim_pb": "기초원 피치 pb = AD = π·m·cos α = 8.856 mm",
            "fig4_dim_ga": "실제 접촉 궤적 AE (ga = gf + ga = 14.558 mm)",
            "fig4_dim_bd": "단일 치 접촉 구간 BD (g1 = 3.16 mm)",
            "summary_card_title": "[물림선 접촉 궤적 및 정면 물림률 닫힌 해 수식]",
            "summary_formula_1": "(1) 물림길이 닫힌 해: ga = √(ra1² - rb1²) + √(ra2² - rb2²) - a·sin α = 14.558 mm",
            "summary_formula_2": "(2) 정면 물림률: εα = ga / pb = 14.558 / 8.856 = 1.644 ≥ 1.20 (설계 합격)",
            "summary_formula_3": "(3) 접촉 구간 분담: 단일 치 접촉 g1 = 3.155 mm (21.7%), 이중 치 접촉 g2 = 11.403 mm (78.3%)",
            "summary_formula_note": "[공학적 의의] εα ≥ 1.20 확보로 전달 오차 완충 및 무충격 연속 동력 전달 보장"
        },
        "en": {
            "fig4_title": "Figure 4: Line of Action, Path of Contact, and Transverse Contact Ratio",
            "fig4_loa": "Line of Action (n-n)",
            "fig4_pitch_line": "Pitch Tangent (tP - tP)",
            "fig4_centerline": "Line of Centers",
            "fig4_point_p": "P (Pitch Point)",
            "fig4_point_a": "A (Start of Active Profile, SAP)",
            "fig4_point_e": "E (End of Active Profile, EAP)",
            "fig4_point_b": "B (Lowest Point of Single Tooth Contact)",
            "fig4_point_d": "D (Highest Point of Single Tooth Contact)",
            "fig4_point_n1": "N1 (Pinion Base Circle Tangency)",
            "fig4_point_n2": "N2 (Gear Base Circle Tangency)",
            "fig4_gear_tip": "Gear Tip Circle (ra2 = 73.5 mm)",
            "fig4_pinion_tip": "Pinion Tip Circle (ra1 = 31.5 mm)",
            "fig4_dim_pb": "Base Pitch pb = AD = π·m·cos α = 8.856 mm",
            "fig4_dim_ga": "Actual Path of Contact AE (ga = gf + ga = 14.558 mm)",
            "fig4_dim_bd": "Single Contact Zone BD (g1 = 3.16 mm)",
            "summary_card_title": "[Closed-Form Kinematics of Contact Path & Contact Ratio]",
            "summary_formula_1": "(1) Contact Length: ga = √(ra1² - rb1²) + √(ra2² - rb2²) - a·sin α = 14.558 mm",
            "summary_formula_2": "(2) Contact Ratio: εα = ga / pb = 14.558 / 8.856 = 1.644 ≥ 1.20 (Design Approved)",
            "summary_formula_3": "(3) Zone Sharing: Single Tooth g1 = 3.155 mm (21.7%), Double Tooth g2 = 11.403 mm (78.3%)",
            "summary_formula_note": "[Engineering Significance] εα ≥ 1.20 ensures continuous low-vibration power transfer"
        },
        "de": {
            "fig4_title": "Abbildung 4: Eingriffslinie, Eingriffsstrecke und Profilüberdeckung",
            "fig4_loa": "Eingriffslinie (n-n)",
            "fig4_pitch_line": "Wälztangente (tP - tP)",
            "fig4_centerline": "Zentralachse",
            "fig4_point_p": "P (Wälzpunkt)",
            "fig4_point_a": "A (Eingriffsbeginn, SAP)",
            "fig4_point_e": "E (Eingriffsende, EAP)",
            "fig4_point_b": "B (Unterer Einzeleingriffspunkt)",
            "fig4_point_d": "D (Oberer Einzeleingriffspunkt)",
            "fig4_point_n1": "N1 (Ritzel-Grundkreistangente)",
            "fig4_point_n2": "N2 (Rad-Grundkreistangente)",
            "fig4_gear_tip": "Rad-Kopfkreis (ra2 = 73,5 mm)",
            "fig4_pinion_tip": "Ritzel-Kopfkreis (ra1 = 31,5 mm)",
            "fig4_dim_pb": "Grundkreisteilung pb = AD = π·m·cos α = 8,856 mm",
            "fig4_dim_ga": "Eingriffsstrecke AE (ga = gf + ga = 14,558 mm)",
            "fig4_dim_bd": "Einzeleingriffsstrecke BD (g1 = 3,16 mm)",
            "summary_card_title": "[Geschlossene Kinematikformeln der Profilüberdeckung]",
            "summary_formula_1": "(1) Eingriffsstrecke: ga = √(ra1² - rb1²) + √(ra2² - rb2²) - a·sin α = 14,558 mm",
            "summary_formula_2": "(2) Profilüberdeckung: εα = ga / pb = 14,558 / 8,856 = 1,644 ≥ 1,20 (Erfüllt)",
            "summary_formula_3": "(3) Zonenaufteilung: Einzeleingriff g1 = 3,155 mm (21,7%), Doppeleingriff g2 = 11,403 mm (78,3%)",
            "summary_formula_note": "[Bedeutung] εα ≥ 1,20 sichert stoßfreie, kontinuierliche Drehmomentübertragung"
        },
        "ja": {
            "fig4_title": "図 4: かみ合い線(Line of Action)・接触軌跡および正面かみ合い率",
            "fig4_loa": "かみ合い作用線 (Line of Action, n-n)",
            "fig4_pitch_line": "ピッチ接線 (tP - tP)",
            "fig4_centerline": "中心線 (Line of Centers)",
            "fig4_point_p": "P (ピッチ点)",
            "fig4_point_a": "A (かみ合い開始点, SAP)",
            "fig4_point_e": "E (かみ合い終了点, EAP)",
            "fig4_point_b": "B (単一接触下限点)",
            "fig4_point_d": "D (単一接触上限点)",
            "fig4_point_n1": "N1 (小歯車基礎円接点)",
            "fig4_point_n2": "N2 (大歯車基礎円接点)",
            "fig4_gear_tip": "大歯車歯先円 (ra2 = 73.5 mm)",
            "fig4_pinion_tip": "小歯車歯先円 (ra1 = 31.5 mm)",
            "fig4_dim_pb": "基礎円ピッチ pb = AD = π·m·cos α = 8.856 mm",
            "fig4_dim_ga": "実接触軌跡 AE (ga = gf + ga = 14.558 mm)",
            "fig4_dim_bd": "単一歯接触区間 BD (g1 = 3.16 mm)",
            "summary_card_title": "[かみ合い線接触軌跡および正面かみ合い率 厳密解数式]",
            "summary_formula_1": "(1) かみ合い長さ厳密解: ga = √(ra1² - rb1²) + √(ra2² - rb2²) - a·sin α = 14.558 mm",
            "summary_formula_2": "(2) 正面かみ合い率: εα = ga / pb = 14.558 / 8.856 = 1.644 ≥ 1.20 (設計合格)",
            "summary_formula_3": "(3) 接触区間分担: 単一歯接触 g1 = 3.155 mm (21.7%), 複歯接触 g2 = 11.403 mm (78.3%)",
            "summary_formula_note": "[工学的意義] εα ≥ 1.20 確保により伝達誤差緩衝と無衝撃連続動力伝達を保証"
        }
    }
    return dicts


def main():
    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    spec = compute_fig4_spec()
    spec_path = SPECS_DIR / "fig4_spec.json"
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"[OK] Exported geometry spec to: {spec_path}")

    # Export i18n dictionaries
    dicts = get_i18n_dictionaries()
    for lang, d in dicts.items():
        lang_dir = LOCALES_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        dict_path = lang_dir / "fig4_labels.json"
        with open(dict_path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(f"[OK] Exported {lang.upper()} dictionary to: {dict_path}")


if __name__ == "__main__":
    main()
