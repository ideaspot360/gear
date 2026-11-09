---
title: Chapter 1 Contact Kinematics of Planar Curves and Conjugate Action
description: Mathematical proof of the fundamental law of gearing and invariant transmission ratio of involute profiles
---

## 1. Definition of Conjugate Action

To transmit a strictly constant angular velocity ratio ($u = \omega_1 / \omega_2$) between two rotating shafts, the meshing tooth profiles must satisfy **conjugate action**.

When two tooth profiles $\Sigma_1$ and $\Sigma_2$ contact at any instantaneous point $K$, the common normal $\vec{n}$ at the contact point must pass through a fixed point $P$ (the Pitch Point) located on the line of centers connecting $O_1$ and $O_2$:

$$
\frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \text{constant} = u
$$

This formulation constitutes the **Fundamental Law of Gearing (Willis Law)**.

---

## 2. Differential Geometry Derivation

Let $S_1(O_1; x_1, y_1)$ and $S_2(O_2; x_2, y_2)$ denote coordinate frames rigidly attached to Gear 1 and Gear 2, rotating at angular velocities $\omega_1$ and $\omega_2$ relative to the fixed reference frame $S_f(O_f; x_f, y_f)$.

The relative velocity vector $\vec{v}^{(12)}$ at the instantaneous contact point $K$ is defined as:

$$
\vec{v}^{(12)} = \vec{v}^{(1)} - \vec{v}^{(2)} = (\vec{\omega}_1 \times \vec{r}_1) - (\vec{\omega}_2 \times \vec{r}_2)
$$

The necessary and sufficient geometric condition for continuous engagement without penetration or separation is that the projection of the relative velocity along the common surface normal $\vec{n}$ must vanish:

$$
\vec{v}^{(12)} \cdot \vec{n} = 0
$$

Expanding this relation through scalar triple products demonstrates that the intersection of the line of action and the centerline remains stationary:

$$
(\vec{\omega}_1 \times \vec{O_1 K} - \vec{\omega}_2 \times \vec{O_2 K}) \cdot \vec{n} = 0 \implies (r_1 \omega_1 \cos\alpha - r_2 \omega_2 \cos\alpha) = 0
$$

Consequently, the pitch point $P$ remains invariant over the entire meshing cycle.

---

## 3. Mathematical Invariance of Involute Curves

The parametric equations of an involute of a circle with base radius $r_b$ are expressed as:

$$
\begin{cases}
x(\theta) = r_b (\cos\theta + \theta \sin\theta) \\
y(\theta) = r_b (\sin\theta - \theta \cos\theta)
\end{cases}
$$

The singular engineering superiority of the involute profile lies in its **center distance insensitivity**: even when the nominal center distance $a$ is altered to $a'$ due to manufacturing tolerances or thermal growth, the working pressure angle $\alpha_{wt}$ adjusts deterministically while maintaining an exact velocity ratio:

$$
a' \cos\alpha_{wt} = a \cos\alpha_t = r_{b1} + r_{b2}
$$

