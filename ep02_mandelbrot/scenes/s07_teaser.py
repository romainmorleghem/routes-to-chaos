"""Seq 7 — Teaser for Part 3: continuous time, three dimensions, the Lorenz attractor."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, ORBIT, ACCENT, DIAG
from common.narrative import Narrated


def lorenz(n=12000, dt=0.004, s=10.0, r=28.0, b=8 / 3):
    x = np.array([1.0, 1.0, 1.0])
    out = np.empty((n, 3))
    f = lambda v: np.array([s * (v[1] - v[0]), v[0] * (r - v[2]) - v[1], v[0] * v[1] - b * v[2]])
    for i in range(n):
        k1 = f(x); k2 = f(x + dt / 2 * k1); k3 = f(x + dt / 2 * k2); k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[i] = x
    return out


class Teaser(Narrated):
    def construct(self):
        self.chapter(r"6 \,$\cdot$\, Julia sets: one world per point", animate=False)
        self.chapter(r"Epilogue \,$\cdot$\, When time flows")
        self.say(r"Parts 1 and 2: one variable, and time that jumps, step after step.")
        P = lorenz()[1000:]
        pts = [np.array([0.17 * x, 0.15 * (z - 25), 0]) + np.array([0, 0.2, 0]) for x, _, z in P]
        path = VMobject(stroke_width=1.6).set_points_smoothly(pts[::3])
        path.set_stroke(color=[DIAG, ACCENT, ORBIT, MAP])
        eqs = MathTex(r"\dot x = \sigma(y - x)", r"\quad \dot y = x(\rho - z) - y", r"\quad \dot z = xy - \beta z",
                      font_size=32, color=FG).to_edge(UP, buff=0.7)
        self.say(r"What if time flows \emph{continuously}, in three dimensions — like the weather? "
                 r"Three innocent equations (Lorenz, 1963)\ldots", anims=[Write(eqs)])
        self.say(r"\ldots and a trajectory that never repeats, never escapes, never settles: "
                 r"a \emph{strange attractor}.", anims=[Create(path)], run_time=9, wait=1.0)
        self.unsay()
        nxt = Tex(r"Next \,$\cdot$\, Part 3", font_size=40, color=MUTED)
        ttl = Tex(r"Strange Attractors: Chaos Without Energy Conservation", font_size=50, color=FG
                  ).next_to(nxt, DOWN, buff=0.3)
        g = VGroup(nxt, ttl).move_to([0, -2.6, 0])
        bgr = BackgroundRectangle(g, fill_opacity=0.85, buff=0.2)
        self.play(FadeIn(bgr), FadeIn(nxt), FadeIn(ttl, shift=0.2 * UP), FadeOut(self.chapter_tag))
        self.wait(3)
        self.play(FadeOut(Group(bgr, nxt, ttl, path, eqs)))
