# Episode 1 — The Logistic Map & Feigenbaum's Universal Constant

No voice-over: captions (bottom, paced at ~3 words/s, `common/narrative.py`) carry the explanation;
chapter tag top-left. Each scene **starts on the exact last frame of the previous one** (shared layouts in
`scenes/_stages.py`), so `render.py` simply concatenates them. Current preview: **13 min 27 s**.

Narrative thread (each chapter answers the question the previous one ends on):

| Seq | File / scene | Question opened → answered | Key visual | Ends on |
|---|---|---|---|---|
| 0 | `s00_cold_open` BifurcationZoom | "a number that appears everywhere" | self-similar zoom (δ in r, α in x) | title card → black |
| 1 | `s01_map` TheMap | what is the rule? how to iterate it? | equation built term by term, cobweb explained step by step, fixed point x* = 1 − 1/r | cobweb stage r = 2.6 — *"turn up r…"* |
| 2 | `s02_stability` Stability | why does it converge? why does it stop? | linearisation, slope 2 − r on a number line, f∘f and the 2-cycle, **box = upside-down copy (seed of Seq 6)** | cobweb stage r = 3.5 — *"where does this end?"* |
| 3 | `s03_cascade` Cascade | where does doubling end? | time series → column of points → sweep builds the bifurcation diagram; gaps Δₙ; 60-digit table → δ; geometric sum → r∞ | diagram + r∞ — *"beyond r∞?"* |
| 4 | `s04_chaos` Chaos | is it random? | two orbits 10⁻⁸ apart, log-gap line, **λ = mean ln\|f′\| (link to Seq 2)**, λ(r) under the diagram, zoom in period-3 window → mini copy | *"why the same number again?"* → black |
| 5 | `s05_universality` Universality | is δ about the parabola? | logistic / sine / Ricker → same δ (6 digits); quartic top → 7.2847; lab experiments | *"why would a liquid know 4.669?"* → black |
| 6 | `s06_renormalization` Renormalization | why? | **box from Seq 2** rotated 180° and scaled by \|α\| matches f; f⁴, f⁸ → g; T[f] = α f(f(x/α)), T[g] = g (echo of x* in Seq 1); function-space cartoon: stretch δ along one direction; any family crossing the surface → universality | summary δ, α → black |
| 7 | `s07_teaser` Teaser | what's next? | z = r(½ − x) ⇒ z² + c; c-diagram aligned over the Mandelbrot set (forks ↔ bulb junctions, window ↔ mini-brot) | "Next · Part 2" card |

## Numbers used (all computed in `compute/`, nothing hard-coded from memory)
- `feigenbaum.py` (60 digits): r₁…r₁₂, R₀…R₁₃, δ → 4.6692016, α → −2.5029079, rescaled curves.
- `universality.py`: δ for logistic 4.669201, sine 4.669199, Ricker 4.669196, quartic 7.284698.

## To check before publishing
- ⚠️ Seq 5 lab card: "δ measured ≈ 4.3–4.8, compiled in Cvitanović, *Universality in Chaos* (1989)" —
  verify the range and the reference against the book (Libchaber & Maurer; Testa, Pérez & Jeffries; …).
- Seq 6 cartoon is schematic (stretch factor drawn as 2, labelled "not to scale").

## Ideas / open polish
- Seq 3: highlight the column of the current r while sweeping (link with the right-hand time series).
- Seq 4: show the exponential gap on the cobweb too (two webs).
- Music: calm, ~70 bpm; cut points at chapter tags.
