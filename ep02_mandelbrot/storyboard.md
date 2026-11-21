# Episode 2 — The Mandelbrot Set is a Map of Chaos

Same rules as Ep 1: no voice-over, reading-paced captions (`common/narrative.py`), chapter tag top-left,
palette and LaTeX template from `common/style.py`, every scene starts on the previous scene's last frame,
`render.py` concatenates. Every number on screen comes from `compute/` (see `data/bulbs.json`).
Target 14–16 min.

## The thread with Ep 1 (say it explicitly on screen)
Ep 1 ended on: *"The real line was only a slice. What happens off it?"* over the bifurcation diagram
aligned on the Mandelbrot set. Ep 2 **opens on that exact frame** and keeps returning to Ep 1's ideas:

| Ep 1 idea | Its Ep 2 echo |
|---|---|
| stability: \|f′(x*)\| < 1 (ch. 2) | main cardioid = all c with \|f′(z*)\| = \|2z*\| < 1 → its equation drops out (ch. 3) |
| period doubling 1→2→4… (ch. 3) | chain of bulbs on the real axis, sizes shrinking by **the same δ** (ch. 5) |
| the critical point x = ½ (superstable Rₙ, ch. 6) | why M uses the orbit of **0** = the critical point of z²+c (ch. 6) |
| period-3 window = mini copy (ch. 4) | mini-Mandelbrot at c = −1.7549 (ch. 5) |
| cobweb = picture of an orbit | orbit drawn as a path in the plane (ch. 2) |

## Sequences

**0 · Cold open (~0:45)** — Ep 1's last frame (c-diagram over M). The diagram fades, the camera dives
along the boundary (seahorse valley → a mini-brot). Text: *"Last time, one line. Today, the whole plane."*
Title card *Part 2 · The Mandelbrot Set is a Map of Chaos*.

**1 · Squaring in the plane (~1:45)** — A complex number as a point/arrow. z² squares the length and
**doubles the angle** (animate an arrow, then a whole polar grid warped by z ↦ z²). +c is a shift.
So z ↦ z² + c = "stretch-and-turn, then shift". Unit circle is invariant under z², inside shrinks to 0,
outside flies away.

**2 · Orbits and the definition of M (~2:30)** — Pick c, start from 0, draw the orbit as a path:
spiral into a point / jump between 2 points / escape. Escape lemma on screen (if \|z\| > 2 the orbit
leaves; 3-line argument). Definition **M = { c : the orbit of 0 stays bounded }**. Build the picture:
sweep c over the plane, colour by escape time (same colormap as Ep 1). Mention: M is connected
(Douady–Hubbard 1982), boundary of dimension 2 (Shishikura 1998), area ≈ 1.5066 (not known exactly).

**3 · The cardioid is Ep 1's stability criterion (~2:00)** — Fixed point z* = z*² + c, multiplier
f′(z*) = 2z*. Stable ⇔ \|2z*\| < 1 (*"exactly the test of Ep 1, chapter 2"*). Boundary: 2z* = e^{iθ} ⇒
c = e^{iθ}/2 − e^{2iθ}/4: trace it as θ turns → the cardioid appears on top of M. At θ = π: c = −¾ = r₁.
Same for the 2-cycle: multiplier 4(c+1) ⇒ disk \|c + 1\| < ¼.

**4 · Bulbs, rotations, Farey & Fibonacci (~3:00)** — Colour the interior by the **period** of the
attracting cycle (a "period map"). The bulb attached at angle θ = 2πp/q has period q, and its cycle
**rotates by p/q of a turn** around the fixed point (show orbits: triangle for 1/3, pentagram for 2/5).
Read the period by counting the **spokes of the antenna**. Size ≈ sin(πp/q)/q² (verified: q²·size =
0.858 for 1/3, 0.706 for 1/4, 0.961 for 2/5). **Farey rule**: between the p/q and p′/q′ bulbs the largest
is the mediant (p+p′)/(q+q′) — verified for 4 pairs. Following 1/2, 1/3, 2/5, 3/8, 5/13 gives the
Fibonacci periods 2, 3, 5, 8, 13 and the angles converge to the golden ratio.

**5 · Back on the real axis (~2:00)** — Zoom on the real axis: the period-2 bulb, then 4, 8…:
**Ep 1's cascade is a chain of bulbs**. Centres −1, −1.3107, −1.3815…; ratio of gaps → 4.6692
(computed: 4.66855, 4.66906, 4.66917, 4.66920). Past c∞ = −1.40116 the real axis is the chaotic part;
at c = −1.75488 the period-3 window = a **mini-Mandelbrot** with its own cascade (dive into it).

**6 · Julia sets: the map (~3:00)** — For a fixed c, colour each **starting point** z₀ by escape →
filled Julia set K_c. Split screen: M on the left with a moving cursor c, K_c on the right morphing live
(cardioid: a blob; 2-bulb: "basilica"; 1/3-bulb: "rabbit"; c = i: dendrite; c outside M: dust).
Theorem (Fatou–Julia): K_c is connected ⇔ the orbit of the **critical point 0** stays bounded ⇔ c ∈ M.
That is why M is defined with z₀ = 0 (*"like x = ½ in Ep 1"*). Climax (Tan Lei 1990): at c = i
(0 → i → −1+i → −i → −1+i…, pre-periodic), zoom on M near i and on K_i near i side by side: they look
alike. **M is a catalogue of all the Julia sets: a map of every possible dynamics.**

**7 · Teaser Ep 3 (~0:40)** — Everything so far: one variable, discrete steps. What if time flows
continuously in 3 dimensions — the weather? A Lorenz trajectory draws itself. *Next · Part 3 · Strange
Attractors.*

## Technical plan
- `common/fractals.py`: escape-time + smooth colouring, interior period detection, Julia sets. Move Ep 1
  s07's Mandelbrot colouring there so Ep 2 s00 starts on an identical frame.
- Speed: zooms at 4K need ~10⁹ iterations per frame → **numba** (`@njit(parallel=True)`), numpy fallback.
  Keep zooms above 10⁻¹² (double precision); no perturbation theory needed.
- Interior colour: Ep 1 used cream for M. Keep cream in s00 for the seam, then switch progressively to
  the "period map" colouring in ch. 4.
- Web page `web/ep2/`: WebGL shader explorer (float32 → zoom limited to ~10⁻⁵, enough for teaching),
  click c → live Julia set + orbit of 0 drawn as a path; toggle period colouring; real-axis cascade view.

## To verify before publishing
- Dates/attributions: Douady–Hubbard 1982 (connectedness), Shishikura 1998 (dimension 2), Tan Lei 1990
  (similarity at Misiurewicz points), Devaney's Farey/Fibonacci article (Amer. Math. Monthly, 1999).
- Area value 1.5066 (estimate, not exact).

## Status (preview rendered, 12 min 51 s)
All 8 sequences exist (`scenes/s00…s07`), joins checked frame by frame, `render.py` assembles.
Original elements kept from the plan and added while building:
- two-panel device (parameter plane | dynamical plane) on screen from Seq 2 to Seq 6;
- cardioid traced live while z* runs on |z| = ½ (Seq 3);
- 5-spoke antenna zoom located offline (`tgt = centre + 0.06·u`, width 0.2);
- "dragon" c = −0.8 + 0.156i: iterations raised live, the cream evaporates into dust (Seq 6);
- Julia mosaic converging to M (Seq 6), Tan Lei side-by-side zoom at c = i (Seq 6);
- cold open dives to the period-39 mini-brot −0.74364230 + 0.13182652i (Newton).
Web page `web/ep2/`: WebGL M ↔ Julia explorer, gallery, bulb finder, Farey & δ tables, mosaic mode.
