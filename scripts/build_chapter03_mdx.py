"""
build_chapter03_mdx.py
================================================================================
Generates 4-language MDX files for Series 1 Part A Chapter 3:
  - ko/series1-theory/part-a-spur/03-meshing-kinematics.mdx
  - en/series1-theory/part-a-spur/03-meshing-kinematics.mdx
  - de/series1-theory/part-a-spur/03-meshing-kinematics.mdx
  - ja/series1-theory/part-a-spur/03-meshing-kinematics.mdx

Guarantees 100% mathematical invariance and display math block SHA-256 equivalence.
Adheres strictly to Constitutional Article 12 (AdSense Compliance, No AI Clichés,
20-Year CAE Engineer Authentic Voice) and Zero Code / UI terminology.
================================================================================
"""

import hashlib
import re
from pathlib import Path

# Shared KaTeX display math blocks (exactly 30 blocks, strictly identical in all 4 languages)
DISPLAY_BLOCKS = [
    # 0: Continuous meshing condition
    r"\epsilon_\alpha = \frac{g_\alpha}{p_b} \ge 1.20 > 1.0",
    # 1: Action line total tangent length
    r"\overline{T_1 T_2} = (r_{b1} + r_{b2})\tan\alpha_0 = a \sin\alpha_0",
    # 2: Point A (SAP) coordinate
    r"s_A = \overline{T_1 A} = a \sin\alpha_0 - \sqrt{r_{a2}^2 - r_{b2}^2}",
    # 3: Point E (EAP) coordinate
    r"s_E = \overline{T_1 E} = \sqrt{r_{a1}^2 - r_{b1}^2}",
    # 4: Point B (LPSTC) and Point D (HPSTC) coordinates
    r"s_B = s_E - p_b, \quad s_D = s_A + p_b",
    # 5: Point C/P (Pitch point) coordinate
    r"s_C = r_{b1}\tan\alpha_0 = r_1 \sin\alpha_0",
    # 6: Monotonic ordering along line of action
    r"0 < s_A < s_B < s_C < s_D < s_E < \overline{T_1 T_2}",
    # 7: Approach and recess path lengths
    r"g_f = \overline{AP} = s_C - s_A = \sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha_0, \quad g_a = \overline{PE} = s_E - s_C = \sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha_0",
    # 8: Total active path of contact
    r"g_\alpha = g_a + g_f = \sqrt{r_{a1}^2 - r_{b1}^2} + \sqrt{r_{a2}^2 - r_{b2}^2} - a \sin\alpha_0",
    # 9: Base pitch
    r"p_b = p \cos\alpha_0 = \pi m \cos\alpha_0",
    # 10: Transverse contact ratio closed-form
    r"\epsilon_\alpha = \frac{g_\alpha}{p_b} = \frac{\sqrt{r_{a1}^2 - r_{b1}^2} + \sqrt{r_{a2}^2 - r_{b2}^2} - a \sin\alpha_0}{\pi m \cos\alpha_0}",
    # 11: Single and double contact zone lengths
    r"g_1 = \overline{BD} = 2p_b - g_\alpha, \quad g_2 = \overline{AB} + \overline{DE} = 2(g_\alpha - p_b)",
    # 12: Contact zone length conservation
    r"g_1 + g_2 = (2p_b - g_\alpha) + 2(g_\alpha - p_b) = g_\alpha",
    # 13: Linear tangential velocities along line of action
    r"v_{t1}(s) = \omega_1 \rho_1 = \omega_1 s, \quad v_{t2}(s) = \omega_2 \rho_2 = \omega_2 (\overline{T_1 T_2} - s)",
    # 14: Relative sliding velocity along line of action
    r"v_g(s) = v_{t1}(s) - v_{t2}(s) = (\omega_1 + \omega_2)(s - s_C) = (\omega_1 + \omega_2) x",
    # 15: Pinion specific sliding definition
    r"k_1(s) = \frac{v_g(s)}{v_{t1}(s)} = 1 - \frac{\omega_2 \rho_2}{\omega_1 \rho_1} = 1 - \frac{z_1 \rho_2}{z_2 \rho_1} = 1 - \frac{\rho_2}{u \rho_1}",
    # 16: Gear specific sliding definition
    r"k_2(s) = \frac{-v_g(s)}{v_{t2}(s)} = 1 - \frac{\omega_1 \rho_1}{\omega_2 \rho_2} = 1 - \frac{z_2 \rho_1}{z_1 \rho_2} = 1 - \frac{u \rho_1}{\rho_2}",
    # 17: Invariant algebraic identity
    r"(1 - k_1)(1 - k_2) \equiv 1.0",
    # 18: Benchmark gear pair parameters
    r"m = 3.000000\text{ mm}, \quad \alpha_0 = 20.000000^\circ, \quad z_1 = 18, \quad z_2 = 54, \quad a = 108.000000\text{ mm}",
    # 19: Benchmark pitch and base radii
    r"r_1 = 27.000000\text{ mm}, \quad r_2 = 81.000000\text{ mm}, \quad r_{b1} = 25.371701\text{ mm}, \quad r_{b2} = 76.115102\text{ mm}",
    # 20: Numerical contact ratio
    r"g_\alpha = 14.602024\text{ mm}, \quad p_b = 8.856394\text{ mm}, \quad \epsilon_\alpha = \frac{14.602024}{8.856394} = 1.648755",
    # 21: Numerical contact zones
    r"g_1 = 3.110764\text{ mm}\; (21.3037\%), \quad g_2 = 11.491260\text{ mm}\; (78.6963\%)",
    # 22: Specific sliding numerical values at singular points
    r"\begin{cases} k_1(A) = -7.420059, & k_2(A) = +0.881236 \\ k_1(P) = 0.000000, & k_2(P) = 0.000000 \\ k_1(E) = +0.564204, & k_2(E) = -1.294650 \end{cases}",
    # 23: Contact load intensity step function
    r"w_N(s) = \begin{cases} \dfrac{F_n}{b} & (s \in [s_B, s_D]) \\[2ex] \dfrac{F_n}{2b} & (s \in [s_A, s_B) \cup (s_D, s_E]) \end{cases}",
    # 24: 2-axis forces decomposition
    r"F_t = \frac{2000 T_1}{d_1}, \quad F_r = F_t \tan\alpha_0, \quad F_n = \frac{F_t}{\cos\alpha_0} = \sqrt{F_t^2 + F_r^2}",
    # 25: Benchmark forces for T1 = 100 N*m
    r"F_t = 3703.703704\text{ N}, \quad F_r = 1348.037905\text{ N}, \quad F_n = 3941.399157\text{ N}",
    # 26: HPSTC vs EAP tooth bending moment comparison
    r"M_{b,D} = 1.0 F_n \cdot h_D, \quad M_{b,E} \approx 0.5 F_n \cdot h_E \approx 0.5 F_n (1.20 h_D) = 0.60 F_n h_D",
    # 27: HPSTC bending dominance ratio
    r"\frac{M_{b,D}}{M_{b,E}} \approx \frac{1.0 F_n h_D}{0.60 F_n h_D} \approx 1.666667 > 1.0",
    # 28: Shaft bearing reactions on simply supported shaft
    r"R_{Ax} = F_t \frac{L - L_1}{L}, \quad R_{Bx} = F_t \frac{L_1}{L}, \quad R_{Ay} = F_r \frac{L - L_1}{L}, \quad R_{By} = F_r \frac{L_1}{L}",
    # 29: Total radial bearing loads
    r"F_{rA} = \sqrt{R_{Ax}^2 + R_{Ay}^2} = F_n \frac{L - L_1}{L}, \quad F_{rB} = \sqrt{R_{Bx}^2 + R_{By}^2} = F_n \frac{L_1}{L}",
]

normalized = "\n---\n".join(b.strip() for b in DISPLAY_BLOCKS)
EQ_HASH = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
print(f"Calculated Common equations_hash: {EQ_HASH}")


def format_math_block(idx: int) -> str:
    return f"$$\n{DISPLAY_BLOCKS[idx]}\n$$"


# -----------------------------------------------------------------------------
# Korean Content Generation (한국어)
# -----------------------------------------------------------------------------
def build_ko() -> str:
    content = r"""---
title: "제3장. 평치차의 물림 역학: 작용선, 물림률 및 미끄럼률"
description: "작용선 상의 5대 특이점 폐쇄형 기하학 유도, 정면 물림률 ε_α와 1쌍/2쌍 하중 분담 구역 역학, 치면 상대 미끄럼률 k1, k2 분포, 그리고 HPSTC 치근 굽힘 하중 집중과 KS B 0002/1405 도면 요목표 작성까지 다루는 정통 평치차 물림 기구학 제3편"
series: theory
part: 1
chapter: 3
gear_type: spur
standards:
  - "KS B 0102"
  - "KS B 1405"
  - "ISO 21771:2007"
  - "DIN 3960"
required_diagrams:
  - "fig1_line_of_action_five_points"
  - "fig2_tooth_load_sharing"
  - "fig3_contact_kinematics_velocities"
  - "fig4_specific_sliding_curves"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-15"
sidebar:
  order: 3
---

## 3.1 직관적 문제 제기 및 물리적 배경

기어 전동의 기본 목적은 두 축 사이에서 각속도비를 단 한순간의 변동이나 미끄러짐 없이 일정하게 전달하는 것입니다. 평치차 쌍이 맞물려 회전할 때, 동력이 중단 없이 부드럽게 전달되려면 기하학적으로 엄격한 연속 물림 조건이 충족되어야 합니다.

### 연속 전동의 역학적 필연성

선행하는 치 한 쌍이 물림을 종료하고 떨어져 나가기 전에, 반드시 후속 치 한 쌍이 먼저 접촉선에 진입하여 하중을 분담해야 합니다. 만약 선행 치가 떨어져 나갈 때까지 후속 치가 물리지 못한다면 어떻게 되겠습니까?

동력 전달선 상에 물림 단절 구간(Dead Zone)이 발생합니다. 구동축과 피동축 사이의 위상차가 순간적으로 벌어지고, 후속 치가 맞물리는 순간 치면끼리 거대한 충격량($F_{\mathrm{dyn}} = I \frac{d\omega}{dt}$)으로 충돌합니다. 이는 감속기에서 심각한 충격음과 진동을 유발할 뿐만 아니라, 치근에 가해지는 충격 하중으로 인해 이가 순식간에 부러지는 대형 파손 사고로 이어집니다.

따라서 전동의 연속성을 보장하기 위해 한 쌍의 이가 작용선 상에서 접촉을 유지하는 길이($g_\alpha$)는 반드시 인접한 치 사이의 간격인 법선 피치($p_b$)보다 커야 합니다. 이를 정량화한 지표가 정면 물림률(Transverse Contact Ratio, $\epsilon_\alpha$)입니다.

__MATH_BLOCK_0__

산업용 동력 전달 기어 설계에서는 제작 공차, 축의 탄성 휨 변형, 열팽창 등을 고려하여 물림률 $\epsilon_\alpha \ge 1.20$ 이상을 절대적인 최소 한계선으로 규정합니다.

### 치면 접촉 부위별 구름과 미끄럼 메커니즘

기어 치면이 맞물릴 때 모든 위치에서 균일한 마찰 거동이 일어나는 것은 아닙니다. 두 기어의 피치원(Pitch Circle)이 외접하는 피치점(Pitch Point, 점 C/P)에서는 두 치면의 접선 선속도가 완벽히 일치하여 상대 미끄럼 속도가 정확히 0이 되는 **순수 구름 접촉(Pure Rolling)**이 일어납니다.

피치점을 벗어나 이뿌리(Dedendum)나 이끝(Addendum) 쪽으로 이동하면 상황이 완전히 달라집니다. 치형 곡률반경의 차이로 인해 두 치면 사이에 강한 상대 미끄럼 마찰(Sliding Friction)이 발생합니다.

- **이뿌리 근방 (Dedendum Flank)**: 접촉면에서 구름과 미끄럼의 방향이 반대로 작용하는 음(-)의 미끄럼 상태가 형성되어 마찰 전단응력이 치면 안쪽으로 집중됩니다. 이는 반복적인 접촉 피로로 인해 치면 살이 쌀알 크기로 떨어져 나가는 **피팅(Pitting)** 현상의 주원인이 됩니다.
- **이끝 근방 (Addendum Flank)**: 상대 미끄럼 속도가 극대화되는 구간입니다. 고속·고하중 조건에서 윤활유 유막(EHL Film)이 파괴되면 치면 순간 플래시 온도(Flash Temperature)가 급상승하여 금속끼리 순간적으로 녹아붙었다가 뜯겨나가는 **소착(Scuffing/Scoring)**이 발생합니다.

기어가 회전함에 따라 접촉점이 단일 접촉 구간(100% 하중 지탱)과 이중 접촉 구간(하중 분담)을 교번하면서 종합 맞물림 강성(Mesh Stiffness)이 주기적으로 요동치게 됩니다. 이 강성 변동이 바로 감속기 하우징을 울리는 고주파 기어 와인 소음(Gear Whine Noise)의 본질적인 원진력입니다.

---

## 3.2 기하·삼각함수·미적분 기반 정통 수학적 유도

### 작용선(Line of Action)과 접선 선분 길이

인볼류트 치형에서 접촉점의 법선은 항상 두 기어의 기초원에 접하는 공통 내접선을 추종하며, 이 직선을 작용선(Line of Action)이라 부릅니다. 구동 피니언의 기초원 접점을 $T_1$, 피동 대기어의 기초원 접점을 $T_2$라 할 때, 두 접점 사이의 총 선분 길이 $\overline{T_1 T_2}$는 중심거리 $a$와 기준 압력각 $\alpha_0$로부터 폐쇄형으로 유도됩니다.

__MATH_BLOCK_1__

### 작용선 5대 특이점(Five Cardinal Points)의 대수적 닫힌 해

작용선 상에서 맞물림 역학을 지배하는 5대 핵심 특이점의 위치를 구동 피니언 기초원 접점 $T_1$($s = 0.0\text{ mm}$)을 원점으로 하는 1차원 좌표 $s$로 정식화합니다.

1. **점 A (SAP, Start of Active Profile - 맞물림 개시점)**: 피동 대기어의 이끝원(반경 $r_{a2}$)이 작용선과 교차하는 점입니다. 직각삼각형 $\Delta O_2 T_2 A$의 기하 관계로부터 대기어 접점 $T_2$로부터의 거리는 $\sqrt{r_{a2}^2 - r_{b2}^2}$이며, 점 $T_1$으로부터의 좌표 $s_A$는 다음과 같습니다.

__MATH_BLOCK_2__

2. **점 E (EAP, End of Active Profile - 맞물림 종료점)**: 구동 피니언의 이끝원(반경 $r_{a1}$)이 작용선과 교차하는 점입니다. 직각삼각형 $\Delta O_1 T_1 E$로부터 직접 유도됩니다.

__MATH_BLOCK_3__

3. **점 B (LPSTC, Lowest Point of Single Tooth Contact - 최하위 단일 치접촉점)**: 구동 피니언의 선행 치가 점 E에서 물림을 종료하는 순간의 후속 치 접촉 위치입니다. 점 E로부터 법선 피치 $p_b$만큼 안쪽에 위치합니다.

4. **점 D (HPSTC, Highest Point of Single Tooth Contact - 최상위 단일 치접촉점)**: 후속 치 쌍이 점 A에서 새로 맞물림을 시작하는 순간의 선행 치 접촉 위치입니다. 점 A로부터 법선 피치 $p_b$만큼 바깥쪽에 위치합니다.

__MATH_BLOCK_4__

5. **점 C / P (Pitch Point - 피치점)**: 두 기준 피치원이 외접하는 점으로, 순수 구름 접촉이 실현되는 기구학적 기준점입니다.

__MATH_BLOCK_5__

5대 특이점은 작용선 상에서 다음과 같은 엄격한 단조 증가 순서를 유지해야만 간섭이나 물림 단절 없는 정상적인 전동이 성립합니다.

__MATH_BLOCK_6__

![작용선 상의 5대 특이점(A, B, C, D, E)과 물림 길이 기하학](/images/part3/ko/fig1_line_of_action_five_points.png)

### 물림길이 및 정면 물림률의 유도

실제 치면 접촉이 진행되는 구간은 선분 $\overline{AE}$입니다. 이를 피치점 $P$를 기준으로 접근 물림길이($g_f = \overline{AP}$)와 후퇴 물림길이($g_a = \overline{PE}$)로 구분합니다.

__MATH_BLOCK_7__

총 유효 물림길이 $g_\alpha$는 두 물림길이의 합으로 정의됩니다.

__MATH_BLOCK_8__

인접한 치 사이의 작용선 상 간격인 법선 피치(기초원 피치) $p_b$는 원주 피치 $p = \pi m$의 기초원 투영 길이입니다.

__MATH_BLOCK_9__

따라서 정면 물림률 $\epsilon_\alpha$의 최종 닫힌 해 공식은 다음과 같습니다.

__MATH_BLOCK_10__

### 단일 치 및 이중 치 하중 분담 구역의 분할

물림률이 $1.0 < \epsilon_\alpha < 2.0$인 일반 평치차의 접촉선은 하중 분담 양상에 따라 세 구역으로 분할됩니다.

1. **이중 접촉 구간 (Double Tooth Contact Zone, $\overline{AB}$ 및 $\overline{DE}$)**:
   - 두 쌍의 치가 동시에 맞물려 회전하므로 전체 전달 법선력의 약 50%씩을 분담합니다.
   - 각 구간의 길이는 $g_\alpha - p_b$이며, 두 구간의 합계 길이는 $2(g_\alpha - p_b)$입니다.
2. **단일 접촉 구간 (Single Tooth Contact Zone, $\overline{BD}$)**:
   - 오직 한 쌍의 치만이 전체 전달 하중의 100%를 오롯이 지탱하는 극히 가혹한 영역입니다.
   - 단일 접촉 구간의 길이는 $g_1 = s_D - s_B = 2p_b - g_\alpha$입니다.

__MATH_BLOCK_11__

접촉 구간의 보존 법칙에 따라 단일 접촉 길이와 이중 접촉 길이의 합은 정확히 총 물림길이 $g_\alpha$와 일치합니다.

__MATH_BLOCK_12__

![작용선 상의 단일 치 및 이중 치 접촉 구간과 하중 분담율 분포](/images/part3/ko/fig2_tooth_load_sharing.png)

### 기구학적 선속도 및 상대 미끄럼 속도 유도

작용선 상의 임의 위치 $s$에서 두 기어의 치형 곡률반경은 각각 $\rho_1(s) = s$, $\rho_2(s) = \overline{T_1 T_2} - s$입니다. 각속도를 $\omega_1, \omega_2$라 할 때 작용선에 수직한 접선 방향 선속도는 다음과 같습니다.

__MATH_BLOCK_13__

두 치면 사이의 상대 미끄럼 속도 $v_g(s)$는 두 접선 선속도의 대수적 차이로 계산됩니다.

__MATH_BLOCK_14__

피치점 거리 $x = s - s_C$에 대하여 미끄럼 속도는 완전한 1차 선형 함수를 이룹니다. 피치점($x = 0$)에서 $v_g = 0$이 되어 순수 구름 접촉이 실현되며, 피치점을 경계로 미끄럼의 방향(부호)이 정반대로 역전됩니다.

![치면 접촉점에서의 선속도 벡터 분해 및 상대 미끄럼 속도 역전 메커니즘](/images/part3/ko/fig3_contact_kinematics_velocities.png)

### 치면 상대 미끄럼률(Specific Sliding)과 대수 항등식

치면의 마모율과 발열량을 정량화하는 무차원 척도가 상대 미끄럼률(Specific Sliding, $k$)입니다. 이는 미끄럼 속도를 자기 자신의 접선 선속도로 나눈 비율로 정의됩니다.

구동 피니언의 미끄럼률 $k_1(s)$:

__MATH_BLOCK_15__

피동 대기어의 미끄럼률 $k_2(s)$:

__MATH_BLOCK_16__

두 미끄럼률 $k_1$과 $k_2$ 사이에는 잇수비나 압력각에 무관하게 항상 성립하는 불변의 대수 항등식이 존재합니다.

__MATH_BLOCK_17__

곡률반경이 0에 수렴하는 기초원 접점 부근($s \to 0$ 또는 $s \to \overline{T_1 T_2}$)에서는 상대 미끄럼률이 음의 무한대($-\infty$)로 급격히 발산합니다. 피니언의 잇수가 적을수록 점 A(피니언 이뿌리)가 기초원에 매우 가까워지므로, 피니언 치근부의 미끄럼률이 극단적으로 악화됩니다. 이것이 바로 소잇수 피니언에 양(+)의 전위계수($x_1 > 0$)를 부여하여 활성 치형을 기초원 바깥으로 밀어내야 하는 결정적인 공학적 이유입니다.

![작용선 상의 피니언 및 대기어 치면 상대 미끄럼률(Specific Sliding) 곡선 분포](/images/part3/ko/fig4_specific_sliding_curves.png)

---

## 3.3 핵심 공식 요약표 및 38개 파라미터 폐쇄형 계산표

본 장의 벤치마크 기어 쌍 설계 사양은 다음과 같습니다.

__MATH_BLOCK_18__

피치원 및 기초원 기본 기하학적 치수:

__MATH_BLOCK_19__

물림길이 및 정면 물림률 계산 결과:

__MATH_BLOCK_20__

단일 및 이중 하중 분담 구역 분할 결과:

__MATH_BLOCK_21__

5대 특이점에서의 상대 미끄럼률 수치 결과:

__MATH_BLOCK_22__

### 38개 파라미터 폐쇄형 정밀 계산표

아래 표는 $m = 3.0\text{ mm}, z_1 = 18, z_2 = 54, \alpha_0 = 20.0^\circ, a = 108.0\text{ mm}$ 표준 무전위 평치차 쌍에 대한 38개 전 항목 닫힌 해 수치 결과입니다.

| 번호 | 파라미터 명칭 | 기호 | 산출 수식 | 계산값 | 단위 |
|:---:|:---|:---:|:---|:---:|:---:|
| 1 | 감속비 | $u$ | $z_2 / z_1$ | 3.000000 | — |
| 2 | 피니언 피치원 직경 | $d_1$ | $m \cdot z_1$ | 54.000000 | mm |
| 3 | 피니언 피치원 반경 | $r_1$ | $d_1 / 2$ | 27.000000 | mm |
| 4 | 대기어 피치원 직경 | $d_2$ | $m \cdot z_2$ | 162.000000 | mm |
| 5 | 대기어 피치원 반경 | $r_2$ | $d_2 / 2$ | 81.000000 | mm |
| 6 | 표준 중심거리 | $a$ | $(d_1 + d_2) / 2$ | 108.000000 | mm |
| 7 | 원주 피치 | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | 기준 치두께 및 치홈 폭 | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | 법선 피치 (기초원 피치) | $p_b$ | $\pi m \cos\alpha_0$ | 8.856394 | mm |
| 10 | 피니언 기초원 직경 | $d_{b1}$ | $d_1 \cos\alpha_0$ | 50.743402 | mm |
| 11 | 피니언 기초원 반경 | $r_{b1}$ | $d_{b1} / 2$ | 25.371701 | mm |
| 12 | 대기어 기초원 직경 | $d_{b2}$ | $d_2 \cos\alpha_0$ | 152.230205 | mm |
| 13 | 대기어 기초원 반경 | $r_{b2}$ | $d_{b2} / 2$ | 76.115102 | mm |
| 14 | 이끝높이 | $h_a$ | $1.0 \cdot m$ | 3.000000 | mm |
| 15 | 이뿌리높이 | $h_f$ | $1.25 \cdot m$ | 3.750000 | mm |
| 16 | 전체 치높이 | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | 이끝틈새 | $c$ | $0.25 \cdot m$ | 0.750000 | mm |
| 18 | 피니언 이끝원 직경 | $d_{a1}$ | $d_1 + 2h_a$ | 60.000000 | mm |
| 19 | 피니언 이끝원 반경 | $r_{a1}$ | $d_{a1} / 2$ | 30.000000 | mm |
| 20 | 대기어 이끝원 직경 | $d_{a2}$ | $d_2 + 2h_a$ | 168.000000 | mm |
| 21 | 대기어 이끝원 반경 | $r_{a2}$ | $d_{a2} / 2$ | 84.000000 | mm |
| 22 | 피니언 이뿌리원 직경 | $d_{f1}$ | $d_1 - 2h_f$ | 46.500000 | mm |
| 23 | 피니언 이뿌리원 반경 | $r_{f1}$ | $d_{f1} / 2$ | 23.250000 | mm |
| 24 | 대기어 이뿌리원 직경 | $d_{f2}$ | $d_2 - 2h_f$ | 154.500000 | mm |
| 25 | 대기어 이뿌리원 반경 | $r_{f2}$ | $d_{f2} / 2$ | 77.250000 | mm |
| 26 | 기준 압력각 인볼류트값 | $\mathrm{inv}\,\alpha_0$ | $\tan 20^\circ - 20^\circ \frac{\pi}{180}$ | 0.014904 | rad |
| 27 | 피니언 이끝원 압력각 | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 32.250479 | deg |
| 28 | 대기어 이끝원 압력각 | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.023798 | deg |
| 29 | 피니언 이끝 인볼류트값 | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.068088 | rad |
| 30 | 대기어 이끝 인볼류트값 | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.030066 | rad |
| 31 | 피니언 이끝 치두께 | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.044991 | mm |
| 32 | 대기어 이끝 치두께 | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.339811 | mm |
| 33 | 후퇴 물림 길이 | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha_0$ | 6.774104 | mm |
| 34 | 접근 물림 길이 | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha_0$ | 7.827921 | mm |
| 35 | 유효 물림 길이 | $g_\alpha$ | $g_a + g_f$ | 14.602024 | mm |
| 36 | 정면 물림률 | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.648755 | — |
| 37 | 단일 치 접촉 구간 길이 | $g_1$ | $2 p_b - g_\alpha$ | 3.110764 | mm |
| 38 | 이중 치 접촉 구간 길이 | $g_2$ | $2(g_\alpha - p_b)$ | 11.491260 | mm |

본 계산 결과에서 이끝 치두께 $s_{a1} = 2.044991\text{ mm} > 0.25m = 0.75\text{ mm}$를 만족하여 첨두화(Pointed Tooth) 위험이 전혀 없으며, 물림률 $\epsilon_\alpha = 1.648755$는 추천 설계 기준인 1.20을 여유 있게 상회하여 전체 접촉 선분의 78.70%가 2쌍 접촉으로 안정되게 유지됨이 확인됩니다.

---

## 3.4 정밀 치수 검사 공학 및 치면 손상 메커니즘

### 하중 분담율 계단 함수와 치면 손상

기어가 회전하면서 접촉선 단위 치폭당 작용하는 법선 하중 $w_N(s)$은 이중 접촉 구간과 단일 접촉 구간 사이에서 급격한 계단형 전이를 겪습니다.

__MATH_BLOCK_23__

치폭을 $b$, 총 전달 법선력을 $F_n$이라 할 때, 단일 접촉 구간인 선분 $\overline{BD}$에 진입하는 순간 치면이 받는 하중 강도는 순식간에 2배로 폭증합니다.

### 피팅(Pitting)의 발생 기전

피팅은 치면에 가해지는 반복 접촉 응력으로 인해 금속 표면하에 미세 균열이 발생하여 살점이 탈락하는 피로 손상입니다.
- 발생 위치: 피치선 바로 아래쪽의 피니언 이뿌리 치면(선분 $\overline{BC}$ 부근)에서 가장 집중적으로 발생합니다.
- 물리적 이유: 피치선 직하부는 구름 운동과 음(-)의 미끄럼 운동이 공존하며, 단일 접촉 구간($\overline{BD}$)에 속해 100%의 최대 하중이 작용합니다. 접촉 타원 중심부 아래 표면하 깊이($z \approx 0.78 b_H$)에서 최대 전단응력($\tau_{\max} \approx 0.30 p_0$)이 발생하고, 표면으로 전파된 균열 안으로 윤활유가 유입된 후 접촉 압력이 입구를 밀폐하면서 내부 유압이 폭증하는 유압 쐐기 효과(Hydraulic Wedge Effect)로 인해 표면 조각이 뜯겨 나가게 됩니다.

### 스코어링(Scuffing/Scoring)의 발생 기전

스코어링은 마찰열에 의해 유막이 순식간에 기화·파괴되면서 치면의 돌기들이 금속 접촉하여 순간 용착(Welding)되었다가 뜯겨 나가는 열적 손상입니다.
- 발생 위치: 작용선 양 끝단인 점 A(피니언 이뿌리/대기어 이끝)와 점 E(피니언 이끝/대기어 이뿌리)에서 발생합니다.
- 물리적 이유: 미끄럼 속도 $v_g$가 극대화되는 지점으로, Blok의 접촉 플래시 온도 이론에 따라 마찰 발열량이 윤활유의 한계 온도를 초과하기 때문입니다.

---

## 3.5 KS B 0002 / KS B 1405 도면 요목표 작성 실무

기어 설계 결과물은 최종적으로 공작기계 가공 및 정밀 측정 검사를 위한 제작 도면 요목표로 완성되어야 합니다. 아래 표는 한국산업표준 KS B 0002(기어 제도) 및 KS B 1405(평치차 및 헬리컬 기어 기본 랙)에 따른 본 벤치마크 기어 쌍의 정식 도면 요목표입니다.

| 항목 (Item) | 설계 데이터 (Data) - 피니언 | 설계 데이터 (Data) - 대기어 | 비고 및 준수 표준 |
|:---|:---:|:---:|:---|
| **기어 치형 (Tooth Profile)** | 표준 인벌류트 (Standard Involute) | 표준 인벌류트 (Standard Involute) | KS B 0102 |
| **기준 랙 치형 (Basic Rack)** | 원통기어용 표준 랙 | 원통기어용 표준 랙 | KS B 1405 / ISO 53 Profile A |
| **모듈 (Module, $m$)** | 3.000 mm | 3.000 mm | 표준 제1계열 |
| **기준 압력각 (Standard Pressure Angle, $\alpha_0$)** | 20.0° | 20.0° | 기본 치형 기준 |
| **잇수 (Number of Teeth, $z$)** | 18 | 54 | 감속비 $u = 3.000$ |
| **전위계수 (Profile Shift Coefficient, $x$)** | 0.0000 | 0.0000 | 표준 무전위 |
| **피치원 직경 (Pitch Diameter, $d$)** | 54.000 mm | 162.000 mm | $d = m \cdot z$ |
| **기초원 직경 (Base Diameter, $d_b$)** | 50.743 mm | 152.230 mm | $d_b = d \cos\alpha_0$ |
| **이끝원 직경 (Tip Diameter, $d_a$)** | 60.000 mm | 168.000 mm | 가공 공차 0 / -0.040 mm |
| **이뿌리원 직경 (Root Diameter, $d_f$)** | 46.500 mm | 154.500 mm | $h_f = 1.25 m$ |
| **전체 치높이 (Whole Depth, $h$)** | 6.750 mm | 6.750 mm | $h = 2.25 m$ |
| **맞물림 기어 잇수 (Mating Teeth)** | 54 | 18 | 상대 맞물림 기어 지정 |
| **표준 중심거리 (Center Distance, $a$)** | 108.000 mm | 108.000 mm | 조립 공차 ±0.020 mm |
| **정면 물림률 (Transverse Contact Ratio, $\epsilon_\alpha$)** | 1.65 (1.648755) | 1.65 (1.648755) | 연속 전동 기준 $\ge 1.20$ 충족 |
| **유효 물림 길이 (Path of Contact, $g_\alpha$)** | 14.602 mm | 14.602 mm | 접촉 활성 구간 |
| **법선 피치 (Normal Pitch, $p_b$)** | 8.856 mm | 8.856 mm | $p_b = \pi m \cos\alpha_0$ |
| **정밀도 등급 (Accuracy Grade)** | KS 5급 (정밀 감속기급) | KS 5급 (정밀 감속기급) | KS B 1416 / ISO 1328-1 |
| **법선 백래시 (Normal Backlash, $j_n$)** | 0.080 ~ 0.130 mm | 0.080 ~ 0.130 mm | 조립 및 열팽창 여유 |

---

## 3.6 2축 분력 및 베어링 하중 해석: HPSTC 치근 굽힘 집중

### 2축 치면 하중 분해

구동 피니언에 토크 $T_1$이 인가될 때, 기준 피치원 직경 $d_1$ 상에서 치면에 작용하는 힘은 작용선 방향의 전 법선력 $F_n$과 이를 회전 좌표계로 분해한 접선력 $F_t$, 반경방향력 $F_r$로 구성됩니다.

__MATH_BLOCK_24__

피니언 입력 토크 $T_1 = 100.0\text{ N}\cdot\text{m}$ 인가 시의 정량적 분력 수치:

__MATH_BLOCK_25__

### HPSTC(점 D) 치근 굽힘 집중의 역학적 필연성 (ISO 6336 Method B)

초보 설계자가 흔히 빠지는 함정 중 하나는 "외팔보 굽힘 모멘트 암이 가장 긴 이끝(점 E)에 하중이 가해질 때 치근 굽힘 응력이 최대가 될 것"이라는 단순 직관입니다. 그러나 실제 치아 굽힘 피로 파손은 이끝이 아니라 **점 D (HPSTC, 최상위 단일 치접촉점)**에서 발생하며, ISO 6336 규격에서도 치형 계수 $Y_F$를 점 D 작용 하중 기준으로 계산하도록 규정하고 있습니다.

1. **이끝(점 E) 접촉 시**: 선행 치가 점 E에 있을 때, 후속 치는 이미 점 B(LPSTC)에서 맞물려 있습니다 ($s_E - s_B = p_b$). 따라서 점 E 접촉은 이중 접촉 구간에 속하며, 전달 하중의 약 50%만이 분담됩니다 ($F_{n,E} \approx 0.5 F_n$).
2. **점 D (HPSTC) 접촉 시**: 접촉점이 치면을 따라 올라갈 때 점 B부터 점 D까지는 **오직 한 치만이 전 하중 100%($F_{n,D} = 1.0 F_n$)를 홀로 지탱**합니다. 점 D는 단일 접촉 구간 중 치근 위험 단면으로부터 모멘트 암이 가장 긴 최상단 위치입니다.
3. **치근 모멘트 대조**: 치근 위험 단면으로부터 점 D까지의 유효 모멘트 암을 $h_D$, 점 E까지의 모멘트 암을 $h_E$라 할 때:

__MATH_BLOCK_26__

스퍼 기어 형상에서 $h_E \approx 1.20 h_D$이므로 모멘트 비를 구하면 다음과 같습니다.

__MATH_BLOCK_27__

점 D에서의 치근 굽힘 모멘트가 이끝 접촉 시보다 약 1.67배나 압도적으로 거대합니다. 기어 치아의 피로 파손(Tooth Root Breakage)은 예외 없이 이 점 D 통과 시의 최대 인장 응력에 의해 발생합니다.

### 단순 지지 축계 베어링 반력 모델

스팬 $L = 100.0\text{ mm}$의 양단 베어링 $A, B$ 사이에서 베어링 A로부터 $L_1 = 40.0\text{ mm}$ 떨어진 위치에 피니언이 장착된 축계의 정역학적 반력:

__MATH_BLOCK_28__

합성 레이디얼 베어링 하중:

__MATH_BLOCK_29__

계산 결과 베어링 A에는 $F_{rA} = 2364.839494\text{ N}$, 베어링 B에는 $F_{rB} = 1576.559663\text{ N}$의 레이디얼 하중이 가해집니다. 이 합성 반력은 베어링의 기본 동정격하중($C_r$) 및 수명($L_{10h}$) 산정의 기초 입력치가 됩니다.

---

## 3.7 국제 표준 규격 비교 및 참고 문헌

### 국제 표준 규격별 정의 및 표기법 비교

| 항목 | 한국산업표준 (KS) | 독일표준 (DIN) | 국제표준화기구 (ISO) | 미국치차제조협회 (AGMA) | Earle Buckingham (1949) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **작용선** | 작용선 | Eingriffslinie | Line of Action | Line of Action | Line of Action |
| **정면 물림률** | 정면 물림률 $\epsilon_\alpha$ | Profilüberdeckung $\epsilon_\alpha$ | Transverse contact ratio $\epsilon_\alpha$ | Contact ratio $m_p$ | Contact ratio CR |
| **기초원 피치** | 법선 피치 $p_b$ | Grundteilung $p_b$ | Base pitch $p_b$ | Base pitch $p_b$ | Normal pitch $p_N$ |
| **물림 개시점** | 점 A (SAP) | Punkt A (Eingriffsbeginn) | Point A ($E_A$) | SAP | Point A |
| **최하위 단일 접촉점** | 점 B (LPSTC) | Punkt B (Innerer Einzeleingriff) | Point B ($B$) | LPSTC | Point B |
| **피치점** | 점 C / P | Punkt C / Wälzpunkt | Pitch point $C$ / $P$ | Pitch point | Pitch point |
| **최상위 단일 접촉점** | 점 D (HPSTC) | Punkt D (Äußerer Einzeleingriff) | Point D ($D$) | HPSTC | Point D |
| **물림 종료점** | 점 E (EAP) | Punkt E (Eingriffsende) | Point E ($E_E$) | EAP | Point E |
| **상대 미끄럼률** | 미끄럼률 $k$ | Spezifisches Gleiten $g$ | Specific sliding $k$ | Specific sliding | Specific sliding |
| **치근 강도 기준점** | 점 D (HPSTC) | Punkt D (DIN 3990) | Point D (ISO 6336-3 Method B) | HPSTC (AGMA 2001) | Point D |

### 참고 문헌 (References)

1. **Earle Buckingham**, *Analytical Mechanics of Gears*, McGraw-Hill Book Company, 1949 (Dover Publications Reprint, 1988), Chapter 18 "Gear Teeth in Action" & Chapter 19 "Efficiencies of Gears".
2. **DIN 3960:1987-03**, *Begriffe und Bestimmungsgrößen für Stirnräder (Zylinderräder) und Stirnradpaare (Zylinderradpaare) mit Evolventenverzahnung*, Deutsches Institut für Normung.
3. **ISO 21771:2007**, *Gears — Cylindrical involute gears and gear pairs — Concepts and geometry*, International Organization for Standardization.
4. **ISO 6336-1/2/3:2019**, *Calculation of load capacity of spur and helical gears — Part 3: Calculation of tooth bending strength (Method B)*.
5. **KS B 0102:2016**, *기어 용어 (Glossary of Gear Terms)*, 한국표준협회.
6. **KS B 0002:2018**, *기어 제도 (Technical Drawings — Gears)*, 한국표준협회.
7. **KS B 1405:2021**, *평치차 및 헬리컬 기어의 기본 랙 (Basic Rack for Spur and Helical Gears)*, 한국표준협회.
8. **Dudley, D. W.**, *Handbook of Practical Gear Design*, CRC Press, 1994.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content


# -----------------------------------------------------------------------------
# English Content Generation (영어)
# -----------------------------------------------------------------------------
def build_en() -> str:
    content = r"""---
title: "Chapter 3. Spur Gear Meshing Kinematics: Line of Action, Contact Ratio, and Specific Sliding"
description: "Rigorous mechanical treatise on spur gear meshing kinematics: closed-form derivation of the five cardinal points on the line of action, transverse contact ratio, single and double tooth load sharing mechanics, relative sliding velocity and specific sliding curves, HPSTC tooth bending dominance under ISO 6336, and production drawing standards."
series: theory
part: 1
chapter: 3
gear_type: spur
standards:
  - "ISO 21771:2007"
  - "DIN 3960"
  - "AGMA 9005-F16"
  - "Buckingham 1949"
required_diagrams:
  - "fig1_line_of_action_five_points"
  - "fig2_tooth_load_sharing"
  - "fig3_contact_kinematics_velocities"
  - "fig4_specific_sliding_curves"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-15"
sidebar:
  order: 3
---

## 3.1 Problem Statement and Physical Background

The fundamental objective of gear transmission is to transfer rotary motion between shafts with an exact, invariant angular velocity ratio and zero slip. For a pair of spur gears in conjugate action, smooth and uninterrupted power transmission requires a strict geometric continuity condition.

### Kinematic Necessity of Continuous Meshing

Before a preceding pair of mating teeth disengages at the recess boundary, the subsequent pair must already enter into contact along the line of action to share the transmitted torque. What transpires if a gear pair operates with a contact ratio below unity ($\epsilon_\alpha < 1.0$)?

A kinematic dead zone is created where no teeth are in contact. The angular phase relationship between the driving and driven shafts drifts instantaneously. When the subsequent tooth pair crashes into mesh, an immense dynamic impact force ($F_{\mathrm{dyn}} = I \frac{d\omega}{dt}$) is unleashed. This results in severe audible clatter, high-amplitude vibrations, and catastrophic tooth root fatigue fractures.

To guarantee uninterrupted conjugate action, the total active path length along the line of action ($g_\alpha$) must exceed the spatial pitch between adjacent teeth, known as the base pitch ($p_b$). This ratio defines the transverse contact ratio ($\epsilon_\alpha$):

__MATH_BLOCK_0__

In heavy-duty industrial drivetrain engineering, accounting for shaft flexure, manufacturing tolerances, and thermo-elastic tooth deflections, standards enforce $\epsilon_\alpha \ge 1.20$ as an inviolable minimum design threshold.

### Contact Tribology: Rolling versus Sliding

Tooth contact across the active profile is far from uniform. At the pitch point (Point C/P), where the operating pitch circles roll upon each other without slip, the tangential linear velocities of both flanks are identical, producing **pure rolling contact** ($v_g = 0$).

Away from the pitch point, significant relative sliding occurs due to differing radii of profile curvature:

- **Dedendum Flank (Tooth Root Region)**: Characterized by negative specific sliding, where tangential rolling and sliding directions oppose one another. This generates cyclic subsurface shear stress concentrations that trigger micro-pitting fatigue under elastohydrodynamic lubrication (EHL) conditions.
- **Addendum Flank (Tooth Tip Region)**: Experiences maximum relative sliding velocity. Under elevated torque and pitch line speeds, frictional heating causes flash temperatures to exceed the lubricant scuffing threshold, resulting in local adhesive micro-welding and scoring.

As gears rotate, the mesh periodically alternates between single-pair contact zones (carrying 100% of the load) and double-pair contact zones (sharing load). This cyclic modulation in aggregate mesh stiffness produces parametric excitation, which serves as the primary root cause of gearbox gear whine noise.

---

## 3.2 Rigorous Mathematical Derivations: Geometry, Trigonometry, and Calculus

### Line of Action and Common Tangent Segment

For involute gearing, the contact normal between mating tooth profiles always tracks the common internal tangent to both base circles. Let $T_1$ be the tangency point on the driving pinion base circle, and $T_2$ be the tangency point on the driven gear base circle. The total distance between tangency points $\overline{T_1 T_2}$ is derived from the center distance $a$ and standard reference pressure angle $\alpha_0$:

__MATH_BLOCK_1__

### Closed-Form Derivation of the Five Cardinal Points

The meshing kinematics along the line of action are governed by five critical singular points, expressed as linear coordinates $s$ measured from the pinion base point $T_1$ ($s = 0.0\text{ mm}$):

1. **Point A (SAP, Start of Active Profile)**: The intersection between the driven gear tip circle (radius $r_{a2}$) and the line of action. From the right triangle $\Delta O_2 T_2 A$, the distance from $T_2$ is $\sqrt{r_{a2}^2 - r_{b2}^2}$. The coordinate $s_A$ from $T_1$ is:

__MATH_BLOCK_2__

2. **Point E (EAP, End of Active Profile)**: The intersection between the driving pinion tip circle (radius $r_{a1}$) and the line of action, derived from triangle $\Delta O_1 T_1 E$:

__MATH_BLOCK_3__

3. **Point B (LPSTC, Lowest Point of Single Tooth Contact)**: The contact position on the driving pinion when the preceding tooth pair disengages at Point E. Located exactly one base pitch $p_b$ inward from Point E:

4. **Point D (HPSTC, Highest Point of Single Tooth Contact)**: The contact position on the driving pinion when the subsequent tooth pair engages at Point A. Located exactly one base pitch $p_b$ outward from Point A:

__MATH_BLOCK_4__

5. **Point C / P (Pitch Point)**: The tangency point of the reference pitch circles, where relative sliding velocity vanishes:

__MATH_BLOCK_5__

Proper kinematic engagement requires the strict monotonic ordering of these five cardinal points along the line of action:

__MATH_BLOCK_6__

![Five Cardinal Points (A, B, C, D, E) and Active Contact Path on the Line of Action](/images/part3/en/fig1_line_of_action_five_points.png)

### Path of Contact and Transverse Contact Ratio

The active path of contact is the segment $\overline{AE}$. Partitioning this segment at the pitch point $P$ yields the approach path ($g_f = \overline{AP}$) and the recess path ($g_a = \overline{PE}$):

__MATH_BLOCK_7__

The total active path length $g_\alpha$ is the sum of both paths:

__MATH_BLOCK_8__

The base pitch $p_b$ represents the spatial distance between successive teeth measured along the normal line of action:

__MATH_BLOCK_9__

Hence, the transverse contact ratio $\epsilon_\alpha$ is expressed in closed form as:

__MATH_BLOCK_10__

### Single-Tooth and Double-Tooth Load Sharing Zones

For standard spur gears where $1.0 < \epsilon_\alpha < 2.0$, the line of contact is divided into three distinct operational regions:

1. **Double-Tooth Contact Zones ($\overline{AB}$ and $\overline{DE}$)**:
   - Two tooth pairs share the transmitted normal force simultaneously, each carrying approximately 50% of the total load.
   - The length of each double contact zone is $g_\alpha - p_b$, totaling $2(g_\alpha - p_b)$.
2. **Single-Tooth Contact Zone ($\overline{BD}$)**:
   - A single tooth pair carries 100% of the entire transmitted normal load without assistance.
   - The single-tooth contact length is $g_1 = s_D - s_B = 2p_b - g_\alpha$.

__MATH_BLOCK_11__

By conservation of contact length, the sum of single-tooth and double-tooth zones equals the total active path length $g_\alpha$:

__MATH_BLOCK_12__

![Single-Tooth and Double-Tooth Contact Zones with Dynamic Load Sharing Distribution](/images/part3/en/fig2_tooth_load_sharing.png)

### Linear Velocities and Relative Sliding Velocity

At any contact coordinate $s$ along the line of action, the radii of profile curvature for the pinion and gear are $\rho_1(s) = s$ and $\rho_2(s) = \overline{T_1 T_2} - s$. With angular velocities $\omega_1$ and $\omega_2$, the linear tangential velocities along the profile normals are:

__MATH_BLOCK_13__

The relative sliding velocity $v_g(s)$ between the contacting tooth surfaces is the algebraic difference between these linear velocities:

__MATH_BLOCK_14__

With directed distance from the pitch point $x = s - s_C$, sliding velocity is a strictly linear function. At the pitch point ($x = 0$), $v_g = 0$, confirming pure rolling contact. The direction of relative sliding reverses upon crossing the pitch point.

![Linear Velocity Vectors and Relative Sliding Velocity Reversal along Path of Contact](/images/part3/en/fig3_contact_kinematics_velocities.png)

### Specific Sliding and Invariant Algebraic Identity

Specific sliding ($k$) normalizes the sliding velocity by the entrainment surface velocity of the respective tooth:

For the driving pinion $k_1(s)$:

__MATH_BLOCK_15__

For the driven gear $k_2(s)$:

__MATH_BLOCK_16__

These two specific sliding quantities satisfy an invariant algebraic identity valid across all cylindrical involute gears:

__MATH_BLOCK_17__

As contact approaches a base circle tangency point ($\rho_1 \to 0$ or $\rho_2 \to 0$), the specific sliding diverges asymptotically to negative infinity ($-\infty$). For low tooth-count pinions, Point A lies dangerously close to the base circle, causing severe dedendum sliding wear. This provides the fundamental engineering rationale for applying a positive profile shift ($x_1 > 0$) to displace the active profile away from the base circle.

![Specific Sliding Curves of Pinion and Gear along the Line of Action](/images/part3/en/fig4_specific_sliding_curves.png)

---

## 3.3 Formula Summary and 38-Parameter Closed-Form Benchmark Table

The benchmark gear pair specification is defined as follows:

__MATH_BLOCK_18__

Fundamental pitch and base circle radii:

__MATH_BLOCK_19__

Calculated contact path lengths and contact ratio:

__MATH_BLOCK_20__

Load sharing zone partitioning:

__MATH_BLOCK_21__

Specific sliding values at the five cardinal points:

__MATH_BLOCK_22__

### 38-Parameter Closed-Form Benchmark Table

The following table presents the exact closed-form benchmark values for the standard spur gear pair ($m = 3.0\text{ mm}, z_1 = 18, z_2 = 54, \alpha_0 = 20.0^\circ, a = 108.0\text{ mm}$):

| No. | Geometric Parameter | Symbol | Closed-Form Formula | Exact Value | Unit |
|:---:|:---|:---:|:---|:---:|:---:|
| 1 | Gear ratio | $u$ | $z_2 / z_1$ | 3.000000 | — |
| 2 | Pinion pitch diameter | $d_1$ | $m \cdot z_1$ | 54.000000 | mm |
| 3 | Pinion pitch radius | $r_1$ | $d_1 / 2$ | 27.000000 | mm |
| 4 | Gear pitch diameter | $d_2$ | $m \cdot z_2$ | 162.000000 | mm |
| 5 | Gear pitch radius | $r_2$ | $d_2 / 2$ | 81.000000 | mm |
| 6 | Standard center distance | $a$ | $(d_1 + d_2) / 2$ | 108.000000 | mm |
| 7 | Circular pitch | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | Tooth thickness and space | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | Base pitch (normal pitch) | $p_b$ | $\pi m \cos\alpha_0$ | 8.856394 | mm |
| 10 | Pinion base diameter | $d_{b1}$ | $d_1 \cos\alpha_0$ | 50.743402 | mm |
| 11 | Pinion base radius | $r_{b1}$ | $d_{b1} / 2$ | 25.371701 | mm |
| 12 | Gear base diameter | $d_{b2}$ | $d_2 \cos\alpha_0$ | 152.230205 | mm |
| 13 | Gear base radius | $r_{b2}$ | $d_{b2} / 2$ | 76.115102 | mm |
| 14 | Addendum | $h_a$ | $1.0 \cdot m$ | 3.000000 | mm |
| 15 | Dedendum | $h_f$ | $1.25 \cdot m$ | 3.750000 | mm |
| 16 | Whole depth | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | Bottom clearance | $c$ | $0.25 \cdot m$ | 0.750000 | mm |
| 18 | Pinion tip diameter | $d_{a1}$ | $d_1 + 2h_a$ | 60.000000 | mm |
| 19 | Pinion tip radius | $r_{a1}$ | $d_{a1} / 2$ | 30.000000 | mm |
| 20 | Gear tip diameter | $d_{a2}$ | $d_2 + 2h_a$ | 168.000000 | mm |
| 21 | Gear tip radius | $r_{a2}$ | $d_{a2} / 2$ | 84.000000 | mm |
| 22 | Pinion root diameter | $d_{f1}$ | $d_1 - 2h_f$ | 46.500000 | mm |
| 23 | Pinion root radius | $r_{f1}$ | $d_{f1} / 2$ | 23.250000 | mm |
| 24 | Gear root diameter | $d_{f2}$ | $d_2 - 2h_f$ | 154.500000 | mm |
| 25 | Gear root radius | $r_{f2}$ | $d_{f2} / 2$ | 77.250000 | mm |
| 26 | Reference pressure angle involute | $\mathrm{inv}\,\alpha_0$ | $\tan 20^\circ - 20^\circ \frac{\pi}{180}$ | 0.014904 | rad |
| 27 | Pinion tip pressure angle | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 32.250479 | deg |
| 28 | Gear tip pressure angle | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.023798 | deg |
| 29 | Pinion tip involute | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.068088 | rad |
| 30 | Gear tip involute | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.030066 | rad |
| 31 | Pinion top land thickness | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.044991 | mm |
| 32 | Gear top land thickness | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.339811 | mm |
| 33 | Recess path length | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha_0$ | 6.774104 | mm |
| 34 | Approach path length | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha_0$ | 7.827921 | mm |
| 35 | Total active path length | $g_\alpha$ | $g_a + g_f$ | 14.602024 | mm |
| 36 | Transverse contact ratio | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.648755 | — |
| 37 | Single-tooth contact length | $g_1$ | $2 p_b - g_\alpha$ | 3.110764 | mm |
| 38 | Double-tooth contact length | $g_2$ | $2(g_\alpha - p_b)$ | 11.491260 | mm |

Both top land thicknesses ($s_{a1} = 2.045\text{ mm}, s_{a2} = 2.340\text{ mm}$) comfortably exceed the anti-pointing criterion of $0.25m = 0.75\text{ mm}$. The contact ratio $\epsilon_\alpha = 1.648755$ exceeds the industrial guideline of 1.20, with 78.70% of the active contact path operating in stable double-tooth load sharing.

---

## 3.4 Dimensional Inspection Engineering and Tooth Surface Failure Modes

### Load Sharing Step Function and Contact Fatigue

As teeth traverse the meshing cycle, the normal load intensity per unit face width $w_N(s)$ undergoes a discrete step-function transition between single-pair and double-pair contact:

__MATH_BLOCK_23__

Entering the single-tooth contact zone ($\overline{BD}$), the normal load carried by a single tooth doubles instantaneously.

### Mechanics of Pitting Formation

Pitting is a surface fatigue failure initiated by cyclic subsurface shear stresses:
- Location: Occurs predominantly on the dedendum flank of the driving pinion just below the pitch line ($\overline{BC}$).
- Physical mechanism: Flank contact in this zone combines high normal load (100% in $\overline{BD}$) with negative specific sliding. The maximum subsurface shear stress ($\tau_{\max} \approx 0.30 p_0$) initiates fatigue micro-cracks at a depth of $z \approx 0.78 b_H$. When cracks breach the surface, pressurized lubricant enters the crack mouth. As rolling contact closes the mouth, hydraulic wedge action drives crack propagation, liberating microscopic pits.

### Mechanics of Scuffing / Scoring

Scuffing is an adhesive failure characterized by the localized breakdown of the elastohydrodynamic lubricant film:
- Location: Peaks at the extremes of the active profile, namely Point A (pinion dedendum) and Point E (pinion addendum).
- Physical mechanism: Maximum relative sliding velocity generates extreme frictional heat. According to Blok's flash temperature theory, when the instantaneous contact temperature exceeds the lubricant desorptive threshold, boundary films collapse, producing micro-welding and tearing of the contacting asperities.

---

## 3.5 Production Drawing Tables: Standards and Industrial Practice

The final engineering deliverable of gear kinematic design is the production drawing data table. The following table represents the formal 17-item manufacturing specification conforming to ISO 21771 and DIN standards:

| Item | Pinion Specification | Gear Specification | Reference Standards / Notes |
|:---|:---:|:---:|:---|
| **Tooth Profile** | Standard Involute | Standard Involute | ISO 21771 / DIN 3960 |
| **Basic Rack** | Standard Cylindrical Rack | Standard Cylindrical Rack | ISO 53 Profile A |
| **Module ($m$)** | 3.000 mm | 3.000 mm | Standard Series 1 |
| **Reference Pressure Angle ($\alpha_0$)** | 20.0° | 20.0° | Basic profile |
| **Number of Teeth ($z$)** | 18 | 54 | Ratio $u = 3.000$ |
| **Profile Shift Coefficient ($x$)** | 0.0000 | 0.0000 | Standard non-shifted |
| **Pitch Diameter ($d$)** | 54.000 mm | 162.000 mm | $d = m \cdot z$ |
| **Base Diameter ($d_b$)** | 50.743 mm | 152.230 mm | $d_b = d \cos\alpha_0$ |
| **Tip Diameter ($d_a$)** | 60.000 mm | 168.000 mm | Machining tolerance 0 / -0.040 mm |
| **Root Diameter ($d_f$)** | 46.500 mm | 154.500 mm | $h_f = 1.25 m$ |
| **Whole Depth ($h$)** | 6.750 mm | 6.750 mm | $h = 2.25 m$ |
| **Mating Teeth** | 54 | 18 | Mating element reference |
| **Center Distance ($a$)** | 108.000 mm | 108.000 mm | Tolerance ±0.020 mm |
| **Transverse Contact Ratio ($\epsilon_\alpha$)** | 1.65 (1.648755) | 1.65 (1.648755) | Exceeds minimum threshold $\ge 1.20$ |
| **Path of Contact ($g_\alpha$)** | 14.602 mm | 14.602 mm | Total active length |
| **Normal Base Pitch ($p_b$)** | 8.856 mm | 8.856 mm | $p_b = \pi m \cos\alpha_0$ |
| **Accuracy Grade** | ISO Grade 5 (Precision Gearing) | ISO Grade 5 (Precision Gearing) | ISO 1328-1 |
| **Normal Backlash ($j_n$)** | 0.080 ~ 0.130 mm | 0.080 ~ 0.130 mm | Assembly and thermal allowance |

---

## 3.6 Two-Axis Force Decomposition, Bearing Loads, and HPSTC Root Bending Mechanics

### Two-Axis Tooth Force Decomposition

Under input torque $T_1$, the normal tooth load $F_n$ acting along the line of action decomposes into orthogonal tangential force $F_t$ and radial force $F_r$:

__MATH_BLOCK_24__

For the benchmark pinion subjected to input torque $T_1 = 100.0\text{ N}\cdot\text{m}$:

__MATH_BLOCK_25__

### Mechanical Rationale for ISO 6336 Method B (HPSTC Bending Dominance)

A common misconception in gear stress analysis is assuming that maximum tooth bending stress occurs when load is applied at the tooth tip (Point E, EAP), where the moment arm is greatest. In actual gear transmissions, tooth root fatigue breakage is governed by **Point D (HPSTC, Highest Point of Single Tooth Contact)**:

1. **Tooth Tip (Point E) Engagement**: When contact reaches Point E, the subsequent tooth pair is already meshing at Point B (LPSTC), since $s_E - s_B = p_b$. Hence, Point E belongs to a double-contact zone, carrying only half the transmitted force ($F_{n,E} \approx 0.5 F_n$).
2. **HPSTC (Point D) Engagement**: Point D marks the outermost boundary of single-tooth contact. Between Point B and Point D, a single tooth carries 100% of the entire load ($F_{n,D} = 1.0 F_n$).
3. **Bending Moment Comparison**: With moment arm $h_D$ at Point D and $h_E$ at Point E:

__MATH_BLOCK_26__

For standard spur gears, $h_E \approx 1.20 h_D$, yielding the bending moment ratio:

__MATH_BLOCK_27__

The root bending moment at HPSTC is approximately 1.67 times greater than at the tooth tip. This constitutes the mechanical basis for ISO 6336 Method B, which mandates evaluating tooth root stress at HPSTC.

### Shaft Bearing Reactions on Simply Supported Shaft

For a shaft of span $L = 100.0\text{ mm}$ supported by bearings A and B, with the pinion located at $L_1 = 40.0\text{ mm}$ from bearing A:

__MATH_BLOCK_28__

Total radial bearing loads:

__MATH_BLOCK_29__

Evaluating these expressions yields $F_{rA} = 2364.839494\text{ N}$ and $F_{rB} = 1576.559663\text{ N}$, serving as primary inputs for bearing life ($L_{10h}$) calculations.

---

## 3.7 International Standards Comparison and Bibliographic References

### Cross-Standard Terminology Comparison

| Concept | ISO 21771:2007 | DIN 3960 | AGMA 9005-F16 / 2001 | Earle Buckingham (1949) |
|:---|:---:|:---:|:---:|:---:|
| **Line of Action** | Line of action | Eingriffslinie | Line of action | Line of action |
| **Contact Ratio** | Transverse contact ratio $\epsilon_\alpha$ | Profilüberdeckung $\epsilon_\alpha$ | Contact ratio $m_p$ | Contact ratio CR |
| **Base Pitch** | Base pitch $p_b$ | Grundteilung $p_b$ | Base pitch $p_b$ | Normal pitch $p_N$ |
| **Start of Active Profile** | Point A ($E_A$) | Punkt A | SAP | Point A |
| **Lowest Single Contact** | Point B ($B$) | Punkt B | LPSTC | Point B |
| **Pitch Point** | Pitch point $C$ / $P$ | Wälzpunkt $C$ | Pitch point | Pitch point |
| **Highest Single Contact** | Point D ($D$) | Punkt D | HPSTC | Point D |
| **End of Active Profile** | Point E ($E_E$) | Punkt E | EAP | Point E |
| **Specific Sliding** | Specific sliding $k$ | Spezifisches Gleiten $g$ | Specific sliding | Specific sliding |
| **Bending Reference Point** | Point D (ISO 6336-3) | Punkt D (DIN 3990) | HPSTC (AGMA 2001) | Point D |

### References

1. **Earle Buckingham**, *Analytical Mechanics of Gears*, McGraw-Hill Book Company, 1949 (Dover Publications Reprint, 1988), Chapter 18 "Gear Teeth in Action" & Chapter 19 "Efficiencies of Gears".
2. **DIN 3960:1987-03**, *Begriffe und Bestimmungsgrößen für Stirnräder (Zylinderräder) und Stirnradpaare (Zylinderradpaare) mit Evolventenverzahnung*, Deutsches Institut für Normung.
3. **ISO 21771:2007**, *Gears — Cylindrical involute gears and gear pairs — Concepts and geometry*, International Organization for Standardization.
4. **ISO 6336-1/2/3:2019**, *Calculation of load capacity of spur and helical gears — Part 3: Calculation of tooth bending strength (Method B)*.
5. **AGMA 9005-F16**, *Industrial Gear Lubrication*, American Gear Manufacturers Association.
6. **Dudley, D. W.**, *Handbook of Practical Gear Design*, CRC Press, 1994.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content


# -----------------------------------------------------------------------------
# German Content Generation (독일어)
# -----------------------------------------------------------------------------
def build_de() -> str:
    content = r"""---
title: "Kapitel 3. Eingriffskinematik der Geradstirnräder: Eingriffslinie, Profilüberdeckung und Spezifisches Gleiten"
description: "Umfassende ingenieurwissenschaftliche Abhandlung zur Eingriffskinematik von Stirnrädern: geschlossene Herleitung der fünf Hauptpunkte der Eingriffslinie, Profilüberdeckung ε_α, Lastaufteilung in Einzeleingriff und Doppeleingriff, relatives Gleiten und spezifisches Gleiten, HPSTC-Zahnfußbiegung nach ISO 6336 und Fertigungszeichnungstabellen nach DIN 3960."
series: theory
part: 1
chapter: 3
gear_type: spur
standards:
  - "DIN 3960"
  - "DIN 867"
  - "ISO 21771:2007"
required_diagrams:
  - "fig1_line_of_action_five_points"
  - "fig2_tooth_load_sharing"
  - "fig3_contact_kinematics_velocities"
  - "fig4_specific_sliding_curves"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-15"
sidebar:
  order: 3
---

## 3.1 Problemstellung und physikalische Grundlagen

Das primäre Ziel jeder Zahnradstufe besteht darin, ein Drehmoment zwischen zwei Wellen mit einem absolut konstanten Übersetzungsverhältnis ohne Schlupf zu übertragen. Bei Geradstirnrädern mit Evolventenprofil erfordert eine stoßfreie und kontinuierliche Leistungsübertragung eine geometrisch streng definierte Eingriffsbedingung.

### Kinematische Notwendigkeit der kontinuierlichen Überdeckung

Bevor ein im Eingriff befindliches Zahnpaar am Eingriffsende den Kontakt verliert, muss das nachfolgende Zahnpaar bereits an der Eingriffslinie in Kontakt getreten sein, um die Last kontinuierlich zu übernehmen. Unterschreitet die Profilüberdeckung den Grenzwert Eins ($\epsilon_\alpha < 1.0$), entsteht eine kinematische Totzone: Für einen kurzen Drehwinkel findet überhaupt kein Zahneingriff statt. Die Phasenbeziehung zwischen treibender und getriebener Welle driftet auseinander. Beim erneuten Zusammentreffen der Zahnflanken tritt ein extrem hoher dynamischer Stoß ($F_{\mathrm{dyn}} = I \frac{d\omega}{dt}$) auf, der zu starker Geräuschentwicklung, Gehäusevibrationen und katastrophalem Zahnfußbruch führt.

Aus diesem Grund muss die wirksame Eingriffsstrecke ($g_\alpha$) stets größer sein als die Grundteilung ($p_b$). Dieser Quotient definiert die Profilüberdeckung ($\epsilon_\alpha$):

__MATH_BLOCK_0__

Im industriellen Getriebebau wird unter Berücksichtigung von Fertigungstoleranzen, Wellendurchbiegungen und thermoelastischen Zahnverformungen ein Mindestwert von $\epsilon_\alpha \ge 1.20$ zwingend gefordert.

### Flankenkontakt: Wälzen und Gleiten

Der Kontakt entlang der Flanke ist keineswegs homogen. Am Wälzpunkt (Punkt C/P), an dem die Teilkreise aufeinander abrollen, sind die Umfangsgeschwindigkeiten beider Zähne exakt identisch. Hier liegt **reines Abwälzen** vor, und die relative Gleitgeschwindigkeit ist exakt null ($v_g = 0$).

Außerhalb des Wälzpunktes tritt aufgrund der unterschiedlichen Krümmungsradien signifikantes Flankengleiten auf:

- **Zahnfußbereich (Dedendum Flank)**: Hier herrscht negatives spezifisches Gleiten vor, bei dem Wälz- und Gleitrichtung gegeneinander gerichtet sind. Dies induziert zyklische Werkstoffscherspannungen, die unter elasto-hydrodynamischen Schmierbedingungen (EHD) zur Bildung von Ermüdungsgrübchen (**Pitting**) führen.
- **Zahnkopfbereich (Addendum Flank)**: Hier erreicht die relative Gleitgeschwindigkeit Maximalwerte. Bei hoher Belastung und Drehzahl bricht der Schmierfilm zusammen, was durch lokale Reibungsüberhitzung (Blitztemperatur nach Blok) zu adhäsivem Verschleiß und Fressschäden (**Scuffing/Fressen**) führt.

Der periodische Wechsel zwischen Einzeleingriff (100% Last auf einem Zahn) und Doppeleingriff (Lastaufteilung) moduliert die Zahnfedersteifigkeit kontinuierlich und bildet die primäre Erregerquelle für hochfrequentes Getriebeheulen (Gear Whine).

---

## 3.2 Mathematische Herleitungen: Geometrie, Trigonometrie und Differentialrechnung

### Eingriffslinie und gemeinsame Grundkreistangente

Bei der Evolventenverzahnung fällt die Eingriffsnormale stets mit der inneren gemeinsamen Tangente an die beiden Grundkreise zusammen. Sind $T_1$ und $T_2$ die Berührpunkte an den Grundkreisen von Ritzel und Rad, so berechnet sich die Tangentenstrecke $\overline{T_1 T_2}$ geschlossen aus Achsabstand $a$ und Normaleingriffswinkel $\alpha_0$:

__MATH_BLOCK_1__

### Geschlossene Koordinaten der fünf Hauptpunkte der Eingriffslinie

Die Eingriffskinematik wird durch fünf signifikante Hauptpunkte bestimmt, deren Positionen als Abstand $s$ vom Ritzelgrundkreispunkt $T_1$ ($s = 0.0\text{ mm}$) definiert werden:

1. **Punkt A (Eingriffsbeginn, SAP)**: Schnittpunkt des Kopfkreises von Rad 2 (Radius $r_{a2}$) mit der Eingriffslinie. Der Abstand von $T_2$ beträgt $\sqrt{r_{a2}^2 - r_{b2}^2}$. Die Koordinate $s_A$ von $T_1$ lautet:

__MATH_BLOCK_2__

2. **Punkt E (Eingriffsende, EAP)**: Schnittpunkt des Kopfkreises von Ritzel 1 (Radius $r_{a1}$) mit der Eingriffslinie:

__MATH_BLOCK_3__

3. **Punkt B (Innerer Einzeleingriffspunkt, LPSTC)**: Kontaktpunkt auf Ritzel 1 beim Austritt des vorangehenden Zahnes bei Punkt E. Er liegt genau eine Grundteilung $p_b$ einwärts von Punkt E:

4. **Punkt D (Äußerer Einzeleingriffspunkt, HPSTC)**: Kontaktpunkt auf Ritzel 1 beim Eintritt des nachfolgenden Zahnes bei Punkt A. Er liegt genau eine Grundteilung $p_b$ auswärts von Punkt A:

__MATH_BLOCK_4__

5. **Punkt C / P (Wälzpunkt, Pitch Point)**: Berührpunkt der Wälzkreise mit reiner Rollbewegung:

__MATH_BLOCK_5__

Zur Gewährleistung eines störungsfreien Betriebs müssen diese fünf Punkte eine streng monotone Reihenfolge entlang der Eingriffslinie einhalten:

__MATH_BLOCK_6__

![Fünf Hauptpunkte (A, B, C, D, E) und Eingriffslänge auf der Eingriffslinie](/images/part3/de/fig1_line_of_action_five_points.png)

### Eingriffsstrecke und Profilüberdeckung

Die aktive Eingriffsstrecke ist die Strecke $\overline{AE}$. Aufgeteilt am Wälzpunkt $P$ ergeben sich die Vorgriffstrecke ($g_f = \overline{AP}$) und die Nachgriffstrecke ($g_a = \overline{PE}$):

__MATH_BLOCK_7__

Die gesamte wirksame Eingriffsstrecke $g_\alpha$ beträgt:

__MATH_BLOCK_8__

Die Grundteilung $p_b$ stellt den Abstand aufeinanderfolgender Zähne auf der Eingriffslinie dar:

__MATH_BLOCK_9__

Damit ergibt sich die geschlossene Formel für die Profilüberdeckung $\epsilon_\alpha$:

__MATH_BLOCK_10__

### Einzeleingriffs- und Doppeleingriffsbereiche

Bei Standardstirnrädern mit $1.0 < \epsilon_\alpha < 2.0$ teilt sich die Eingriffsstrecke in drei Abschnitte:

1. **Doppeleingriffsbereiche ($\overline{AB}$ und $\overline{DE}$)**:
   - Zwei Zahnpaare sind gleichzeitig im Eingriff und teilen sich die Umfangskraft zu je ca. 50%.
   - Die Gesamtlänge beider Bereiche beträgt $2(g_\alpha - p_b)$.
2. **Einzeleingriffsbereich ($\overline{BD}$)**:
   - Ein einziges Zahnpaar trägt 100% der gesamten Normalkraft.
   - Die Länge des Einzeleingriffs beträgt $g_1 = s_D - s_B = 2p_b - g_\alpha$.

__MATH_BLOCK_11__

Nach dem Erhaltungssatz der Wegstrecken entspricht die Summe beider Zonen exakt der Gesamteingriffsstrecke $g_\alpha$:

__MATH_BLOCK_12__

![Einzeleingriffs- und Doppeleingriffsbereiche mit Lastaufteilungsverlauf](/images/part3/de/fig2_tooth_load_sharing.png)

### Flankengeschwindigkeiten und relative Gleitgeschwindigkeit

An jeder Eingriffskoordinate $s$ betragen die Krümmungsradien der Zahnprofile $\rho_1(s) = s$ und $\rho_2(s) = \overline{T_1 T_2} - s$. Mit den Winkelgeschwindigkeiten $\omega_1$ und $\omega_2$ lauten die Tangentialgeschwindigkeiten der Zahnflanken:

__MATH_BLOCK_13__

Die relative Gleitgeschwindigkeit $v_g(s)$ ist die Differenz beider Geschwindigkeiten:

__MATH_BLOCK_14__

Mit dem gerichteten Abstand $x = s - s_C$ vom Wälzpunkt ist die Gleitgeschwindigkeit eine lineare Funktion. Am Wälzpunkt ($x = 0$) wird $v_g = 0$, was das reine Abwälzen bestätigt. Beim Durchgang durch den Wälzpunkt kehrt sich das Vorzeichen der Gleitbewegung um.

![Tangentiale Geschwindigkeitsvektoren und Umkehr der relativen Gleitgeschwindigkeit am Wälzpunkt](/images/part3/de/fig3_contact_kinematics_velocities.png)

### Spezifisches Gleiten und algebraische Invariante

Das spezifische Gleiten ($k$) setzt die Gleitgeschwindigkeit ins Verhältnis zur jeweiligen Flankengeschwindigkeit:

Für das Ritzel $k_1(s)$:

__MATH_BLOCK_15__

Für das Rad $k_2(s)$:

__MATH_BLOCK_16__

Zwischen $k_1$ und $k_2$ gilt die fundamentale algebraische Identität:

__MATH_BLOCK_17__

In der Nähe der Grundkreistangenten ($\rho_1 \to 0$ oder $\rho_2 \to 0$) divergiert das spezifische Gleiten gegen negativ unendlich ($-\infty$). Bei Ritzeln mit kleiner Zähnezahl liegt Punkt A gefährlich nahe am Grundkreis, was zu extremem Fußverschleiß führt. Dies begründet die ingenieurmäßige Notwendigkeit einer positiven Profilverschiebung ($x_1 > 0$).

![Spezifische Gleitkurven von Ritzel und Rad entlang der Eingriffslinie](/images/part3/de/fig4_specific_sliding_curves.png)

---

## 3.3 Formelübersicht und geschlossene 38-Parameter-Referenztabelle

Die Spezifikation des Referenzgetriebes lautet:

__MATH_BLOCK_18__

Teilkreis- und Grundkreisradien:

__MATH_BLOCK_19__

Eingriffslängen und Überdeckung:

__MATH_BLOCK_20__

Aufteilung der Eingriffszonen:

__MATH_BLOCK_21__

Spezifisches Gleiten an den Hauptpunkten:

__MATH_BLOCK_22__

### Geschlossene 38-Parameter-Referenztabelle

Die folgende Tabelle enthält alle 38 analytisch exakten Parameterwerte für die Standardverzahnung ($m = 3.0\text{ mm}, z_1 = 18, z_2 = 54, \alpha_0 = 20.0^\circ, a = 108.0\text{ mm}$):

| Nr. | Geometrischer Parameter | Symbol | Formel | Exakter Wert | Einheit |
|:---:|:---|:---:|:---|:---:|:---:|
| 1 | Übersetzungsverhältnis | $u$ | $z_2 / z_1$ | 3.000000 | — |
| 2 | Ritzelteilkreisdurchmesser | $d_1$ | $m \cdot z_1$ | 54.000000 | mm |
| 3 | Ritzelteilkreisradius | $r_1$ | $d_1 / 2$ | 27.000000 | mm |
| 4 | Radteilkreisdurchmesser | $d_2$ | $m \cdot z_2$ | 162.000000 | mm |
| 5 | Radteilkreisradius | $r_2$ | $d_2 / 2$ | 81.000000 | mm |
| 6 | Standardachsabstand | $a$ | $(d_1 + d_2) / 2$ | 108.000000 | mm |
| 7 | Teilung | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | Zahndicke und Zahnlücke | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | Grundteilung | $p_b$ | $\pi m \cos\alpha_0$ | 8.856394 | mm |
| 10 | Ritzelgrundkreisdurchmesser | $d_{b1}$ | $d_1 \cos\alpha_0$ | 50.743402 | mm |
| 11 | Ritzelgrundkreisradius | $r_{b1}$ | $d_{b1} / 2$ | 25.371701 | mm |
| 12 | Radgrundkreisdurchmesser | $d_{b2}$ | $d_2 \cos\alpha_0$ | 152.230205 | mm |
| 13 | Radgrundkreisradius | $r_{b2}$ | $d_{b2} / 2$ | 76.115102 | mm |
| 14 | Kopfhöhe | $h_a$ | $1.0 \cdot m$ | 3.000000 | mm |
| 15 | Fußhöhe | $h_f$ | $1.25 \cdot m$ | 3.750000 | mm |
| 16 | Zahnhöhe | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | Kopfspiel | $c$ | $0.25 \cdot m$ | 0.750000 | mm |
| 18 | Ritzelkopfkreisdurchmesser | $d_{a1}$ | $d_1 + 2h_a$ | 60.000000 | mm |
| 19 | Ritzelkopfkreisradius | $r_{a1}$ | $d_{a1} / 2$ | 30.000000 | mm |
| 20 | Radkopfkreisdurchmesser | $d_{a2}$ | $d_2 + 2h_a$ | 168.000000 | mm |
| 21 | Radkopfkreisradius | $r_{a2}$ | $d_{a2} / 2$ | 84.000000 | mm |
| 22 | Ritzelfußkreisdurchmesser | $d_{f1}$ | $d_1 - 2h_f$ | 46.500000 | mm |
| 23 | Ritzelfußkreisradius | $r_{f1}$ | $d_{f1} / 2$ | 23.250000 | mm |
| 24 | Radfußkreisdurchmesser | $d_{f2}$ | $d_2 - 2h_f$ | 154.500000 | mm |
| 25 | Radfußkreisradius | $r_{f2}$ | $d_{f2} / 2$ | 77.250000 | mm |
| 26 | Evolventenfunktion Normaleingriffswinkel | $\mathrm{inv}\,\alpha_0$ | $\tan 20^\circ - 20^\circ \frac{\pi}{180}$ | 0.014904 | rad |
| 27 | Ritzelkopf-Eingriffswinkel | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 32.250479 | deg |
| 28 | Radkopf-Eingriffswinkel | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.023798 | deg |
| 29 | Ritzelkopf-Evolvente | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.068088 | rad |
| 30 | Radkopf-Evolvente | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.030066 | rad |
| 31 | Ritzelkopfdicke | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.044991 | mm |
| 32 | Radkopfdicke | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.339811 | mm |
| 33 | Nachgrifflänge | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha_0$ | 6.774104 | mm |
| 34 | Vorgrifflänge | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha_0$ | 7.827921 | mm |
| 35 | Gesamte Eingriffslänge | $g_\alpha$ | $g_a + g_f$ | 14.602024 | mm |
| 36 | Profilüberdeckung | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.648755 | — |
| 37 | Einzeleingriffslänge | $g_1$ | $2 p_b - g_\alpha$ | 3.110764 | mm |
| 38 | Doppeleingriffslänge | $g_2$ | $2(g_\alpha - p_b)$ | 11.491260 | mm |

Beide Kopfdicken ($s_{a1} = 2.045\text{ mm}, s_{a2} = 2.340\text{ mm}$) übertreffen den Grenzwert gegen Zuspitzung ($0.25m = 0.75\text{ mm}$) deutlich. Die Überdeckung $\epsilon_\alpha = 1.648755$ liegt weit über dem Grenzwert von 1.20, wobei 78.70% der Eingriffslinie im stabilen Doppeleingriff verbleiben.

---

## 3.4 Maßprüftechnik und Schadensmechanismen der Zahnflanken

### Laststufenfunktion und Flankenbeanspruchung

Die bezogene Normallast pro Millimeter Zahnbreite $w_N(s)$ weist beim Durchlaufen der Eingriffsstrecke eine ausgeprägte Stufenfunktion auf:

__MATH_BLOCK_23__

Im Einzeleingriffsbereich ($\overline{BD}$) verdoppelt sich die Belastung des einzelnen Zahnes schlagartig.

### Entstehung von Flankengrübchen (Pitting)

Pitting ist eine Ermüdungserscheinung infolge zyklischer Hertzscher Pressung:
- Ort: Tritt bevorzugt im Ritzelfußbereich knapp unterhalb des Wälzpunktes ($\overline{BC}$) auf.
- Mechanismus: Hier überlagern sich 100% Volllast und negatives spezifisches Gleiten. Die maximale Werkstoffscherspannung ($\tau_{\max} \approx 0.30 p_0$) in der Tiefe $z \approx 0.78 b_H$ induziert Mikrorisse. Bei Rissöffnung dringt Schmieröl ein; beim Überrollen schließt sich der Rissmund und der hydraulische Spaltkeildruck sprengt mikroskopische Werkstoffpartikel ab.

### Entstehung von Fressschäden (Scuffing)

Fressen ist ein thermo-adhäsives Schadensbild bei Schmierfilmzusammenbruch:
- Ort: Maxima an den Extrempunkten der Eingriffsstrecke A (Ritzelfuß) und E (Ritzelzahnkopf).
- Mechanismus: Hohe Gleitgeschwindigkeiten führen nach der Blitztemperaturhypothese von Blok zur Überhitzung. Sobald die Grenzschichten versagen, kommt es zum metallischen Kontakt, Heißverschweißen und anschließendem Ausreißen von Flankenteilchen.

---

## 3.5 Fertigungszeichnungstabellen nach DIN 3960 und ISO-Normen

Die Konstruktionsergebnisse werden in der Zeichnungstabelle zusammengefasst. Die folgende Tabelle entspricht der formalen 17-Punkte-Normtabelle nach DIN 3960 und ISO 21771:

| Merkmal | Ritzelspezifikation | Radspezifikation | Normen und Prüfvorschriften |
|:---|:---:|:---:|:---|
| **Zahnform** | Standard-Evolvente | Standard-Evolvente | DIN 3960 / ISO 21771 |
| **Bezugsprofil** | Norm-Bezugsprofil | Norm-Bezugsprofil | DIN 867 / ISO 53 Profil A |
| **Modul ($m$)** | 3.000 mm | 3.000 mm | Normreihe 1 |
| **Eingriffswinkel ($\alpha_0$)** | 20.0° | 20.0° | Bezugswinkel |
| **Zähnezahl ($z$)** | 18 | 54 | Übersetzung $u = 3.000$ |
| **Profilverschiebungsfaktor ($x$)** | 0.0000 | 0.0000 | Nullverzahnung |
| **Teilkreisdurchmesser ($d$)** | 54.000 mm | 162.000 mm | $d = m \cdot z$ |
| **Grundkreisdurchmesser ($d_b$)** | 50.743 mm | 152.230 mm | $d_b = d \cos\alpha_0$ |
| **Kopfkreisdurchmesser ($d_a$)** | 60.000 mm | 168.000 mm | Toleranz 0 / -0.040 mm |
| **Fußkreisdurchmesser ($d_f$)** | 46.500 mm | 154.500 mm | $h_f = 1.25 m$ |
| **Zahnhöhe ($h$)** | 6.750 mm | 6.750 mm | $h = 2.25 m$ |
| **Gepaarungszähnezahl** | 54 | 18 | Gegenrad |
| **Achsabstand ($a$)** | 108.000 mm | 108.000 mm | Toleranz ±0.020 mm |
| **Profilüberdeckung ($\epsilon_\alpha$)** | 1.65 (1.648755) | 1.65 (1.648755) | Mindestwert $\ge 1.20$ erfüllt |
| **Eingriffslänge ($g_\alpha$)** | 14.602 mm | 14.602 mm | Wirksamer Eingriffsweg |
| **Grundteilung ($p_b$)** | 8.856 mm | 8.856 mm | $p_b = \pi m \cos\alpha_0$ |
| **Verzahnungsqualität** | DIN Qualität 5 (Präzisionsstufe) | DIN Qualität 5 (Präzisionsstufe) | DIN 3962 / ISO 1328-1 |
| **Normalflankenspiel ($j_n$)** | 0.080 ~ 0.130 mm | 0.080 ~ 0.130 mm | Betriebsflankenspiel |

---

## 3.6 Zweiachsige Kraftzerlegung, Lagerreaktionen und HPSTC-Zahnfußbeanspruchung

### Zweiachsige Kraftzerlegung an der Flanke

Unter dem Ritzeldrehmoment $T_1$ zerfällt die Flankennormalkraft $F_n$ in die Umfangskraft $F_t$ und die Radialkraft $F_r$:

__MATH_BLOCK_24__

Für das Referenzritzel bei $T_1 = 100.0\text{ N}\cdot\text{m}$:

__MATH_BLOCK_25__

### Mechanische Begründung der ISO 6336 Methode B (Biegebruch am HPSTC)

Ein verbreiteter Trugschluss besteht in der Annahme, die maximale Zahnfußbiegespannung trete bei Lastangriff am Zahnkopf (Punkt E) auf. Tatsächlich wird der Dauerfestigkeitsnachweis nach ISO 6336 Methode B am **äußeren Einzeleingriffspunkt (Punkt D, HPSTC)** geführt:

1. **Zahnkopfberührung (Punkt E)**: Befindet sich das Zahnpaar bei Punkt E, steht das nachfolgende Paar bereits bei Punkt B im Eingriff ($s_E - s_B = p_b$). Die Last verteilt sich auf zwei Zähne ($F_{n,E} \approx 0.5 F_n$).
2. **HPSTC (Punkt D)**: Punkt D ist der äußerste Punkt des Einzeleingriffs. Hier greift die volle Zahnkraft zu 100% an einem einzelnen Zahn an ($F_{n,D} = 1.0 F_n$).
3. **Vergleich der Biegemomente**: Mit dem Hebelarm $h_D$ bei Punkt D und $h_E$ bei Punkt E:

__MATH_BLOCK_26__

Wegen $h_E \approx 1.20 h_D$ ergibt sich das Verhältnis:

__MATH_BLOCK_27__

Das Biegemoment bei Punkt D ist rund 1.67-mal größer als bei Punkt E. Zahnfußbrüche entstehen ausnahmslos durch diese maximale Zugspannung bei Punkt D.

### Lagerreaktionen bei beidseitig gelagerter Welle

Für eine Welle mit Lagerabstand $L = 100.0\text{ mm}$ und Ritzelabstand $L_1 = 40.0\text{ mm}$ von Lager A:

__MATH_BLOCK_28__

Radiale Lagerbelastungen:

__MATH_BLOCK_29__

Die Auswertung liefert $F_{rA} = 2364.839494\text{ N}$ und $F_{rB} = 1576.559663\text{ N}$, die als Eingangsgrößen für die Lagerlebensdauerrechnung ($L_{10h}$) dienen.

---

## 3.7 Internationaler Normenvergleich und Literaturverzeichnis

### Vergleich der Normbegriffe

| Begriff | ISO 21771:2007 | DIN 3960 | AGMA 9005-F16 / 2001 | Earle Buckingham (1949) |
|:---|:---:|:---:|:---:|:---:|
| **Eingriffslinie** | Line of action | Eingriffslinie | Line of action | Line of action |
| **Überdeckung** | Transverse contact ratio $\epsilon_\alpha$ | Profilüberdeckung $\epsilon_\alpha$ | Contact ratio $m_p$ | Contact ratio CR |
| **Grundteilung** | Base pitch $p_b$ | Grundteilung $p_b$ | Base pitch $p_b$ | Normal pitch $p_N$ |
| **Eingriffsbeginn** | Point A ($E_A$) | Punkt A | SAP | Point A |
| **Innerer Einzeleingriff** | Point B ($B$) | Punkt B | LPSTC | Point B |
| **Wälzpunkt** | Pitch point $C$ / $P$ | Wälzpunkt $C$ | Pitch point | Pitch point |
| **Äußerer Einzeleingriff** | Point D ($D$) | Punkt D | HPSTC | Point D |
| **Eingriffsende** | Point E ($E_E$) | Punkt E | EAP | Point E |
| **Spezifisches Gleiten** | Specific sliding $k$ | Spezifisches Gleiten $g$ | Specific sliding | Specific sliding |
| **Biegebruch-Referenz** | Point D (ISO 6336-3) | Punkt D (DIN 3990) | HPSTC (AGMA 2001) | Point D |

### Literaturverzeichnis

1. **Earle Buckingham**, *Analytical Mechanics of Gears*, McGraw-Hill Book Company, 1949 (Dover Publications Reprint, 1988), Chapter 18 "Gear Teeth in Action" & Chapter 19 "Efficiencies of Gears".
2. **DIN 3960:1987-03**, *Begriffe und Bestimmungsgrößen für Stirnräder (Zylinderräder) und Stirnradpaare (Zylinderradpaare) mit Evolventenverzahnung*, Deutsches Institut für Normung.
3. **ISO 21771:2007**, *Gears — Cylindrical involute gears and gear pairs — Concepts and geometry*, International Organization for Standardization.
4. **ISO 6336-1/2/3:2019**, *Calculation of load capacity of spur and helical gears — Part 3: Calculation of tooth bending strength (Method B)*.
5. **DIN 867:1986-02**, *Bezugsprofile für Evolventenverzahnungen an Stirnrädern (Zylinderrädern) für den allgemeinen Maschinenbau und den Schwermaschinenbau*.
6. **Dudley, D. W.**, *Handbook of Practical Gear Design*, CRC Press, 1994.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content


# -----------------------------------------------------------------------------
# Japanese Content Generation (일본어)
# -----------------------------------------------------------------------------
def build_ja() -> str:
    content = r"""---
title: "第3章. 平歯車のかみ合い運動力学：作用線、正面かみ合い率および滑り率"
description: "平歯車のかみ合い運動力学に関する本格的機械工学論考：作用線上の5大特異点の閉形式幾何学的導出、正面かみ合い率ε_αと単一歯・2歯荷重分担領域の力学、相対滑り速度および滑り率k1, k2の分布特性、ISO 6336に基づくHPSTC歯元曲げ応力集中、およびJIS/KS製作図面要目表の実務体系。"
series: theory
part: 1
chapter: 3
gear_type: spur
standards:
  - "JIS B 0102"
  - "JIS B 1701"
  - "ISO 21771:2007"
  - "DIN 3960"
required_diagrams:
  - "fig1_line_of_action_five_points"
  - "fig2_tooth_load_sharing"
  - "fig3_contact_kinematics_velocities"
  - "fig4_specific_sliding_curves"
academic_level: undergraduate
equations_hash: "{EQ_HASH}"
review_date: "2026-11-15"
sidebar:
  order: 3
---

## 3.1 直観的問題提起と物理的背景

歯車伝動の基本目的は、2軸間で角速度比を一切の滑りや変動なく一定に維持しながら動力を伝達することです。平歯車対がかみ合って回転する際、動力を途切れなく円滑に伝達するためには、幾何学的に厳密な連続かみ合い条件が満たされなければなりません。

### 連続伝動の力学的必然性

先行するかみ合い歯対が接触を終了して離脱する前に、必ず後続の歯対が作用線上で接触を開始していなければなりません。もし正面かみ合い率が1を下回る場合（$\epsilon_\alpha < 1.0$）、かみ合いの空白領域（デッドゾーン）が発生します。

この瞬間、駆動軸と従動軸の間の位相差が瞬間的に開き、後続の歯がかみ合う際に歯面同士が極めて過大な動的衝撃力（$F_{\mathrm{dyn}} = I \frac{d\omega}{dt}$）で衝突します。これは減速機内部で激しい衝撃騒音と振動を引き起こすだけでなく、歯元に加わる衝撃曲げ応力によって歯が根元からへし折れる歯欠け事故を招きます。

伝動の連続性を保証するためには、作用線上での有効かみ合い長さ（$g_\alpha$）が、隣接する歯の法線ピッチ（$p_b$）を常に上回る必要があります。この比率を指標化したものが正面かみ合い率（Transverse Contact Ratio, $\epsilon_\alpha$）です。

__MATH_BLOCK_0__

産業用動力伝動設計においては、製作誤差、軸のたわみ、歯の熱変形などを考慮し、$\epsilon_\alpha \ge 1.20$ を絶対的な推奨最小基準として規定しています。

### 歯面接触部位別の転動と滑りのメカニズム

歯面接触において、すべての接触位置で一様な摩擦状態が生じるわけではありません。基準ピッチ円同士が外接するピッチ点（点C/P）では、双方の歯面の接線線速度が完全に一致し、相対滑り速度が厳密にゼロとなる**純粋転がり接触（Pure Rolling）**が実現されます。

ピッチ点から離れて歯元や歯先へ移動すると、状況は一変します。歯形曲率半径の差異によって激しい相対滑り摩擦（Sliding Friction）が発生します。

- **歯元領域（Dedendum Flank）**：転がり方向と滑り方向が逆転する負の滑り率状態となり、摩擦せん断応力が歯面内部に集中します。これにより、微細な金属片が脱落する転動疲労損傷である**ピッチング（Pitting）**が発生します。
- **歯先領域（Addendum Flank）**：相対滑り速度が最大に達する領域です。高トルク・高速運転下で弾性流体潤滑膜（EHL油膜）が破断すると、瞬時フラッシュ温度の上昇によって金属表面同士が凝着し、引き裂かれる**スコーリング（Scuffing/焼付き）**が生じます。

歯車が回転するにつれて、1組の歯が全荷重を担う単一歯かみ合い領域と、2組の歯が荷重を分け合う2歯かみ合い領域が交互に入れ替わります。この総合かみ合い剛性の周期的変動が、減速機ハウジングを共振させる高周波歯車騒音（ギアワインノイズ）の根本加振源となります。

---

## 3.2 幾何学・三角関数・微積分に基づく正統数学的導出

### 作用線と共通接線線分の長さ

インボリュート歯形において、接触点の法線は常に2つの基礎円に接する共通内接線を追従し、この直線を作用線（Line of Action）と呼びます。駆動ピニオンの基礎円接点を$T_1$、従動歯車の基礎円接点を$T_2$とするとき、接点間の全線分長さ$\overline{T_1 T_2}$は中心距離$a$と基準圧力角$\alpha_0$から閉形式で導出されます。

__MATH_BLOCK_1__

### 作用線上の5大特異点（Five Cardinal Points）の閉形式導出

作用線上のかみ合い力学を支配する5大特異点の位置を、ピニオン基礎円接点$T_1$（$s = 0.0\text{ mm}$）を原点とする1次元座標$s$として定式化します。

1. **点A（SAP, かみ合い開始点）**：従動大歯車の歯先円（半径$r_{a2}$）が作用線と交差する点です。直角三角形$\Delta O_2 T_2 A$から接点$T_2$からの距離は$\sqrt{r_{a2}^2 - r_{b2}^2}$であり、点$T_1$からの座標$s_A$は次式となります。

__MATH_BLOCK_2__

2. **点E（EAP, かみ合い終了点）**：駆動ピニオンの歯先円（半径$r_{a1}$）が作用線と交差する点であり、直角三角形$\Delta O_1 T_1 E$から直接求まります。

__MATH_BLOCK_3__

3. **点B（LPSTC, 単一歯かみ合い最内点）**：駆動ピニオンの先行歯が点Eでかみ合いを終了する瞬間の後続歯の接触位置であり、点Eから法線ピッチ$p_b$だけ内側に位置します。

4. **点D（HPSTC, 単一歯かみ合い最外点）**：後続歯対が点Aで新たにかみ合いを開始する瞬間の先行歯の接触位置であり、点Aから法線ピッチ$p_b$だけ外側に位置します。

__MATH_BLOCK_4__

5. **点C / P（ピッチ点）**：ピッチ円同士の接点であり、純粋転がり接触が成立する基準点です。

__MATH_BLOCK_5__

これら5大特異点は、正常なかみ合いを維持するために作用線上で厳密な単調増加順序を保たなければなりません。

__MATH_BLOCK_6__

![作用線上の5大特異点（A, B, C, D, E）とかみ合い長さの幾何学](/images/part3/ja/fig1_line_of_action_five_points.png)

### かみ合い長さと正面かみ合い率の導出

実際の有効かみ合い線分は$\overline{AE}$です。ピッチ点$P$を境として接近かみ合い長さ（$g_f = \overline{AP}$）と遠退かみ合い長さ（$g_a = \overline{PE}$）に区分されます。

__MATH_BLOCK_7__

全有効かみ合い長さ$g_\alpha$は両者の和となります。

__MATH_BLOCK_8__

作用線上の歯の法線間隔である法線ピッチ（基礎円ピッチ）$p_b$は円ピッチ$p = \pi m$の基礎円投影です。

__MATH_BLOCK_9__

したがって、正面かみ合い率$\epsilon_\alpha$の閉形式公式が導かれます。

__MATH_BLOCK_10__

### 単一歯および2歯荷重分担領域の分割

かみ合い率が$1.0 < \epsilon_\alpha < 2.0$の平歯車において、接触線は荷重分担状態に応じて3領域に分割されます。

1. **2歯かみ合い領域（$\overline{AB}$および$\overline{DE}$）**：
   - 2対の歯が同時にかみ合い、全伝達法線力を約50%ずつ分担します。
   - 各領域の長さは$g_\alpha - p_b$であり、合計長さは$2(g_\alpha - p_b)$です。
2. **単一歯かみ合い領域（$\overline{BD}$）**：
   - 唯一対の歯のみが全伝達荷重の100%を独占して支える過酷な領域です。
   - 単一歯かみ合い長さは$g_1 = s_D - s_B = 2p_b - g_\alpha$です。

__MATH_BLOCK_11__

幾何学的長さ保存則により、単一歯領域と2歯領域の和は厳密に全かみ合い長さ$g_\alpha$に一致します。

__MATH_BLOCK_12__

![作用線上の単一歯および2歯かみ合い領域と荷重分担率の分布](/images/part3/ja/fig2_tooth_load_sharing.png)

### 線速度および相対滑り速度の導出

作用線上の任意座標$s$におけるピニオンおよび大歯車の歯形曲率半径はそれぞれ$\rho_1(s) = s$、$\rho_2(s) = \overline{T_1 T_2} - s$です。角速度を$\omega_1, \omega_2$とするとき、歯面法線方向の接線線速度は次の通りです。

__MATH_BLOCK_13__

歯面間の相対滑り速度$v_g(s)$は両線速度の差として求まります。

__MATH_BLOCK_14__

ピッチ点からの距離$x = s - s_C$に対して滑り速度は完全な1次線形関係をなし、ピッチ点（$x = 0$）で$v_g = 0$となって純粋転がりが成立します。ピッチ点を境に滑りの方向が反転します。

![歯面接触点における線速度ベクトル分解と相対滑り速度の反転機構](/images/part3/ja/fig3_contact_kinematics_velocities.png)

### 滑り率（Specific Sliding）と代数恒等式

歯面の摩耗および摩擦発熱の指標となる無次元量が滑り率（Specific Sliding, $k$）です。

駆動ピニオンの滑り率$k_1(s)$：

__MATH_BLOCK_15__

従動大歯車の滑り率$k_2(s)$：

__MATH_BLOCK_16__

両滑り率の間には、歯数や圧力角によらず常に厳密に成立する不変の代数恒等式が存在します。

__MATH_BLOCK_17__

基礎円接点付近（$\rho \to 0$）では、滑り率が負の無限大（$-\infty$）へと急激に発散します。歯数の少ないピニオンでは点A（歯元部）が基礎円に接近するため、歯元の滑り摩耗リスクが跳ね上がります。これこそが、小歯数ピニオンに正の転位係数（$x_1 > 0$）を与えて有効歯形を基礎円の外側へと逃がさなければならない決定的な力学的理由です。

![作用線上のピニオンおよび大歯車の相対滑り率（Specific Sliding）曲線分布](/images/part3/ja/fig4_specific_sliding_curves.png)

---

## 3.3 主要公式要約表および38項目閉形式計算表

ベンチマーク諸元：

__MATH_BLOCK_18__

基準ピッチ円および基礎円半径：

__MATH_BLOCK_19__

かみ合い長さおよびかみ合い率計算結果：

__MATH_BLOCK_20__

単一歯・2歯かみ合い領域の分割：

__MATH_BLOCK_21__

5大特異点における滑り率計算値：

__MATH_BLOCK_22__

### 38項目閉形式計算値表

以下は、$m = 3.0\text{ mm}, z_1 = 18, z_2 = 54, \alpha_0 = 20.0^\circ, a = 108.0\text{ mm}$の標準平歯車対に関する38項目の理論的閉形式計算値です。

| 番号 | 幾何学的パラメータ | 記号 | 算出公式 | 理論的厳密値 | 単位 |
|:---:|:---|:---:|:---|:---:|:---:|
| 1 | 減速比 | $u$ | $z_2 / z_1$ | 3.000000 | — |
| 2 | ピニオン基準ピッチ円直径 | $d_1$ | $m \cdot z_1$ | 54.000000 | mm |
| 3 | ピニオン基準ピッチ円半径 | $r_1$ | $d_1 / 2$ | 27.000000 | mm |
| 4 | 大歯車基準ピッチ円直径 | $d_2$ | $m \cdot z_2$ | 162.000000 | mm |
| 5 | 大歯車基準ピッチ円半径 | $r_2$ | $d_2 / 2$ | 81.000000 | mm |
| 6 | 標準中心距離 | $a$ | $(d_1 + d_2) / 2$ | 108.000000 | mm |
| 7 | 円ピッチ | $p$ | $\pi m$ | 9.424778 | mm |
| 8 | 基準歯厚および歯溝幅 | $s, e$ | $p / 2$ | 4.712389 | mm |
| 9 | 基礎円ピッチ（法線ピッチ） | $p_b$ | $\pi m \cos\alpha_0$ | 8.856394 | mm |
| 10 | ピニオン基礎円直径 | $d_{b1}$ | $d_1 \cos\alpha_0$ | 50.743402 | mm |
| 11 | ピニオン基礎円半径 | $r_{b1}$ | $d_{b1} / 2$ | 25.371701 | mm |
| 12 | 大歯車基礎円直径 | $d_{b2}$ | $d_2 \cos\alpha_0$ | 152.230205 | mm |
| 13 | 大歯車基礎円半径 | $r_{b2}$ | $d_{b2} / 2$ | 76.115102 | mm |
| 14 | 歯先たけ | $h_a$ | $1.0 \cdot m$ | 3.000000 | mm |
| 15 | 歯底たけ | $h_f$ | $1.25 \cdot m$ | 3.750000 | mm |
| 16 | 全歯たけ | $h$ | $h_a + h_f$ | 6.750000 | mm |
| 17 | 頂げき | $c$ | $0.25 \cdot m$ | 0.750000 | mm |
| 18 | ピニオン歯先円直径 | $d_{a1}$ | $d_1 + 2h_a$ | 60.000000 | mm |
| 19 | ピニオン歯先円半径 | $r_{a1}$ | $d_{a1} / 2$ | 30.000000 | mm |
| 20 | 大歯車歯先円直径 | $d_{a2}$ | $d_2 + 2h_a$ | 168.000000 | mm |
| 21 | 大歯車歯先円半径 | $r_{a2}$ | $d_{a2} / 2$ | 84.000000 | mm |
| 22 | ピニオン歯底円直径 | $d_{f1}$ | $d_1 - 2h_f$ | 46.500000 | mm |
| 23 | ピニオン歯底円半径 | $r_{f1}$ | $d_{f1} / 2$ | 23.250000 | mm |
| 24 | 大歯車歯底円直径 | $d_{f2}$ | $d_2 - 2h_f$ | 154.500000 | mm |
| 25 | 大歯車歯底円半径 | $r_{f2}$ | $d_{f2} / 2$ | 77.250000 | mm |
| 26 | 基準圧力角インボリュート値 | $\mathrm{inv}\,\alpha_0$ | $\tan 20^\circ - 20^\circ \frac{\pi}{180}$ | 0.014904 | rad |
| 27 | ピニオン歯先圧力角 | $\alpha_{a1}$ | $\arccos(r_{b1} / r_{a1})$ | 32.250479 | deg |
| 28 | 大歯車歯先圧力角 | $\alpha_{a2}$ | $\arccos(r_{b2} / r_{a2})$ | 25.023798 | deg |
| 29 | ピニオン歯先インボリュート値 | $\mathrm{inv}\,\alpha_{a1}$ | $\tan\alpha_{a1} - \alpha_{a1}$ | 0.068088 | rad |
| 30 | 大歯車歯先インボリュート値 | $\mathrm{inv}\,\alpha_{a2}$ | $\tan\alpha_{a2} - \alpha_{a2}$ | 0.030066 | rad |
| 31 | ピニオン歯先頂幅 | $s_{a1}$ | $2 r_{a1} \psi_{a1}$ | 2.044991 | mm |
| 32 | 大歯車歯先頂幅 | $s_{a2}$ | $2 r_{a2} \psi_{a2}$ | 2.339811 | mm |
| 33 | 遠退かみ合い長さ | $g_a$ | $\sqrt{r_{a1}^2 - r_{b1}^2} - r_{b1}\tan\alpha_0$ | 6.774104 | mm |
| 34 | 接近かみ合い長さ | $g_f$ | $\sqrt{r_{a2}^2 - r_{b2}^2} - r_{b2}\tan\alpha_0$ | 7.827921 | mm |
| 35 | 全かみ合い長さ | $g_\alpha$ | $g_a + g_f$ | 14.602024 | mm |
| 36 | 正面かみ合い率 | $\epsilon_\alpha$ | $g_\alpha / p_b$ | 1.648755 | — |
| 37 | 単一歯かみ合い長さ | $g_1$ | $2 p_b - g_\alpha$ | 3.110764 | mm |
| 38 | 2歯かみ合い長さ | $g_2$ | $2(g_\alpha - p_b)$ | 11.491260 | mm |

ピニオンおよび大歯車の歯先頂幅（$s_{a1} = 2.045\text{ mm}, s_{a2} = 2.340\text{ mm}$）は限界値$0.25m = 0.75\text{ mm}$を大幅に上回り、尖頭化の危険はありません。正面かみ合い率$\epsilon_\alpha = 1.648755$は推奨基準1.20を超え、全かみ合い長さの78.70%において安定した2歯接触が維持されます。

---

## 3.4 精密寸法検査工学と歯面損傷メカニズム

### 荷重分担ステップ関数と歯面損傷

作用線上を進行する単位歯幅あたりの法線荷重強度$w_N(s)$は、単一歯領域と2歯領域の間で急激な階段状遷移を示します。

__MATH_BLOCK_23__

単一歯かみ合い領域（$\overline{BD}$）に突入すると、1本の歯が担う荷重強度は一気に2倍に跳ね上がります。

### ピッチング（Pitting）の発生機構

ピッチングは歯面に加わる繰返し接触応力による表面疲労破壊です。
- 発生位置：ピッチ線直下のピニオン歯元領域（線分$\overline{BC}$付近）に集中します。
- 物理的理由：単一歯かみ合い領域（100%全荷重）において負の滑りが作用し、表面下深さ（$z \approx 0.78 b_H$）で最大せん断応力（$\tau_{\max} \approx 0.30 p_0$）が発生します。開口した微小き裂に潤滑油が浸入し、転動に伴う油圧くさび作用（Hydraulic Wedge Effect）によって金属片がはぎ取られます。

### スコーリング（Scuffing/焼付き）の発生機構

スコーリングは摩擦熱により油膜が破壊され、金属同士が凝着・引裂きを起こす熱的損傷です。
- 発生位置：作用線の両端である点A（ピニオン歯元）および点E（ピニオン歯先）で発生します。
- 物理的理由：相対滑り速度が最大となる位置であり、Blokのフラッシュ温度理論に従い摩擦発熱が潤滑油の限界温度を超過するためです。

---

## 3.5 JIS B 0003 / KS B 0002 製作図面要目表の実務体系

歯車設計の最終成果物は、工作機械による歯切り加工および測定検査のための製作図面要目表です。以下は、JIS B 0003（歯車製図）およびISO規格に準拠した17大項目の要目表です。

| 項目（Item） | ピニオン設計データ | 大歯車設計データ | 備考および準拠規格 |
|:---|:---:|:---:|:---|
| **歯形（Tooth Profile）** | 標準インボリュート | 標準インボリュート | JIS B 0102 / KS B 0102 |
| **基準ラック歯形（Basic Rack）** | 円筒歯車用基準ラック | 円筒歯車用基準ラック | JIS B 1701 / ISO 53 Profile A |
| **モジュール（Module, $m$）** | 3.000 mm | 3.000 mm | 標準第1系列 |
| **基準圧力角（Standard Pressure Angle, $\alpha_0$）** | 20.0° | 20.0° | 基準歯形 |
| **歯数（Number of Teeth, $z$）** | 18 | 54 | 減速比 $u = 3.000$ |
| **転位係数（Profile Shift Coefficient, $x$）** | 0.0000 | 0.0000 | 標準並歯（無転位） |
| **基準ピッチ円直径（Pitch Diameter, $d$）** | 54.000 mm | 162.000 mm | $d = m \cdot z$ |
| **基礎円直径（Base Diameter, $d_b$）** | 50.743 mm | 152.230 mm | $d_b = d \cos\alpha_0$ |
| **歯先円直径（Tip Diameter, $d_a$）** | 60.000 mm | 168.000 mm | 加工公差 0 / -0.040 mm |
| **歯底円直径（Root Diameter, $d_f$）** | 46.500 mm | 154.500 mm | $h_f = 1.25 m$ |
| **全歯たけ（Whole Depth, $h$）** | 6.750 mm | 6.750 mm | $h = 2.25 m$ |
| **相手歯数（Mating Teeth）** | 54 | 18 | かみ合い相手歯車指定 |
| **標準中心距離（Center Distance, $a$）** | 108.000 mm | 108.000 mm | 組立公差 ±0.020 mm |
| **正面かみ合い率（Transverse Contact Ratio, $\epsilon_\alpha$）** | 1.65 (1.648755) | 1.65 (1.648755) | 推奨基準 $\ge 1.20$ 充足 |
| **有効かみ合い長さ（Path of Contact, $g_\alpha$）** | 14.602 mm | 14.602 mm | 作用接触長さ |
| **法線ピッチ（Normal Pitch, $p_b$）** | 8.856 mm | 8.856 mm | $p_b = \pi m \cos\alpha_0$ |
| **精度等級（Accuracy Grade）** | JIS 5級（精密減速機級） | JIS 5級（精密減速機級） | JIS B 1702-1 / ISO 1328-1 |
| **法線バックラッシ（Normal Backlash, $j_n$）** | 0.080 ~ 0.130 mm | 0.080 ~ 0.130 mm | 組立・熱膨張余裕 |

---

## 3.6 2軸分力および軸受荷重解析：HPSTC歯元曲げ応力集中

### 2軸歯面分力の分解

ピニオンに駆動トルク$T_1$が入力されるとき、法線力$F_n$は接線力$F_t$と半径方向力$F_r$に直交分解されます。

__MATH_BLOCK_24__

ピニオン入力トルク$T_1 = 100.0\text{ N}\cdot\text{m}$に対する各分力の計算値：

__MATH_BLOCK_25__

### ISO 6336 Method Bの力学的根拠（HPSTC歯元曲げ支配性）

「曲げモーメント腕の最も長い歯先（点E）に荷重が加わるときに歯元曲げ応力が最大になる」という直観的誤解が存在しますが、実際の疲労破壊は**点D（HPSTC, 単一歯かみ合い最外点）**で発生し、ISO 6336規格でも歯形係数$Y_F$を点Dの荷重条件で算定するよう義務付けています。

1. **歯先（点E）接触時**：接触が点Eにあるとき、後続歯は既に点B（LPSTC）でかみ合っています（$s_E - s_B = p_b$）。したがって2歯かみ合いとなり、荷重は約半分に分担されます（$F_{n,E} \approx 0.5 F_n$）。
2. **点D（HPSTC）接触時**：点Bから点Dまでは単一の歯が100%全荷重を担います（$F_{n,D} = 1.0 F_n$）。点Dは全荷重が加わる最も歯元から遠い最外端位置です。
3. **歯元モーメント比較**：危険断面から点Dおよび点Eまでのモーメント腕を$h_D, h_E$とするとき：

__MATH_BLOCK_26__

平歯車幾何学において$h_E \approx 1.20 h_D$であるため、モーメント比は次の通りです。

__MATH_BLOCK_27__

点Dでの歯元曲げモーメントは歯先接触時よりも約1.67倍大きく、歯元曲げ疲労破断は例外なく点D通過時の最大引張応力によって引き起こされます。

### 単純支持軸系の軸受反力モデル

軸受間スパン$L = 100.0\text{ mm}$、軸受Aからピニオンまでの距離$L_1 = 40.0\text{ mm}$の静力学反力：

__MATH_BLOCK_28__

合成ラジアル軸受荷重：

__MATH_BLOCK_29__

計算により、軸受Aには$F_{rA} = 2364.839494\text{ N}$、軸受Bには$F_{rB} = 1576.559663\text{ N}$の荷重が作用し、これが軸受寿命（$L_{10h}$）計算の基本値となります。

---

## 3.7 国際標準規格比較および参考文献

### 規格別用語の対照比較

| 概念 | ISO 21771:2007 | DIN 3960 | AGMA 9005-F16 / 2001 | Earle Buckingham (1949) |
|:---|:---:|:---:|:---:|:---:|
| **作用線** | Line of action | Eingriffslinie | Line of action | Line of action |
| **かみ合い率** | Transverse contact ratio $\epsilon_\alpha$ | Profilüberdeckung $\epsilon_\alpha$ | Contact ratio $m_p$ | Contact ratio CR |
| **基礎円ピッチ** | Base pitch $p_b$ | Grundteilung $p_b$ | Base pitch $p_b$ | Normal pitch $p_N$ |
| **かみ合い開始点** | Point A ($E_A$) | Punkt A | SAP | Point A |
| **単一歯最内点** | Point B ($B$) | Punkt B | LPSTC | Point B |
| **ピッチ点** | Pitch point $C$ / $P$ | Wälzpunkt $C$ | Pitch point | Pitch point |
| **単一歯最外点** | Point D ($D$) | Punkt D | HPSTC | Point D |
| **かみ合い終了点** | Point E ($E_E$) | Punkt E | EAP | Point E |
| **滑り率** | Specific sliding $k$ | Spezifisches Gleiten $g$ | Specific sliding | Specific sliding |
| **曲げ強度基準点** | Point D (ISO 6336-3) | Punkt D (DIN 3990) | HPSTC (AGMA 2001) | Point D |

### 参考文献

1. **Earle Buckingham**, *Analytical Mechanics of Gears*, McGraw-Hill Book Company, 1949 (Dover Publications Reprint, 1988), Chapter 18 "Gear Teeth in Action" & Chapter 19 "Efficiencies of Gears".
2. **DIN 3960:1987-03**, *Begriffe und Bestimmungsgrößen für Stirnräder (Zylinderräder) und Stirnradpaare (Zylinderradpaare) mit Evolventenverzahnung*, Deutsches Institut für Normung.
3. **ISO 21771:2007**, *Gears — Cylindrical involute gears and gear pairs — Concepts and geometry*, International Organization for Standardization.
4. **ISO 6336-1/2/3:2019**, *Calculation of load capacity of spur and helical gears — Part 3: Calculation of tooth bending strength (Method B)*.
5. **JIS B 0102:2013**, *歯車用語 — 幾何学的定義*, 日本規格協会.
6. **JIS B 1701-1:2012**, *円筒歯車 — インボリュート歯車歯形 — 第1部：標準基準ラック歯形*, 日本規格協会.
7. **JIS B 0003:2012**, *製図 — 歯車製図*, 日本規格協会.
8. **Dudley, D. W.**, *Handbook of Practical Gear Design*, CRC Press, 1994.
"""
    content = content.replace("{EQ_HASH}", EQ_HASH)
    for _idx in range(len(DISPLAY_BLOCKS)):
        content = content.replace(f"__MATH_BLOCK_{_idx}__", format_math_block(_idx))
    return content


# -----------------------------------------------------------------------------
# Main Builder Pipeline
# -----------------------------------------------------------------------------
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
        out_file = out_dir / "03-meshing-kinematics.mdx"
        out_file.write_text(content, encoding="utf-8")
        print(f"Generated: {out_file} ({len(content)} chars)")

        # Verify KaTeX display blocks and hash locally
        display_blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
        norm = "\n---\n".join(b.strip() for b in display_blocks)
        cur_hash = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        assert cur_hash == EQ_HASH, f"Hash mismatch in {lang}: {cur_hash} != {EQ_HASH}"
        assert len(display_blocks) == len(DISPLAY_BLOCKS), (
            f"Display blocks count mismatch in {lang}: {len(display_blocks)} != {len(DISPLAY_BLOCKS)}"
        )
        print(f"  -> Verified {len(display_blocks)} display blocks, hash: {cur_hash} (OK)")

    print("\nAll 4 Chapter 3 MDX files generated and verified successfully!")


if __name__ == "__main__":
    main()
