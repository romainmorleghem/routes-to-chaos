"""Seq 8 — Epilogue: the four routes, the lessons, end card."""
from _common import *  # noqa
import numpy as np
from numba import njit
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.fractals import mandelbrot, colorize
from _stages import raster_points, lorenz_points
from _viz import portrait

W, H = 4.9, 2.35


@njit(cache=True)
def logistic_cloud(r0, r1, nr, n_keep):
    xs = np.empty(nr * n_keep); ys = np.empty(nr * n_keep)
    for i in range(nr):
        r = r0 + (r1 - r0) * i / (nr - 1)
        x = 0.5
        for _ in range(500):
            x = r * x * (1 - x)
        for j in range(n_keep):
            x = r * x * (1 - x)
            xs[i * n_keep + j] = r; ys[i * n_keep + j] = x
    return xs, ys


class Finale(Narrated):
    def construct(self):
        self.chapter(r"Epilogue \,$\cdot$\, Four routes")
        pos = [np.array([-3.4, 1.85, 0]), np.array([3.4, 1.85, 0]), np.array([-3.4, -0.9, 0]),
               np.array([3.4, -0.9, 0])]
        xs, ys = logistic_cloud(2.8, 4.0, 1400, 300)
        t1 = raster_points(xs, ys, (2.8, 4.0), (0, 1), W, H, color_hex="#F2A541", gain=1.5)
        esc = mandelbrot(-2.3, 0.8, -0.74, 0.74, 900, 430, 250)
        t2 = ImageMobject(colorize(esc, 250, "ep1")).stretch_to_fit_width(W).stretch_to_fit_height(H)
        P = lorenz_points(T=300, dt=0.004, skip=5)
        t3 = raster_points(P[:, 0], P[:, 2], (-22, 22), (0, 52), W, H, color_hex="#E85D75", gain=1.4)
        t4 = portrait(0.971635, W, H, n=900)
        tiles = [t1, t2, t3, t4]
        labs = [r"1 \,$\cdot$\, Period doubling \quad $\delta = 4.6692$",
                r"2 \,$\cdot$\, Fractal boundaries \quad bulbs $P/q$",
                r"3 \,$\cdot$\, Strange attractors \quad $\lambda_1 = %.3f$" %
                json.loads((ROOT / "ep03_lorenz" / "data" / "facts.json").read_text())["lyapunov"][0],
                r"4 \,$\cdot$\, Conservative chaos \quad $\delta = 8.7210$"]
        grp = Group()
        for t, p, l in zip(tiles, pos, labs):
            t.move_to(p)
            box = SurroundingRectangle(t, color=MUTED, stroke_width=1.2, buff=0.02)
            lab = Tex(l, font_size=26, color=FG).next_to(t, DOWN, buff=0.1)
            grp.add(Group(t, box, lab))
        self.say(r"Four episodes, four routes to chaos.", anims=[FadeIn(grp[0])])
        for g in grp[1:]:
            self.play(FadeIn(g), run_time=0.8)
        self.say(r"A one-line map doubling its period at a universal rhythm. A boundary with infinite detail. "
                 r"A flow that forgets its past at a measurable rate. A kicked rod whose chaos follows its own "
                 r"laws, until quantum interference stops it.")
        self.say(r"Each time, the same lessons: simple deterministic rules can be unpredictable; unpredictable "
                 r"does not mean structureless; and the structure carries numbers that do not depend on the details.")
        self.say(r"Every number in this series was computed for it, and every picture can be explored "
                 r"on the companion website.")
        self.unsay()
        ttl = Tex(r"Routes to Chaos", font_size=72, color=FG)
        th = Tex(r"Thanks for watching", font_size=36, color=MUTED).next_to(ttl, DOWN, buff=0.35)
        url = Tex(r"romainmorleghem.github.io/routes-to-chaos", font_size=30, color=ACCENT).next_to(th, DOWN,
                                                                                                   buff=0.3)
        self.play(FadeOut(grp), FadeOut(self.chapter_tag), run_time=1.2)
        self.play(FadeIn(ttl, shift=0.2 * UP), FadeIn(th), FadeIn(url), run_time=1.5)
        self.wait(5)
        self.play(FadeOut(VGroup(ttl, th, url)), run_time=1.5)
        self.wait(0.5)
