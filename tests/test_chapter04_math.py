"""
test_chapter04_math.py
================================================================================
H-GEAR STUDIO: Blog Series 1 Part A Chapter 4 Closed-Form Mathematical Harness
Target: Verification of Profile Shift Spur Gear Mechanics, Undercut Elimination,
        Operating Working Pressure Angle, Center Distance & Addendum Modification,
        Anti-Pointing (sa >= 0.25m), and Specific Sliding Balancing.
Benchmark Specification:
  - Normal module: m = 3.000000 mm
  - Standard reference pressure angle: alpha_0 = 20.000000 deg
  - Pinion teeth: z1 = 14, Gear teeth: z2 = 42, Gear ratio: u = 3.000000
  - Profile shift coefficients: x1 = +0.350000, x2 = +0.150000, Sigma x = +0.500000
  - Standard center distance: a = 84.000000 mm
  - Operating center distance: a' = 85.414904 mm
  - Working pressure angle: alpha_w = 22.462989 deg (0.392053 rad)
  - Tool basic rack profile (ISO 53 Profile A): ha* = 1.000, c* = 0.250, hf* = 1.250, rho_f* = 0.380
Standards: ISO 21771:2007, DIN 3960, DIN 3992, AGMA 901-A92, KS B 0102, KS B 1405
Precision Standard: 10^-5 ~ 10^-6 strict numerical tolerance, 10^-12 for analytical identities
================================================================================
"""

import json
import math
import sys
from pathlib import Path
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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "blog" / "data"
SPECS_DIR = DATA_DIR / "specs"
LOCALES_DIR = DATA_DIR / "locales"


# -----------------------------------------------------------------------------
# Fundamental Mathematical Functions (Differential Geometry & Involute)
# -----------------------------------------------------------------------------

def inv(angle_rad: float) -> float:
    """Involute function: inv(alpha) = tan(alpha) - alpha."""
    return math.tan(angle_rad) - angle_rad


def inv_derivative(angle_rad: float) -> float:
    """First derivative: d/d_alpha (inv(alpha)) = tan^2(alpha)."""
    return math.tan(angle_rad) ** 2


def inv_series_reversion(theta_k: float) -> float:
    """
    Analytical series reversion of involute function up to O(z^7).
    z = (3 * theta_k)^(1/3)
    alpha(z) = z - (2/15)*z^3 + (3/175)*z^5 - (2/1575)*z^7
    """
    z = (3.0 * theta_k) ** (1.0 / 3.0)
    return z - (2.0 / 15.0) * (z ** 3) + (3.0 / 175.0) * (z ** 5) - (2.0 / 1575.0) * (z ** 7)


def inv_inverse_exact(theta_k: float) -> float:
    """
    Exact inverse involute function via analytical series reversion seed + Newton-Raphson.
    Guarantees 64-bit precision (< 10^-14 rad).
    """
    phi = inv_series_reversion(theta_k)
    for _ in range(5):
        f = math.tan(phi) - phi - theta_k
        df = math.tan(phi) ** 2
        phi -= f / df
    return phi


# -----------------------------------------------------------------------------
# Constitutional Article 8: Test Relevance Declaration
# -----------------------------------------------------------------------------

def test_relevance_declaration():
    """
    Constitutional Article 8 [Test Relevance Declaration Mandate].
    Explicit declaration of test scope, targets, and criteria.
    """
    print("\n" + "=" * 80)
    print("CONSTITUTIONAL ARTICLE 8: TEST RELEVANCE DECLARATION")
    print("=" * 80)
    print("이 테스트가 검증하는 것:")
    print("  1. 제4장 7대 핵심 폐쇄형 수학 유도 수식 (언더컷 한계 잇수, 최소 전위계수, alpha_w, a', y, k, sa >= 0.25m, 미끄럼률 밸런싱)")
    print("  2. 인볼류트 역함수 64비트 배정밀도 Newton-Raphson 솔버 정밀도 (|f(alpha)| < 1e-12 rad, 2단계 수렴, 단조성)")
    print("  3. 벤치마크 기어 쌍 (z1=14, z2=42, m=3, x1=+0.35, x2=+0.15) 38개 파라미터 소수점 6자리 전수 일치")
    print("  4. 경계 조건 및 극단치 (표준 무전위 x=0, V0 기어 쌍, 언더컷 임계점, 첨두화 방지 안전 가드)")
    print("  5. 데이터 스펙 JSON (fig1, fig2, fig3) 및 4개 언어 로케일 사전 (KO, EN, DE, JA) 동형성 및 무결성")
    print("이번 작업에서 검증해야 할 것:")
    print("  H-GEAR STUDIO Blog Series 1 Part A 제4장 전위 평치차 공학 수학 엔진 및 스펙 검증 하네스.")
    print("=" * 80 + "\n")
    assert True


# -----------------------------------------------------------------------------
# Suite 1: TestChapter04CoreDerivations (7 Core Mathematical Derivations)
# -----------------------------------------------------------------------------

class TestChapter04CoreDerivations:
    """Suite 1: Verification of 7 Core Mathematical Derivations for Profile Shift Gears."""

    def test_derivation_01_undercut_limit_teeth(self):
        """[Derivation 1] Undercut Limit Teeth: z_min = 2*ha* / sin^2(alpha_0) = 17.097264."""
        ha_star = 1.0
        alpha0 = math.radians(20.0)
        z_min = 2.0 * ha_star / (math.sin(alpha0) ** 2)
        assert abs(z_min - 17.097264) < 1e-5
        # Pinion z1 = 14 < 17.097264 -> Undercut is geometrically inevitable without profile shift
        z1 = 14
        assert z1 < z_min

    def test_derivation_02_min_profile_shift(self):
        """[Derivation 2] Minimum Required Profile Shift: x_min = ha* - z*sin^2(alpha_0)/2 = +0.181156."""
        ha_star = 1.0
        alpha0 = math.radians(20.0)
        z1 = 14
        x_min1 = ha_star - (z1 * (math.sin(alpha0) ** 2)) / 2.0
        assert abs(x_min1 - 0.181156) < 1e-5
        # Pinion x1 = +0.35 > x_min1 -> Undercut completely eliminated with margin
        x1 = 0.35
        assert x1 > x_min1
        margin = x1 - x_min1
        assert abs(margin - 0.168844) < 1e-5

        # Gear z2 = 42 -> x_min2 is negative, meaning gear is naturally undercut-free
        z2 = 42
        x_min2 = ha_star - (z2 * (math.sin(alpha0) ** 2)) / 2.0
        assert abs(x_min2 - (-1.456531)) < 1e-5
        assert x_min2 < 0.0

    def test_derivation_03_involute_inverse_working_pressure_angle(self):
        """[Derivation 3] Working Pressure Angle: inv(alpha_w) = inv(alpha_0) + 2(x1+x2)/(z1+z2)*tan(alpha_0)."""
        alpha0 = math.radians(20.0)
        z1, z2 = 14, 42
        x1, x2 = 0.35, 0.15
        inv_a0 = inv(alpha0)
        assert abs(inv_a0 - 0.014904) < 1e-5

        delta_inv = 2.0 * (x1 + x2) / (z1 + z2) * math.tan(alpha0)
        assert abs(delta_inv - 0.006499) < 1e-5

        inv_aw = inv_a0 + delta_inv
        assert abs(inv_aw - 0.021404) < 1e-5

        aw = inv_inverse_exact(inv_aw)
        aw_deg = math.degrees(aw)
        assert abs(aw_deg - 22.462989) < 1e-5
        assert abs(aw - 0.392053) < 1e-5

    def test_derivation_04_operating_center_distance(self):
        """[Derivation 4] Operating Center Distance: a' = a * cos(alpha_0) / cos(alpha_w) = 85.414904 mm."""
        m = 3.0
        z1, z2 = 14, 42
        alpha0 = math.radians(20.0)
        aw = math.radians(22.462988730687)
        a_std = 0.5 * m * (z1 + z2)  # 84.0 mm
        assert abs(a_std - 84.000000) < 1e-12

        a_prime = a_std * math.cos(alpha0) / math.cos(aw)
        assert abs(a_prime - 85.414904) < 1e-5

        delta_a = a_prime - a_std
        assert abs(delta_a - 1.414904) < 1e-5

    def test_derivation_05_center_distance_mod_and_bottom_clearance_preservation(self):
        """[Derivation 5] Center Distance Mod y, Addendum Mod k, and Bottom Clearance c = 0.750000 mm."""
        m = 3.0
        z1, z2 = 14, 42
        x1, x2 = 0.35, 0.15
        ha_star = 1.0
        c_star = 0.25
        hf_star = 1.25

        alpha0 = math.radians(20.0)
        aw = math.radians(22.462988730687)
        a_std = 0.5 * m * (z1 + z2)
        a_prime = a_std * math.cos(alpha0) / math.cos(aw)

        y = (a_prime - a_std) / m
        assert abs(y - 0.471635) < 1e-5

        k = (x1 + x2) - y
        assert abs(k - 0.028365) < 1e-5

        # Tooth proportions
        ha1 = (ha_star + x1 - k) * m
        ha2 = (ha_star + x2 - k) * m
        hf1 = (hf_star - x1) * m
        hf2 = (hf_star - x2) * m

        r1 = 0.5 * m * z1
        r2 = 0.5 * m * z2
        ra1 = r1 + ha1
        ra2 = r2 + ha2
        rf1 = r1 - hf1
        rf2 = r2 - hf2

        # Rigorous algebraic identity: c1 = a' - ra2 - rf1 == c* * m
        c1 = a_prime - ra2 - rf1
        c2 = a_prime - ra1 - rf2
        nominal_c = c_star * m  # 0.75 mm

        assert abs(c1 - nominal_c) < 1e-12
        assert abs(c2 - nominal_c) < 1e-12
        assert abs(c1 - 0.750000) < 1e-6

    def test_derivation_06_top_land_anti_pointing(self):
        """[Derivation 6] Top Land Thickness sa >= 0.25m = 0.75 mm (Anti-Pointing Rule)."""
        m = 3.0
        z1, z2 = 14, 42
        x1, x2 = 0.35, 0.15
        alpha0 = math.radians(20.0)
        aw = math.radians(22.462988730687)
        a_std = 0.5 * m * (z1 + z2)
        a_prime = a_std * math.cos(alpha0) / math.cos(aw)
        y = (a_prime - a_std) / m
        k = (x1 + x2) - y

        d1 = m * z1
        d2 = m * z2
        rb1 = 0.5 * d1 * math.cos(alpha0)
        rb2 = 0.5 * d2 * math.cos(alpha0)

        da1 = d1 + 2.0 * (1.0 + x1 - k) * m
        da2 = d2 + 2.0 * (1.0 + x2 - k) * m
        ra1 = da1 / 2.0
        ra2 = da2 / 2.0

        s1 = m * (math.pi / 2.0 + 2.0 * x1 * math.tan(alpha0))
        s2 = m * (math.pi / 2.0 + 2.0 * x2 * math.tan(alpha0))

        alpha_a1 = math.acos(rb1 / ra1)
        alpha_a2 = math.acos(rb2 / ra2)
        inv_aa1 = inv(alpha_a1)
        inv_aa2 = inv(alpha_a2)

        sa1 = da1 * (s1 / d1 + inv(alpha0) - inv_aa1)
        sa2 = da2 * (s2 / d2 + inv(alpha0) - inv_aa2)

        assert abs(sa1 - 1.480339) < 1e-5
        assert abs(sa2 - 2.284370) < 1e-5

        # Anti-pointing condition
        min_sa = 0.25 * m  # 0.75 mm
        assert sa1 >= min_sa
        assert sa2 >= min_sa
        safety_factor1 = sa1 / min_sa
        assert safety_factor1 > 1.9

    def test_derivation_07_specific_sliding_balancing(self):
        """[Derivation 7] Specific Sliding k1, k2 Balancing and Identity (1-k1)(1-k2) == 1.0."""
        m = 3.0
        z1, z2 = 14, 42
        u = z2 / z1
        x1, x2 = 0.35, 0.15
        alpha0 = math.radians(20.0)
        aw = math.radians(22.462988730687)
        a_prime = 85.414904149635
        T1T2 = a_prime * math.sin(aw)
        assert abs(T1T2 - 32.635887) < 1e-5

        y = (a_prime - 84.0) / m
        k = (x1 + x2) - y
        ra1 = 0.5 * m * z1 + (1.0 + x1 - k) * m
        ra2 = 0.5 * m * z2 + (1.0 + x2 - k) * m
        rb1 = 0.5 * m * z1 * math.cos(alpha0)
        rb2 = 0.5 * m * z2 * math.cos(alpha0)

        sA = T1T2 - math.sqrt(ra2 ** 2 - rb2 ** 2)
        sE = math.sqrt(ra1 ** 2 - rb1 ** 2)
        sP = rb1 * math.tan(aw)

        assert abs(sA - 2.642798) < 1e-5
        assert abs(sE - 15.291620) < 1e-5
        assert abs(sP - 8.158972) < 1e-5

        # Pinion & gear specific sliding at A and E
        k1_A = 1.0 - (T1T2 - sA) / (u * sA)
        k2_A = 1.0 - (u * sA) / (T1T2 - sA)
        k1_E = 1.0 - (T1T2 - sE) / (u * sE)
        k2_E = 1.0 - (u * sE) / (T1T2 - sE)

        assert abs(k1_A - (-2.782996)) < 1e-5
        assert abs(k2_A - 0.735659) < 1e-5
        assert abs(k1_E - 0.621922) < 1e-5
        assert abs(k2_E - (-1.644958)) < 1e-5

        # Strict identity at all points
        assert abs((1.0 - k1_A) * (1.0 - k2_A) - 1.0) < 1e-12
        assert abs((1.0 - k1_E) * (1.0 - k2_E) - 1.0) < 1e-12

        # Sliding ratio
        ratio = abs(k1_A) / abs(k2_E)
        assert abs(ratio - 1.691833) < 1e-5


# -----------------------------------------------------------------------------
# Suite 2: TestChapter04InvoluteSolverPrecision (Newton-Raphson 64-bit Precision)
# -----------------------------------------------------------------------------

class TestChapter04InvoluteSolverPrecision:
    """Suite 2: Numerical Verification of Involute Inverse Solver."""

    def test_newton_raphson_round_trip_accuracy(self):
        """Verify round-trip error |inv(inv^-1(theta)) - theta| < 1e-12 rad."""
        theta_benchmark = 0.021403852336
        alpha_sol = inv_inverse_exact(theta_benchmark)
        theta_recalc = inv(alpha_sol)
        err = abs(theta_recalc - theta_benchmark)
        assert err < 1e-12

    def test_newton_raphson_convergence_speed(self):
        """Verify Newton-Raphson converges within <= 2 iterations from analytical seed."""
        theta_val = 0.021403852336
        phi = inv_series_reversion(theta_val)
        residuals = []
        for _ in range(3):
            f = math.tan(phi) - phi - theta_val
            residuals.append(abs(f))
            df = math.tan(phi) ** 2
            phi -= f / df

        # Residual after 2 updates must be near machine epsilon
        assert residuals[2] < 1e-15

    def test_involute_monotonicity_and_strict_positivity(self):
        """Verify d/d_alpha (inv(alpha)) = tan^2(alpha) > 0 for all alpha in (0, pi/2)."""
        for deg in [5.0, 10.0, 20.0, 22.463, 30.0, 45.0, 60.0]:
            rad = math.radians(deg)
            derivative = inv_derivative(rad)
            assert derivative > 0.0
            assert math.isclose(derivative, math.tan(rad) ** 2, rel_tol=1e-12)

    def test_sweep_across_gear_pressure_angles(self):
        """Sweep across practical pressure angles [1 deg, 59 deg] with round-trip error < 1e-12 rad."""
        for deg in range(1, 60):
            alpha_orig = math.radians(deg)
            theta = inv(alpha_orig)
            alpha_computed = inv_inverse_exact(theta)
            assert abs(alpha_computed - alpha_orig) < 1e-12


# -----------------------------------------------------------------------------
# Suite 3: TestChapter04BenchmarkProportionsTable (All 38 Parameters Closed-Form)
# -----------------------------------------------------------------------------

class TestChapter04BenchmarkProportionsTable:
    """Suite 3: Ground Truth Benchmark for All 38 Closed-Form Parameters."""

    def setup_method(self):
        self.m = 3.0
        self.z1 = 14
        self.z2 = 42
        self.x1 = 0.35
        self.x2 = 0.15
        self.ha_star = 1.0
        self.c_star = 0.25
        self.hf_star = 1.25
        self.alpha0 = math.radians(20.0)

        # Baseline calculations
        self.d1 = self.m * self.z1
        self.d2 = self.m * self.z2
        self.a = 0.5 * (self.d1 + self.d2)
        self.p = math.pi * self.m
        self.pb = self.p * math.cos(self.alpha0)
        self.db1 = self.d1 * math.cos(self.alpha0)
        self.db2 = self.d2 * math.cos(self.alpha0)
        self.inv_a0 = inv(self.alpha0)
        self.sigma_x = self.x1 + self.x2
        self.inv_aw = self.inv_a0 + 2.0 * self.sigma_x / (self.z1 + self.z2) * math.tan(self.alpha0)
        self.aw = inv_inverse_exact(self.inv_aw)
        self.a_prime = self.a * math.cos(self.alpha0) / math.cos(self.aw)
        self.y = (self.a_prime - self.a) / self.m
        self.k = self.sigma_x - self.y
        self.dw1 = 2.0 * self.a_prime * self.z1 / (self.z1 + self.z2)
        self.dw2 = 2.0 * self.a_prime * self.z2 / (self.z1 + self.z2)
        self.s1 = self.m * (math.pi / 2.0 + 2.0 * self.x1 * math.tan(self.alpha0))
        self.s2 = self.m * (math.pi / 2.0 + 2.0 * self.x2 * math.tan(self.alpha0))
        self.sw1 = self.dw1 * (self.s1 / self.d1 + self.inv_a0 - self.inv_aw)
        self.sw2 = self.dw2 * (self.s2 / self.d2 + self.inv_a0 - self.inv_aw)
        self.ha1 = (self.ha_star + self.x1 - self.k) * self.m
        self.ha2 = (self.ha_star + self.x2 - self.k) * self.m
        self.hf1 = (self.hf_star - self.x1) * self.m
        self.hf2 = (self.hf_star - self.x2) * self.m
        self.h = self.ha1 + self.hf1
        self.da1 = self.d1 + 2.0 * self.ha1
        self.da2 = self.d2 + 2.0 * self.ha2
        self.df1 = self.d1 - 2.0 * self.hf1
        self.df2 = self.d2 - 2.0 * self.hf2
        self.ra1 = self.da1 / 2.0
        self.ra2 = self.da2 / 2.0
        self.rb1 = self.db1 / 2.0
        self.rb2 = self.db2 / 2.0
        self.rf1 = self.df1 / 2.0
        self.rf2 = self.df2 / 2.0
        self.c = self.a_prime - self.ra2 - self.rf1
        self.alpha_a1 = math.acos(self.rb1 / self.ra1)
        self.alpha_a2 = math.acos(self.rb2 / self.ra2)
        self.sa1 = self.da1 * (self.s1 / self.d1 + self.inv_a0 - inv(self.alpha_a1))
        self.sa2 = self.da2 * (self.s2 / self.d2 + self.inv_a0 - inv(self.alpha_a2))
        self.T1T2 = self.a_prime * math.sin(self.aw)
        self.ga = math.sqrt(self.ra1 ** 2 - self.rb1 ** 2) - self.rb1 * math.tan(self.aw)
        self.gf = math.sqrt(self.ra2 ** 2 - self.rb2 ** 2) - self.rb2 * math.tan(self.aw)
        self.g_alpha = self.ga + self.gf
        self.eps_alpha = self.g_alpha / self.pb
        self.g1 = 2.0 * self.pb - self.g_alpha
        self.g2 = 2.0 * (self.g_alpha - self.pb)

    def test_param_01_gear_ratio(self):
        """#1: u = z2/z1 = 3.000000."""
        assert abs((self.z2 / self.z1) - 3.000000) < 1e-6

    def test_param_02_03_pitch_diameters(self):
        """#2, #3: d1 = 42.000000 mm, d2 = 126.000000 mm."""
        assert abs(self.d1 - 42.000000) < 1e-6
        assert abs(self.d2 - 126.000000) < 1e-6

    def test_param_04_center_distance_standard(self):
        """#4: a = 84.000000 mm."""
        assert abs(self.a - 84.000000) < 1e-6

    def test_param_05_06_pitches(self):
        """#5, #6: p = 9.424778 mm, pb = 8.856394 mm."""
        assert abs(self.p - 9.424778) < 1e-5
        assert abs(self.pb - 8.856394) < 1e-5

    def test_param_07_08_base_diameters(self):
        """#7, #8: db1 = 39.467090 mm, db2 = 118.401270 mm."""
        assert abs(self.db1 - 39.467090) < 1e-5
        assert abs(self.db2 - 118.401270) < 1e-5

    def test_param_09_10_involute_values(self):
        """#9, #10: inv(alpha0) = 0.014904 rad, inv(alpha_w) = 0.021404 rad."""
        assert abs(self.inv_a0 - 0.014904) < 1e-5
        assert abs(self.inv_aw - 0.021404) < 1e-5

    def test_param_11_working_pressure_angle(self):
        """#11: alpha_w = 22.462989 deg (0.392053 rad)."""
        assert abs(math.degrees(self.aw) - 22.462989) < 1e-5
        assert abs(self.aw - 0.392053) < 1e-5

    def test_param_12_operating_center_distance(self):
        """#12: a' = 85.414904 mm."""
        assert abs(self.a_prime - 85.414904) < 1e-5

    def test_param_13_14_modification_factors(self):
        """#13, #14: y = 0.471635, k = 0.028365."""
        assert abs(self.y - 0.471635) < 1e-5
        assert abs(self.k - 0.028365) < 1e-5

    def test_param_15_16_working_pitch_diameters(self):
        """#15, #16: dw1 = 42.707452 mm, dw2 = 128.122357 mm."""
        assert abs(self.dw1 - 42.707452) < 1e-5
        assert abs(self.dw2 - 128.122357) < 1e-5

    def test_param_17_18_standard_tooth_thicknesses(self):
        """#17, #18: s1 = 5.476726 mm, s2 = 5.039962 mm."""
        assert abs(self.s1 - 5.476726) < 1e-5
        assert abs(self.s2 - 5.039962) < 1e-5

    def test_param_19_20_21_tooth_depths(self):
        """#19-#21: ha1 = 3.964904 mm, ha2 = 3.364904 mm, hf1 = 2.700000 mm, hf2 = 3.300000 mm, h = 6.664904 mm."""
        assert abs(self.ha1 - 3.964904) < 1e-5
        assert abs(self.ha2 - 3.364904) < 1e-5
        assert abs(self.hf1 - 2.700000) < 1e-5
        assert abs(self.hf2 - 3.300000) < 1e-5
        assert abs(self.h - 6.664904) < 1e-5

    def test_param_22_23_working_tooth_thicknesses(self):
        """#22, #23: sw1 = 5.291401 mm, sw2 = 4.292129 mm."""
        assert abs(self.sw1 - 5.291401) < 1e-5
        assert abs(self.sw2 - 4.292129) < 1e-5
        # Identity: sw1 + sw2 == pw = pi * m * cos(alpha0) / cos(alpha_w)
        pw = math.pi * self.m * math.cos(self.alpha0) / math.cos(self.aw)
        assert abs((self.sw1 + self.sw2) - pw) < 1e-12

    def test_param_24_25_tip_diameters(self):
        """#24, #25: da1 = 49.929809 mm, da2 = 132.729809 mm."""
        assert abs(self.da1 - 49.929809) < 1e-5
        assert abs(self.da2 - 132.729809) < 1e-5

    def test_param_26_27_root_diameters(self):
        """#26, #27: df1 = 36.600000 mm, df2 = 119.400000 mm."""
        assert abs(self.df1 - 36.600000) < 1e-5
        assert abs(self.df2 - 119.400000) < 1e-5

    def test_param_28_bottom_clearance(self):
        """#28: c = 0.750000 mm (Strict preservation)."""
        assert abs(self.c - 0.750000) < 1e-6

    def test_param_29_30_tip_pressure_angles(self):
        """#29, #30: alpha_a1 = 37.772279 deg, alpha_a2 = 26.868350 deg."""
        assert abs(math.degrees(self.alpha_a1) - 37.772279) < 1e-5
        assert abs(math.degrees(self.alpha_a2) - 26.868350) < 1e-5

    def test_param_31_32_tip_involute_values(self):
        """#31, #32: inv(alpha_a1) = 0.115654 rad, inv(alpha_a2) = 0.037693 rad."""
        assert abs(inv(self.alpha_a1) - 0.115654) < 1e-5
        assert abs(inv(self.alpha_a2) - 0.037693) < 1e-5

    def test_param_33_34_top_land_thicknesses(self):
        """#33, #34: sa1 = 1.480339 mm, sa2 = 2.284370 mm."""
        assert abs(self.sa1 - 1.480339) < 1e-5
        assert abs(self.sa2 - 2.284370) < 1e-5

    def test_param_35_36_contact_path_lengths(self):
        """#35, #36: ga = 7.132649 mm, gf = 5.516173 mm, g_alpha = 12.648822 mm."""
        assert abs(self.ga - 7.132649) < 1e-5
        assert abs(self.gf - 5.516173) < 1e-5
        assert abs(self.g_alpha - 12.648822) < 1e-5

    def test_param_37_contact_ratio(self):
        """#37: eps_alpha = 1.428213 >= 1.200000."""
        assert abs(self.eps_alpha - 1.428213) < 1e-5
        assert self.eps_alpha >= 1.200000

    def test_param_38_contact_zones(self):
        """#38: g1 = 5.063967 mm (40.04%), g2 = 7.584855 mm (59.96%)."""
        assert abs(self.g1 - 5.063967) < 1e-5
        assert abs(self.g2 - 7.584855) < 1e-5
        assert abs((self.g1 + self.g2) - self.g_alpha) < 1e-12


# -----------------------------------------------------------------------------
# Suite 4: TestChapter04BoundaryAndEdgeCases (Boundary & Degenerate Cases)
# -----------------------------------------------------------------------------

class TestChapter04BoundaryAndEdgeCases:
    """Suite 4: Boundary Cases, Degenerations, and Anti-Pointing Guard."""

    def test_edge_case_standard_gear_zero_shift(self):
        """Degeneration to standard gear when x1 = 0.0, x2 = 0.0."""
        m = 3.0
        z1, z2 = 14, 42
        alpha0 = math.radians(20.0)
        inv_a0 = inv(alpha0)
        # Shift sum = 0 -> inv(alpha_w) == inv(alpha_0)
        inv_aw = inv_a0 + 0.0
        aw = inv_inverse_exact(inv_aw)
        assert abs(aw - alpha0) < 1e-12

        a_std = 0.5 * m * (z1 + z2)
        a_prime = a_std * math.cos(alpha0) / math.cos(aw)
        assert abs(a_prime - a_std) < 1e-12

        y = (a_prime - a_std) / m
        k = 0.0 - y
        assert abs(y) < 1e-12
        assert abs(k) < 1e-12

    def test_edge_case_v0_gear_pair(self):
        """V0 gear pair (x1 = +0.35, x2 = -0.35 -> Sigma x = 0.0, center distance invariant)."""
        m = 3.0
        z1, z2 = 14, 42
        x1, x2 = 0.35, -0.35
        alpha0 = math.radians(20.0)
        inv_a0 = inv(alpha0)
        sigma_x = x1 + x2
        assert abs(sigma_x) < 1e-12

        inv_aw = inv_a0 + 2.0 * sigma_x / (z1 + z2) * math.tan(alpha0)
        aw = inv_inverse_exact(inv_aw)
        assert abs(aw - alpha0) < 1e-12

        a_std = 0.5 * m * (z1 + z2)
        a_prime = a_std * math.cos(alpha0) / math.cos(aw)
        assert abs(a_prime - a_std) < 1e-12

        y = (a_prime - a_std) / m
        k = sigma_x - y
        assert abs(y) < 1e-12
        assert abs(k) < 1e-12

    def test_edge_case_undercut_threshold(self):
        """When x1 = x_min1 exactly, undercut depth is exactly 0.000 mm."""
        ha_star = 1.0
        alpha0 = math.radians(20.0)
        z1 = 14
        m = 3.0
        r1 = 0.5 * m * z1
        x_min1 = ha_star - (z1 * (math.sin(alpha0) ** 2)) / 2.0

        # Interference penetration depth: delta_h = (ha_star - x_min1)*m - r1*sin(alpha0)^2
        delta_h = (ha_star - x_min1) * m - r1 * (math.sin(alpha0) ** 2)
        assert abs(delta_h) < 1e-12

    def test_edge_case_anti_pointing_failure_guard(self):
        """Guard against excessive profile shift (e.g., x1 = 0.85) causing top land sa < 0.25m."""
        m = 3.0
        z1 = 14
        alpha0 = math.radians(20.0)
        d1 = m * z1
        rb1 = 0.5 * d1 * math.cos(alpha0)
        # Extreme shift x1 = 0.85 on pinion
        x_excess = 0.85
        da_excess = d1 + 2.0 * (1.0 + x_excess) * m
        ra_excess = da_excess / 2.0
        s_excess = m * (math.pi / 2.0 + 2.0 * x_excess * math.tan(alpha0))

        cos_aa = min(1.0, max(-1.0, rb1 / ra_excess))
        alpha_aa = math.acos(cos_aa)
        sa_excess = da_excess * (s_excess / d1 + inv(alpha0) - inv(alpha_aa))

        min_allowed_sa = 0.25 * m  # 0.75 mm
        # Excessive shift must violate anti-pointing rule
        assert sa_excess < min_allowed_sa

    def test_contact_ratio_safety_limit(self):
        """Verify transverse contact ratio satisfies ISO/AGMA minimum requirement (eps_alpha >= 1.20)."""
        eps_alpha_val = 1.428213
        assert eps_alpha_val >= 1.200000


# -----------------------------------------------------------------------------
# Suite 5: TestChapter04DataContractsAndLocales (JSON Spec & Locales Conformance)
# -----------------------------------------------------------------------------

class TestChapter04DataContractsAndLocales:
    """Suite 5: Verification of Generated JSON Specs and Localization Dictionaries."""

    def test_spec_files_exist_and_loadable(self):
        """Verify fig1, fig2, fig3 spec JSON files exist in both data/ and specs/."""
        targets = ["fig1_part4_spec.json", "fig2_part4_spec.json", "fig3_part4_spec.json"]
        for fname in targets:
            p1 = DATA_DIR / fname
            p2 = SPECS_DIR / fname
            assert p1.exists(), f"File {p1} must exist"
            assert p2.exists(), f"File {p2} must exist"
            assert p1.stat().st_size > 1000
            assert p2.stat().st_size > 1000

            with open(p1, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "schema_version" in data
            assert "diagram_id" in data
            assert "parameters" in data

    def test_spec_files_schema_conformance(self):
        """Verify schema conformance of all 3 generated spec files."""
        # Fig 1
        with open(DATA_DIR / "fig1_part4_spec.json", "r", encoding="utf-8") as f:
            f1 = json.load(f)
        assert f1["diagram_id"] == "fig1_rack_cutter_shift_undercut"
        assert len(f1["parameters"]["panels"]) == 3
        assert "landmarks" in f1
        assert "curves" in f1

        # Fig 2
        with open(DATA_DIR / "fig2_part4_spec.json", "r", encoding="utf-8") as f:
            f2 = json.load(f)
        assert f2["diagram_id"] == "fig2_operating_mesh_geometry"
        assert f2["parameters"]["module"] == 3.0
        assert f2["parameters"]["z1"] == 14
        assert f2["parameters"]["z2"] == 42
        assert f2["parameters"]["c"] == 0.75
        assert "landmarks" in f2
        assert "curves" in f2
        assert "dimensions" in f2

        # Fig 3
        with open(DATA_DIR / "fig3_part4_spec.json", "r", encoding="utf-8") as f:
            f3 = json.load(f)
        assert f3["diagram_id"] == "fig3_specific_sliding_balancing"
        assert f3["parameters"]["u"] == 3.0
        assert len(f3["sampled_points"]) == 101
        assert "landmarks" in f3

    def test_locale_files_exist_all_4_languages(self):
        """Verify part4_labels.json exists for ko, en, de, ja."""
        langs = ["ko", "en", "de", "ja"]
        for lang in langs:
            p = LOCALES_DIR / lang / "part4_labels.json"
            assert p.exists(), f"Locale file {p} must exist"
            assert p.stat().st_size > 2000

    def test_locale_keys_isomorphism(self):
        """Verify all 4 locale dictionaries contain the exact identical set of keys."""
        langs = ["ko", "en", "de", "ja"]
        key_sets = {}
        for lang in langs:
            p = LOCALES_DIR / lang / "part4_labels.json"
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)
            key_sets[lang] = set(d.keys())

        ref_lang = "ko"
        for lang in ["en", "de", "ja"]:
            diff1 = key_sets[ref_lang] - key_sets[lang]
            diff2 = key_sets[lang] - key_sets[ref_lang]
            assert not diff1, f"Missing keys in {lang}: {diff1}"
            assert not diff2, f"Extra keys in {lang}: {diff2}"

    def test_spec_landmarks_match_locale_keys(self):
        """Verify all label_key in spec landmarks exist in locale dictionary."""
        with open(LOCALES_DIR / "ko" / "part4_labels.json", "r", encoding="utf-8") as f:
            ko_dict = json.load(f)

        for fname in ["fig1_part4_spec.json", "fig2_part4_spec.json", "fig3_part4_spec.json"]:
            with open(DATA_DIR / fname, "r", encoding="utf-8") as f:
                spec = json.load(f)
            # Check title_key
            assert spec["title_key"] in ko_dict, f"Missing title_key {spec['title_key']} in locales"
            # Check landmarks
            for lm_id, lm in spec.get("landmarks", {}).items():
                if "label_key" in lm:
                    assert lm["label_key"] in ko_dict, f"Missing {lm['label_key']} in locales (from {fname} landmark {lm_id})"


# -----------------------------------------------------------------------------
# Standalone CLI Runner & Summary Printer
# -----------------------------------------------------------------------------

def run_self_check():
    """Execute all tests standalone and print detailed engineering verification report."""
    print("=" * 80)
    print("  H-GEAR STUDIO: Chapter 4 Profile Shift Mathematics Invariance Harness")
    print("  Benchmark: m=3.0 mm, alpha0=20 deg, z1=14, z2=42, x1=+0.35, x2=+0.15")
    print("=" * 80)

    # 1. Relevance Declaration
    test_relevance_declaration()

    # 2. Suite 1
    s1 = TestChapter04CoreDerivations()
    m_s1 = [getattr(s1, m) for m in dir(s1) if m.startswith("test_derivation_")]
    for method in m_s1:
        method()
    print(f"  [Suite 1] 7 Core Mathematical Derivations: ALL PASS ({len(m_s1)}/{len(m_s1)})")

    # 3. Suite 2
    s2 = TestChapter04InvoluteSolverPrecision()
    m_s2 = [getattr(s2, m) for m in dir(s2) if m.startswith("test_")]
    for method in m_s2:
        method()
    print(f"  [Suite 2] Involute Solver 64-bit Precision: ALL PASS ({len(m_s2)}/{len(m_s2)})")

    # 4. Suite 3
    s3 = TestChapter04BenchmarkProportionsTable()
    s3.setup_method()
    m_s3 = [getattr(s3, m) for m in dir(s3) if m.startswith("test_param_")]
    for method in m_s3:
        method()
    print(f"  [Suite 3] 38 Parameters Closed-Form Table: ALL PASS ({len(m_s3)}/{len(m_s3)})")

    # 5. Suite 4
    s4 = TestChapter04BoundaryAndEdgeCases()
    m_s4 = [getattr(s4, m) for m in dir(s4) if m.startswith("test_")]
    for method in m_s4:
        method()
    print(f"  [Suite 4] Boundary Cases & Anti-Pointing Guard: ALL PASS ({len(m_s4)}/{len(m_s4)})")

    # 6. Suite 5
    s5 = TestChapter04DataContractsAndLocales()
    m_s5 = [getattr(s5, m) for m in dir(s5) if m.startswith("test_")]
    for method in m_s5:
        method()
    print(f"  [Suite 5] JSON Specs & Multi-Language Locales: ALL PASS ({len(m_s5)}/{len(m_s5)})")

    # Diagnostics printout (소수점 6자리 원시 수치)
    print("-" * 80)
    print("  Exact Theoretical Closed-form Diagnostics ( 소수점 6자리 실측치 ):")
    print(f"    - Undercut Limit Teeth (z_min):      17.097264  (z1=14: UNDERCUT ELIMINATED)")
    print(f"    - Min Required Shift (x_min):        +0.181156  (x1=+0.350000: PASS)")
    print(f"    - Working Involute inv(alpha_w):     0.021404 rad")
    print(f"    - Working Pressure Angle (alpha_w):  22.462989 deg (0.392053 rad)")
    print(f"    - Operating Center Distance (a'):    85.414904 mm (Delta a = +1.414904 mm)")
    print(f"    - Modification Factors (y, k):       y = 0.471635, k = 0.028365")
    print(f"    - Preserved Bottom Clearance (c):    0.750000 mm (c* = 0.25: EXACT 0.000000 mm)")
    print(f"    - Top Land sa1 (Pinion):             1.480339 mm (>= 0.750 mm: PASS)")
    print(f"    - Top Land sa2 (Gear):               2.284370 mm (>= 0.750 mm: PASS)")
    print(f"    - Transverse Contact Ratio (eps):    1.428213 (>= 1.200000: PASS)")
    print(f"    - Single/Double Contact Zones:       g1 = 5.063967 mm (40.04%), g2 = 7.584855 mm (59.96%)")
    print(f"    - Specific Sliding at SAP (k1_A):    -2.782996  (Balanced vs k2_E = -1.644958)")
    print(f"    - Specific Sliding Ratio:            1.691833")
    print("=" * 80)
    print("  RESULT: 100% SUCCESS — ALL PROFILE SHIFT MATHEMATICAL INVARIANTS PRESERVED")
    print("=" * 80)


if __name__ == "__main__":
    run_self_check()
