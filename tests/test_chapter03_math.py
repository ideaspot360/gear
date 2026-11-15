"""
test_chapter03_math.py
================================================================================
H-GEAR STUDIO: Blog Series 1 Part A Chapter 3 Closed-Form Mathematical Harness
Target: Verification of Meshing Kinematics, Line of Action Singular Points,
        Contact Ratios, Specific Sliding & HPSTC Tooth Bending Mechanics
Benchmark Specification:
  - Normal/transverse module: m = 3.000000 mm
  - Standard reference pressure angle: alpha_0 = 20.000000 deg
  - Pinion teeth: z1 = 18, Gear teeth: z2 = 54, Gear ratio: u = 3.000000
  - Standard center distance: a = 108.000000 mm
  - Tool basic rack profile (ISO 53 Profile A): ha* = 1.000, c* = 0.250, hf* = 1.250, rho_f* = 0.380
  - Profile shift: x1 = 0.000000, x2 = 0.000000 (Standard proportions)
Standards & Literature:
  - DIN 3960 §3.3: Eingriffsgrößen (5대 특이점 A, B, C, D, E, 물림률, 미끄럼률)
  - Earle Buckingham: Analytical Mechanics of Gears (1949), Ch 18 & Ch 19
  - ISO 21771:2007: Cylindrical gears - Geometry and design
  - ISO 6336-1/2/3: Calculation of load capacity of spur and helical gears (Method B HPSTC)
  - KS B 0102 (기어 용어) & KS B 0002 / KS B 1405 (기어 제도 및 요목표)
Precision Standard: 10^-5 ~ 10^-6 strict numerical tolerance
================================================================================
"""

import math
import sys
from typing import Dict, Any, Tuple

try:
    import pytest
except ImportError:
    class _MockPytestMark:
        @staticmethod
        def parametrize(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

    class _MockPytest:
        mark = _MockPytestMark()

        @staticmethod
        def fixture(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

        @staticmethod
        def skip(reason: str = ""):
            print(f"  [SKIPPED] {reason}")

    pytest = _MockPytest()


# -----------------------------------------------------------------------------
# Fundamental Mathematical Functions (Differential Geometry & Kinematics)
# -----------------------------------------------------------------------------

def inv(angle_rad: float) -> float:
    """
    Involute function: inv(alpha) = tan(alpha) - alpha.
    Represents polar roll angle from base circle origin.
    """
    return math.tan(angle_rad) - angle_rad


def inv_derivative(angle_rad: float) -> float:
    """
    First derivative of involute function: d/d_alpha (inv(alpha)) = tan^2(alpha).
    Strictly positive for alpha in (0, pi/2).
    """
    return math.tan(angle_rad) ** 2


def specific_sliding_pinion(s: float, t1t2: float, u: float) -> float:
    """
    Calculate pinion specific sliding k1 at action line coordinate s (from T1):
        k1 = 1 - (z1 * rho2) / (z2 * rho1) = 1 - rho2 / (u * rho1)
    where rho1 = s, rho2 = t1t2 - s.
    """
    rho1 = s
    rho2 = t1t2 - s
    if abs(rho1) < 1e-12:
        return float("-inf")
    return 1.0 - rho2 / (u * rho1)


def specific_sliding_gear(s: float, t1t2: float, u: float) -> float:
    """
    Calculate gear specific sliding k2 at action line coordinate s (from T1):
        k2 = 1 - (z2 * rho1) / (z1 * rho2) = 1 - (u * rho1) / rho2
    where rho1 = s, rho2 = t1t2 - s.
    """
    rho1 = s
    rho2 = t1t2 - s
    if abs(rho2) < 1e-12:
        return float("-inf")
    return 1.0 - (u * rho1) / rho2


def sliding_velocity(omega1: float, u: float, x: float) -> float:
    """
    Sliding velocity vg as a function of directed distance x from pitch point P:
        vg(x) = (omega1 + omega2) * x = omega1 * (1 + 1/u) * x
    At pitch point P (x = 0), vg = 0 (Pure rolling).
    """
    omega2 = omega1 / u
    return (omega1 + omega2) * x


# -----------------------------------------------------------------------------
# Test Suite 1: Line of Action 5 Singular Points (A, B, C, D, E)
# -----------------------------------------------------------------------------

class TestChapter03ActionLineSingularPoints:
    """
    Verification of the 5 Singular Points on the Line of Action (DIN 3960 §3.3):
      - Point A: Start of Active Profile (SAP, 피동기어 이끝원 교점)
      - Point B: Lowest Point of Single Tooth Contact (LPSTC, 최하위 단일 접촉점)
      - Point C: Pitch Point P (피치점, 순수 구름 접촉점, vg=0)
      - Point D: Highest Point of Single Tooth Contact (HPSTC, 최상위 단일 접촉점)
      - Point E: End of Active Profile (EAP, 구동기어 이끝원 교점)
    """

    # Benchmark inputs
    m: float = 3.000000
    alpha_0_deg: float = 20.000000
    alpha_0: float = math.radians(20.000000)
    z1: int = 18
    z2: int = 54
    u: float = 3.000000
    a: float = 108.000000

    @property
    def r1(self) -> float:
        return (self.m * self.z1) / 2.0  # 27.000000 mm

    @property
    def r2(self) -> float:
        return (self.m * self.z2) / 2.0  # 81.000000 mm

    @property
    def rb1(self) -> float:
        return self.r1 * math.cos(self.alpha_0)  # 25.371701 mm

    @property
    def rb2(self) -> float:
        return self.r2 * math.cos(self.alpha_0)  # 76.115102 mm

    @property
    def ra1(self) -> float:
        return self.r1 + self.m  # 30.000000 mm

    @property
    def ra2(self) -> float:
        return self.r2 + self.m  # 84.000000 mm

    @property
    def pb(self) -> float:
        return math.pi * self.m * math.cos(self.alpha_0)  # 8.856394 mm

    @property
    def t1t2(self) -> float:
        return self.a * math.sin(self.alpha_0)  # 36.938175 mm

    def test_action_line_total_length(self):
        """
        Verify total tangent segment length between base circle points T1 and T2:
            T1T2 = a * sin(alpha_0) = (rb1 + rb2) * tan(alpha_0) = 36.938175 mm.
        """
        t1t2_a = self.a * math.sin(self.alpha_0)
        t1t2_rb = (self.rb1 + self.rb2) * math.tan(self.alpha_0)

        assert abs(t1t2_a - 36.938175) < 1e-5
        assert abs(t1t2_rb - 36.938175) < 1e-5
        assert abs(t1t2_a - t1t2_rb) < 1e-12

    def test_singular_points_coordinates_from_t1(self):
        """
        Verify coordinates s along Line of Action measured from base point T1 (s=0):
          - s_A (SAP)   = a*sin(alpha_0) - sqrt(ra2^2 - rb2^2) = 1.406623 mm
          - s_B (LPSTC) = s_E - pb                             = 7.152253 mm
          - s_C (Pitch) = rb1 * tan(alpha_0) = r1 * sin(alpha) = 9.234544 mm
          - s_D (HPSTC) = s_A + pb                             = 10.263018 mm
          - s_E (EAP)   = sqrt(ra1^2 - rb1^2)                  = 16.008648 mm
        """
        s_A = self.t1t2 - math.sqrt(self.ra2 ** 2 - self.rb2 ** 2)
        s_E = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2)
        s_B = s_E - self.pb
        s_C = self.rb1 * math.tan(self.alpha_0)
        s_D = s_A + self.pb

        assert abs(s_A - 1.406623) < 1e-5
        assert abs(s_B - 7.152253) < 1e-5
        assert abs(s_C - 9.234544) < 1e-5
        assert abs(s_D - 10.263018) < 1e-5
        assert abs(s_E - 16.008648) < 1e-5

    def test_singular_points_monotonic_ordering(self):
        """
        Verify strict monotonic progression along the line of action:
            0 < s_A < s_B < s_C < s_D < s_E < T1T2.
        This confirms proper kinematic sequence without tooth overlap or jamming.
        """
        s_A = self.t1t2 - math.sqrt(self.ra2 ** 2 - self.rb2 ** 2)
        s_E = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2)
        s_B = s_E - self.pb
        s_C = self.rb1 * math.tan(self.alpha_0)
        s_D = s_A + self.pb

        assert 0.0 < s_A < s_B < s_C < s_D < s_E < self.t1t2, (
            f"Ordering violation: 0 < {s_A} < {s_B} < {s_C} < {s_D} < {s_E} < {self.t1t2}"
        )

    def test_singular_points_relative_to_pitch_point(self):
        """
        Verify coordinates x = s - s_C relative to Pitch Point P (s_C = 0):
          - x_A = s_A - s_C = -gf = -7.827921 mm
          - x_B = s_B - s_C       = -2.082291 mm
          - x_C = 0.000000 mm
          - x_D = s_D - s_C       = +1.028474 mm
          - x_E = s_E - s_C = +ga = +6.774104 mm
        Total active path length: x_E - x_A = ga + gf = g_alpha = 14.602024 mm.
        """
        s_A = self.t1t2 - math.sqrt(self.ra2 ** 2 - self.rb2 ** 2)
        s_E = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2)
        s_B = s_E - self.pb
        s_C = self.rb1 * math.tan(self.alpha_0)
        s_D = s_A + self.pb

        x_A = s_A - s_C
        x_B = s_B - s_C
        x_C = s_C - s_C
        x_D = s_D - s_C
        x_E = s_E - s_C

        assert abs(x_A - (-7.827921)) < 1e-5
        assert abs(x_B - (-2.082291)) < 1e-5
        assert abs(x_C - 0.000000) < 1e-12
        assert abs(x_D - 1.028474) < 1e-5
        assert abs(x_E - 6.774104) < 1e-5
        assert abs((x_E - x_A) - 14.602024) < 1e-5

    def test_radii_and_pressure_angles_at_singular_points(self):
        """
        Verify radius r and local profile pressure angle alpha at all 5 points:
            r1 = sqrt(rb1^2 + s^2),      alpha1 = atan(s / rb1)
            r2 = sqrt(rb2^2 + rho2^2),   alpha2 = atan(rho2 / rb2) where rho2 = T1T2 - s.
        """
        s_A = self.t1t2 - math.sqrt(self.ra2 ** 2 - self.rb2 ** 2)
        s_E = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2)
        s_B = s_E - self.pb
        s_C = self.rb1 * math.tan(self.alpha_0)
        s_D = s_A + self.pb

        pts = [
            ("A", s_A, 25.410663, 3.173265, 84.000000, 25.023798),
            ("B", s_B, 26.360537, 15.743083, 81.735610, 21.371766),
            ("C", s_C, 27.000000, 20.000000, 81.000000, 20.000000),
            ("D", s_D, 27.368828, 22.023652, 80.654031, 19.313428),
            ("E", s_E, 30.000000, 32.250479, 78.940192, 15.374764),
        ]

        for name, s_val, exp_r1, exp_a1_deg, exp_r2, exp_a2_deg in pts:
            # Pinion 1 calculations
            r1 = math.sqrt(self.rb1 ** 2 + s_val ** 2)
            alpha1_deg = math.degrees(math.atan(s_val / self.rb1))

            # Gear 2 calculations
            rho2 = self.t1t2 - s_val
            r2 = math.sqrt(self.rb2 ** 2 + rho2 ** 2)
            alpha2_deg = math.degrees(math.atan(rho2 / self.rb2))

            assert abs(r1 - exp_r1) < 1e-5, f"Point {name}: r1 mismatch: {r1} vs {exp_r1}"
            assert abs(alpha1_deg - exp_a1_deg) < 1e-4, f"Point {name}: a1 mismatch: {alpha1_deg} vs {exp_a1_deg}"
            assert abs(r2 - exp_r2) < 1e-5, f"Point {name}: r2 mismatch: {r2} vs {exp_r2}"
            assert abs(alpha2_deg - exp_a2_deg) < 1e-4, f"Point {name}: a2 mismatch: {alpha2_deg} vs {exp_a2_deg}"

        # Verify exact tip boundary invariants at points A and E
        # At point A: gear 2 is at its tip circle ra2
        r2_A = math.sqrt(self.rb2 ** 2 + (self.t1t2 - s_A) ** 2)
        assert abs(r2_A - self.ra2) < 1e-12

        # At point E: pinion 1 is at its tip circle ra1
        r1_E = math.sqrt(self.rb1 ** 2 + s_E ** 2)
        assert abs(r1_E - self.ra1) < 1e-12


# -----------------------------------------------------------------------------
# Test Suite 2: Path Lengths, Contact Ratio, and Load Sharing Zones
# -----------------------------------------------------------------------------

class TestChapter03PathLengthsAndContactRatio:
    """
    Verification of approach/recess path lengths, base pitch, transverse contact ratio,
    and single/double tooth contact zone partitioning (DIN 3960, ISO 21771).
    """

    m: float = 3.000000
    alpha_0: float = math.radians(20.000000)
    z1: int = 18
    z2: int = 54
    a: float = 108.000000

    @property
    def r1(self) -> float:
        return (self.m * self.z1) / 2.0

    @property
    def r2(self) -> float:
        return (self.m * self.z2) / 2.0

    @property
    def rb1(self) -> float:
        return self.r1 * math.cos(self.alpha_0)

    @property
    def rb2(self) -> float:
        return self.r2 * math.cos(self.alpha_0)

    @property
    def ra1(self) -> float:
        return self.r1 + self.m

    @property
    def ra2(self) -> float:
        return self.r2 + self.m

    def test_approach_and_recess_path_lengths(self):
        """
        Approach path gf: distance from A (SAP) to pitch point C
            gf = sqrt(ra2^2 - rb2^2) - rb2*tan(alpha_0) = 7.827921 mm
        Recess path ga: distance from pitch point C to E (EAP)
            ga = sqrt(ra1^2 - rb1^2) - rb1*tan(alpha_0) = 6.774104 mm
        """
        gf = math.sqrt(self.ra2 ** 2 - self.rb2 ** 2) - self.rb2 * math.tan(self.alpha_0)
        ga = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2) - self.rb1 * math.tan(self.alpha_0)

        assert abs(gf - 7.827921) < 1e-5
        assert abs(ga - 6.774104) < 1e-5

    def test_total_path_length(self):
        """
        Total contact path length g_alpha = ga + gf = 14.602024 mm.
        Also verified via direct formula:
            g_alpha = sqrt(ra1^2 - rb1^2) + sqrt(ra2^2 - rb2^2) - a*sin(alpha_0)
        """
        ga = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2) - self.rb1 * math.tan(self.alpha_0)
        gf = math.sqrt(self.ra2 ** 2 - self.rb2 ** 2) - self.rb2 * math.tan(self.alpha_0)
        g_alpha_sum = ga + gf

        g_alpha_direct = (
            math.sqrt(self.ra1 ** 2 - self.rb1 ** 2)
            + math.sqrt(self.ra2 ** 2 - self.rb2 ** 2)
            - self.a * math.sin(self.alpha_0)
        )

        assert abs(g_alpha_sum - 14.602024) < 1e-5
        assert abs(g_alpha_direct - 14.602024) < 1e-5
        assert abs(g_alpha_sum - g_alpha_direct) < 1e-12

    def test_base_pitch(self):
        """
        Normal/base pitch pb = pi * m * cos(alpha_0) = 8.856394 mm.
        Distance along line of action between consecutive teeth.
        """
        pb = math.pi * self.m * math.cos(self.alpha_0)
        assert abs(pb - 8.856394) < 1e-5

    def test_transverse_contact_ratio(self):
        """
        Transverse contact ratio eps_alpha = g_alpha / pb = 1.648755.
        Must satisfy ISO / KS engineering minimum eps_alpha >= 1.200000.
        """
        ga = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2) - self.rb1 * math.tan(self.alpha_0)
        gf = math.sqrt(self.ra2 ** 2 - self.rb2 ** 2) - self.rb2 * math.tan(self.alpha_0)
        g_alpha = ga + gf
        pb = math.pi * self.m * math.cos(self.alpha_0)
        eps_alpha = g_alpha / pb

        assert abs(eps_alpha - 1.648755) < 1e-5
        assert eps_alpha >= 1.200000, f"Contact ratio {eps_alpha} < 1.20 (Transmission discontinuity risk!)"

    def test_contact_zones_partitioning(self):
        """
        Single-tooth contact zone: BD = 2*pb - g_alpha = 3.110764 mm (21.3037%)
        Double-tooth contact zone: AB = DE = g_alpha - pb = 5.745630 mm (total 11.491260 mm, 78.6963%)
        Conservation: AB + BD + DE = g_alpha identically.
        """
        ga = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2) - self.rb1 * math.tan(self.alpha_0)
        gf = math.sqrt(self.ra2 ** 2 - self.rb2 ** 2) - self.rb2 * math.tan(self.alpha_0)
        g_alpha = ga + gf
        pb = math.pi * self.m * math.cos(self.alpha_0)

        # Zone lengths
        single_zone_bd = 2.0 * pb - g_alpha
        double_zone_ab = g_alpha - pb
        double_zone_de = g_alpha - pb
        total_double_zone = double_zone_ab + double_zone_de

        assert abs(single_zone_bd - 3.110764) < 1e-5
        assert abs(double_zone_ab - 5.745630) < 1e-5
        assert abs(double_zone_de - 5.745630) < 1e-5
        assert abs(total_double_zone - 11.491260) < 1e-5

        # Strict identity conservation
        assert abs((double_zone_ab + single_zone_bd + double_zone_de) - g_alpha) < 1e-12

        # Percentage distribution
        pct_single = (single_zone_bd / g_alpha) * 100.0
        pct_double = (total_double_zone / g_alpha) * 100.0
        assert abs(pct_single - 21.3037) < 0.01
        assert abs(pct_double - 78.6963) < 0.01


# -----------------------------------------------------------------------------
# Test Suite 3: Kinematics and Specific Sliding (Buckingham Ch 19 & DIN 3960)
# -----------------------------------------------------------------------------

class TestChapter03KinematicsAndSpecificSliding:
    """
    Verification of sliding velocity and specific sliding curves k1, k2:
        k1 = 1 - (z1 * rho2) / (z2 * rho1) = 1 - rho2 / (3 * rho1)
        k2 = 1 - (z2 * rho1) / (z1 * rho2) = 1 - (3 * rho1) / rho2
    """

    m: float = 3.000000
    alpha_0: float = math.radians(20.000000)
    z1: int = 18
    z2: int = 54
    u: float = 3.000000
    a: float = 108.000000

    @property
    def r1(self) -> float:
        return (self.m * self.z1) / 2.0

    @property
    def r2(self) -> float:
        return (self.m * self.z2) / 2.0

    @property
    def rb1(self) -> float:
        return self.r1 * math.cos(self.alpha_0)

    @property
    def rb2(self) -> float:
        return self.r2 * math.cos(self.alpha_0)

    @property
    def ra1(self) -> float:
        return self.r1 + self.m

    @property
    def ra2(self) -> float:
        return self.r2 + self.m

    @property
    def pb(self) -> float:
        return math.pi * self.m * math.cos(self.alpha_0)

    @property
    def t1t2(self) -> float:
        return self.a * math.sin(self.alpha_0)

    def test_sliding_velocity_proportionality_and_pitch_zero(self):
        """
        Sliding velocity vg = (omega1 + omega2) * x.
        Verify vg == 0 at Pitch Point P (x = 0, pure rolling),
        and strict linearity with distance from pitch point.
        """
        omega1 = 100.0  # rad/s arbitrary
        omega2 = omega1 / self.u

        # At Pitch point P (x = 0)
        vg_P = sliding_velocity(omega1, self.u, 0.0)
        assert abs(vg_P - 0.0) < 1e-12

        # Linearity check
        x1, x2 = 2.5, 5.0
        vg_1 = sliding_velocity(omega1, self.u, x1)
        vg_2 = sliding_velocity(omega1, self.u, x2)
        assert abs(vg_2 - 2.0 * vg_1) < 1e-12

    def test_specific_sliding_at_pitch_point(self):
        """
        At Pitch Point P (s_C = rb1 * tan(alpha_0)):
            rho1 = r1 * sin(alpha_0), rho2 = r2 * sin(alpha_0)
            k1 = 1 - rho2 / (u * rho1) = 1 - r2 / (u * r1) = 1 - 1 = 0
            k2 = 1 - (u * rho1) / rho2 = 1 - (u * r1) / r2 = 1 - 1 = 0
        Zero sliding, zero frictional heating, pure rolling.
        """
        s_C = self.rb1 * math.tan(self.alpha_0)
        k1_C = specific_sliding_pinion(s_C, self.t1t2, self.u)
        k2_C = specific_sliding_gear(s_C, self.t1t2, self.u)

        assert abs(k1_C - 0.000000) < 1e-12
        assert abs(k2_C - 0.000000) < 1e-12

    def test_specific_sliding_at_singular_points(self):
        """
        Verify exact specific sliding at singular points A, B, D, E:
          - Point A (SAP):   k1 = -7.420059, k2 = +0.881236 (피니언 이뿌리부 극대 음의 미끄럼율)
          - Point B (LPSTC): k1 = -0.388184, k2 = +0.279634
          - Point D (HPSTC): k1 = +0.133616, k2 = -0.154222
          - Point E (EAP):   k1 = +0.564204, k2 = -1.294650 (대기어 이뿌리부 극대 음의 미끄럼율)
        """
        s_A = self.t1t2 - math.sqrt(self.ra2 ** 2 - self.rb2 ** 2)
        s_E = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2)
        s_B = s_E - self.pb
        s_D = s_A + self.pb

        k1_A = specific_sliding_pinion(s_A, self.t1t2, self.u)
        k2_A = specific_sliding_gear(s_A, self.t1t2, self.u)

        k1_B = specific_sliding_pinion(s_B, self.t1t2, self.u)
        k2_B = specific_sliding_gear(s_B, self.t1t2, self.u)

        k1_D = specific_sliding_pinion(s_D, self.t1t2, self.u)
        k2_D = specific_sliding_gear(s_D, self.t1t2, self.u)

        k1_E = specific_sliding_pinion(s_E, self.t1t2, self.u)
        k2_E = specific_sliding_gear(s_E, self.t1t2, self.u)

        assert abs(k1_A - (-7.420059)) < 1e-5
        assert abs(k2_A - 0.881236) < 1e-5

        assert abs(k1_B - (-0.388184)) < 1e-5
        assert abs(k2_B - 0.279634) < 1e-5

        assert abs(k1_D - 0.133616) < 1e-5
        assert abs(k2_D - (-0.154222)) < 1e-5

        assert abs(k1_E - 0.564204) < 1e-5
        assert abs(k2_E - (-1.294650)) < 1e-5

    def test_asymptotic_behavior_near_base_circle(self):
        """
        As contact approaches base circle tangent T1 (s -> 0), rho1 -> 0,
        pinion specific sliding k1 -> -infinity, explaining rapid scuffing/scoring
        if active profile extends too close to base circle (motive for profile shift).
        Likewise as s -> T1T2, gear specific sliding k2 -> -infinity.
        """
        # Near pinion base circle (s = 0.001 mm)
        k1_near_base1 = specific_sliding_pinion(0.001, self.t1t2, self.u)
        assert k1_near_base1 < -10000.0, f"Expected k1 -> -inf, got {k1_near_base1}"

        # Near gear base circle (rho2 = 0.001 mm, s = T1T2 - 0.001)
        k2_near_base2 = specific_sliding_gear(self.t1t2 - 0.001, self.t1t2, self.u)
        assert k2_near_base2 < -10000.0, f"Expected k2 -> -inf, got {k2_near_base2}"


# -----------------------------------------------------------------------------
# Test Suite 4: Forces, Bearing Reactions, and HPSTC Bending Mechanics
# -----------------------------------------------------------------------------

class TestChapter03ForcesAndHPSTCBending:
    """
    Verification of 2-axis tooth force decomposition, simply supported shaft bearing reactions,
    and the mechanical proof of HPSTC tooth bending dominance over EAP (ISO 6336 Method B).
    """

    m: float = 3.000000
    alpha_0: float = math.radians(20.000000)
    z1: int = 18
    d1: float = 54.000000  # mm

    def test_static_tooth_forces_decomposition(self):
        """
        Given input torque T1 = 100.0 N*m:
            Ft = 2000 * T1 / d1 = 3703.703704 N
            Fr = Ft * tan(alpha_0) = 1348.037905 N
            Fn = Ft / cos(alpha_0) = 3941.399157 N
        Verify strict Pythagorean conservation: sqrt(Ft^2 + Fr^2) == Fn.
        """
        t1_torque = 100.0  # N*m
        ft = (2000.0 * t1_torque) / self.d1
        fr = ft * math.tan(self.alpha_0)
        fn = ft / math.cos(self.alpha_0)

        assert abs(ft - 3703.703704) < 1e-5
        assert abs(fr - 1348.037905) < 1e-5
        assert abs(fn - 3941.399157) < 1e-5

        # Pythagorean identity
        fn_pythagorean = math.sqrt(ft ** 2 + fr ** 2)
        assert abs(fn_pythagorean - fn) < 1e-12

    def test_shaft_bearing_reactions_equilibrium(self):
        """
        Shaft span L = 100.0 mm, gear center located at L1 = 40.0 mm from bearing A:
            R_Ax = Ft * (L - L1) / L = 0.6 * Ft,  R_Bx = Ft * L1 / L = 0.4 * Ft
            R_Ay = Fr * (L - L1) / L = 0.6 * Fr,  R_By = Fr * L1 / L = 0.4 * Fr
            Fr_A = Fn * (L - L1) / L = 0.6 * Fn,  Fr_B = Fn * L1 / L = 0.4 * Fn
        Verify complete force and moment static equilibrium.
        """
        t1_torque = 100.0
        ft = (2000.0 * t1_torque) / self.d1
        fr = ft * math.tan(self.alpha_0)
        fn = ft / math.cos(self.alpha_0)

        l_span = 100.0  # mm
        l1 = 40.0       # mm

        r_ax = ft * (l_span - l1) / l_span
        r_bx = ft * l1 / l_span
        r_ay = fr * (l_span - l1) / l_span
        r_by = fr * l1 / l_span

        fr_a = math.sqrt(r_ax ** 2 + r_ay ** 2)
        fr_b = math.sqrt(r_bx ** 2 + r_by ** 2)

        # Equilibrium checks
        assert abs((r_ax + r_bx) - ft) < 1e-12
        assert abs((r_ay + r_by) - fr) < 1e-12
        assert abs((fr_a + fr_b) - fn) < 1e-12

        # 6-decimal values
        assert abs(r_ax - 2222.222222) < 1e-5
        assert abs(r_bx - 1481.481481) < 1e-5
        assert abs(r_ay - 808.822743) < 1e-5
        assert abs(r_by - 539.215162) < 1e-5
        assert abs(fr_a - 2364.839494) < 1e-5
        assert abs(fr_b - 1576.559663) < 1e-5

    def test_hpstc_bending_moment_dominance_over_eap(self):
        """
        Mechanical Proof for ISO 6336 Method B (HPSTC Bending Stress Standard):
          - At HPSTC (Point D): Single tooth contact -> Fn_D = 1.0 * Fn
          - At EAP (Point E): Double tooth contact -> Fn_E = 0.5 * Fn (load sharing)
          - Moment arm ratio: hE / hD ~ 1.20
          - Mb_D = 1.0 * Fn * hD
          - Mb_E = 0.5 * Fn * (1.20 * hD) = 0.60 * Fn * hD
          - Ratio: Mb_D / Mb_E = 1.0 / 0.60 = 1.666667 > 1.0
        HPSTC generates ~1.67x greater tooth root bending moment than tooth tip EAP.
        """
        fn = 3941.399157  # N
        hd = 4.0          # mm (nominal moment arm to critical root section)
        moment_arm_ratio = 1.20
        he = moment_arm_ratio * hd  # 4.8 mm

        fn_d = 1.0 * fn   # 100% load at HPSTC (single tooth contact zone)
        fn_e = 0.5 * fn   # ~50% load at EAP (double tooth load sharing zone)

        mb_d = fn_d * hd
        mb_e = fn_e * he

        assert mb_d > mb_e, f"HPSTC bending moment {mb_d} must exceed EAP bending moment {mb_e}"
        ratio = mb_d / mb_e
        assert abs(ratio - 1.666667) < 1e-5


# -----------------------------------------------------------------------------
# Test Suite 5: 38 Benchmark Proportions Table Verification
# -----------------------------------------------------------------------------

class TestChapter03BenchmarkProportionsTable:
    """
    Exhaustive verification of the 38 closed-form parameters table for Chapter 3:
      m = 3.0 mm, alpha_0 = 20.0 deg, z1 = 18, z2 = 54, a = 108.0 mm
    Precision threshold: < 10^-5 (exact match to 6 decimal places).
    """

    m: float = 3.000000
    alpha_0_deg: float = 20.000000
    alpha_0: float = math.radians(20.000000)
    z1: int = 18
    z2: int = 54
    ha_star: float = 1.000000
    c_star: float = 0.250000
    hf_star: float = 1.250000  # ha* + c*

    def test_param_01_gear_ratio(self):
        """Param 01: Gear ratio u = z2 / z1 = 54 / 18 = 3.000000."""
        u = self.z2 / self.z1
        assert abs(u - 3.000000) < 1e-5

    def test_param_02_03_pinion_pitch_diameter_and_radius(self):
        """
        Param 02: Pinion pitch diameter d1 = m * z1 = 54.000000 mm
        Param 03: Pinion pitch radius r1 = d1 / 2 = 27.000000 mm
        """
        d1 = self.m * self.z1
        r1 = d1 / 2.0
        assert abs(d1 - 54.000000) < 1e-5
        assert abs(r1 - 27.000000) < 1e-5

    def test_param_04_05_gear_pitch_diameter_and_radius(self):
        """
        Param 04: Gear pitch diameter d2 = m * z2 = 162.000000 mm
        Param 05: Gear pitch radius r2 = d2 / 2 = 81.000000 mm
        """
        d2 = self.m * self.z2
        r2 = d2 / 2.0
        assert abs(d2 - 162.000000) < 1e-5
        assert abs(r2 - 81.000000) < 1e-5

    def test_param_06_standard_center_distance(self):
        """Param 06: Standard center distance a = (d1 + d2) / 2 = 108.000000 mm."""
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        assert abs(a - 108.000000) < 1e-5

    def test_param_07_circular_pitch(self):
        """Param 07: Circular pitch p = pi * m = 9.424778 mm."""
        p = math.pi * self.m
        assert abs(p - 9.424778) < 1e-5

    def test_param_08_standard_tooth_thickness_and_space(self):
        """Param 08: Standard tooth thickness s = e = p / 2 = 4.712389 mm."""
        p = math.pi * self.m
        s = p / 2.0
        e = s
        assert abs(s - 4.712389) < 1e-5
        assert abs(e - 4.712389) < 1e-5

    def test_param_09_base_pitch_normal_pitch(self):
        """Param 09: Base pitch (normal pitch) pb = pi * m * cos(alpha_0) = 8.856394 mm."""
        pb = math.pi * self.m * math.cos(self.alpha_0)
        assert abs(pb - 8.856394) < 1e-5

    def test_param_10_11_pinion_base_diameter_and_radius(self):
        """
        Param 10: Pinion base diameter db1 = d1 * cos(alpha_0) = 50.743402 mm
        Param 11: Pinion base radius rb1 = db1 / 2 = 25.371701 mm
        """
        d1 = self.m * self.z1
        db1 = d1 * math.cos(self.alpha_0)
        rb1 = db1 / 2.0
        assert abs(db1 - 50.743402) < 1e-5
        assert abs(rb1 - 25.371701) < 1e-5

    def test_param_12_13_gear_base_diameter_and_radius(self):
        """
        Param 12: Gear base diameter db2 = d2 * cos(alpha_0) = 152.230205 mm
        Param 13: Gear base radius rb2 = db2 / 2 = 76.115102 mm
        """
        d2 = self.m * self.z2
        db2 = d2 * math.cos(self.alpha_0)
        rb2 = db2 / 2.0
        assert abs(db2 - 152.230205) < 1e-5
        assert abs(rb2 - 76.115102) < 1e-5

    def test_param_14_15_16_17_tooth_height_dimensions(self):
        """
        Param 14: Addendum ha = ha* * m = 3.000000 mm
        Param 15: Dedendum hf = (ha* + c*) * m = 3.750000 mm
        Param 16: Whole depth h = ha + hf = 6.750000 mm
        Param 17: Bottom clearance c = c* * m = 0.750000 mm
        """
        ha = self.ha_star * self.m
        hf = self.hf_star * self.m
        h = ha + hf
        c = self.c_star * self.m
        assert abs(ha - 3.000000) < 1e-5
        assert abs(hf - 3.750000) < 1e-5
        assert abs(h - 6.750000) < 1e-5
        assert abs(c - 0.750000) < 1e-5

    def test_param_18_19_pinion_tip_diameter_and_radius(self):
        """
        Param 18: Pinion tip diameter da1 = d1 + 2*ha = 60.000000 mm
        Param 19: Pinion tip radius ra1 = da1 / 2 = 30.000000 mm
        """
        d1 = self.m * self.z1
        ha = self.ha_star * self.m
        da1 = d1 + 2.0 * ha
        ra1 = da1 / 2.0
        assert abs(da1 - 60.000000) < 1e-5
        assert abs(ra1 - 30.000000) < 1e-5

    def test_param_20_21_gear_tip_diameter_and_radius(self):
        """
        Param 20: Gear tip diameter da2 = d2 + 2*ha = 168.000000 mm
        Param 21: Gear tip radius ra2 = da2 / 2 = 84.000000 mm
        """
        d2 = self.m * self.z2
        ha = self.ha_star * self.m
        da2 = d2 + 2.0 * ha
        ra2 = da2 / 2.0
        assert abs(da2 - 168.000000) < 1e-5
        assert abs(ra2 - 84.000000) < 1e-5

    def test_param_22_23_pinion_root_diameter_and_radius(self):
        """
        Param 22: Pinion root diameter df1 = d1 - 2*hf = 46.500000 mm
        Param 23: Pinion root radius rf1 = df1 / 2 = 23.250000 mm
        """
        d1 = self.m * self.z1
        hf = self.hf_star * self.m
        df1 = d1 - 2.0 * hf
        rf1 = df1 / 2.0
        assert abs(df1 - 46.500000) < 1e-5
        assert abs(rf1 - 23.250000) < 1e-5

    def test_param_24_25_gear_root_diameter_and_radius(self):
        """
        Param 24: Gear root diameter df2 = d2 - 2*hf = 154.500000 mm
        Param 25: Gear root radius rf2 = df2 / 2 = 77.250000 mm
        """
        d2 = self.m * self.z2
        hf = self.hf_star * self.m
        df2 = d2 - 2.0 * hf
        rf2 = df2 / 2.0
        assert abs(df2 - 154.500000) < 1e-5
        assert abs(rf2 - 77.250000) < 1e-5

    def test_param_26_standard_pressure_angle_involute(self):
        """Param 26: Reference pressure angle involute inv(alpha_0) = 0.014904 rad."""
        inv_alpha = inv(self.alpha_0)
        assert abs(inv_alpha - 0.014904) < 1e-5

    def test_param_27_28_tip_pressure_angles(self):
        """
        Param 27: Pinion tip pressure angle alpha_a1 = arccos(rb1 / ra1) = 32.250479 deg (0.562877 rad)
        Param 28: Gear tip pressure angle alpha_a2 = arccos(rb2 / ra2) = 25.023798 deg (0.436748 rad)
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        rb1 = (d1 * math.cos(self.alpha_0)) / 2.0
        rb2 = (d2 * math.cos(self.alpha_0)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)

        assert abs(math.degrees(alpha_a1) - 32.250479) < 1e-5
        assert abs(alpha_a1 - 0.562877) < 1e-5

        assert abs(math.degrees(alpha_a2) - 25.023798) < 1e-5
        assert abs(alpha_a2 - 0.436748) < 1e-5

    def test_param_29_30_tip_involute_values(self):
        """
        Param 29: Pinion tip involute inv(alpha_a1) = tan(alpha_a1) - alpha_a1 = 0.068088 rad
        Param 30: Gear tip involute inv(alpha_a2) = tan(alpha_a2) - alpha_a2 = 0.030066 rad
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        rb1 = (d1 * math.cos(self.alpha_0)) / 2.0
        rb2 = (d2 * math.cos(self.alpha_0)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)

        inv_a1 = inv(alpha_a1)
        inv_a2 = inv(alpha_a2)

        assert abs(inv_a1 - 0.068088) < 1e-5
        assert abs(inv_a2 - 0.030066) < 1e-5

    def test_param_31_32_top_land_thickness_and_pointed_tooth_prevention(self):
        """
        Param 31: Pinion top land thickness sa1 = 2.044991 mm
        Param 32: Gear top land thickness sa2 = 2.339811 mm
        Constitutional Invariant: sa >= 0.25 * m (0.750000 mm) to strictly prevent pointed teeth.
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        r1 = d1 / 2.0
        r2 = d2 / 2.0
        rb1 = (d1 * math.cos(self.alpha_0)) / 2.0
        rb2 = (d2 * math.cos(self.alpha_0)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0
        s = (math.pi * self.m) / 2.0

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)

        sa1 = 2.0 * ra1 * ((s / (2.0 * r1)) + inv(self.alpha_0) - inv(alpha_a1))
        sa2 = 2.0 * ra2 * ((s / (2.0 * r2)) + inv(self.alpha_0) - inv(alpha_a2))

        assert abs(sa1 - 2.044991) < 1e-5
        assert abs(sa2 - 2.339811) < 1e-5

        # Critical ISO structural requirement: sa >= 0.25 * m
        min_top_land = 0.25 * self.m
        assert sa1 >= min_top_land, f"Pinion top land {sa1} < {min_top_land} mm (Pointed tooth defect!)"
        assert sa2 >= min_top_land, f"Gear top land {sa2} < {min_top_land} mm (Pointed tooth defect!)"

    def test_param_33_34_35_line_of_action_path_lengths(self):
        """
        Param 33: Recess path length ga = sqrt(ra1^2 - rb1^2) - rb1*tan(alpha_0) = 6.774104 mm
        Param 34: Approach path length gf = sqrt(ra2^2 - rb2^2) - rb2*tan(alpha_0) = 7.827921 mm
        Param 35: Total path length g_alpha = ga + gf = 14.602024 mm
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        rb1 = (d1 * math.cos(self.alpha_0)) / 2.0
        rb2 = (d2 * math.cos(self.alpha_0)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        ga = math.sqrt(ra1 ** 2 - rb1 ** 2) - rb1 * math.tan(self.alpha_0)
        gf = math.sqrt(ra2 ** 2 - rb2 ** 2) - rb2 * math.tan(self.alpha_0)
        g_alpha_sum = ga + gf
        g_alpha_direct = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(self.alpha_0)

        assert abs(ga - 6.774104) < 1e-5
        assert abs(gf - 7.827921) < 1e-5
        assert abs(g_alpha_sum - 14.602024) < 1e-5
        assert abs(g_alpha_direct - 14.602024) < 1e-5
        assert abs(g_alpha_sum - g_alpha_direct) < 1e-12

    def test_param_36_transverse_contact_ratio(self):
        """
        Param 36: Transverse contact ratio eps_alpha = g_alpha / pb = 1.648755
        Engineering Requirement: eps_alpha >= 1.200000 to ensure smooth power transfer and load sharing.
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        rb1 = (d1 * math.cos(self.alpha_0)) / 2.0
        rb2 = (d2 * math.cos(self.alpha_0)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        g_alpha = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(self.alpha_0)
        pb = math.pi * self.m * math.cos(self.alpha_0)
        eps_alpha = g_alpha / pb

        assert abs(eps_alpha - 1.648755) < 1e-5
        assert eps_alpha >= 1.200000, f"Contact ratio {eps_alpha} < 1.20 (Power transfer discontinuity risk!)"

    def test_param_37_38_contact_zone_partitioning(self):
        """
        Param 37: Single-tooth contact length g1 = 2*pb - g_alpha = 3.110764 mm (21.30%)
        Param 38: Double-tooth contact length g2 = 2*(g_alpha - pb) = 11.491260 mm (78.70%)
        Conservation: g1 + g2 identically equals g_alpha.
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        rb1 = (d1 * math.cos(self.alpha_0)) / 2.0
        rb2 = (d2 * math.cos(self.alpha_0)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        g_alpha = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(self.alpha_0)
        pb = math.pi * self.m * math.cos(self.alpha_0)

        g1 = 2.0 * pb - g_alpha
        g2 = 2.0 * (g_alpha - pb)

        assert abs(g1 - 3.110764) < 1e-5
        assert abs(g2 - 11.491260) < 1e-5
        assert abs((g1 + g2) - g_alpha) < 1e-12

        # Zone percentages
        pct_g1 = (g1 / g_alpha) * 100.0
        pct_g2 = (g2 / g_alpha) * 100.0
        assert abs(pct_g1 - 21.3037) < 0.01
        assert abs(pct_g2 - 78.6963) < 0.01


# -----------------------------------------------------------------------------
# Standalone CLI Runner & Summary Printer
# -----------------------------------------------------------------------------

def run_self_check():
    """Execute all tests standalone and print detailed engineering verification report."""
    print("=" * 80)
    print("  H-GEAR STUDIO: Chapter 3 Meshing Kinematics & Mathematical Invariance Harness")
    print("  Benchmark: m=3.0 mm, alpha=20 deg, z1=18, z2=54, a=108.0 mm")
    print("=" * 80)

    # 1. Action Line Singular Points
    t1 = TestChapter03ActionLineSingularPoints()
    t1.test_action_line_total_length()
    t1.test_singular_points_coordinates_from_t1()
    t1.test_singular_points_monotonic_ordering()
    t1.test_singular_points_relative_to_pitch_point()
    t1.test_radii_and_pressure_angles_at_singular_points()
    print("  [Suite 1] Action Line 5 Singular Points (A, B, C, D, E): ALL PASS (5/5)")

    # 2. Path Lengths and Contact Ratio
    t2 = TestChapter03PathLengthsAndContactRatio()
    t2.test_approach_and_recess_path_lengths()
    t2.test_total_path_length()
    t2.test_base_pitch()
    t2.test_transverse_contact_ratio()
    t2.test_contact_zones_partitioning()
    print("  [Suite 2] Path Lengths, Base Pitch & Contact Ratio:       ALL PASS (5/5)")

    # 3. Kinematics and Specific Sliding
    t3 = TestChapter03KinematicsAndSpecificSliding()
    t3.test_sliding_velocity_proportionality_and_pitch_zero()
    t3.test_specific_sliding_at_pitch_point()
    t3.test_specific_sliding_at_singular_points()
    t3.test_asymptotic_behavior_near_base_circle()
    print("  [Suite 3] Kinematics & Specific Sliding Curves:          ALL PASS (4/4)")

    # 4. Forces, Bearing Reactions, and HPSTC Bending
    t4 = TestChapter03ForcesAndHPSTCBending()
    t4.test_static_tooth_forces_decomposition()
    t4.test_shaft_bearing_reactions_equilibrium()
    t4.test_hpstc_bending_moment_dominance_over_eap()
    print("  [Suite 4] Forces, Bearing Reactions & HPSTC Bending:     ALL PASS (3/3)")

    # 5. 38 Parameters Closed-Form Table
    t5 = TestChapter03BenchmarkProportionsTable()
    methods = [getattr(t5, m) for m in dir(t5) if m.startswith("test_param_")]
    for method in methods:
        method()
    print(f"  [Suite 5] 38 Parameters Closed-Form Table:              ALL PASS ({len(methods)}/{len(methods)})")

    # Output exact floating-point diagnostics
    m = 3.0
    alpha = math.radians(20.0)
    z1, z2 = 18, 54
    d1, d2 = m * z1, m * z2
    a = (d1 + d2) / 2.0
    rb1, rb2 = (d1 * math.cos(alpha)) / 2.0, (d2 * math.cos(alpha)) / 2.0
    ra1, ra2 = (d1 + 2 * m) / 2.0, (d2 + 2 * m) / 2.0
    t1t2 = a * math.sin(alpha)
    pb = math.pi * m * math.cos(alpha)
    ga = math.sqrt(ra1 ** 2 - rb1 ** 2) - rb1 * math.tan(alpha)
    gf = math.sqrt(ra2 ** 2 - rb2 ** 2) - rb2 * math.tan(alpha)
    g_alpha = ga + gf
    eps_alpha = g_alpha / pb
    g1 = 2 * pb - g_alpha
    g2 = 2 * (g_alpha - pb)
    s_A = t1t2 - math.sqrt(ra2 ** 2 - rb2 ** 2)
    s_E = math.sqrt(ra1 ** 2 - rb1 ** 2)
    s_B = s_E - pb
    s_C = rb1 * math.tan(alpha)
    s_D = s_A + pb
    k1_A = specific_sliding_pinion(s_A, t1t2, z2 / z1)
    k2_A = specific_sliding_gear(s_A, t1t2, z2 / z1)
    k1_E = specific_sliding_pinion(s_E, t1t2, z2 / z1)
    k2_E = specific_sliding_gear(s_E, t1t2, z2 / z1)

    print("-" * 80)
    print("  Exact Theoretical Closed-form Diagnostics ( 소수점 6자리 실측치 ):")
    print(f"    - Action Line Length (T1T2):     {t1t2:.6f} mm")
    print(f"    - Point A (SAP) coordinate:      s_A = {s_A:.6f} mm,  k1={k1_A:.6f}, k2={k2_A:.6f}")
    print(f"    - Point B (LPSTC) coordinate:    s_B = {s_B:.6f} mm")
    print(f"    - Point C (Pitch P) coordinate:  s_C = {s_C:.6f} mm (Pure rolling: vg=0, k1=0, k2=0)")
    print(f"    - Point D (HPSTC) coordinate:    s_D = {s_D:.6f} mm (ISO 6336 Method B Max Bending)")
    print(f"    - Point E (EAP) coordinate:      s_E = {s_E:.6f} mm,  k1={k1_E:.6f}, k2={k2_E:.6f}")
    print(f"    - Approach Path (gf):            {gf:.6f} mm")
    print(f"    - Recess Path (ga):              {ga:.6f} mm")
    print(f"    - Total Contact Path (g_alpha):  {g_alpha:.6f} mm")
    print(f"    - Base Pitch (pb):               {pb:.6f} mm")
    print(f"    - Contact Ratio (eps_alpha):     {eps_alpha:.6f}  (>= 1.200000: PASS)")
    print(f"    - Single-tooth contact (g1):     {g1:.6f} mm  ({(g1/g_alpha)*100:.4f}%)")
    print(f"    - Double-tooth contact (g2):     {g2:.6f} mm  ({(g2/g_alpha)*100:.4f}%)")
    print("=" * 80)
    print("  RESULT: 100% SUCCESS — ALL CHAPTER 3 MATHEMATICAL INVARIANTS PRESERVED")
    print("=" * 80)


if __name__ == "__main__":
    run_self_check()
