---
title: 제1장 평면 곡선의 접촉 기구학과 공액 치형(Conjugate Tooth Profiles)
description: 윌리스 맞물림 법칙의 수학적 증명 및 인볼류트 곡선의 공액 접촉 불변성 해석
---

## 1. 공액 치형(Conjugate Profiles)의 정의

두 회전체 사이에서 일정한 각속도비($u = \omega_1 / \omega_2$)를 전달하기 위해서는, 맞물리는 치형 곡선 쌍이 **공액 관계(Conjugate Action)**를 만족해야 한다.

두 치형 곡선 $\Sigma_1$과 $\Sigma_2$가 임의의 접점 $K$에서 접촉할 때, 접촉점에서의 공통 법선(Common Normal) $\vec{n}$은 두 기어의 회전 중심 $O_1, O_2$를 잇는 중심선과 반드시 고정된 한 점 $P$(피치점, Pitch Point)에서 교차해야 한다.

$$
\frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \text{constant} = u
$$

이것이 기어 기하학의 근본을 이루는 **윌리스(Willis)의 맞물림 기본 법칙**이다.

---

## 2. 윌리스 맞물림 법칙의 미분기하학적 증명

각 기어의 고정 좌표계를 $S_1(O_1; x_1, y_1)$ 및 $S_2(O_2; x_2, y_2)$라 하고, 고정 프레임 $S_f(O_f; x_f, y_f)$에 대해 각속도 $\omega_1, \omega_2$로 회전한다고 가정하자.

접점 $K$에서의 상대 속도 벡터 $\vec{v}^{(12)}$는 다음과 같이 표현된다:

$$
\vec{v}^{(12)} = \vec{v}^{(1)} - \vec{v}^{(2)} = (\vec{\omega}_1 \times \vec{r}_1) - (\vec{\omega}_2 \times \vec{r}_2)
$$

연속 접촉(Continuous Contact)이 유지되기 위한 기하학적 필요충분조건은 치면 법선 방향의 상대 속도가 $0$이어야 한다는 점이다:

$$
\vec{v}^{(12)} \cdot \vec{n} = 0
$$

이를 스칼라 삼중적으로 전개하면, 순간 회전축(Instantaneous Axis of Rotation)과 법선 벡터의 기하학적 관계로부터 다음의 결론이 도출된다:

$$
(\vec{\omega}_1 \times \vec{O_1 K} - \vec{\omega}_2 \times \vec{O_2 K}) \cdot \vec{n} = 0 \implies (r_1 \omega_1 \cos\alpha - r_2 \omega_2 \cos\alpha) = 0
$$

따라서 두 회전 중심 $O_1, O_2$와 공통 법선의 교점 $P$의 위치는 시간에 무관하게 고정되며, 각속도비 $u$는 영구히 일정하게 유지된다.

---

## 3. 인볼류트 곡선의 수학적 필연성

인볼류트 곡선(Involute Curve)은 기초원(Base Circle) 반경 $r_b$로부터 풀려 나오는 실의 끝점이 그리는 궤적이다:

$$
\begin{cases}
x(\theta) = r_b (\cos\theta + \theta \sin\theta) \\
y(\theta) = r_b (\sin\theta - \theta \cos\theta)
\end{cases}
$$

인볼류트 치형의 가장 독보적인 공학적 장점은 **중심거리 $a$가 조립 오차나 베어링 처짐으로 인해 $a'$로 변동하더라도, 작용 압력각 $\alpha_w$가 다음 식에 의해 자가 적응(Self-Adapting)하여 각속도비 $u$가 단 $0.000000\%$의 왜곡도 없이 일정하게 보존**된다는 점이다:

$$
a' \cos\alpha_{wt} = a \cos\alpha_t = r_{b1} + r_{b2}
$$

이것이 수 세기 동안 수많은 곡선 중 인볼류트가 정밀 기계 동력 전달의 세계 표준으로 군당한 수학적 이유이다.

