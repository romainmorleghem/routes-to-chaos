# Routes to Chaos

A four-part video series (YouTube, no voice-over, captions only) and an interactive companion website on
**how simple deterministic rules become unpredictable, and why that unpredictability still has laws**.

Website: <https://romainmorleghem.github.io/routes-to-chaos/> (each episode: the video + interactive widgets).

| Ep | Title | Length | Video | Web page |
|----|-------|--------|-------|----------|
| 1 | One Equation, Infinite Chaos: the Logistic Map & Feigenbaum's Constant | 13 min | `web/ep1/ep01_1080p.mp4` | [ep1](https://romainmorleghem.github.io/routes-to-chaos/ep1/) |
| 2 | The Mandelbrot Set is a Map of Chaos | 12 min 51 s | `web/ep2/ep02_1080p.mp4` | [ep2](https://romainmorleghem.github.io/routes-to-chaos/ep2/) |
| 3 | Strange Attractors: Chaos Without Energy Conservation | 11 min 38 s | `web/ep3/ep03_1080p.mp4` | [ep3](https://romainmorleghem.github.io/routes-to-chaos/ep3/) |
| 4 | The Kicked Rotor: Order, Chaos, and a Quantum Brake | 11 min 43 s | `web/ep4/ep04_1080p.mp4` | [ep4](https://romainmorleghem.github.io/routes-to-chaos/ep4/) |

---

## The four episodes in a nutshell

### 1 · The logistic map: period doubling and universality
`x → r x (1 − x)`, a one-line model of a population. As `r` grows, the long-term behaviour goes from a
fixed value to a cycle of 2, then 4, 8, 16… (**period doubling**), then chaos at `r∞ = 3.5699…`.
The distances between successive doublings shrink by a fixed factor **δ = 4.6692…** (Feigenbaum).
The surprise: the *same* δ appears for any map with a single smooth hump (sine map, Ricker…) and in real
experiments (fluids, circuits). Reason: zooming on the cascade and renormalizing gives the same picture
every time, a fixed point of a "zoom" operator. **Lesson: chaos has universal numbers.**

### 2 · The Mandelbrot set: a map of all the logistic maps
Replace the population `x` by a complex number `z` and iterate `z → z² + c`. The Mandelbrot set is the set
of `c` for which the orbit of 0 stays bounded. Read as a catalogue of dynamics:
- the main **cardioid** = parameters with a stable fixed point (a stability test, `|2z| < 1`);
- each **bulb** = a stable cycle, labelled by a fraction `P/q` (how the cycle rotates);
  bulbs follow the Farey order (between 1/3 and 1/2 the largest is 2/5);
- the **real axis** is exactly Part 1's cascade seen from above, with the same δ;
- each point `c` has its own **Julia set**: connected if `c` is in the Mandelbrot set, dust otherwise.

**Lesson: the fractal boundary is where the dynamics changes character.**

### 3 · Lorenz: strange attractors
Three equations for a convection roll (equivalently, a leaky water wheel). With friction, every blob of
initial states shrinks in volume (`div F = −13.67`), yet motion never settles: it lives on a
**strange attractor** of dimension 2.06 (Kaplan–Yorke). Measured in the episode:
- the **butterfly effect**, λ₁ = 0.907 (errors double every 0.76 time units, so each factor 10 of
  precision buys only 2.5 time units of forecast);
- *stretching and folding* of a drop of ink;
- the **Lorenz map** (successive maxima of z) is a one-hump map, so Part 1 hides inside the flow:
  near ρ ≈ 99.5 a period-doubling cascade with δ_k = 4.31, 4.59, 4.65 → 4.669, computed precisely
  (Floquet multipliers, two time steps);
- the attractor's skeleton: unstable periodic orbits.

**Lesson: dissipation + stretching + folding = strange attractor.**

### 4 · The kicked rotor: chaos without friction, then quantum
A rod kicked once per second gives the **standard map** `p' = p + K sin θ, θ' = θ + p'`. It preserves
areas, so there is no attractor and order and chaos coexist:
- **KAM curves** (unbroken walls) and **island chains** at rational speeds `P/q` (same fractions as
  Part 2's bulbs);
- the last wall is the **golden** curve; it breaks at **K_c = 0.971635** (Greene's residue criterion,
  recomputed up to orbits of period 987);
- above it, the speed performs a **random walk**: ⟨Δp²⟩ = D n with D ≈ K²/2 (Rechester–White
  corrections, accelerator modes);
- period doubling also exists without friction, but with another universal constant:
  **δ = 8.7210** (computed: 8.302, 8.659, 8.716, 8.7203, 8.72103);
- **quantum** rotor: the spread of momentum grows, then *stops* (**dynamical localization**), with an
  exponential profile of width λ ≈ D/ħ². Reason: an exact mapping to an electron in a disordered crystal
  (Anderson localization), observed with cold atoms (Raizen 1995). At ħ = 4π, a resonance instead gives
  ballistic growth ⟨m²⟩ = k²n²/2.

**Lesson: without friction chaos has other laws, and quantum interference can freeze it.**

### The common thread
| | Part 1 | Part 2 | Part 3 | Part 4 |
|---|---|---|---|---|
| system | 1-D map | complex map | 3-D flow, friction | 2-D map, no friction |
| route | period doubling | boundary of stability | stretch & fold | KAM breakdown |
| universal number | δ = 4.6692 | same δ on the real axis | δ again, λ₁ = 0.907 | K_c = 0.9716, δ = 8.7210 |

Every number in the videos is computed from scratch in `epXX_*/compute/` and checked for convergence.

---

## Repository layout
```
common/              shared style (palette, LaTeX), narration helper, numerics
                     (logistic.py, fractals.py, lorenz.py, kicked.py)
epXX_*/compute/      heavy computations -> epXX_*/data/*.json (committed)
epXX_*/scenes/       Manim Community scenes, one file per sequence (sNN_*.py)
epXX_*/render.py     renders all sequences and concatenates them
epXX_*/storyboard.md plan of the episode (episodes 1–3)
web/                 static website: index + one page per episode (canvas + ES modules, KaTeX)
web/data/epN.json    small data exported for the pages
media/               render outputs (not published)
```

Key computations:
| Episode | Script | What |
|---|---|---|
| 1 | `ep01_logistic/compute/feigenbaum.py`, `universality.py` | superstable parameters, δ, α, renormalization |
| 2 | `ep02_mandelbrot/compute/bulbs.py` | bulb centres, periods and P/q labels |
| 3 | `ep03_lorenz/compute/facts.py`, `doubling_floquet.py`, `upo.py`, `bifurcation.py` | Lyapunov spectrum, Lorenz map, precise doublings (Floquet), periodic orbits |
| 4 | `ep04_kicked_rotor/compute/greene.py`, `doubling.py`, `facts.py` | Greene residues → K_c, area-preserving cascade → δ, diffusion, quantum rotor (FFT) |

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # Manim needs LaTeX + pango/cairo system libraries
```

## Render an episode
```bash
cd ep04_kicked_rotor
python compute/greene.py && python compute/doubling.py && python compute/facts.py   # regenerate data
python compute/export_web.py      # data for the web page
python render.py                  # 480p preview -> media/ep04/ep04_480p15.mp4
python render.py -q f             # 1080p30      -> media/ep04/ep04_1080p30.mp4
python render.py -q f --only s03  # re-render one sequence and re-assemble
```
Episodes 1–2 write to `media/`, episodes 3–4 to `media/ep03`, `media/ep04` (scene file names repeat).
Videos published on the site must stay under ~95 MB (GitHub's 100 MB file limit).

## Website
Static, no build step. Modules need HTTP, not `file://`:
```bash
cd web && python -m http.server 8000     # open http://localhost:8000
```
GitHub Pages: `.github/workflows/pages.yml` deploys `web/` on every push to `main`.
