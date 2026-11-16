import json
from pathlib import Path

locales_dir = Path("blog/data/locales")

labels = {
    'ko': {
        'fig1_title': "그림 1: 작용선(Line of Action) 5대 특이점과 맞물림 궤적 기하학",
        'fig1_point_a': "A (접촉 시작점, SAP)",
        'fig1_point_b': "B (단일 접촉 하한점, LPSTC)",
        'fig1_point_p': "P (피치점, 순수 구름 vg = 0)",
        'fig1_point_d': "D (단일 접촉 상한점, HPSTC)",
        'fig1_point_e': "E (접촉 종료점, EAP)",
        'fig1_point_n1': "T1 (피니언 기초원 접점)",
        'fig1_point_n2': "T2 (대기어 기초원 접점)",
        'fig1_loa': "물림 작용선 (Line of Action, n-n)",
        'fig1_pitch_line': "피치 접선 (tP - tP)",
        'fig1_pinion_tip': "피니언 이끝원 (ra1 = 30.0 mm)",
        'fig1_gear_tip': "대기어 이끝원 (ra2 = 84.0 mm)",
        'fig1_dim_pb': "기초원 피치 pb = AD = π·m·cos α = 8.856 mm",
        'fig1_dim_ga': "실제 접촉 궤적 AE (ga = gf + ga = 14.602 mm)",
        'fig1_dim_bd': "단일 치 접촉 구간 BD (g1 = 3.111 mm)",
        'summary_card_title': "[작용선 5대 특이점과 맞물림 궤적 기하학적 정밀 요약]",
        'summary_formula_1': "(1) 5대 특이점: 점 A (SAP) ➔ 점 B (LPSTC) ➔ 점 P (피치점) ➔ 점 D (HPSTC) ➔ 점 E (EAP)",
        'summary_formula_2': "(2) 물림길이 및 법선 피치: gf = 7.828 mm, ga = 6.774 mm ➔ ga = 14.602 mm, pb = 8.856 mm",
        'summary_formula_3': "(3) 정면 물림률: εα = ga / pb = 14.602 / 8.856 = 1.649 ≥ 1.200 (설계 합격)",
        'summary_formula_note': "[공학적 의의] 단일 접촉 21.3% (g1 = 3.111 mm), 이중 접촉 78.7% (g2 = 11.491 mm) 분할 보존",
        'summary_params_header': "[설계 제원]"
    },
    'en': {
        'fig1_title': "Fig 1: Line of Action Five Singular Points and Meshing Path Geometry",
        'fig1_point_a': "A (Start of Active Profile, SAP)",
        'fig1_point_b': "B (Lowest Point Single Contact, LPSTC)",
        'fig1_point_p': "P (Pitch Point, Pure Rolling vg = 0)",
        'fig1_point_d': "D (Highest Point Single Contact, HPSTC)",
        'fig1_point_e': "E (End of Active Profile, EAP)",
        'fig1_point_n1': "T1 (Pinion Base Circle Tangency)",
        'fig1_point_n2': "T2 (Gear Base Circle Tangency)",
        'fig1_loa': "Line of Action (n-n)",
        'fig1_pitch_line': "Pitch Tangent (tP - tP)",
        'fig1_pinion_tip': "Pinion Tip Circle (ra1 = 30.0 mm)",
        'fig1_gear_tip': "Gear Tip Circle (ra2 = 84.0 mm)",
        'fig1_dim_pb': "Base Pitch pb = AD = π·m·cos α = 8.856 mm",
        'fig1_dim_ga': "Active Contact Path AE (ga = gf + ga = 14.602 mm)",
        'fig1_dim_bd': "Single Contact Zone BD (g1 = 3.111 mm)",
        'summary_card_title': "[Summary: Line of Action Five Singular Points & Contact Ratio]",
        'summary_formula_1': "(1) Singular Points: Point A (SAP) ➔ Point B (LPSTC) ➔ Point P (Pitch) ➔ Point D (HPSTC) ➔ Point E (EAP)",
        'summary_formula_2': "(2) Path Lengths: gf = 7.828 mm, ga = 6.774 mm ➔ ga = 14.602 mm, pb = 8.856 mm",
        'summary_formula_3': "(3) Transverse Contact Ratio: εα = ga / pb = 14.602 / 8.856 = 1.649 ≥ 1.200 (Design Qualified)",
        'summary_formula_note': "[Engineering Significance] Single Contact 21.3% (g1 = 3.111 mm), Double Contact 78.7% (g2 = 11.491 mm)",
        'summary_params_header': "[Design Parameters]"
    },
    'de': {
        'fig1_title': "Abb. 1: Fünf singuläre Punkte der Eingriffslinie und Geometrie der Eingriffsstrecke",
        'fig1_point_a': "A (Eingriffsbeginn, SAP)",
        'fig1_point_b': "B (Unterer Einzeleingriffspunkt, LPSTC)",
        'fig1_point_p': "P (Wälzpunkt, Reines Rollen vg = 0)",
        'fig1_point_d': "D (Oberer Einzeleingriffspunkt, HPSTC)",
        'fig1_point_e': "E (Eingriffsende, EAP)",
        'fig1_point_n1': "T1 (Grundkreis Ritzel Berührung)",
        'fig1_point_n2': "T2 (Grundkreis Rad Berührung)",
        'fig1_loa': "Eingriffslinie (n-n)",
        'fig1_pitch_line': "Wälztangente (tP - tP)",
        'fig1_pinion_tip': "Ritzel-Kopfkreis (ra1 = 30.0 mm)",
        'fig1_gear_tip': "Rad-Kopfkreis (ra2 = 84.0 mm)",
        'fig1_dim_pb': "Eingriffsteilung pb = AD = π·m·cos α = 8.856 mm",
        'fig1_dim_ga': "Aktive Eingriffsstrecke AE (ga = gf + ga = 14.602 mm)",
        'fig1_dim_bd': "Einzeleingriffsstrecke BD (g1 = 3.111 mm)",
        'summary_card_title': "[Zusammenfassung: Fünf singuläre Eingriffspunkte & Profilüberdeckung]",
        'summary_formula_1': "(1) Singuläre Punkte: Punkt A (SAP) ➔ Punkt B (LPSTC) ➔ Punkt P (Wälzpunkt) ➔ Punkt D (HPSTC) ➔ Punkt E (EAP)",
        'summary_formula_2': "(2) Eingriffsstrecken: gf = 7.828 mm, ga = 6.774 mm ➔ ga = 14.602 mm, pb = 8.856 mm",
        'summary_formula_3': "(3) Profilüberdeckung: εα = ga / pb = 14.602 / 8.856 = 1.649 ≥ 1.200 (Auslegung qualifiziert)",
        'summary_formula_note': "[Ingenieurtechnische Bedeutung] Einzeleingriff 21.3% (g1 = 3.111 mm), Doppeleingriff 78.7% (g2 = 11.491 mm)",
        'summary_params_header': "[Auslegungsparameter]"
    },
    'ja': {
        'fig1_title': "図 1: 作用線上の5大特異点と噛合い軌跡幾何学",
        'fig1_point_a': "A (噛合い開始点, SAP)",
        'fig1_point_b': "B (単一歯接触最下点, LPSTC)",
        'fig1_point_p': "P (ピッチ点, 純粋転がり vg = 0)",
        'fig1_point_d': "D (単一歯接触最上点, HPSTC)",
        'fig1_point_e': "E (噛合い終了点, EAP)",
        'fig1_point_n1': "T1 (ピニオン基礎円接点)",
        'fig1_point_n2': "T2 (大歯車基礎円接点)",
        'fig1_loa': "作用線 (Line of Action, n-n)",
        'fig1_pitch_line': "ピッチ接線 (tP - tP)",
        'fig1_pinion_tip': "ピニオン歯先円 (ra1 = 30.0 mm)",
        'fig1_gear_tip': "大歯車歯先円 (ra2 = 84.0 mm)",
        'fig1_dim_pb': "基礎円ピッチ pb = AD = π·m·cos α = 8.856 mm",
        'fig1_dim_ga': "実際の噛合い軌跡 AE (ga = gf + ga = 14.602 mm)",
        'fig1_dim_bd': "単一歯接触区間 BD (g1 = 3.111 mm)",
        'summary_card_title': "[作用線5大特異点と噛合い率の幾何学的精密要約]",
        'summary_formula_1': "(1) 5大特異点: 点 A (SAP) ➔ 点 B (LPSTC) ➔ 点 P (ピッチ点) ➔ 点 D (HPSTC) ➔ 点 E (EAP)",
        'summary_formula_2': "(2) 噛合い長さ・法線ピッチ: gf = 7.828 mm, ga = 6.774 mm ➔ ga = 14.602 mm, pb = 8.856 mm",
        'summary_formula_3': "(3) 正面噛合い率: εα = ga / pb = 14.602 / 8.856 = 1.649 ≥ 1.200 (設計合格)",
        'summary_formula_note': "[工学的意義] 単一接触 21.3% (g1 = 3.111 mm), 2歯接触 78.7% (g2 = 11.491 mm) 分担保持",
        'summary_params_header': "[設計諸元]"
    }
}

for lang, data in labels.items():
    p = locales_dir / lang / "fig1_part3_labels.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Written: {p}")
