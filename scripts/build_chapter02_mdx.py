"""
build_chapter02_mdx.py
================================================================================
Generates 4-language MDX files for Series 1 Part A Chapter 2:
  - ko/series1-theory/part-a-spur/02-involute-geometry.mdx
  - en/series1-theory/part-a-spur/02-involute-geometry.mdx
  - de/series1-theory/part-a-spur/02-involute-geometry.mdx
  - ja/series1-theory/part-a-spur/02-involute-geometry.mdx

Guarantees 100% mathematical invariance and display math block SHA-256 equivalence.
================================================================================
"""

import hashlib
import re
from pathlib import Path

# Shared KaTeX display math blocks (exactly 29 blocks, strictly identical in all 4 languages)
DISPLAY_BLOCKS = [
    # 0: Base circle tangency & string length
    r"\mathbf{r}_T(\theta) = \begin{bmatrix} r_b \cos\theta \\ r_b \sin\theta \end{bmatrix}, \quad L(\theta) = r_b \theta",
    # 1: Cartesian parametric equations
    r"\mathbf{r}_K(\theta) = \mathbf{r}_T(\theta) + L(\theta)\begin{bmatrix} \sin\theta \\ -\cos\theta \end{bmatrix} = \begin{bmatrix} r_b(\cos\theta + \theta\sin\theta) \\ r_b(\sin\theta - \theta\cos\theta) \end{bmatrix}",
    # 2: Velocity & unit normal vector
    r"\mathbf{v}_K(\theta) = \frac{d\mathbf{r}_K}{d\theta} = r_b \theta \begin{bmatrix} \cos\theta \\ \sin\theta \end{bmatrix}, \quad \mathbf{n}(\theta) = \begin{bmatrix} -\sin\theta \\ \cos\theta \end{bmatrix}",
    # 3: Curvature radius
    r"\rho_K(\theta) = \frac{1}{\kappa(\theta)} = r_b \theta = r_b \tan\alpha_K",
    # 4: Radius and roll angle relation
    r"r_K = |\mathbf{r}_K| = r_b \sqrt{1 + \theta^2} = \frac{r_b}{\cos\alpha_K} \quad \Longleftrightarrow \quad \theta = \tan\alpha_K",
    # 5: Polar coordinate system
    r"\begin{cases} r(\alpha) = \dfrac{r_b}{\cos\alpha} \\ \theta_k(\alpha) = \tan\alpha - \alpha = \mathrm{inv}\,\alpha \end{cases}",
    # 6: Involute function definition
    r"\mathrm{inv}\,\alpha \equiv \tan\alpha - \alpha",
    # 7: Strict monotonicity
    r"\frac{d}{d\alpha}(\mathrm{inv}\,\alpha) = \sec^2\alpha - 1 = \tan^2\alpha > 0 \quad \left(\forall \alpha \in \left(0, \frac{\pi}{2}\right)\right)",
    # 8: Taylor series expansion
    r"\mathrm{inv}\,\alpha = \frac{1}{3}\alpha^3 + \frac{2}{15}\alpha^5 + \frac{17}{315}\alpha^7 + \frac{62}{2835}\alpha^9 + \mathcal{O}(\alpha^{11})",
    # 9: Analytical series reversion
    r"\alpha(z) = z - \frac{2}{15}z^3 + \frac{3}{175}z^5 - \frac{2}{1575}z^7 + \mathcal{O}(z^9), \quad z = (3\theta_k)^{1/3}",
    # 10: 1-step Newton-Raphson update
    r"\alpha_{n+1} = \alpha_n - \frac{\tan\alpha_n - \alpha_n - \theta_k}{\tan^2\alpha_n}",
    # 11: Pitch diameter and radius
    r"d = m \cdot z, \quad r = \frac{d}{2} = \frac{m z}{2}",
    # 12: Base circle diameter and radius
    r"d_b = d \cos\alpha = m z \cos\alpha, \quad r_b = \frac{d_b}{2} = \frac{m z \cos\alpha}{2}",
    # 13: Tip circle diameter and radius
    r"d_a = d + 2h_a = m(z + 2h_a^*), \quad r_a = r + h_a^* m",
    # 14: Root circle diameter and radius
    r"d_f = d - 2h_f = m(z - 2(h_a^* + c^*)), \quad r_f = r - (h_a^* + c^*)m",
    # 15: Circular pitch and tooth thickness
    r"p = \pi m = s + e, \quad s = e = \frac{\pi m}{2}",
    # 16: Base pitch
    r"p_b = p \cos\alpha = \pi m \cos\alpha",
    # 17: Tooth half-angle at arbitrary radius
    r"\psi_r = \frac{s}{2r} + \mathrm{inv}\,\alpha - \mathrm{inv}\,\alpha_r \quad \Longrightarrow \quad s_r = 2r \psi_r = r \left[ \frac{s}{r} + 2(\mathrm{inv}\,\alpha - \mathrm{inv}\,\alpha_r) \right]",
    # 18: Top land thickness condition
    r"s_a = r_a \left[ \frac{s}{r} + 2(\mathrm{inv}\,\alpha - \mathrm{inv}\,\alpha_a) \right] \ge 0.25 m, \quad \alpha_a = \arccos\left(\frac{r_b}{r_a}\right)",
    # 19: Center distance and action tangent
    r"a = r_1 + r_2 = \frac{m(z_1 + z_2)}{2}, \quad \overline{T_1 T_2} = (r_{b1} + r_{b2})\tan\alpha = a \sin\alpha",
    # 20: Approach path of contact
    r"g_f = \overline{AP} = \sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha",
    # 21: Recess path of contact
    r"g_a = \overline{PE} = \sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha",
    # 22: Total active path of contact
    r"g_\alpha = g_a + g_f = \sqrt{r_{a1}^2 - r_{b1}^2} + \sqrt{r_{a2}^2 - r_{b2}^2} - a \sin\alpha",
    # 23: Transverse contact ratio
    r"\epsilon_\alpha = \frac{g_\alpha}{p_b} = \frac{\sqrt{r_{a1}^2 - r_{b1}^2} + \sqrt{r_{a2}^2 - r_{b2}^2} - a \sin\alpha}{\pi m \cos\alpha} \ge 1.20",
    # 24: Single and double contact length
    r"g_1 = (2 - \epsilon_\alpha)p_b = 2p_b - g_\alpha, \quad g_2 = 2(\epsilon_\alpha - 1)p_b = 2(g_\alpha - p_b)",
    # 25: Contact conservation
    r"g_1 + g_2 = (2 - \epsilon_\alpha)p_b + 2(\epsilon_\alpha - 1)p_b = g_\alpha",
    # 26: Benchmark gear parameters
    r"m = 3.000000\text{ mm}, \quad \alpha = 20.000000^\circ, \quad z_1 = 19, \quad z_2 = 47, \quad a = 99.000000\text{ mm}",
    # 27: Tip pressure angles
    r"\alpha_{a1} = \arccos\left(\frac{r_{b1}}{r_{a1}}\right) = 31.766779^\circ, \quad \alpha_{a2} = \arccos\left(\frac{r_{b2}}{r_{a2}}\right) = 25.665521^\circ",
    # 28: Numerical contact ratio
    r"g_\alpha = 14.557670\text{ mm}, \quad p_b = 8.856394\text{ mm}, \quad \epsilon_\alpha = \frac{14.557670}{8.856394} = 1.643747"
]

normalized = "\n---\n".join(b.strip() for b in DISPLAY_BLOCKS)
EQ_HASH = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
print(f"Calculated Common equations_hash: {EQ_HASH}")


def format_math_block(idx: int) -> str:
    return f"$$\n{DISPLAY_BLOCKS[idx]}\n$$"


# -----------------------------------------------------------------------------
# Korean Content Generation
# -----------------------------------------------------------------------------
def build_ko() -> str:
    content = r"""---
title: 제2장. 인볼류트 치형 곡선의 기하학과 기초 제원 수학 체계
description: 기초원 실타래 미분기하학 궤적, 인볼류트 함수 inv α의 폐쇄형 역전개, 4대 기본 원과 ISO 53 치형 규격, 그리고 물림선 작용선 상의 정면 물림률 ε_α 닫힌 해 유도까지 다루는 정통 평치차 기하학 제2편
series: theory
part: 1
chapter: 2
gear_type: spur
standards:
  - "KS B 0102"
  - "KS B 0053"
  - "ISO 53:1998"
  - "ISO 21771:2007"
required_diagrams:
  - "fig1_involute_generation"
  - "fig2_involute_function_geometry"
  - "fig3_spur_gear_four_circles"
  - "fig4_line_of_action_contact_path"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-13"
sidebar:
  order: 2
---

## 1. 인볼류트 곡선의 미분기하학적 정의 및 창성 기하학

기계공학에서 평치차(Spur Gear)의 치형 곡선으로 인볼류트(Involute)가 채택된 근본 이유는, 두 기어가 회전할 때 접촉점의 법선이 항상 두 기초원의 공통 내접선을 일관되게 추종하여 중심거리 변동에도 일정한 각속도비를 완벽히 유지하기 때문입니다.

### 기초원 실타래 풀림 기하학

반지름이 $r_b$인 기초원(Base Circle) 중심을 직교좌표계 원점 $O(0, 0)$에 배치합니다. 둘레에 감겨 있는 팽팽한 실(Taut String)을 전개각(Roll Angle) $\theta$ (단위: $\text{rad}$)만큼 반시계 방향으로 풀어낼 때, 기초원 둘레에서 실이 접선 방향으로 떨어져 나가는 접점 $T(\theta)$의 위치 벡터는 다음과 같이 정의됩니다.

__MATH_BLOCK_0__

풀려나온 실의 길이 $L(\theta)$는 기초원 호의 길이와 미끄럼 없이 완전히 일치합니다. 실은 접점 $T$에서 기초원의 접선 방향으로 팽팽히 유지되므로, 실 끝점 $K(\theta)$의 위치 벡터 $\mathbf{r}_K(\theta)$는 기초원 접점 벡터에 접선 방향 벡터를 합성하여 유도됩니다.

__MATH_BLOCK_1__

이것이 인볼류트 곡선의 직교좌표 매개변수 방정식(Cartesian Parametric Equations)입니다.

### 미분기하학적 접선, 법선 및 곡률반경

매개변수 $\theta$에 대한 1계 도함수를 계산하면 인볼류트 곡선의 접선 벡터 및 속도 벡터 $\mathbf{v}_K(\theta)$가 도출됩니다.

__MATH_BLOCK_2__

단위 법선 벡터 $\mathbf{n}(\theta)$는 접점 $T$에서 점 $K$를 향하는 접선 선분과 동일 선상에 놓이며, 항상 기초원 둘레에 접합니다. 미분기하학의 곡률 공식 $\kappa = |d\mathbf{t}/ds|$에 의해 곡률반경 $\rho_K(\theta)$는 정확히 풀려나온 실의 길이 $L(\theta)$와 일치합니다.

__MATH_BLOCK_3__

기초원 상의 시작점($\theta=0$)에서 곡률반경은 $\rho_K = 0$이 되어 첨점(Cusp)을 형성하므로, 인볼류트 치형은 기하학적으로 기초원 안쪽 영역에는 절대 존재할 수 없습니다.

### 전개각 $\theta$와 압력각 $\alpha_K$의 관계 및 극좌표 방정식

원점에서 점 $K$까지의 거리 $r_K$는 피타고라스 정리에 의해 직각삼각형 $\Delta O T K$로부터 결정됩니다.

__MATH_BLOCK_4__

점 $K$에서의 접촉 법선과 원주 속도 벡터(반경선 $OK$에 수직) 사이의 각도를 압력각(Pressure Angle) $\alpha_K$라 정의하면, $\cos\alpha_K = r_b / r_K$가 성립하며 전개각 $\theta$는 압력각의 탄젠트값인 $\theta = \tan\alpha_K$로 귀결됩니다. 기준 반경선으로부터 점 $K$의 극각(Polar Angle) $\theta_k$는 다음과 같이 극좌표계 닫힌 해로 표현됩니다.

__MATH_BLOCK_5__

![그림 1: 기초원 실타래 풀림 기하학과 인볼류트 곡선의 미분기하학적 발생 원리](/images/part2/ko/fig1_involute_generation.png)

---

## 2. 인볼류트 함수 $\mathrm{inv}\,\alpha$의 물리/기하학적 의미 및 연산

### 인볼류트 함수의 물리적 정의

기어 기하학의 핵심 초월함수인 인볼류트 함수(Involute Function)는 다음과 같이 정의됩니다.

__MATH_BLOCK_6__

기하학적으로 $\tan\alpha$는 기초원 반경으로 무차원화된 접선 길이 $L / r_b$를 의미하며, $\alpha$는 접점 반경선 $OT$와 접점-인볼류트 점 반경선 $OK$ 사이의 사잇각($\text{rad}$)을 의미합니다. 따라서 $\mathrm{inv}\,\alpha$는 실이 풀려나가면서 형성되는 순수한 기하학적 각도 위상차를 나타냅니다.

### 엄밀한 단조증가성과 1:1 전단사 대응

인볼류트 함수의 1계 도함수를 해석적으로 전개하면 다음과 같습니다.

__MATH_BLOCK_7__

실무 기어 압력각 범위인 $0 < \alpha < \pi/2$ 구간에서 도함수가 항시 양수($\tan^2\alpha > 0$)이므로, 인볼류트 함수는 엄격한 단조증가(Strictly Monotonic Increasing) 함수입니다. 이에 따라 역함수 $\alpha = \mathrm{inv}^{-1}(\theta_k)$가 단 하나로 유일하게 존재합니다.

### 테일러 급수 역전개(Series Reversion)를 통한 닫힌 해 근사

$\tan\alpha$의 맥클로린 급수 전개로부터 $\mathrm{inv}\,\alpha$의 급수를 도출합니다.

__MATH_BLOCK_8__

주어진 인볼류트 극각 $\theta_k$로부터 압력각 $\alpha$를 직접 계산하기 위해 $z = (3\theta_k)^{1/3}$을 도입하고 급수 역전개(Series Reversion)를 적용하면 $\mathcal{O}(z^9)$까지의 정밀 닫힌 해를 얻을 수 있습니다.

__MATH_BLOCK_9__

이 해석적 역전개식은 상용 기어 압력각 범위($10^\circ \sim 35^\circ$)에서 반복 연산 없이도 오차 $10^{-8}\text{ rad}$ 이하의 정밀도를 보장합니다.

### 1회 반복 초정밀 Newton-Raphson 수렴법

컴퓨터 공학 커널 및 상용 CAE 솔버(H-GEAR STUDIO)에서는 위 급수 역전개값을 초기값 $\alpha_0$로 취한 후 단 1회의 Newton-Raphson 반복을 수행하여 64비트 배정밀도 머신 엡실론($< 10^{-15}\text{ rad}$)에 수렴시킵니다.

__MATH_BLOCK_10__

![그림 2: 인볼류트 함수 inv α의 기하학적 정의 및 호-접선 길이 일치 관계](/images/part2/ko/fig2_involute_function_geometry.png)

---

## 3. 표준 스퍼 기어의 4대 기본 원 및 ISO 53 치형 치수 규격

스퍼 기어의 단품 기하학은 모듈 $m$, 잇수 $z$, 기준 압력각 $\alpha=20^\circ$를 기준으로 4개의 동심원에 의해 완전히 구속됩니다.

### 4대 기본 원의 정의

1. **피치원(Reference Pitch Circle)**: 기어의 맞물림 기준이 되는 직경 $d$의 가상 원.
__MATH_BLOCK_11__
2. **기초원(Base Circle)**: 인볼류트 곡선이 수학적으로 출발하는 직경 $d_b$의 기준 원.
__MATH_BLOCK_12__
3. **이끝원(Tip / Addendum Circle)**: 기어 이의 가장 바깥쪽 외경을 형성하는 직경 $d_a$의 원.
__MATH_BLOCK_13__
4. **이뿌리원(Root / Dedendum Circle)**: 기어 이홈의 바닥면을 형성하는 직경 $d_f$의 원.
__MATH_BLOCK_14__

### ISO 53 / KS B 0053 표준 기본 랙 치형 계수

국제 표준 ISO 53 (Profile A) 및 KS B 0053 표준 평치차 기본 랙 치형 계수는 다음과 같습니다.
- 모듈: $m$
- 기준 압력각: $\alpha = 20.0^\circ$
- 이끝높이 계수: $h_a^* = 1.000 \implies h_a = 1.000 m$
- 이뿌리틈새 계수: $c^* = 0.250 \implies c = 0.250 m$
- 이뿌리높이 계수: $h_f^* = h_a^* + c^* = 1.250 \implies h_f = 1.250 m$
- 전체 치높이 계수: $h^* = h_a^* + h_f^* = 2.250 \implies h = 2.250 m$
- 공구 이끝 둥글기 계수: $\rho_f^* = 0.380 \implies \rho_f = 0.380 m$

### 피치 및 임의 반경 치두께 계산식

피치원 상의 원주 피치 $p$와 치두께 $s$, 치홈 폭 $e$는 다음과 같습니다.

__MATH_BLOCK_15__

기초원 상의 법선 피치 $p_b$는 작용선 상에서 연속된 두 이의 진입 간격과 일치합니다.

__MATH_BLOCK_16__

임의 반경 $r$ ($r \ge r_b$)에서의 압력각을 $\alpha_r = \arccos(r_b / r)$이라 할 때, 인볼류트 곡선의 확산에 따른 치 반각 $\psi_r$ 및 원주 치두께 $s_r$은 다음과 같이 계산됩니다.

__MATH_BLOCK_17__

### 이끝 치두께(Top Land)와 이끝 뾰족화 방지 조건

이끝원 반경 $r_a$에서의 치두께 $s_a$(Top Land)는 열처리 경화 시 이끝 취성 파손 및 치핑을 방지하기 위하여 다음 조건을 반드시 충족해야 합니다.

__MATH_BLOCK_18__

$s_a < 0.25m$인 경우 이끝이 칼날처럼 뾰족해지는 첨두화(Pointed Tooth) 현상이 발생하여 국부 응력 집중과 열처리 균열이 초래됩니다.

![그림 3: 표준 스퍼 기어의 4대 기본 원과 ISO 53 기본 랙 치형 치수 체계](/images/part2/ko/fig3_spur_gear_four_circles.png)

---

## 4. 물림선(Line of Action) 접촉 궤적과 정면 물림률($\epsilon_\alpha$) 닫힌 해 유도

### 물림 작용선과 접촉 특이점

두 기어가 맞물려 회전할 때 접촉점들의 궤적은 두 기초원의 공통 내접선인 **물림선(Line of Action, 작용선)**을 형성합니다. 두 기초원과의 접점을 각각 $T_1$, $T_2$라 하고 중심거리를 $a = r_1 + r_2$라 할 때 접선 선분 길이는 다음과 같습니다.

__MATH_BLOCK_19__

물림선 상의 유효 접촉 궤적은 다음 3대 특이점에 의해 분할됩니다.
- **접촉 시작점 $A$ (SAP)**: 종동 기어(Gear 2)의 이끝원($r_{a2}$)이 작용선과 교차하는 점. 피치점 $P$까지의 거리를 접근 물림길이 $g_f$라 합니다.
__MATH_BLOCK_20__
- **접촉 종료점 $E$ (EAP)**: 구동 기어(Pinion 1)의 이끝원($r_{a1}$)이 작용선과 교차하는 점. 피치점 $P$로부터의 거리를 후퇴 물림길이 $g_a$라 합니다.
__MATH_BLOCK_21__
- **피치점 $P$**: 두 기어의 피치원이 외접하는 순간 중심점.

### 총 유효 물림길이 $g_\alpha$ 및 정면 물림률 $\epsilon_\alpha$

총 유효 물림길이 $g_\alpha$는 접근 물림길이와 후퇴 물림길이의 합으로 정의됩니다.

__MATH_BLOCK_22__

정면 물림률(Transverse Contact Ratio) $\epsilon_\alpha$는 유효 물림길이 $g_\alpha$를 기초원 피치 $p_b$로 나눈 무차원 기하학적 비입니다.

__MATH_BLOCK_23__

### $\epsilon_\alpha \ge 1.20$ 유지의 역학적 필연성과 하중 분담

정면 물림률 $\epsilon_\alpha$는 한 쌍의 이가 접촉을 마치고 떨어지기 전에 다음 이가 얼마나 중첩되어 맞물리는지를 나타냅니다.
1. **단일 치 접촉 구간($g_1$)과 이중 치 접촉 구간($g_2$)의 분할**:
__MATH_BLOCK_24__
__MATH_BLOCK_25__
2. **동력 전달의 연속성**: $\epsilon_\alpha < 1.0$이면 선행 이가 물림을 종료한 후 후속 이가 진입할 때까지 접촉 공백이 발생하여 심각한 충격 타격과 치 파단이 발생합니다.
3. **진동 및 소음(NVH) 저감**: $\epsilon_\alpha \ge 1.20$을 확보하면 전체 접촉 구간의 최소 40% 이상에서 두 쌍의 이가 하중을 안정적으로 분담(Load Sharing)하여 단일 치에 걸리는 최대 굽힘 응력과 접촉 압력을 획기적으로 낮춥니다.

![그림 4: 물림선 작용선 접촉 궤적과 정면 물림률 ε_α 닫힌 해 유도](/images/part2/ko/fig4_line_of_action_contact_path.png)

---

## 5. 실무 계산 예제 (Closed-Form Exact Math Benchmark)

본 섹션에서는 산업 표준 감속기 사양을 모사한 스퍼 기어 쌍에 대하여 연속 미분기하학 닫힌 해 수식으로 38개 파라미터의 소수점 6자리 이론적 참값을 계산하고 검증합니다.

### 벤치마크 기어 쌍 제원

__MATH_BLOCK_26__
- 치형 규격: ISO 53 Profile A ($h_a^* = 1.000000, c^* = 0.250000, h_f^* = 1.250000, \rho_f^* = 0.380000$)
- 전위계수: $x_1 = 0.000000, x_2 = 0.000000$ (표준 무전위 평치차)

이끝원 압력각 및 인볼류트값은 다음과 같이 엄밀하게 계산됩니다.

__MATH_BLOCK_27__

작용선 상의 물림길이 및 물림률 계산값은 다음과 같습니다.

__MATH_BLOCK_28__

### 38개 파라미터 폐쇄형 정밀 참값 계산표

다음 표는 `blog/tests/test_chapter02_math.py` 및 백엔드 지오메트리 하네스에 의해 100% 검증된 38개 파라미터의 기준 계산표입니다.

| 번호 | 기하학적 파라미터 | 기호 | 산출 수식 | 이론적 참값 (Closed-form) | 단위 |
| :---: | :--- | :---: | :--- | :---: | :---: |
| 1 | 감속비 | $u$ | $z_2 / z_1$ | 2.473684 | — |
| 2 | 피니언 피치원 직경 | $d_1$ | $m \cdot z_1$ | 57.000000 | mm |
| 3 | 피니언 피치원 반경 | $r_1$ | $d_1 / 2$ | 28.500000 | mm |
| 4 | 기어 피치원 직경 | $d_2$ | $m \cdot z_2$ | 141.000000 | mm |
| 5 | 기어 피치원 반경 | $r_2$ | $d_2 / 2$ | 70.500000 | mm |
| 6 | 표준 중심거리 | $a$ | $(d_1 + d_2) / 2$ | 99.000000 | mm |
| 7 | 원주 피치 | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | 기준 치두께 및 치홈 폭 | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | 기초원 피치 (법선 피치) | $p_b$ | $\pi m \cos\alpha$ | 8.856394 | mm |
| 10 | 피니언 기초원 직경 | $d_{b1}$ | $d_1 \cos\alpha$ | 53.562479 | mm |
| 11 | 피니언 기초원 반경 | $r_{b1}$ | $d_{b1} / 2$ | 26.781240 | mm |
| 12 | 기어 기초원 직경 | $d_{b2}$ | $d_2 \cos\alpha$ | 132.496660 | mm |
| 13 | 기어 기초원 반경 | $r_{b2}$ | $d_{b2} / 2$ | 66.248330 | mm |
| 14 | 이끝높이 | $h_a$ | $h_a^* \cdot m$ | 3.000000 | mm |
| 15 | 이뿌리높이 | $h_f$ | $(h_a^* + c^*) m$ | 3.750000 | mm |
| 16 | 전체 치높이 | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | 이끝틈새 | $c$ | $c^* \cdot m$ | 0.750000 | mm |
| 18 | 피니언 이끝원 직경 | $d_{a1}$ | $d_1 + 2h_a$ | 63.000000 | mm |
| 19 | 피니언 이끝원 반경 | $r_{a1}$ | $d_{a1} / 2$ | 31.500000 | mm |
| 20 | 기어 이끝원 직경 | $d_{a2}$ | $d_2 + 2h_a$ | 147.000000 | mm |
| 21 | 기어 이끝원 반경 | $r_{a2}$ | $d_{a2} / 2$ | 73.500000 | mm |
| 22 | 피니언 이뿌리원 직경 | $d_{f1}$ | $d_1 - 2h_f$ | 49.500000 | mm |
| 23 | 피니언 이뿌리원 반경 | $r_{f1}$ | $d_{f1} / 2$ | 24.750000 | mm |
| 24 | 기어 이뿌리원 직경 | $d_{f2}$ | $d_2 - 2h_f$ | 133.500000 | mm |
| 25 | 기어 이뿌리원 반경 | $r_{f2}$ | $d_{f2} / 2$ | 66.750000 | mm |
| 26 | 기준 압력각 인볼류트값 | $\mathrm{inv}\,\alpha$ | $\tan 20^\circ - 20^\circ \frac{\pi}{180}$ | 0.014904 | rad |
| 27 | 피니언 이끝원 압력각 | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 31.766779 | deg |
| 28 | 기어 이끝원 압력각 | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.665521 | deg |
| 29 | 피니언 이끝 인볼류트값 | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.064789 | rad |
| 30 | 기어 이끝 인볼류트값 | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.032579 | rad |
| 31 | 피니언 이끝 치두께 (Top Land) | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.065702 | mm |
| 32 | 기어 이끝 치두께 (Top Land) | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.314789 | mm |
| 33 | 후퇴 물림 길이 (피니언 이끝) | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha$ | 6.836008 | mm |
| 34 | 접근 물림 길이 (기어 이끝) | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha$ | 7.721662 | mm |
| 35 | 유효 물림 길이 | $g_\alpha$ | $g_a + g_f$ | 14.557670 | mm |
| 36 | 정면 물림률 | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.643747 | — |
| 37 | 단일 치 접촉 구간 길이 | $g_1$ | $2 p_b - g_\alpha$ | 3.155118 | mm |
| 38 | 이중 치 접촉 구간 길이 | $g_2$ | $2(g_\alpha - p_b)$ | 11.402552 | mm |

본 벤치마크 결과, 피니언 및 대기어의 이끝원 치두께(Top Land)는 각각 $s_{a1}=2.065702\text{ mm}$, $s_{a2}=2.314789\text{ mm}$로 계산되어 안전 하한선인 $0.25m = 0.750000\text{ mm}$를 여유 있게 상회하여 이끝 뾰족화가 완벽히 방지됨을 입증합니다. 또한 정면 물림률은 $\epsilon_\alpha = 1.643747$로 산업 권장 규격인 $1.200000$을 크게 상회하며, 유효 물림 구간의 78.33%($g_2=11.402552\text{ mm}$) 동안 두 쌍의 이가 하중을 안정적으로 분담하여 이상적인 무충격 동력 전달이 실현됩니다.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content



# -----------------------------------------------------------------------------
# English Content Generation
# -----------------------------------------------------------------------------
def build_en() -> str:
    content = r"""---
title: Chapter 2. Involute Tooth Geometry and Mathematical Framework of Fundamental Gear Dimensions
description: From differential geometry of base circle unwinding and closed-form involute series reversion to the 4 fundamental circles, ISO 53 rack proportions, and transverse contact ratio ε_α derivation along the line of action.
series: theory
part: 1
chapter: 2
gear_type: spur
standards:
  - "ISO 53:1998"
  - "ISO 21771:2007"
  - "DIN 3960"
  - "AGMA 9005-F16"
required_diagrams:
  - "fig1_involute_generation"
  - "fig2_involute_function_geometry"
  - "fig3_spur_gear_four_circles"
  - "fig4_line_of_action_contact_path"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-13"
sidebar:
  order: 2
---

## 1. Differential Geometry of Involute Tooth Profile and Curve Generation

The fundamental reason the involute curve is universally adopted as the standard profile for spur gear teeth in mechanical engineering is that the common normal at any instantaneous contact point consistently follows the common internal tangent of the two base circles, ensuring an invariant velocity ratio regardless of center distance variations.

### Base Circle Cord Unwinding Kinematics

Consider a base circle of radius $r_b$ centered at origin $O(0, 0)$ in the Cartesian plane. When a taut string is unwound counterclockwise from the circumference through roll angle $\theta$ (in radians), the position vector of the tangency point $T(\theta)$ on the base circle is defined as:

__MATH_BLOCK_0__

The length of the unwound cord $L(\theta)$ matches the circular arc length of the base circle without slip. Because the string extends along the tangent direction at point $T$, the position vector $\mathbf{r}_K(\theta)$ of the curve tracing end point $K(\theta)$ is derived by vector addition:

__MATH_BLOCK_1__

These equations constitute the Cartesian parametric equations of the circular involute curve.

### Differential Properties: Tangent, Normal, and Radius of Curvature

Differentiating $\mathbf{r}_K(\theta)$ with respect to roll angle $\theta$ gives the velocity vector $\mathbf{v}_K(\theta)$ and unit normal vector $\mathbf{n}(\theta)$:

__MATH_BLOCK_2__

The unit normal vector $\mathbf{n}(\theta)$ aligns precisely with segment $TK$ and remains perpetually tangent to the base circle. Applying the differential curvature relation $\kappa = |d\mathbf{t}/ds|$, the radius of curvature $\rho_K(\theta)$ equals the instantaneous unwound cord length $L(\theta)$:

__MATH_BLOCK_3__

At the base circle origin ($\theta = 0$), the curvature radius vanishes ($\rho_K = 0$), forming a geometric cusp. Consequently, an involute profile cannot physically exist inside its base circle.

### Relation Between Roll Angle $\theta$ and Pressure Angle $\alpha_K$ in Polar Coordinates

The radial distance $r_K$ from origin $O$ to point $K$ is obtained from right triangle $\Delta OTK$:

__MATH_BLOCK_4__

Defining the pressure angle $\alpha_K$ as the angle between the tooth profile normal and the circumferential velocity vector (perpendicular to radius $OK$), the relationship $\cos\alpha_K = r_b / r_K$ holds, yielding $\theta = \tan\alpha_K$. The polar angle $\theta_k$ relative to the start of the involute is given in closed form:

__MATH_BLOCK_5__

![Figure 1: Differential Geometry of Base Circle Cord Unwinding and Involute Curve Generation](/images/part2/en/fig1_involute_generation.png)

---

## 2. Involute Function $\mathrm{inv}\,\alpha$ and Analytical Series Reversion

### Physical and Mathematical Definition

The involute function is an indispensable transcendental function in gear mathematics:

__MATH_BLOCK_6__

Geometrically, $\tan\alpha$ represents the dimensionless unwound cord length $L / r_b$, whereas $\alpha$ denotes the angular offset between tangent radius $OT$ and position vector $OK$. Therefore, $\mathrm{inv}\,\alpha$ represents the net polar angle traversed by the involute curve.

### Strict Monotonicity and Bijective Invertibility

The first derivative of the involute function is strictly positive for all working pressure angles:

__MATH_BLOCK_7__

Because $d(\mathrm{inv}\,\alpha)/d\alpha = \tan^2\alpha > 0$ for all $\alpha \in (0, \pi/2)$, the function is strictly monotonically increasing, guaranteeing that the inverse $\alpha = \mathrm{inv}^{-1}(\theta_k)$ is unique and well-defined.

### Analytical Series Reversion up to $\mathcal{O}(z^9)$

Expanding $\tan\alpha$ into its Maclaurin series yields the series for $\mathrm{inv}\,\alpha$:

__MATH_BLOCK_8__

To compute pressure angle $\alpha$ directly from a given polar angle $\theta_k$ without iterative root-finding, substituting $z = (3\theta_k)^{1/3}$ and performing analytical series reversion yields:

__MATH_BLOCK_9__

This analytical closed-form reversion achieves an absolute angular accuracy of better than $10^{-8}\text{ rad}$ across practical gearing pressure angles ($10^\circ \sim 35^\circ$).

### 1-Step Newton-Raphson Machine-Epsilon Precision

In commercial engineering software kernels such as H-GEAR STUDIO, seeding the Newton-Raphson scheme with the reversion formula achieves 64-bit machine-epsilon precision ($< 10^{-15}\text{ rad}$) in a single update step:

__MATH_BLOCK_10__

![Figure 2: Geometric Interpretation of Involute Function inv α and Arc-Tangent Length Equivalence](/images/part2/en/fig2_involute_function_geometry.png)

---

## 3. Four Fundamental Circles of Spur Gears and ISO 53 Rack Proportions

The individual geometry of a standard spur gear is governed by four concentric circles parameterized by module $m$, tooth count $z$, and reference pressure angle $\alpha = 20^\circ$.

### The Four Fundamental Circles

1. **Reference Pitch Circle**: Kinematic reference cylinder of diameter $d$:
__MATH_BLOCK_11__
2. **Base Circle**: Generating origin of the involute tooth profile of diameter $d_b$:
__MATH_BLOCK_12__
3. **Tip Circle (Addendum Circle)**: Outermost boundary circle of diameter $d_a$:
__MATH_BLOCK_13__
4. **Root Circle (Dedendum Circle)**: Bottom boundary cylinder of diameter $d_f$:
__MATH_BLOCK_14__

### ISO 53 Standard Basic Rack Tooth Profile Proportions

In accordance with ISO 53 (Profile A) and ISO 21771 standard rack parameters:
- Module: $m$
- Reference pressure angle: $\alpha = 20.0^\circ$
- Addendum coefficient: $h_a^* = 1.000 \implies h_a = 1.000 m$
- Bottom clearance coefficient: $c^* = 0.250 \implies c = 0.250 m$
- Dedendum coefficient: $h_f^* = h_a^* + c^* = 1.250 \implies h_f = 1.250 m$
- Whole depth coefficient: $h^* = h_a^* + h_f^* = 2.250 \implies h = 2.250 m$
- Tool tip radius coefficient: $\rho_f^* = 0.380 \implies \rho_f = 0.380 m$

### Pitches and Arc Tooth Thickness Formulation

The circular pitch $p$, standard tooth thickness $s$, and space width $e$ along the pitch circle are:

__MATH_BLOCK_15__

The base pitch $p_b$ along the base circle corresponds to the distance between consecutive profiles along the line of action:

__MATH_BLOCK_16__

At an arbitrary radius $r \ge r_b$ with local pressure angle $\alpha_r = \arccos(r_b / r)$, the tooth half-angle $\psi_r$ and circular tooth thickness $s_r$ are:

__MATH_BLOCK_17__

### Top Land Thickness and Pointed Tooth Prevention Invariant

At the tip circle radius $r_a$, the tooth crest thickness $s_a$ (top land width) must satisfy the strict structural integrity invariant to prevent brittle failure:

__MATH_BLOCK_18__

Any design violating $s_a \ge 0.25m$ creates a sharp knife-edge condition prone to quench cracking and impact flaking.

![Figure 3: Four Fundamental Circles of Spur Gears and ISO 53 Standard Basic Rack Dimensions](/images/part2/en/fig3_spur_gear_four_circles.png)

---

## 4. Line of Action Contact Path and Closed-Form Transverse Contact Ratio $\epsilon_\alpha$

### Action Path Kinematics and Critical Contact Singularities

During conjugate gear rotation, the instantaneous point of contact moves along the **line of action**, which forms the common internal tangent to both base circles. For center distance $a = r_1 + r_2$, the tangent distance is:

__MATH_BLOCK_19__

The active contact path $\overline{AE}$ is bounded by three critical points:
- **Point A (Start of Active Profile, SAP)**: Intersection of the driven gear tip circle ($r_{a2}$) with the line of action. Distance to pitch point $P$ is the approach path length $g_f$:
__MATH_BLOCK_20__
- **Point E (End of Active Profile, EAP)**: Intersection of the driving pinion tip circle ($r_{a1}$) with the line of action. Distance from $P$ is the recess path length $g_a$:
__MATH_BLOCK_21__
- **Pitch Point P**: Instantaneous rolling contact point where the pitch circles meet.

### Total Path of Contact $g_\alpha$ and Transverse Contact Ratio $\epsilon_\alpha$

The total active path of contact $g_\alpha$ is the sum of recess and approach lengths:

__MATH_BLOCK_22__

The transverse contact ratio $\epsilon_\alpha$ expresses the ratio of active contact length to the base pitch $p_b$:

__MATH_BLOCK_23__

### Engineering Necessity of $\epsilon_\alpha \ge 1.20$ and Load Sharing Partitioning

The contact ratio quantifies the angular overlap between successive tooth pairs:
1. **Single-Tooth ($g_1$) and Double-Tooth ($g_2$) Contact Zone Partitioning**:
__MATH_BLOCK_24__
__MATH_BLOCK_25__
2. **Kinematic Continuity**: When $\epsilon_\alpha < 1.0$, a discontinuity occurs where the leading tooth disengages before the trailing tooth engages, producing severe shock loading and tooth breakage.
3. **NVH and Fatigue Attenuation**: Maintaining $\epsilon_\alpha \ge 1.20$ guarantees that dual pairs share transmission loads over at least 40% of the mesh cycle, significantly lowering tooth bending stresses and operational vibration.

![Figure 4: Line of Action Contact Path and Closed-Form Transverse Contact Ratio ε_α Derivation](/images/part2/en/fig4_line_of_action_contact_path.png)

---

## 5. Closed-Form Exact Math Benchmark Verification

This section validates the analytical closed-form equations across 38 fundamental gear parameters to 6 decimal places for an industrial standard spur gear set.

### Benchmark Gear Set Parameters

__MATH_BLOCK_26__
- Tooth profile standard: ISO 53 Profile A ($h_a^* = 1.000000, c^* = 0.250000, h_f^* = 1.250000, \rho_f^* = 0.380000$)
- Profile shift coefficients: $x_1 = 0.000000, x_2 = 0.000000$ (Standard unmodified gearing)

The tip pressure angles and tip involute values are computed analytically:

__MATH_BLOCK_27__

The resulting contact path lengths and transverse contact ratio evaluate to:

__MATH_BLOCK_28__

### 38-Parameter Closed-Form Ground Truth Benchmark Table

The following table presents the exact theoretical values verified by `blog/tests/test_chapter02_math.py` and the H-GEAR STUDIO geometry kernel:

| No. | Geometric Parameter | Symbol | Formula | Theoretical Exact Value (Closed-form) | Unit |
| :---: | :--- | :---: | :--- | :---: | :---: |
| 1 | Gear ratio | $u$ | $z_2 / z_1$ | 2.473684 | — |
| 2 | Pinion reference pitch diameter | $d_1$ | $m \cdot z_1$ | 57.000000 | mm |
| 3 | Pinion reference pitch radius | $r_1$ | $d_1 / 2$ | 28.500000 | mm |
| 4 | Gear reference pitch diameter | $d_2$ | $m \cdot z_2$ | 141.000000 | mm |
| 5 | Gear reference pitch radius | $r_2$ | $d_2 / 2$ | 70.500000 | mm |
| 6 | Standard center distance | $a$ | $(d_1 + d_2) / 2$ | 99.000000 | mm |
| 7 | Circular pitch | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | Standard tooth thickness and space width | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | Base pitch (normal pitch) | $p_b$ | $\pi m \cos\alpha$ | 8.856394 | mm |
| 10 | Pinion base diameter | $d_{b1}$ | $d_1 \cos\alpha$ | 53.562479 | mm |
| 11 | Pinion base radius | $r_{b1}$ | $d_{b1} / 2$ | 26.781240 | mm |
| 12 | Gear base diameter | $d_{b2}$ | $d_2 \cos\alpha$ | 132.496660 | mm |
| 13 | Gear base radius | $r_{b2}$ | $d_{b2} / 2$ | 66.248330 | mm |
| 14 | Addendum | $h_a$ | $h_a^* \cdot m$ | 3.000000 | mm |
| 15 | Dedendum | $h_f$ | $(h_a^* + c^*) m$ | 3.750000 | mm |
| 16 | Whole depth | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | Bottom clearance | $c$ | $c^* \cdot m$ | 0.750000 | mm |
| 18 | Pinion tip diameter | $d_{a1}$ | $d_1 + 2h_a$ | 63.000000 | mm |
| 19 | Pinion tip radius | $r_{a1}$ | $d_{a1} / 2$ | 31.500000 | mm |
| 20 | Gear tip diameter | $d_{a2}$ | $d_2 + 2h_a$ | 147.000000 | mm |
| 21 | Gear tip radius | $r_{a2}$ | $d_{a2} / 2$ | 73.500000 | mm |
| 22 | Pinion root diameter | $d_{f1}$ | $d_1 - 2h_f$ | 49.500000 | mm |
| 23 | Pinion root radius | $r_{f1}$ | $d_{f1} / 2$ | 24.750000 | mm |
| 24 | Gear root diameter | $d_{f2}$ | $d_2 - 2h_f$ | 133.500000 | mm |
| 25 | Gear root radius | $r_{f2}$ | $d_{f2} / 2$ | 66.750000 | mm |
| 26 | Reference pressure angle involute | $\mathrm{inv}\,\alpha$ | $\tan 20^\circ - 20^\circ\frac{\pi}{180}$ | 0.014904 | rad |
| 27 | Pinion tip pressure angle | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 31.766779 | deg |
| 28 | Gear tip pressure angle | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.665521 | deg |
| 29 | Pinion tip involute | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.064789 | rad |
| 30 | Gear tip involute | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.032579 | rad |
| 31 | Pinion top land thickness | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.065702 | mm |
| 32 | Gear top land thickness | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.314789 | mm |
| 33 | Recess path length | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha$ | 6.836008 | mm |
| 34 | Approach path length | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha$ | 7.721662 | mm |
| 35 | Total active path of contact | $g_\alpha$ | $g_a + g_f$ | 14.557670 | mm |
| 36 | Transverse contact ratio | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.643747 | — |
| 37 | Single-tooth contact length | $g_1$ | $2 p_b - g_\alpha$ | 3.155118 | mm |
| 38 | Double-tooth contact length | $g_2$ | $2(g_\alpha - p_b)$ | 11.402552 | mm |

In this benchmark, both the pinion and gear top lands ($s_{a1} = 2.065702\text{ mm}$, $s_{a2} = 2.314789\text{ mm}$) safely surpass the pointed tooth threshold of $0.25m = 0.750000\text{ mm}$. The transverse contact ratio of $\epsilon_\alpha = 1.643747$ comfortably exceeds the minimum requirement of $1.200000$, ensuring smooth, shock-free continuous power transmission with $78.33\%$ double-tooth load sharing.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content



# -----------------------------------------------------------------------------
# German Content Generation
# -----------------------------------------------------------------------------
def build_de() -> str:
    content = r"""---
title: Kapitel 2. Geometrie der Evolventenverzahnung und mathematisches System der Grundabmessungen
description: Von der Differentialgeometrie des Fadenabwickelns und der geschlossenen Umkehrung der Evolventenfunktion inv α bis zu den vier Grundkreisen, ISO 53 Bezugsprofilen und der geschlossenen Herleitung der Profilüberdeckung ε_α auf der Eingriffslinie.
series: theory
part: 1
chapter: 2
gear_type: spur
standards:
  - "DIN 867"
  - "DIN 3960"
  - "ISO 53:1998"
  - "ISO 21771:2007"
required_diagrams:
  - "fig1_involute_generation"
  - "fig2_involute_function_geometry"
  - "fig3_spur_gear_four_circles"
  - "fig4_line_of_action_contact_path"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-13"
sidebar:
  order: 2
---

## 1. Differentialgeometrie der Evolventenkurve und Erzeugungsprinzip

Der grundlegende Grund für die universelle Anwendung der Kreisevolvente als Zahnflankenform für Stirnräder im Maschinenbau liegt darin, dass die Flankennormale in jedem Berührungspunkt stets die gemeinsame innere Tangente der beiden Grundkreise bildet. Dadurch bleibt das Übersetzungsverhältnis selbst bei Achsabstandsabweichungen exakt konstant.

### Kinematik des Fadenabwickelns am Grundkreis

Betrachten wir einen Grundkreis mit Radius $r_b$, dessen Mittelpunkt im Ursprung $O(0, 0)$ des kartesischen Koordinatensystems liegt. Wird ein gespannter Faden um den Abwälzwinkel $\theta$ (in Radiant) gegen den Uhrzeigersinn abgewickelt, so lautet der Ortsvektor des Berührungspunktes $T(\theta)$ auf dem Grundkreis:

__MATH_BLOCK_0__

Die abgewickelte Fadenlänge $L(\theta)$ entspricht exakt der Bogenlänge auf dem Grundkreis ohne Schlupf. Da der Faden tangential vom Punkt $T$ absteht, ergibt sich der Ortsvektor $\mathbf{r}_K(\theta)$ des Kurvenendpunktes $K(\theta)$ durch Vektoraddition:

__MATH_BLOCK_1__

Dies sind die kartesischen Parametergleichungen der Kreisevolvente.

### Differentialgeometrische Flankennormale und Krümmungsradius

Die Ableitung von $\mathbf{r}_K(\theta)$ nach dem Abwälzwinkel $\theta$ liefert den Geschwindigkeitsvektor $\mathbf{v}_K(\theta)$ und den Einheitsnormalenvektor $\mathbf{n}(\theta)$:

__MATH_BLOCK_2__

Der Einheitsnormalenvektor $\mathbf{n}(\theta)$ fällt exakt mit der Fadengeraden $TK$ zusammen und berührt stets den Grundkreis. Gemäß der Frenet-Formel $\kappa = |d\mathbf{t}/ds|$ entspricht der Krümmungsradius $\rho_K(\theta)$ der abgewickelten Fadenlänge $L(\theta)$:

__MATH_BLOCK_3__

Am Schnittpunkt mit dem Grundkreis ($\theta = 0$) verschwindet der Krümmungsradius ($\rho_K = 0$), wodurch eine geometrische Spitze (Spitzpunkt) entsteht. Folglich kann eine Evolventenflanke innerhalb des Grundkreises physikalisch nicht existieren.

### Zusammenhang zwischen Abwälzwinkel $\theta$ und Eingriffswinkel $\alpha_K$

Der Abstand $r_K$ vom Ursprung zum Punkt $K$ ergibt sich aus dem rechtwinkligen Dreieck $\Delta OTK$:

__MATH_BLOCK_4__

Definiert man den Profil-Eingriffswinkel $\alpha_K$ als Winkel zwischen der Flankennormale und der Tangente an den Kreis mit Radius $r_K$, gilt $\cos\alpha_K = r_b / r_K$ und folglich $\theta = \tan\alpha_K$. Der Polarwinkel $\theta_k$ der Evolvente lautet in geschlossener Form:

__MATH_BLOCK_5__

![Abbildung 1: Differentialgeometrie des Fadenabwickelns und Erzeugung der Evolventenkurve](/images/part2/de/fig1_involute_generation.png)

---

## 2. Die Evolventenfunktion $\mathrm{inv}\,\alpha$ und analytische Reiheniumkehrung

### Physikalische und geometrische Definition

Die Evolventenfunktion (Involutfunktion) ist die fundamentale transzendente Funktion der Zahnradgeometrie:

__MATH_BLOCK_6__

Geometrisch beschreibt $\tan\alpha$ die auf den Grundkreisradius bezogene dimensionslose Fadenlänge $L / r_b$, während $\alpha$ die Winkeldifferenz zwischen $OT$ und $OK$ darstellt. $\mathrm{inv}\,\alpha$ ist somit die reine winkelmäßige Auslenkung der Evolvente.

### Strenge Monotonie und Bijektivität

Die erste Ableitung der Evolventenfunktion ist für alle praxisrelevanten Eingriffswinkel positiv:

__MATH_BLOCK_7__

Da $d(\mathrm{inv}\,\alpha)/d\alpha = \tan^2\alpha > 0$ für alle $\alpha \in (0, \pi/2)$, ist die Funktion streng monoton wachsend. Daher existiert die Umkehrfunktion $\alpha = \mathrm{inv}^{-1}(\theta_k)$ eindeutig.

### Analytische Reiheniumkehrung bis $\mathcal{O}(z^9)$

Aus der Maclaurin-Reihe von $\tan\alpha$ folgt die Reihenentwicklung für $\mathrm{inv}\,\alpha$:

__MATH_BLOCK_8__

Zur direkten analytischen Berechnung von $\alpha$ aus einem gegebenen Involutwert $\theta_k$ führt die Substitution $z = (3\theta_k)^{1/3}$ zur Reiheniumkehrung bis zur Ordnung $\mathcal{O}(z^9)$:

__MATH_BLOCK_9__

Diese geschlossene Näherung liefert für praktische Eingriffswinkel ($10^\circ \sim 35^\circ$) ohne Iteration eine Winkelgenauigkeit von besser als $10^{-8}\text{ rad}$.

### 1-Schritt Newton-Raphson Maschinengenauigkeit

Im Berechnungskern von H-GEAR STUDIO wird dieser analytische Startwert $\alpha_0$ in einen einzigen Newton-Raphson-Schritt eingespeist, was unmittelbar zu 64-Bit-Maschinengenauigkeit ($< 10^{-15}\text{ rad}$) führt:

__MATH_BLOCK_10__

![Abbildung 2: Geometrische Definition der Evolventenfunktion inv α und Bogen-Tangenten-Längengleichheit](/images/part2/de/fig2_involute_function_geometry.png)

---

## 3. Die vier Grundkreise von Stirnrädern und Bezugsprofil nach ISO 53 / DIN 867

Die Geometrie eines Standard-Stirnrads wird durch Modul $m$, Zähnezahl $z$ und Normaleingriffswinkel $\alpha = 20^\circ$ über vier konzentrische Kreise vollständig definiert.

### Definition der vier Grundkreise

1. **Teilkreis**: Referenzzylinder des Durchmessers $d$:
__MATH_BLOCK_11__
2. **Grundkreis**: Ursprungskreis der Evolventenverzahnung mit Durchmesser $d_b$:
__MATH_BLOCK_12__
3. **Kopfkreis**: Äußerer Begrenzungsdurchmesser $d_a$:
__MATH_BLOCK_13__
4. **Fußkreis**: Innerer Begrenzungsdurchmesser am Zahngrund $d_f$:
__MATH_BLOCK_14__

### Abmessungen des Norm-Bezugsprofils nach ISO 53 / DIN 867

Gemäß ISO 53 (Profil A) und DIN 867 gelten folgende Bezugsprofil-Koeffizienten:
- Modul: $m$
- Normaleingriffswinkel: $\alpha = 20.0^\circ$
- Kopfhöhenfaktor: $h_a^* = 1.000 \implies h_a = 1.000 m$
- Kopfspielfaktor: $c^* = 0.250 \implies c = 0.250 m$
- Fußhöhenfaktor: $h_f^* = h_a^* + c^* = 1.250 \implies h_f = 1.250 m$
- Gesamtzahnhöhenfaktor: $h^* = h_a^* + h_f^* = 2.250 \implies h = 2.250 m$
- Werkzeug-Kantenrundungsfaktor: $\rho_f^* = 0.380 \implies \rho_f = 0.380 m$

### Teilungen und Bogenzahndicke

Die Teilung am Teilkreis $p$, die Zahndicke $s$ und die Zahnlückenweite $e$ lauten:

__MATH_BLOCK_15__

Die Grundkreisteilung (Eingriffsteilung) $p_b$ entspricht dem Abstand aufeinanderfolgender Flanken auf der Eingriffslinie:

__MATH_BLOCK_16__

Auf einem beliebigen Radius $r \ge r_b$ mit lokalem Eingriffswinkel $\alpha_r = \arccos(r_b / r)$ betragen der halbe Zahnwinkel $\psi_r$ und die Bogenzahndicke $s_r$:

__MATH_BLOCK_17__

### Zahnkopfbreite und Vermeidung von Kopfanspitzung

Am Kopfkreisradius $r_a$ muss die Zahnkopfbreite $s_a$ (Top Land) zur Vermeidung von Sprödbruch und Härtespitzigkeit folgende Bedingung erfüllen:

__MATH_BLOCK_18__

Wird $s_a < 0.25m$ unterschritten, entsteht eine messerscharfe Zahnspitze, die zu Kantenausbrüchen unter Last neigt.

![Abbildung 3: Die vier Grundkreise von Stirnrädern und Bezugsprofil-Abmessungen nach ISO 53](/images/part2/de/fig3_spur_gear_four_circles.png)

---

## 4. Eingriffslinie, Berührungspfad und geschlossene Herleitung der Profilüberdeckung $\epsilon_\alpha$

### Kinematik der Eingriffslinie und charakteristische Punkte

Beim Abwälzen der Zahnflanken wandert der Berührungspunkt entlang der **Eingriffslinie**, welche die gemeinsame innere Tangente der beiden Grundkreise darstellt. Bei Null-Achsabstand $a = r_1 + r_2$ beträgt der Abstand der Tangentenpunkte:

__MATH_BLOCK_19__

Die wirksame Eingriffsstrecke $\overline{AE}$ wird durch drei Hauptpunkte bestimmt:
- **Eingriffsbeginn A (Punkt A)**: Schnittpunkt des Kopfkreises des Rades ($r_{a2}$) mit der Eingriffslinie. Abstand zum Wälzpunkt $P$ ist die Vor-Eingriffsstrecke $g_f$:
__MATH_BLOCK_20__
- **Eingriffsende E (Punkt E)**: Schnittpunkt des Kopfkreises des Ritzels ($r_{a1}$) mit der Eingriffslinie. Abstand zu $P$ ist die Nach-Eingriffsstrecke $g_a$:
__MATH_BLOCK_21__
- **Wälzpunkt P**: Berührungspunkt der beiden Teilkreise auf der Zentrallinie.

### Gesamte Eingriffsstrecke $g_\alpha$ und Profilüberdeckung $\epsilon_\alpha$

Die gesamte Eingriffsstrecke $g_\alpha$ ist die Summe aus Vor- und Nach-Eingriffsstrecke:

__MATH_BLOCK_22__

Die Profilüberdeckung $\epsilon_\alpha$ ist das Verhältnis der Eingriffsstrecke $g_\alpha$ zur Eingriffsteilung $p_b$:

__MATH_BLOCK_23__

### Mechanische Notwendigkeit von $\epsilon_\alpha \ge 1.20$ und Lastaufteilung

Die Profilüberdeckung bestimmt den kontinuierlichen Kraftfluss der Verzahnung:
1. **Aufteilung in Einzeleingriff ($g_1$) und Doppeleingriff ($g_2$)**:
__MATH_BLOCK_24__
__MATH_BLOCK_25__
2. **Kontinuität der Bewegung**: Bei $\epsilon_\alpha < 1.0$ entsteht eine kinematische Lücke, bei der das vorangehende Zahnpaar den Eingriff verlässt, bevor das nachfolgende eingreift. Dies führt zu schweren Stoßbelastungen.
3. **Schwingungs- und Geräuschminderung (NVH)**: Ein Wert von $\epsilon_\alpha \ge 1.20$ stellt sicher, dass über mindestens 40% der Eingriffsdauer zwei Zahnpaare gleichzeitig im Eingriff sind, was die Flankenpressung und Biegespannungen drastisch reduziert.

![Abbildung 4: Eingriffslinie, Berührungspfad und geschlossene Herleitung der Profilüberdeckung ε_α](/images/part2/de/fig4_line_of_action_contact_path.png)

---

## 5. Praxis-Berechnungsbeispiel (Closed-Form Exact Math Benchmark)

In diesem Abschnitt werden alle 38 geometrischen Parameter eines industriellen Stirnradpaares mit geschlossenen Formeln auf 6 Nachkommastellen exakt berechnet.

### Spezifikation des Benchmark-Radsatzes

__MATH_BLOCK_26__
- Bezugsprofil: ISO 53 Profil A ($h_a^* = 1.000000, c^* = 0.250000, h_f^* = 1.250000, \rho_f^* = 0.380000$)
- Profilverschiebungsfaktoren: $x_1 = 0.000000, x_2 = 0.000000$ (Null-Verzahnung)

Die Kopfeingriffswinkel und Kopf-Involutwerte lauten analytisch:

__MATH_BLOCK_27__

Für die Eingriffsstrecken und die Profilüberdeckung ergeben sich:

__MATH_BLOCK_28__

### Exakte 38-Parameter Referenztabelle

Die nachfolgende Tabelle enthält die exakten geschlossenen Referenzwerte, die durch `blog/tests/test_chapter02_math.py` verifiziert sind:

| Nr. | Geometrischer Parameter | Symbol | Berechnungsformel | Theoretischer Exakter Wert (Closed-form) | Einheit |
| :---: | :--- | :---: | :--- | :---: | :---: |
| 1 | Übersetzungsverhältnis | $u$ | $z_2 / z_1$ | 2.473684 | — |
| 2 | Teilkreisdurchmesser Ritzel | $d_1$ | $m \cdot z_1$ | 57.000000 | mm |
| 3 | Teilkreisradius Ritzel | $r_1$ | $d_1 / 2$ | 28.500000 | mm |
| 4 | Teilkreisdurchmesser Rad | $d_2$ | $m \cdot z_2$ | 141.000000 | mm |
| 5 | Teilkreisradius Rad | $r_2$ | $d_2 / 2$ | 70.500000 | mm |
| 6 | Null-Achsabstand | $a$ | $(d_1 + d_2) / 2$ | 99.000000 | mm |
| 7 | Teilung am Teilkreis | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | Zahndicke und Zahnlückenweite | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | Eingriffsteilung (Grundkreisteilung) | $p_b$ | $\pi m \cos\alpha$ | 8.856394 | mm |
| 10 | Grundkreisdurchmesser Ritzel | $d_{b1}$ | $d_1 \cos\alpha$ | 53.562479 | mm |
| 11 | Grundkreisradius Ritzel | $r_{b1}$ | $d_{b1} / 2$ | 26.781240 | mm |
| 12 | Grundkreisdurchmesser Rad | $d_{b2}$ | $d_2 \cos\alpha$ | 132.496660 | mm |
| 13 | Grundkreisradius Rad | $r_{b2}$ | $d_{b2} / 2$ | 66.248330 | mm |
| 14 | Kopfhöhe | $h_a$ | $h_a^* \cdot m$ | 3.000000 | mm |
| 15 | Fußhöhe | $h_f$ | $(h_a^* + c^*) m$ | 3.750000 | mm |
| 16 | Gesamtzahnhöhe | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | Kopfspiel | $c$ | $c^* \cdot m$ | 0.750000 | mm |
| 18 | Kopfkreisdurchmesser Ritzel | $d_{a1}$ | $d_1 + 2h_a$ | 63.000000 | mm |
| 19 | Kopfkreisradius Ritzel | $r_{a1}$ | $d_{a1} / 2$ | 31.500000 | mm |
| 20 | Kopfkreisdurchmesser Rad | $d_{a2}$ | $d_2 + 2h_a$ | 147.000000 | mm |
| 21 | Kopfkreisradius Rad | $r_{a2}$ | $d_{a2} / 2$ | 73.500000 | mm |
| 22 | Fußkreisdurchmesser Ritzel | $d_{f1}$ | $d_1 - 2h_f$ | 49.500000 | mm |
| 23 | Fußkreisradius Ritzel | $r_{f1}$ | $d_{f1} / 2$ | 24.750000 | mm |
| 24 | Fußkreisdurchmesser Rad | $d_{f2}$ | $d_2 - 2h_f$ | 133.500000 | mm |
| 25 | Fußkreisradius Rad | $r_{f2}$ | $d_{f2} / 2$ | 66.750000 | mm |
| 26 | Evolventenwert des Normaleingriffswinkels | $\mathrm{inv}\,\alpha$ | $\tan 20^\circ - 20^\circ\frac{\pi}{180}$ | 0.014904 | rad |
| 27 | Kopf-Eingriffswinkel Ritzel | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 31.766779 | deg |
| 28 | Kopf-Eingriffswinkel Rad | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.665521 | deg |
| 29 | Evolventenwert Kopf Ritzel | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.064789 | rad |
| 30 | Evolventenwert Kopf Rad | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.032579 | rad |
| 31 | Zahnkopfbreite Ritzel | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.065702 | mm |
| 32 | Zahnkopfbreite Rad | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.314789 | mm |
| 33 | Nach-Eingriffsstrecke | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha$ | 6.836008 | mm |
| 34 | Vor-Eingriffsstrecke | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha$ | 7.721662 | mm |
| 35 | Gesamte Eingriffsstrecke | $g_\alpha$ | $g_a + g_f$ | 14.557670 | mm |
| 36 | Profilüberdeckung | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.643747 | — |
| 37 | Einzeleingriffsstrecke | $g_1$ | $2 p_b - g_\alpha$ | 3.155118 | mm |
| 38 | Doppeleingriffsstrecke | $g_2$ | $2(g_\alpha - p_b)$ | 11.402552 | mm |

Die Berechnung zeigt, dass die Zahnkopfbreiten von Ritzel und Rad ($s_{a1} = 2.065702\text{ mm}$, $s_{a2} = 2.314789\text{ mm}$) weit über der Sicherheitsgrenze $0.25m = 0.750000\text{ mm}$ liegen. Eine Kopfanspitzung ist somit ausgeschlossen. Die Profilüberdeckung von $\epsilon_\alpha = 1.643747$ übertrifft die Mindestgrenze von $1.200000$ signifikant, womit ein stoßfreier und geräuscharmer Zahneingriff mit $78.33\%$ Doppeleingriffsdauer gewährleistet ist.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content



# -----------------------------------------------------------------------------
# Japanese Content Generation
# -----------------------------------------------------------------------------
def build_ja() -> str:
    content = r"""---
title: 第2章. インボリュート歯形曲線の幾何学と基本諸元数学体系
description: 基礎円伸開線の微分幾何学軌跡、インボリュート関数 inv αの閉形式逆展開、4大基本円とISO 53標準ラック諸元、そして作用線上の正面かみ合い率 ε_α 閉形式導出までを網羅する平歯車幾何学理論第2編
series: theory
part: 1
chapter: 2
gear_type: spur
standards:
  - "JIS B 0102"
  - "JIS B 1701"
  - "ISO 53:1998"
  - "ISO 21771:2007"
required_diagrams:
  - "fig1_involute_generation"
  - "fig2_involute_function_geometry"
  - "fig3_spur_gear_four_circles"
  - "fig4_line_of_action_contact_path"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-13"
sidebar:
  order: 2
---

## 1. インボリュート歯形曲線の微分幾何学的定義と創成原理

機械工学において平歯車の歯形曲線としてインボリュート（Involute、伸開線）が採用される根本的な理由は、歯車が回転するとき接触点の共通法線が常に2つの基礎円の共通内接線と一致し、中心距離の変動に対しても角速度比を完全に一定に保つことができるためです。

### 基礎円伸開線の幾何学

半径 $r_b$ の基礎円（Base Circle）の中心を直交座標系の原点 $O(0, 0)$ に配置します。基礎円の周囲に巻き付けられた張った糸（Taut String）を展開角（ロール角、Roll Angle） $\theta$ （単位: $\text{rad}$）だけ反時計回りにほどくとき、基礎円上で糸が接線方向に離れる接点 $T(\theta)$ の位置ベクトルは次のように定義されます。

__MATH_BLOCK_0__

ほどけた糸の長さ $L(\theta)$ は基礎円の円弧長さと滑りなく完全に一致します。糸は接点 $T$ において基礎円の接線方向に緊張しているため、糸の端点 $K(\theta)$ の位置ベクトル $\mathbf{r}_K(\theta)$ は基礎円接点ベクトルと接線方向ベクトルの合成によって導かれます。

__MATH_BLOCK_1__

これがインボリュート曲線の直交座標媒介変数方程式（Cartesian Parametric Equations）です。

### 微分幾何学的接線・法線および曲率半径

媒介変数 $\theta$ に関する1階導関数を計算すると、インボリュート曲線の速度ベクトル $\mathbf{v}_K(\theta)$ と単位法線ベクトル $\mathbf{n}(\theta)$ が得られます。

__MATH_BLOCK_2__

単位法線ベクトル $\mathbf{n}(\theta)$ は線分 $TK$ と同一直線上にあり、常に基礎円に接します。微分幾何学の曲率公式 $\kappa = |d\mathbf{t}/ds|$ より、曲率半径 $\rho_K(\theta)$ はほどけた糸の長さ $L(\theta)$ と完全に一致します。

__MATH_BLOCK_3__

基礎円上の開始点（$\theta=0$）において曲率半径は $\rho_K = 0$ となり尖点（Cusp）を形成するため、インボリュート歯形は基礎円の内側領域には幾何学的に決して存在できません。

### 展開角 $\theta$ と圧力角 $\alpha_K$ の関係および極座標方程式

原点から点 $K$ までの半径距離 $r_K$ は直角三角形 $\Delta OTK$ からピタゴラスの定理により導かれます。

__MATH_BLOCK_4__

点 $K$ における歯形法線と円周速度ベクトル（半径線 $OK$ に垂直）とのなす角を圧力角（Pressure Angle） $\alpha_K$ と定義すると、 $\cos\alpha_K = r_b / r_K$ が成り立ち、展開角 $\theta$ は圧力角の正接値 $\theta = \tan\alpha_K$ に帰着します。基準半径線からの極角（Polar Angle） $\theta_k$ は次のような閉形式極座標方程式で表されます。

__MATH_BLOCK_5__

![図 1: 基礎円伸開線幾何学とインボリュート曲線の微分幾何学的創成原理](/images/part2/ja/fig1_involute_generation.png)

---

## 2. インボリュート関数 $\mathrm{inv}\,\alpha$ の物理的・幾何学的意味と数値演算

### インボリュート関数の定義

歯車工学の基礎となる超越関数であるインボリュート関数（Involute Function）は次のように定義されます。

__MATH_BLOCK_6__

幾何学的に $\tan\alpha$ は基礎円半径で無次元化された接線長さ $L / r_b$ を表し、 $\alpha$ は接点半径線 $OT$ と半径線 $OK$ との位相差角（$\text{rad}$）を表します。したがって $\mathrm{inv}\,\alpha$ は、糸がほどけることによって形成される純粋な角度位相変位を意味します。

### 厳密な単調増加性と1対1全単射

インボリュート関数の導関数は実用圧力角の範囲で常に正の値を取ります。

__MATH_BLOCK_7__

$0 < \alpha < \pi/2$ の区間において $d(\mathrm{inv}\,\alpha)/d\alpha = \tan^2\alpha > 0$ であるため、インボリュート関数は厳密に単調増加（Strictly Monotonic Increasing）します。これにより逆関数 $\alpha = \mathrm{inv}^{-1}(\theta_k)$ が一意に存在します。

### テーラー級数逆展開（Series Reversion）による解析的閉形式解

$\tan\alpha$ のマクローリン展開から $\mathrm{inv}\,\alpha$ の級数展開が導かれます。

__MATH_BLOCK_8__

極角 $\theta_k$ から圧力角 $\alpha$ を直接解析的に求めるため、 $z = (3\theta_k)^{1/3}$ を導入して級数逆展開（Series Reversion）を行うと、 $\mathcal{O}(z^9)$ までの高精度な閉形式解が得られます。

__MATH_BLOCK_9__

この解析的逆展開式は、実用歯車の圧力角範囲（$10^\circ \sim 35^\circ$）において反復計算なしで誤差 $10^{-8}\text{ rad}$ 以下の精度を保証します。

### 1回反復ニュートン・ラフソン法によるマシンイプシロン収束

商用CAEエンジニアリングカーネル（H-GEAR STUDIO）では、この級数逆展開値を初期値 $\alpha_0$ として採用し、わずか1回のニュートン・ラフソン反復を行うことで64ビット倍精度マシンイプシロン（$< 10^{-15}\text{ rad}$）へと収束させます。

__MATH_BLOCK_10__

![図 2: インボリュート関数 inv α の幾何学的定義と弧・接線長さ一致関係](/images/part2/ja/fig2_involute_function_geometry.png)

---

## 3. 標準平歯車の4大基本円とISO 53 / JIS B 1701 歯形諸元体系

平歯車の幾何形状は、モジュール $m$、歯数 $z$、基準圧力角 $\alpha=20^\circ$ を基準とする4つの同心円によって完全に規定されます。

### 4大基本円の定義

1. **基準ピッチ円（Reference Pitch Circle）**: かみ合いの基準となる直径 $d$ の円筒面。
__MATH_BLOCK_11__
2. **基礎円（Base Circle）**: インボリュート曲線が発生する直径 $d_b$ の幾何学的基準円。
__MATH_BLOCK_12__
3. **歯先円（Tip / Addendum Circle）**: 歯の最外径を形成する直径 $d_a$ の円。
__MATH_BLOCK_13__
4. **歯底円（Root / Dedendum Circle）**: 歯溝底面を形成する直径 $d_f$ の円。
__MATH_BLOCK_14__

### ISO 53 / JIS B 1701 標準基本ラック歯形諸元

国際規格 ISO 53（Profile A）および JIS B 1701 における標準基本ラック諸元係数は次の通りです。
- モジュール: $m$
- 基準圧力角: $\alpha = 20.0^\circ$
- 歯先たけ係数: $h_a^* = 1.000 \implies h_a = 1.000 m$
- 頂げき係数: $c^* = 0.250 \implies c = 0.250 m$
- 歯底たけ係数: $h_f^* = h_a^* + c^* = 1.250 \implies h_f = 1.250 m$
- 全歯たけ係数: $h^* = h_a^* + h_f^* = 2.250 \implies h = 2.250 m$
- 工具歯先丸み半径係数: $\rho_f^* = 0.380 \implies \rho_f = 0.380 m$

### ピッチおよび任意半径における歯厚計算式

ピッチ円上の円周ピッチ $p$、歯厚 $s$、および歯溝の幅 $e$ は次の関係を満たします。

__MATH_BLOCK_15__

基礎円ピッチ（法線ピッチ） $p_b$ は、かみ合い作用線上における隣接歯面の法線方向間隔に一致します。

__MATH_BLOCK_16__

任意半径 $r \ge r_b$ における局所圧力角を $\alpha_r = \arccos(r_b / r)$ とすると、インボリュート曲線の広がり角を考慮した半歯角 $\psi_r$ および円弧歯厚 $s_r$ は次式で計算されます。

__MATH_BLOCK_17__

### 歯先頂幅（Top Land）と尖頭化防止条件

歯先円半径 $r_a$ における歯先頂幅 $s_a$（Top Land）は、熱処理硬化時の焼割れや衝撃チッピングを防止するため、次の不変条件を満たす必要があります。

__MATH_BLOCK_18__

$s_a < 0.25m$ となると歯先がナイフエッジ状に尖る尖頭化（Pointed Tooth）現象が生じ、歯先の強度低下と熱処理欠陥を招きます。

![図 3: 標準平歯車の4大基本円とISO 53基本ラック歯形諸元体系](/images/part2/ja/fig3_spur_gear_four_circles.png)

---

## 4. かみ合い作用線上の接触軌跡と正面かみ合い率 $\epsilon_\alpha$ 閉形式導出

### 作用線とかみ合い特異点

歯車が回転して動力を伝達するとき、接触点の幾何学的軌跡は2つの基礎円の共通内接線である**かみ合い線（作用線、Line of Action）**を形成します。中心距離を $a = r_1 + r_2$ とするとき、接線線分の長さは次式で表されます。

__MATH_BLOCK_19__

作用線上の有効接触区間は次の3大特異点によって規定されます。
- **かみ合い開始点 A（SAP）**: 被動歯車（Gear 2）の歯先円（$r_{a2}$）が作用線と交差する点。ピッチ点 $P$ までの長さを接近かみ合い長さ $g_f$ と呼びます。
__MATH_BLOCK_20__
- **かみ合い終了点 E（EAP）**: 駆動歯車（Pinion 1）の歯先円（$r_{a1}$）が作用線と交差する点。ピッチ点 $P$ からの長さを遠退かみ合い長さ $g_a$ と呼びます。
__MATH_BLOCK_21__
- **ピッチ点 P**: 2つのピッチ円が接する瞬間中心点。

### 全かみ合い長さ $g_\alpha$ および正面かみ合い率 $\epsilon_\alpha$

全かみ合い長さ $g_\alpha$ は、接近かみ合い長さと遠退かみ合い長さの和として定義されます。

__MATH_BLOCK_22__

正面かみ合い率（Transverse Contact Ratio） $\epsilon_\alpha$ は、全かみ合い長さ $g_\alpha$ を基礎円ピッチ $p_b$ で除した無次元幾何学的比率です。

__MATH_BLOCK_23__

### $\epsilon_\alpha \ge 1.20$ 保持の力学的必然性と荷重分担

かみ合い率は連続した歯車の円滑な動力伝達度合いを定量化する指標です。
1. **単一歯かみ合い区間（$g_1$）と2歯かみ合い区間（$g_2$）の分割**:
__MATH_BLOCK_24__
__MATH_BLOCK_25__
2. **動力伝達の連続性**: $\epsilon_\alpha < 1.0$ の場合、先行する歯がかみ合いを離脱してから後続の歯がかみ合うまでに接触の途切れが生じ、致命的な衝撃衝突と歯の折損が発生します。
3. **振動・騒音（NVH）の抑制**: $\epsilon_\alpha \ge 1.20$ を確保することにより、全かみ合い区間の40%以上において2対の歯が荷重を均等に分担（Load Sharing）し、歯元曲げ応力と接触面圧を大幅に低減できます。

![図 4: かみ合い作用線上の接触軌跡と正面かみ合い率 ε_α 閉形式導出](/images/part2/ja/fig4_line_of_action_contact_path.png)

---

## 5. 実務計算例題（Closed-Form Exact Math Benchmark）

本節では、産業用標準減速機諸元を想定した平歯車対に対し、連続微分幾何学の閉形式数式を用いて38個の幾何パラメータの理論的真値を小数点以下6桁で厳密に計算・検証します。

### ベンチマーク歯車対仕様

__MATH_BLOCK_26__
- 歯形規格: ISO 53 Profile A（$h_a^* = 1.000000, c^* = 0.250000, h_f^* = 1.250000, \rho_f^* = 0.380000$）
- 転位係数: $x_1 = 0.000000, x_2 = 0.000000$（標準無転位歯車）

歯先円圧力角および歯先インボリュート値は次のように厳密に算出されます。

__MATH_BLOCK_27__

作用線長さおよび正面かみ合い率の計算結果は次の通りです。

__MATH_BLOCK_28__

### 38パラメータ閉形式理論的真値計算表

以下の表は `blog/tests/test_chapter02_math.py` によって小数点以下6桁まで完全に立証された38パラメータの基準計算表です。

| 番号 | 幾何学的パラメータ | 記号 | 算出数式 | 理論的真値 (Closed-form) | 単位 |
| :---: | :--- | :---: | :--- | :---: | :---: |
| 1 | 減速比 | $u$ | $z_2 / z_1$ | 2.473684 | — |
| 2 | ピニオン基準ピッチ円直径 | $d_1$ | $m \cdot z_1$ | 57.000000 | mm |
| 3 | ピニオン基準ピッチ円半径 | $r_1$ | $d_1 / 2$ | 28.500000 | mm |
| 4 | 歯車基準ピッチ円直径 | $d_2$ | $m \cdot z_2$ | 141.000000 | mm |
| 5 | 歯車基準ピッチ円半径 | $r_2$ | $d_2 / 2$ | 70.500000 | mm |
| 6 | 標準中心距離 | $a$ | $(d_1 + d_2) / 2$ | 99.000000 | mm |
| 7 | 円周ピッチ | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | 基準歯厚および歯溝の幅 | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | 基礎円ピッチ (法線ピッチ) | $p_b$ | $\pi m \cos\alpha$ | 8.856394 | mm |
| 10 | ピニオン基礎円直径 | $d_{b1}$ | $d_1 \cos\alpha$ | 53.562479 | mm |
| 11 | ピニオン基礎円半径 | $r_{b1}$ | $d_{b1} / 2$ | 26.781240 | mm |
| 12 | 歯車基礎円直径 | $d_{b2}$ | $d_2 \cos\alpha$ | 132.496660 | mm |
| 13 | 歯車基礎円半径 | $r_{b2}$ | $d_{b2} / 2$ | 66.248330 | mm |
| 14 | 歯先たけ | $h_a$ | $h_a^* \cdot m$ | 3.000000 | mm |
| 15 | 歯底たけ | $h_f$ | $(h_a^* + c^*) m$ | 3.750000 | mm |
| 16 | 全歯たけ | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | 頂げき (隙間) | $c$ | $c^* \cdot m$ | 0.750000 | mm |
| 18 | ピニオン歯先円直径 | $d_{a1}$ | $d_1 + 2h_a$ | 63.000000 | mm |
| 19 | ピニオン歯先円半径 | $r_{a1}$ | $d_{a1} / 2$ | 31.500000 | mm |
| 20 | 歯車歯先円直径 | $d_{a2}$ | $d_2 + 2h_a$ | 147.000000 | mm |
| 21 | 歯車歯先円半径 | $r_{a2}$ | $d_{a2} / 2$ | 73.500000 | mm |
| 22 | ピニオン歯底円直径 | $d_{f1}$ | $d_1 - 2h_f$ | 49.500000 | mm |
| 23 | ピニオン歯底円半径 | $r_{f1}$ | $d_{f1} / 2$ | 24.750000 | mm |
| 24 | 歯車歯底円直径 | $d_{f2}$ | $d_2 - 2h_f$ | 133.500000 | mm |
| 25 | 歯車歯底円半径 | $r_{f2}$ | $d_{f2} / 2$ | 66.750000 | mm |
| 26 | 基準圧力角インボリュート値 | $\mathrm{inv}\,\alpha$ | $\tan 20^\circ - 20^\circ\frac{\pi}{180}$ | 0.014904 | rad |
| 27 | ピニオン歯先円圧力角 | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 31.766779 | deg |
| 28 | 歯車歯先円圧力角 | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.665521 | deg |
| 29 | ピニオン歯先インボリュート値 | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.064789 | rad |
| 30 | 歯車歯先インボリュート値 | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.032579 | rad |
| 31 | ピニオン歯先頂幅 | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.065702 | mm |
| 32 | 歯車歯先頂幅 | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.314789 | mm |
| 33 | 遠退かみ合い長さ | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha$ | 6.836008 | mm |
| 34 | 接近かみ合い長さ | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha$ | 7.721662 | mm |
| 35 | 全かみ合い長さ | $g_\alpha$ | $g_a + g_f$ | 14.557670 | mm |
| 36 | 正面かみ合い率 | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.643747 | — |
| 37 | 単一歯かみ合い長さ | $g_1$ | $2 p_b - g_\alpha$ | 3.155118 | mm |
| 38 | 2歯かみ合い長さ | $g_2$ | $2(g_\alpha - p_b)$ | 11.402552 | mm |

本計算結果より、ピニオンおよび大歯車の歯先頂幅（$s_{a1} = 2.065702\text{ mm}$、$s_{a2} = 2.314789\text{ mm}$）は、安全限界である $0.25m = 0.750000\text{ mm}$ を十分に上回り、尖頭化が完全に防止されていることが証明されました。また正面かみ合い率は $\epsilon_\alpha = 1.643747$ となり、推奨値 $1.200000$ を大きく超えて全かみ合い区間の78.33%において2対の歯による安定した荷重分担が実現されています。
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content



def main():
    docs_root = Path("blog/src/content/docs")
    languages = {
        "ko": build_ko(),
        "en": build_en(),
        "de": build_de(),
        "ja": build_ja(),
    }

    for lang, content in languages.items():
        out_dir = docs_root / lang / "series1-theory" / "part-a-spur"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "02-involute-geometry.mdx"
        out_file.write_text(content, encoding="utf-8")
        print(f"Generated: {out_file} ({len(content)} chars)")

        # Verify hash locally
        display_blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
        norm = "\n---\n".join(b.strip() for b in display_blocks)
        cur_hash = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        assert cur_hash == EQ_HASH, f"Hash mismatch in {lang}: {cur_hash} != {EQ_HASH}"
        print(f"  -> Verified {len(display_blocks)} display blocks, hash: {cur_hash} (OK)")

    print("\nAll 4 MDX files generated and verified successfully!")


if __name__ == "__main__":
    main()
