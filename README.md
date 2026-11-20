# Routes to Chaos

A video series (YouTube, no voice-over) and an interactive companion website on how
deterministic systems become chaotic.

| Ep | Title | Status |
|----|-------|--------|
| 1 | The Logistic Map & Feigenbaum's Universal Constant | full preview (13 min) + web page |
| 2 | The Mandelbrot Set is a Map of Chaos | storyboard + verified numbers |
| 3 | Strange Attractors: Chaos Without Energy Conservation | — |
| 4 | The Standard Map & the Quantum Kicked Rotor | — |

## Layout
```
common/          shared style (palette, LaTeX template) and numerics
epXX_*/compute/  heavy computations -> epXX_*/data/ (committed, small JSON)
epXX_*/scenes/   Manim Community scenes, one file per storyboard sequence
epXX_*/storyboard.md
web/             companion website (WebGL), one page per episode
```

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # needs LaTeX + pango/cairo system libs for Manim
```

## Render an episode
```bash
cd ep01_logistic
python compute/feigenbaum.py && python compute/universality.py   # regenerate data/*.json
python render.py              # all sequences at 480p + concatenation -> media/ep01_480p15.mp4
python render.py -q k         # 4K -> media/ep01_2160p60.mp4
python render.py --only s04   # re-render one sequence and re-assemble
```
Scenes that recompute the bifurcation diagram per frame (s00, s04 zoom) take a few minutes at 4K.

## Website
Static, no build step (ES modules + canvas, KaTeX from CDN). Modules need HTTP, not `file://`:
```bash
cd web && python -m http.server 8000     # open http://localhost:8000
```
Publish with GitHub Pages: the workflow `.github/workflows/pages.yml` deploys `web/` on every push to `main`
(one-time setup: Settings → Pages → Source = "GitHub Actions").
