---
title: Kapitel 1 Kontaktkinematik ebener Kurven und das Verzahnungsgesetz
description: Mathematischer Beweis des Willis-Verzahnungsgesetzes und Invarianz des Evolventenprofils
---

## 1. Definition der konjugierten Profile

Um zwischen zwei rotierenden Wellen ein streng konstantes Übersetzungsverhältnis ($u = \omega_1 / \omega_2$) zu übertragen, müssen die Zahnflanken das **Verzahnungsgesetz** erfüllen.

Berühren sich zwei Profile $\Sigma_1$ und $\Sigma_2$ im Punkt $K$, so muss die gemeinsame Flankennormale $\vec{n}$ stets durch den festen Wälzpunkt $P$ auf der Zentrale $O_1 O_2$ gehen:

$$
\frac{\omega_1}{\omega_2} = \frac{O_2 P}{O_1 P} = \text{konstant} = u
$$

Dies ist das grundlegende **Verzahnungsgesetz nach Willis**.

---

## 2. Differentialgeometrische Herleitung

Die Relativgeschwindigkeit $\vec{v}^{(12)}$ im Eingriffspunkt $K$ ist gegeben durch:

$$
\vec{v}^{(12)} = (\vec{\omega}_1 \times \vec{r}_1) - (\vec{\omega}_2 \times \vec{r}_2)
$$

Die kinematische Kontaktbedingung erfordert, dass die Normalkomponente der Relativgeschwindigkeit verschwindet:

$$
\vec{v}^{(12)} \cdot \vec{n} = 0
$$

Hieraus folgt unmittelbar die Stationarität des Wälzpunktes $P$ und die Erhaltung des Winkelgeschwindigkeitsverhältnisses.

---

## 3. Mathematische Einzigartigkeit der Kreisevolvente

Die Kreisevolvente eines Grundkreises mit Radius $r_b$ gehorcht der Parameterdarstellung:

$$
\begin{cases}
x(\theta) = r_b (\cos\theta + \theta \sin\theta) \\
y(\theta) = r_b (\sin\theta - \theta \cos\theta)
\end{cases}
$$

Der entscheidende Vorteil der Evolventenverzahnung liegt in ihrer **Achsabstandsunempfindlichkeit**: Ändert sich der Achsabstand $a$ auf $a'$, so stellt sich der Betriebseingriffswinkel $\alpha_{wt}$ automatisch ein, ohne das Übersetzungsverhältnis $u$ zu verfälschen:

$$
a' \cos\alpha_{wt} = a \cos\alpha_t = r_{b1} + r_{b2}
$$
