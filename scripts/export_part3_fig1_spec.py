"""
Export analytical geometry specification for Part 3 Fig 1:
Line of Action Five Singular Points and Meshing Path Geometry.
Standard Gear Pair: m=3, z1=18, z2=54, alpha_0=20 deg, a=108 mm.
"""

import json
import math
from pathlib import Path

# Parameters
m = 3.0
z1 = 18
z2 = 54
alpha_deg = 20.0
alpha_rad = math.radians(alpha_deg)

r1 = 0.5 * m * z1       # 27.0 mm
r2 = 0.5 * m * z2       # 81.0 mm
a = r1 + r2             # 108.0 mm
rb1 = r1 * math.cos(alpha_rad)  # 25.371701 mm
rb2 = r2 * math.cos(alpha_rad)  # 76.115102 mm
ra1 = r1 + m                  # 30.0 mm
ra2 = r2 + m                  # 84.0 mm
rf1 = r1 - 1.25 * m           # 23.25 mm
rf2 = r2 - 1.25 * m           # 77.25 mm
pb = math.pi * m * math.cos(alpha_rad)  # 8.856394 mm

gf = math.sqrt(ra2**2 - rb2**2) - r2 * math.sin(alpha_rad)  # 7.827921 mm
ga = math.sqrt(ra1**2 - rb1**2) - r1 * math.sin(alpha_rad)  # 6.774104 mm
g_alpha = gf + ga                                          # 14.602025 mm
eps_alpha = g_alpha / pb                                   # 1.648755

g1 = 2 * pb - g_alpha                                      # 3.110763 mm (Single contact)
g2 = 2 * (g_alpha - pb)                                    # 11.491262 mm (Double contact sum)
ratio_single = (g1 / g_alpha) * 100                        # 21.3 %
ratio_double = 100.0 - ratio_single                        # 78.7 %

t_A = -gf               # -7.827921 mm
t_B = ga - pb           # -2.082290 mm
t_P = 0.0               #  0.000000 mm
t_D = -gf + pb          # +1.028474 mm
t_E = ga                # +6.774104 mm

t_N1 = -r1 * math.sin(alpha_rad)  # -9.234544 mm
t_N2 = r2 * math.sin(alpha_rad)   # +27.703632 mm

u_loa = [math.cos(alpha_rad), -math.sin(alpha_rad)]
norm_loa = [math.sin(alpha_rad), math.cos(alpha_rad)]

def t_to_coord(t):
    return [t * u_loa[0], t * u_loa[1]]

spec = {
    "schema_version": "1.0.0",
    "diagram_id": "fig1_line_of_action_five_points",
    "title_key": "fig1_title",
    "parameters": {
        "module": m,
        "z1": z1,
        "z2": z2,
        "alpha_deg": alpha_deg,
        "center_distance": a,
        "r1": r1,
        "r2": r2,
        "rb1": rb1,
        "rb2": rb2,
        "ra1": ra1,
        "ra2": ra2,
        "rf1": rf1,
        "rf2": rf2,
        "gf": gf,
        "ga": ga,
        "g_alpha": g_alpha,
        "pb": pb,
        "g1": g1,
        "g2_total": g2,
        "contact_ratio_transverse": eps_alpha,
        "ratio_single_percent": round(ratio_single, 1),
        "ratio_double_percent": round(ratio_double, 1)
    },
    "viewport": {
        "x_min": -32.0,
        "x_max": 38.0,
        "y_min": -20.0,
        "y_max": 24.0,
        "aspect_ratio": "equal"
    },
    "landmarks": {
        "N1": {
            "coord": t_to_coord(t_N1),
            "t": t_N1,
            "label_key": "fig1_point_n1",
            "preferred_side": "west",
            "marker_style": "square",
            "color_role": "base_circle"
        },
        "ra2_arc": {
            "coord": [-14.0, -r2 + math.sqrt(ra2**2 - 14.0**2)],
            "label_key": "fig1_gear_tip",
            "preferred_side": "west",
            "marker_style": "arrow_to_curve",
            "target_curve": "tip_circle_gear",
            "color_role": "gear"
        },
        "A": {
            "coord": t_to_coord(t_A),
            "t": t_A,
            "label_key": "fig1_point_a",
            "preferred_side": "west",
            "marker_style": "circle",
            "color_role": "contact_point"
        },
        "loa_label": {
            "coord": [-24.0, 12.0],
            "label_key": "fig1_loa",
            "preferred_side": "west",
            "marker_style": "none",
            "color_role": "action_line"
        },
        "B": {
            "coord": t_to_coord(t_B),
            "t": t_B,
            "label_key": "fig1_point_b",
            "preferred_side": "north_west",
            "marker_style": "circle",
            "color_role": "contact_limit"
        },
        "P": {
            "coord": [0.0, 0.0],
            "t": 0.0,
            "label_key": "fig1_point_p",
            "preferred_side": "south",
            "marker_style": "circle",
            "color_role": "pitch_point"
        },
        "D": {
            "coord": t_to_coord(t_D),
            "t": t_D,
            "label_key": "fig1_point_d",
            "preferred_side": "north_east",
            "marker_style": "circle",
            "color_role": "contact_limit"
        },
        "ra1_arc": {
            "coord": [14.0, r1 - math.sqrt(ra1**2 - 14.0**2)],
            "label_key": "fig1_pinion_tip",
            "preferred_side": "east",
            "marker_style": "arrow_to_curve",
            "target_curve": "tip_circle_pinion",
            "color_role": "pinion"
        },
        "pitch_line": {
            "coord": [20.0, 0.0],
            "label_key": "fig1_pitch_line",
            "preferred_side": "east",
            "marker_style": "arrow_to_curve",
            "target_curve": "pitch_tangent",
            "color_role": "pitch_line"
        },
        "E": {
            "coord": t_to_coord(t_E),
            "t": t_E,
            "label_key": "fig1_point_e",
            "preferred_side": "east",
            "marker_style": "circle",
            "color_role": "contact_point"
        },
        "N2": {
            "coord": t_to_coord(t_N2),
            "t": t_N2,
            "label_key": "fig1_point_n2",
            "preferred_side": "east",
            "marker_style": "square",
            "color_role": "base_circle"
        }
    }
}

out_path = Path("blog/data/specs/fig1_part3_spec.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Generated spec: {out_path} ({out_path.stat().st_size} bytes)")
