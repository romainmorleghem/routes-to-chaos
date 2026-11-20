# Episode 1 — The Logistic Map & Feigenbaum's Universal Constant

No voice-over: on-screen text is short, equations carry the argument, music sets the pace.
Target 10–14 min. Audience: comfortable with derivatives, fixed points, a bit of analysis.

Legend: ✅ scene exists (preview) · 🔧 to build · ✏️ to rework

## Seq 0 — Cold open (~0:40) ✅ `s00_cold_open.py::BifurcationZoom`
- Full bifurcation diagram, r ∈ [2.8, 4].
- Continuous zoom toward (r∞, ½): r shrinks by δ, x by |α| per level, 3 levels.
  The picture repeats itself (flipped at each level since α < 0).
- Text: *This picture hides a number that appears everywhere.* → **δ = 4.669 201 609…**
- Title card: *Routes to Chaos — Part 1*. 🔧

## Seq 1 — The map (~1:30) ✅ `s01_cobweb.py::Cobweb`
- x_{n+1} = r x_n (1 − x_n). One line of context: discrete population model (May, 1976). 🔧
- Cobweb on the left, time series on the right, r slider.
- r = 2.6 → fixed point. ✏️ add the fixed point x* = 1 − 1/r as a dot.

## Seq 2 — Stability & the first doubling (~2:00) 🔧
- Linearise: x* stable iff |f′(x*)| = |2 − r| < 1 → loses stability at r = 3 (f′ = −1).
- Show f∘f: its two new fixed points = the 2-cycle. Zoom on f∘f near x*: it looks like
  a small upside-down copy of f — **plant the seed of renormalisation here**.
- 2-cycle loses stability at r₂ = 1 + √6.

## Seq 3 — The cascade (~1:30) ✅ `s03_cascade.py::Cascade`
- Bifurcation diagram builds up as r sweeps 2.8 → 3.57. 🔧
- Table: r_n and ratios (computed to 16 digits, `compute/feigenbaum.py`).
- δ = lim (r_n − r_{n−1}) / (r_{n+1} − r_n) = 4.669 201 609 102 990…
- r∞ = 3.569 945 671 87… (geometric accumulation).

## Seq 4 — Chaos (~2:00) 🔧
- Beyond r∞: Lyapunov exponent λ(r) plotted under the diagram (λ > 0 ⇔ chaos).
- Two orbits from x₀ and x₀ + 10⁻¹⁰ diverge (exponential growth, slope λ).
- Period-3 window at r = 1 + √8: tangent bifurcation of f³, intermittency just before.
  Text: *Period three implies chaos* (Li & Yorke, 1975). Sharkovskii ordering as a bonus card.
- ✏️ Cobweb at r ≈ 3.83 currently shows the transient: discard first iterates.

## Seq 5 — Universality (~1:30) 🔧
- Same cascade for r sin(πx), r x(1−x²)… compute δ for each: same 4.6692.
- Real experiments: Libchaber & Maurer (Rayleigh–Bénard convection, 1980), dripping faucet,
  nonlinear electronic circuits. Show measured δ values vs 4.669.
- Condition: smooth unimodal map with a quadratic maximum (quartic max → other δ).

## Seq 6 — Why: renormalisation (~3:00) ✅ v1 `s06_renormalization.py::Renormalization`
- f^{2ⁿ}_{R_n} near x = ½, rescaled by αⁿ → converges to universal g.
- Feigenbaum–Cvitanović: g(x) = α g(g(x/α)), α = −2.502 907 875…
- δ = the unstable eigenvalue of the doubling operator T[f] = α f∘f(x/α) at its fixed point g.
- ✏️ v2: show the box-zoom explicitly (square around ½ on the graph of f², expanded &
  flipped, laid onto f) before the curve-convergence plot. Then a cartoon of function space:
  fixed point g, its stable manifold, the one unstable direction with eigenvalue δ.

## Seq 7 — Teaser for Ep 2 (~0:40) 🔧
- *What if x were complex?* Change of variable z = r(½ − x) turns the map into z ↦ z² + c,
  c = r/2 − r²/4. The real axis of the Mandelbrot set lines up with the bifurcation diagram.

## Data
`compute/feigenbaum.py` (mpmath, 60 digits) → `data/cascade.json`:
superstable R_n (n ≤ 13), bifurcation points r_n (n ≤ 12), δ and α estimates, rescaled curves.
