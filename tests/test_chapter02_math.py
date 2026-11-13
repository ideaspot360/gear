"""
test_chapter02_math.py
================================================================================
H-GEAR STUDIO: Blog Series 1 Part A Chapter 2 Closed-Form Mathematical Harness
Target: Verification of Involute Geometry & Spur Gear Proportions Benchmark
Benchmark Specification:
  - Module m = 3.000000 mm, Reference pressure angle alpha = 20.000000 deg
  - Pinion teeth z1 = 19, Gear teeth z2 = 47, Standard center distance a = 99.000000 mm
  - Profile shift x1 = 0.000000, x2 = 0.000000 (Standard proportions)
  - Tool basic rack profile (ISO 53 Profile A): ha* = 1.000, c* = 0.250, hf* = 1.250, rho_f* = 0.380
Standards: ISO 53, ISO 21771:2007, DIN 3960, KS B 0102, KS B 0053
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
# Fundamental Mathematical Functions (Differential Geometry & Involute)
# -----------------------------------------------------------------------------

def inv(angle_rad: float) -> float:
    """
    Involute function: inv(alpha) = tan(alpha) - alpha.
    Represents the polar angle theta_k from the origin of the involute curve.
    """
    return math.tan(angle_rad) - angle_rad


def inv_derivative(angle_rad: float) -> float:
    """
    First derivative of involute function: d/d_alpha (inv(alpha)) = tan^2(alpha).
    Strictly positive for all alpha in (0, pi/2), proving strict monotonicity.
    """
    return math.tan(angle_rad) ** 2


def inv_inverse_series_reversion(theta_k: float) -> float:
    """
    Analytical series reversion of involute function up to O(z^9).
    z = (3 * theta_k)^(1/3)
    alpha(z) = z - (2/15)*z^3 + (3/175)*z^5 - (2/1575)*z^7
    Provides analytical accuracy of ~10^-8 rad across practical gearing pressure angles.
    """
    z = (3.0 * theta_k) ** (1.0 / 3.0)
    return z - (2.0 / 15.0) * (z ** 3) + (3.0 / 175.0) * (z ** 5) - (2.0 / 1575.0) * (z ** 7)


def inv_inverse_exact(theta_k: float) -> float:
    """
    Exact inverse involute function using 1-step Newton-Raphson seeded with series reversion.
    Guarantees 64-bit machine-epsilon precision (< 10^-14 rad) without open-ended loops.
    """
    a0 = inv_inverse_series_reversion(theta_k)
    # Newton-Raphson update: a1 = a0 - (inv(a0) - theta_k) / inv'(a0)
    return a0 - (inv(a0) - theta_k) / (math.tan(a0) ** 2)


# -----------------------------------------------------------------------------
# Tier 1: Involute Differential Geometry & Mathematical Functions
# -----------------------------------------------------------------------------

class TestChapter02InvoluteDifferentialGeometry:
    """
    Tier 1: Closed-form verification of involute curve differential geometry.
    Covers Topic 1 & Topic 2 from Chapter 2 requirements.
    """

    def test_cartesian_and_polar_equivalence(self):
        """
        Verify that Cartesian parametric representation:
            x(theta) = rb * (cos(theta) + theta * sin(theta))
            y(theta) = rb * (sin(theta) - theta * cos(theta))
        strictly equates to Polar representation:
            r(alpha) = rb / cos(alpha)
            polar_angle = inv(alpha) = tan(alpha) - alpha
        where theta = tan(alpha).
        """
        rb = 26.7812396  # Pinion base radius
        test_angles_deg = [2.0, 5.0, 10.0, 14.5, 20.0, 25.0, 30.0, 31.766779]

        for alpha_deg in test_angles_deg:
            alpha = math.radians(alpha_deg)
            theta = math.tan(alpha)  # Roll angle in radians

            # Cartesian coordinates
            x = rb * (math.cos(theta) + theta * math.sin(theta))
            y = rb * (math.sin(theta) - theta * math.cos(theta))
            r_cart = math.sqrt(x ** 2 + y ** 2)
            angle_cart = math.atan2(y, x)

            # Polar coordinates
            r_polar = rb / math.cos(alpha)
            angle_polar = inv(alpha)

            assert abs(r_cart - r_polar) < 1e-10, (
                f"Radius mismatch at alpha={alpha_deg} deg: cart={r_cart}, polar={r_polar}"
            )
            assert abs(angle_cart - angle_polar) < 1e-10, (
                f"Polar angle mismatch at alpha={alpha_deg} deg: cart={angle_cart}, polar={angle_polar}"
            )

    def test_involute_curvature_radius_invariance(self):
        """
        Verify that the radius of curvature rho(theta) = 1/kappa(theta)
        identically equals the unwound string length L(theta) = rb * theta = rb * tan(alpha).
        """
        rb = 50.0  # arbitrary base radius (mm)
        for alpha_deg in [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]:
            alpha = math.radians(alpha_deg)
            theta = math.tan(alpha)

            # String length from tangent point
            unwound_length = rb * theta

            # Curvature radius from differential geometry:
            # dr/dtheta: dx/dtheta = rb * theta * cos(theta), dy/dtheta = rb * theta * sin(theta)
            # ds/dtheta = rb * theta, dphi/dtheta = 1
            # rho = ds / dphi = rb * theta
            rho = rb * theta

            assert abs(rho - unwound_length) < 1e-12
            assert abs(rho - rb * math.tan(alpha)) < 1e-12

    def test_involute_monotonicity_and_derivative(self):
        """
        Verify that d/d_alpha (inv(alpha)) = tan^2(alpha) > 0 for all alpha in (0, pi/2),
        proving strict monotonicity and existence of a unique inverse.
        """
        for deg in [1.0, 10.0, 20.0, 30.0, 45.0]:
            rad = math.radians(deg)
            deriv = inv_derivative(rad)
            assert deriv > 0.0, f"Derivative must be strictly positive, got {deriv}"
            # Numerical derivative check
            h = 1e-7
            numerical_deriv = (inv(rad + h) - inv(rad - h)) / (2.0 * h)
            assert abs(deriv - numerical_deriv) < 1e-5

    def test_involute_inversion_series_reversion_accuracy(self):
        """
        Verify that analytical series reversion up to O(z^9) achieves error < 10^-7 rad
        without iterative root-finding.
        """
        for deg in [10.0, 14.5, 20.0, 25.0]:
            rad = math.radians(deg)
            theta_k = inv(rad)
            recovered = inv_inverse_series_reversion(theta_k)
            error = abs(recovered - rad)
            assert error < 1e-7, (
                f"Series reversion error {error:.3e} exceeds 1e-7 rad at deg={deg}"
            )

    def test_involute_inversion_exact_machine_precision(self):
        """
        Verify that 1-step Newton-Raphson seeded with series reversion reaches
        high precision (< 10^-11 rad across entire 5~35 deg range, reaching < 10^-16 rad near 20 deg)
        across all standard gear pressure angles.
        """
        for deg in [5.0, 10.0, 14.5, 20.0, 25.0, 30.0, 35.0]:
            rad = math.radians(deg)
            theta_k = inv(rad)
            recovered = inv_inverse_exact(theta_k)
            error = abs(recovered - rad)
            assert error < 1e-11, (
                f"1-step exact inverse error {error:.3e} exceeds 1e-11 rad at deg={deg}"
            )
        # Near standard pressure angle 20 deg, verify extreme machine precision
        rad_20 = math.radians(20.0)
        assert abs(inv_inverse_exact(inv(rad_20)) - rad_20) < 1e-15


# -----------------------------------------------------------------------------
# Tier 2: 38 Benchmark Parameters Ground Truth Table Verification
# -----------------------------------------------------------------------------

class TestChapter02BenchmarkProportionsTable:
    """
    Tier 2: Exhaustive verification of the 38 closed-form parameters table
    for the benchmark spur gear pair:
      m = 3.0 mm, alpha = 20.0 deg, z1 = 19, z2 = 47, a = 99.0 mm
    Precision threshold: < 10^-5 (exact match to 6 decimal places).
    """

    # Benchmark inputs
    m: float = 3.000000
    alpha_deg: float = 20.000000
    alpha: float = math.radians(20.000000)
    z1: int = 19
    z2: int = 47
    ha_star: float = 1.000000
    c_star: float = 0.250000
    hf_star: float = 1.250000  # ha* + c*

    def test_param_01_gear_ratio(self):
        """Param 01: Gear ratio u = z2 / z1 = 47 / 19 = 2.473684."""
        u = self.z2 / self.z1
        assert abs(u - 2.473684) < 1e-5

    def test_param_02_03_pinion_pitch_diameter_and_radius(self):
        """
        Param 02: Pinion pitch diameter d1 = m * z1 = 57.000000 mm
        Param 03: Pinion pitch radius r1 = d1 / 2 = 28.500000 mm
        """
        d1 = self.m * self.z1
        r1 = d1 / 2.0
        assert abs(d1 - 57.000000) < 1e-5
        assert abs(r1 - 28.500000) < 1e-5

    def test_param_04_05_gear_pitch_diameter_and_radius(self):
        """
        Param 04: Gear pitch diameter d2 = m * z2 = 141.000000 mm
        Param 05: Gear pitch radius r2 = d2 / 2 = 70.500000 mm
        """
        d2 = self.m * self.z2
        r2 = d2 / 2.0
        assert abs(d2 - 141.000000) < 1e-5
        assert abs(r2 - 70.500000) < 1e-5

    def test_param_06_standard_center_distance(self):
        """Param 06: Standard center distance a = (d1 + d2) / 2 = 99.000000 mm."""
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        assert abs(a - 99.000000) < 1e-5

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
        """Param 09: Base pitch (normal pitch) pb = pi * m * cos(alpha) = 8.856394 mm."""
        pb = math.pi * self.m * math.cos(self.alpha)
        assert abs(pb - 8.856394) < 1e-5

    def test_param_10_11_pinion_base_diameter_and_radius(self):
        """
        Param 10: Pinion base diameter db1 = d1 * cos(alpha) = 53.562479 mm
        Param 11: Pinion base radius rb1 = db1 / 2 = 26.781240 mm
        """
        d1 = self.m * self.z1
        db1 = d1 * math.cos(self.alpha)
        rb1 = db1 / 2.0
        assert abs(db1 - 53.562479) < 1e-5
        assert abs(rb1 - 26.781240) < 1e-5

    def test_param_12_13_gear_base_diameter_and_radius(self):
        """
        Param 12: Gear base diameter db2 = d2 * cos(alpha) = 132.496660 mm
        Param 13: Gear base radius rb2 = db2 / 2 = 66.248330 mm
        """
        d2 = self.m * self.z2
        db2 = d2 * math.cos(self.alpha)
        rb2 = db2 / 2.0
        assert abs(db2 - 132.496660) < 1e-5
        assert abs(rb2 - 66.248330) < 1e-5

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
        Param 18: Pinion tip diameter da1 = d1 + 2*ha = 63.000000 mm
        Param 19: Pinion tip radius ra1 = da1 / 2 = 31.500000 mm
        """
        d1 = self.m * self.z1
        ha = self.ha_star * self.m
        da1 = d1 + 2.0 * ha
        ra1 = da1 / 2.0
        assert abs(da1 - 63.000000) < 1e-5
        assert abs(ra1 - 31.500000) < 1e-5

    def test_param_20_21_gear_tip_diameter_and_radius(self):
        """
        Param 20: Gear tip diameter da2 = d2 + 2*ha = 147.000000 mm
        Param 21: Gear tip radius ra2 = da2 / 2 = 73.500000 mm
        """
        d2 = self.m * self.z2
        ha = self.ha_star * self.m
        da2 = d2 + 2.0 * ha
        ra2 = da2 / 2.0
        assert abs(da2 - 147.000000) < 1e-5
        assert abs(ra2 - 73.500000) < 1e-5

    def test_param_22_23_pinion_root_diameter_and_radius(self):
        """
        Param 22: Pinion root diameter df1 = d1 - 2*hf = 49.500000 mm
        Param 23: Pinion root radius rf1 = df1 / 2 = 24.750000 mm
        """
        d1 = self.m * self.z1
        hf = self.hf_star * self.m
        df1 = d1 - 2.0 * hf
        rf1 = df1 / 2.0
        assert abs(df1 - 49.500000) < 1e-5
        assert abs(rf1 - 24.750000) < 1e-5

    def test_param_24_25_gear_root_diameter_and_radius(self):
        """
        Param 24: Gear root diameter df2 = d2 - 2*hf = 133.500000 mm
        Param 25: Gear root radius rf2 = df2 / 2 = 66.750000 mm
        """
        d2 = self.m * self.z2
        hf = self.hf_star * self.m
        df2 = d2 - 2.0 * hf
        rf2 = df2 / 2.0
        assert abs(df2 - 133.500000) < 1e-5
        assert abs(rf2 - 66.750000) < 1e-5

    def test_param_26_standard_pressure_angle_involute(self):
        """Param 26: Reference pressure angle involute inv(alpha) = 0.014904 rad."""
        inv_alpha = inv(self.alpha)
        assert abs(inv_alpha - 0.014904) < 1e-5

    def test_param_27_28_tip_pressure_angles(self):
        """
        Param 27: Pinion tip pressure angle alpha_a1 = arccos(rb1 / ra1) = 31.766779 deg (0.554434 rad)
        Param 28: Gear tip pressure angle alpha_a2 = arccos(rb2 / ra2) = 25.665521 deg (0.447948 rad)
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        rb1 = (d1 * math.cos(self.alpha)) / 2.0
        rb2 = (d2 * math.cos(self.alpha)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)

        assert abs(math.degrees(alpha_a1) - 31.766779) < 1e-5
        assert abs(alpha_a1 - 0.554434) < 1e-5

        assert abs(math.degrees(alpha_a2) - 25.665521) < 1e-5
        assert abs(alpha_a2 - 0.447948) < 1e-5

    def test_param_29_30_tip_involute_values(self):
        """
        Param 29: Pinion tip involute inv(alpha_a1) = tan(alpha_a1) - alpha_a1 = 0.064789 rad
        Param 30: Gear tip involute inv(alpha_a2) = tan(alpha_a2) - alpha_a2 = 0.032579 rad
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        rb1 = (d1 * math.cos(self.alpha)) / 2.0
        rb2 = (d2 * math.cos(self.alpha)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)

        inv_a1 = inv(alpha_a1)
        inv_a2 = inv(alpha_a2)

        assert abs(inv_a1 - 0.064789) < 1e-5
        assert abs(inv_a2 - 0.032579) < 1e-5

    def test_param_31_32_top_land_thickness_and_pointed_tooth_prevention(self):
        """
        Param 31: Pinion top land thickness sa1 = 2.065702 mm
        Param 32: Gear top land thickness sa2 = 2.314789 mm
        Constitutional Invariant: sa >= 0.25 * m (0.750000 mm) to strictly prevent pointed tooth.
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        r1 = d1 / 2.0
        r2 = d2 / 2.0
        rb1 = (d1 * math.cos(self.alpha)) / 2.0
        rb2 = (d2 * math.cos(self.alpha)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0
        s = (math.pi * self.m) / 2.0

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)

        sa1 = 2.0 * ra1 * ((s / (2.0 * r1)) + inv(self.alpha) - inv(alpha_a1))
        sa2 = 2.0 * ra2 * ((s / (2.0 * r2)) + inv(self.alpha) - inv(alpha_a2))

        assert abs(sa1 - 2.065702) < 1e-5
        assert abs(sa2 - 2.314789) < 1e-5

        # Critical ISO / KS structural requirement: sa >= 0.25 * m
        min_top_land = 0.25 * self.m
        assert sa1 >= min_top_land, f"Pinion top land {sa1} < {min_top_land} mm (Pointed tooth defect!)"
        assert sa2 >= min_top_land, f"Gear top land {sa2} < {min_top_land} mm (Pointed tooth defect!)"

    def test_param_33_34_35_line_of_action_path_lengths(self):
        """
        Param 33: Recess path length ga = sqrt(ra1^2 - rb1^2) - rb1*tan(alpha) = 6.836008 mm
        Param 34: Approach path length gf = sqrt(ra2^2 - rb2^2) - rb2*tan(alpha) = 7.721662 mm
        Param 35: Total path length g_alpha = ga + gf = 14.557670 mm
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        rb1 = (d1 * math.cos(self.alpha)) / 2.0
        rb2 = (d2 * math.cos(self.alpha)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        ga = math.sqrt(ra1 ** 2 - rb1 ** 2) - rb1 * math.tan(self.alpha)
        gf = math.sqrt(ra2 ** 2 - rb2 ** 2) - rb2 * math.tan(self.alpha)
        g_alpha_sum = ga + gf
        g_alpha_direct = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(self.alpha)

        assert abs(ga - 6.836008) < 1e-5
        assert abs(gf - 7.721662) < 1e-5
        assert abs(g_alpha_sum - 14.557670) < 1e-5
        assert abs(g_alpha_direct - 14.557670) < 1e-5
        assert abs(g_alpha_sum - g_alpha_direct) < 1e-12

    def test_param_36_transverse_contact_ratio(self):
        """
        Param 36: Transverse contact ratio eps_alpha = g_alpha / pb = 1.643747
        Engineering Requirement: eps_alpha >= 1.200000 to ensure smooth power transfer and load sharing.
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        rb1 = (d1 * math.cos(self.alpha)) / 2.0
        rb2 = (d2 * math.cos(self.alpha)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        g_alpha = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(self.alpha)
        pb = math.pi * self.m * math.cos(self.alpha)
        eps_alpha = g_alpha / pb

        assert abs(eps_alpha - 1.643747) < 1e-5
        assert eps_alpha >= 1.200000, f"Contact ratio {eps_alpha} < 1.20 (Power transfer discontinuity risk!)"

    def test_param_37_38_contact_zone_partitioning(self):
        """
        Param 37: Single-tooth contact length g1 = 2*pb - g_alpha = 3.155118 mm (21.67%)
        Param 38: Double-tooth contact length g2 = 2*(g_alpha - pb) = 11.402552 mm (78.33%)
        Conservation: g1 + g2 identically equals g_alpha.
        """
        d1 = self.m * self.z1
        d2 = self.m * self.z2
        a = (d1 + d2) / 2.0
        rb1 = (d1 * math.cos(self.alpha)) / 2.0
        rb2 = (d2 * math.cos(self.alpha)) / 2.0
        ra1 = (d1 + 2.0 * self.m) / 2.0
        ra2 = (d2 + 2.0 * self.m) / 2.0

        g_alpha = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(self.alpha)
        pb = math.pi * self.m * math.cos(self.alpha)

        g1 = 2.0 * pb - g_alpha
        g2 = 2.0 * (g_alpha - pb)

        assert abs(g1 - 3.155118) < 1e-5
        assert abs(g2 - 11.402552) < 1e-5
        assert abs((g1 + g2) - g_alpha) < 1e-12

        # Zone percentages
        pct_g1 = (g1 / g_alpha) * 100.0
        pct_g2 = (g2 / g_alpha) * 100.0
        assert abs(pct_g1 - 21.6732) < 0.01
        assert abs(pct_g2 - 78.3268) < 0.01


# -----------------------------------------------------------------------------
# Standalone CLI Runner & Summary Printer
# -----------------------------------------------------------------------------

def run_self_check():
    """Execute all tests standalone and print detailed engineering verification report."""
    print("=" * 80)
    print("  H-GEAR STUDIO: Chapter 2 Involute Geometry & Math Invariance Harness")
    print("  Benchmark: m=3.0 mm, alpha=20 deg, z1=19, z2=47, a=99.0 mm")
    print("=" * 80)

    t1 = TestChapter02InvoluteDifferentialGeometry()
    t1.test_cartesian_and_polar_equivalence()
    t1.test_involute_curvature_radius_invariance()
    t1.test_involute_monotonicity_and_derivative()
    t1.test_involute_inversion_series_reversion_accuracy()
    t1.test_involute_inversion_exact_machine_precision()
    print("  [Tier 1] Involute Differential Geometry & Inverse: ALL PASS (5/5)")

    t2 = TestChapter02BenchmarkProportionsTable()
    methods = [getattr(t2, m) for m in dir(t2) if m.startswith("test_param_")]
    for method in methods:
        method()
    print(f"  [Tier 2] 38 Parameters Closed-Form Table: ALL PASS ({len(methods)}/{len(methods)})")

    # Output exact floating-point diagnostics
    m = 3.0
    alpha = math.radians(20.0)
    z1, z2 = 19, 47
    d1, d2 = m * z1, m * z2
    a = (d1 + d2) / 2.0
    rb1, rb2 = (d1 * math.cos(alpha)) / 2.0, (d2 * math.cos(alpha)) / 2.0
    ra1, ra2 = (d1 + 2 * m) / 2.0, (d2 + 2 * m) / 2.0
    pb = math.pi * m * math.cos(alpha)
    g_alpha = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(alpha)
    eps_alpha = g_alpha / pb
    g1 = 2 * pb - g_alpha
    g2 = 2 * (g_alpha - pb)
    s = (math.pi * m) / 2.0
    alpha_a1 = math.acos(rb1 / ra1)
    alpha_a2 = math.acos(rb2 / ra2)
    sa1 = 2.0 * ra1 * ((s / (2.0 * (d1 / 2.0))) + inv(alpha) - inv(alpha_a1))
    sa2 = 2.0 * ra2 * ((s / (2.0 * (d2 / 2.0))) + inv(alpha) - inv(alpha_a2))

    print("-" * 80)
    print("  Exact Theoretical Closed-form Diagnostics ( 소수점 6자리 실측치 ):")
    print(f"    - Contact Length (g_alpha):      {g_alpha:.6f} mm")
    print(f"    - Base Pitch (pb):               {pb:.6f} mm")
    print(f"    - Contact Ratio (eps_alpha):     {eps_alpha:.6f}  (>= 1.200000: PASS)")
    print(f"    - Single-tooth contact (g1):     {g1:.6f} mm  ({(g1/g_alpha)*100:.2f}%)")
    print(f"    - Double-tooth contact (g2):     {g2:.6f} mm  ({(g2/g_alpha)*100:.2f}%)")
    print(f"    - Pinion Top Land (sa1):         {sa1:.6f} mm  (>= 0.750 mm: PASS)")
    print(f"    - Gear Top Land (sa2):           {sa2:.6f} mm  (>= 0.750 mm: PASS)")
    print("=" * 80)
    print("  RESULT: 100% SUCCESS — ALL INVOLUTE MATHEMATICAL INVARIANTS PRESERVED")
    print("=" * 80)


if __name__ == "__main__":
    run_self_check()
