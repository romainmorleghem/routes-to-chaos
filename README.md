# Routes to Chaos

A video series (YouTube, no voice-over) and an interactive companion website on how
deterministic systems become chaotic.

| Ep | Title | Status |
|----|-------|--------|
| 1 | The Logistic Map & Feigenbaum's Universal Constant | storyboard + first scenes |
| 2 | The Mandelbrot Set is a Map of Chaos | — |
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

## Render
```bash
cd ep01_logistic
python compute/feigenbaum.py                                   # regenerate data/cascade.json
manim -ql --media_dir ../media scenes/s01_cobweb.py Cobweb     # quick preview
manim -qk --media_dir ../media scenes/s01_cobweb.py Cobweb     # final 4K
```
`s00_cold_open.py` recomputes the bifurcation diagram every frame at the output
resolution: expect a few minutes per scene at 4K.
