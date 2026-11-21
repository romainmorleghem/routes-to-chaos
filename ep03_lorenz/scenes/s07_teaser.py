"""Seq 7 — Teaser for Part 4: what if volume is conserved? The standard map."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, ACCENT, DIAG
from common.narrative import Narrated
from _stages import raster_points

K = 0.971635


def standard_map(n_orb=180, n_it=1500):
    rng = np.random.default_rng(1)
    xs, ys = [], []
    for _ in range(n_orb):
        th, p = rng.random() * 2 * np.pi, rng.random() * 2 * np.pi
        for _ in range(n_it):
            p = (p + K * np.sin(th)) % (2 * np.pi)
            th = (th + p) % (2 * np.pi)
            xs.append(th); ys.append(p)
    return np.array(xs), np.array(ys)


class TeaserLorenz(Narrated):
    def construct(self):
        self.chapter(r"Epilogue \,$\cdot$\, Keeping every volume")
        div = MathTex(r"\nabla\!\cdot\!\mathbf F = -13.67 \ \Rightarrow\ \text{attractor}", font_size=40,
                      color=FG).move_to([0, 1.8, 0])
        self.say(r"Everything in this episode relied on friction: volumes shrink, so motion collapses onto an "
                 r"attractor.", anims=[FadeIn(div)])
        div2 = MathTex(r"\nabla\!\cdot\!\mathbf F = 0 \ \Rightarrow\ \text{no attractor at all}", font_size=40,
                       color=ACCENT).next_to(div, DOWN, buff=0.4)
        self.say(r"But planets, molecules and electrons in a magnetic field lose no energy: their phase-space "
                 r"volume is \emph{conserved} (Liouville). Nothing can attract.", anims=[Write(div2)], run_time=1.5)
        self.play(FadeOut(div), FadeOut(div2))
        xs, ys = standard_map()
        w, h = 5.4, 5.4
        im = raster_points(xs, ys, (0, 2 * np.pi), (0, 2 * np.pi), w, h, color_hex="#F2A541", gain=1.2)
        im.move_to([0, 0.4, 0])
        eq = MathTex(r"p' = p + K\sin\theta,\qquad \theta' = \theta + p'", font_size=34, color=FG
                     ).next_to(im, UP, buff=0.25)
        self.say(r"Can chaos survive without dissipation? A pendulum kicked periodically, "
                 r"the \emph{standard map}:", anims=[FadeIn(eq), FadeIn(im)], run_time=3)
        self.say(r"Order and chaos side by side, islands inside a chaotic sea, forever. And in its quantum "
                 r"version, chaos itself seems to be suppressed\ldots")
        self.unsay()
        nxt = Tex(r"Next \,$\cdot$\, Part 4", font_size=40, color=MUTED)
        ttl = Tex(r"The Standard Map \& the Quantum Kicked Rotor", font_size=50, color=FG
                  ).next_to(nxt, DOWN, buff=0.3)
        g = VGroup(nxt, ttl).move_to([0, -2.6, 0])
        bgr = BackgroundRectangle(g, fill_opacity=0.85, buff=0.2)
        self.play(FadeOut(im), FadeOut(eq), run_time=0.8)
        self.play(FadeIn(bgr), FadeIn(nxt), FadeIn(ttl, shift=0.2 * UP), FadeOut(self.chapter_tag))
        self.wait(3)
        self.play(FadeOut(Group(bgr, nxt, ttl)))
