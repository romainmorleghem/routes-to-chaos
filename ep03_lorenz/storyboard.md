# Part 3 — Strange Attractors (Lorenz)

Same style as Parts 1–2: Manim CE 0.22.1, `common/style.py` palette, LaTeX, captions via `Narrated.say()`,
each scene starts on the previous scene's last frame (`scenes/_stages.py`), no voice-over.
Opens on the last frame of Part 2 (Lorenz equations on black, "Epilogue · When time flows").

## The original angle (the subject is heavily covered on YouTube)
**Validated by the user:** this angle, the water wheel in s01, target length ≈ 12 min.
Do NOT do the usual "butterfly + pretty spinning attractor". Thread: **the Lorenz system secretly
contains Part 1.** Lorenz's own 1963 trick — plot successive maxima z_n → z_{n+1} — gives a 1-D
tent-like map; we cobweb it exactly as in Part 1. Then: chaos is *stretching + folding* (the same
mechanism as x ↦ rx(1−x)), made visible with ink clouds of 10^5 initial conditions.

## Sequences
- s00 Cold open — the equations from Part 2 come alive: one point, then the trajectory traced;
  camera orbits once. Title card "Part 3 · Strange Attractors".
- s01 What the equations mean — Malkus water wheel (convection loop): x = wheel speed, y, z = mass
  distribution. Physical picture before the maths. Divergence = −(σ+1+β) ≈ −13.67: every volume
  shrinks by e^{-13.67} per unit time → attractor has zero volume.
- s02 Journey in ρ (σ=10, β=8/3) — fixed points: origin; C± at ρ=1 (pitchfork, cf. Part 1 r=1);
  ρ≈13.93 homoclinic explosion (transient chaos, show a long chaotic transient that dies);
  ρ_H = σ(σ+β+3)/(σ−β−1) ≈ 24.74 subcritical Hopf; ρ = 28 the attractor. Eigenvalues computed live.
- s03 Sensitivity, quantified — two trajectories 1e-10 apart; log|δ| vs t is a straight line,
  slope λ₁ ≈ 0.906 (computed). Prediction horizon T ≈ (1/λ) ln(tol/δ₀): 10× better measurement buys
  only ≈2.5 time units. Lyapunov spectrum (0.906, 0, −14.57), sum = −13.67 = divergence (check).
- s04 Stretch and fold — ink cloud (10^5 points in a tiny ball) smeared into a sheet, folded
  onto itself; the attractor as a "book of infinitely many pages". Kaplan–Yorke dimension
  2 + 0.906/14.57 ≈ 2.06.
- s05 Part 1 inside Lorenz — Lorenz map z_{n+1} = F(z_n) from the maxima; cobweb it in Part 1's
  style; |F'| > 1 everywhere ⇒ no stable cycle ⇒ chaos. Then the high-ρ window (ρ ≈ 99.5 → 100.8):
  period doubling in the flow, bifurcation diagram of maxima vs ρ, δ ≈ 4.67 measured again
  (verify numerically; if too costly, use Rössler a=b=0.2, c: 2.83→4.2 cascade). Universality pays off.
- s06 Beyond the butterfly — gallery (Rössler, Thomas, Aizawa, Halvorsen, Chen) with what each
  teaches; unstable periodic orbits embedded in the attractor (skeleton: LR, LLR, ... labelled by
  symbolic sequences — the "periodic orbits as skeleton" idea, original on YT).
- s07 Teaser Part 4 — "Lorenz loses volume. What if volume is conserved (Hamiltonian)?"
  → standard map / kicked rotor card.

## Website (web/ep3)
- WebGL 3-D attractor, drag to rotate, sliders σ, ρ, β, dt; presets (ρ=13, 20, 24.5, 28, 99.65, 160).
- "Butterfly duel": two (or N) trajectories with adjustable separation 10^-k; live log|δ|(t) plot,
  fitted slope = λ₁, prediction-horizon readout.
- Ink cloud: 50k particles in a ball, watch stretching/folding.
- Lorenz-map panel: maxima z_n → z_{n+1}, live cobweb (reuse plot.js Plot).
- Bifurcation diagram of z-maxima vs ρ (precomputed JSON) with click → attractor at that ρ.
- Gallery of other attractors.

## Numerics to compute (compute/)
- lyapunov.py: spectrum at ρ=28 (QR method), Kaplan–Yorke dim.
- lorenz_map.py: maxima map data.
- bifurcation.py: z-max vs ρ diagram, period-doubling ρ_k in the high-ρ window, δ estimate.
- upo.py: a few unstable periodic orbits (Newton on Poincaré return map).

## References to verify
Lorenz 1963 (J. Atmos. Sci. 20:130); Sparrow 1982 (The Lorenz Equations); Tucker 1999/2002
(rigorous proof of the attractor); Malkus water wheel; Viswanath 2003 (Lyapunov exponents, UPOs).
