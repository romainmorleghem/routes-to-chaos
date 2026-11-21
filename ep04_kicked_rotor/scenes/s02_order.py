"""Seq 2 — Order: K=0 lines, KAM curves, island chains P/q; the same fractions as Part 2's bulbs."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.fractals import mandelbrot, colorize
from _viz import portrait, Frame

FR = dict(width=4.8, height=4.8, center=(-3.1, 0.25, 0), fs=24)
CHAINS = [(1, 4), (1, 3), (2, 5), (1, 2)]
RE, IM, MW = (-2.0, 0.6), (-1.3, 1.3), 4.8
MC = np.array([3.4, 0.25, 0])


def m2s(c):
    return MC + np.array([(c.real - sum(RE) / 2) / (RE[1] - RE[0]) * MW, (c.imag - sum(IM) / 2) / (IM[1] - IM[0]) * MW, 0])


def bulb(p, q):
    f = 2 * np.pi * p / q
    att = np.exp(1j * f) / 2 - np.exp(2j * f) / 4
    d = 1j * (1j * np.exp(1j * f) / 2 - 1j * np.exp(2j * f) / 2)
    n = d / abs(d)
    if (np.conj(n) * (att + 0.25)).real < 0:
        n = -n
    r = np.sin(np.pi * p / q) / q ** 2
    return att + r * n, n, r


class Order(Narrated):
    def construct(self):
        self.chapter(r"2 \,$\cdot$\, Order: curves and islands")
        fr = Frame(**FR)
        ps = np.linspace(-np.pi, np.pi, 18, endpoint=False) + 0.09
        im0 = portrait(0.0, 4.8, 4.8, n=500, ics=(np.random.default_rng(0).random(18) * 6.28, ps)).move_to(fr.c)
        k0 = MathTex(r"K = 0", font_size=36, color=FG).next_to(fr, UP, buff=0.2).shift(1.2 * RIGHT)
        self.say(r"Without kicks ($K=0$) each rod keeps its speed: the orbit runs along a horizontal line, "
                 r"advancing by $p$ at each step.", anims=[FadeIn(fr), FadeIn(im0), FadeIn(k0)])
        self.say(r"If $p/2\pi$ is a fraction $P/q$, the rod is back after exactly $q$ kicks. If it is irrational, "
                 r"the orbit never closes and slowly fills its line.")
        im1 = portrait(0.6, 4.8, 4.8, n=1800).move_to(fr.c)
        k1 = MathTex(r"K = 0.6", font_size=36, color=FG).move_to(k0)
        self.say(r"Now kick gently: $K = 0.6$. Most lines only bend and survive. These are KAM curves "
                 r"(Kolmogorov, Arnold, Moser): walls that no orbit can ever cross.",
                 anims=[FadeTransform(im0, im1), Transform(k0, k1)], run_time=2)
        labs = VGroup()
        for P, q in CHAINS:
            y = fr.c2p(0, 2 * np.pi * P / q - (2 * np.pi if P / q > 0.5 else 0))[1]
            if P / q == 0.5:
                y = fr.c2p(0, np.pi)[1] - 0.05
            t = MathTex(r"%d/%d" % (P, q), font_size=30, color=MAP).move_to([fr.c[0] + 2.4 + 0.55, y, 0])
            tick = Line([fr.c[0] + 2.4, y, 0], [fr.c[0] + 2.4 + 0.22, y, 0], color=MAP, stroke_width=2)
            labs.add(VGroup(tick, t))
        self.say(r"But at rational speeds the lines break into chains of islands, $q$ islands for $P/q$, "
                 r"each wrapped in a thin chaotic layer.", anims=[FadeIn(labs, lag_ratio=0.3)], run_time=2)
        # Mandelbrot, Part 2
        w = 700
        esc = mandelbrot(RE[0], RE[1], IM[0], IM[1], w, w, 300)
        rgb = colorize(esc, 300, "ep1")
        mim = ImageMobject(rgb).stretch_to_fit_width(MW).stretch_to_fit_height(MW).move_to(MC)
        mlabs = VGroup()
        for P, q in CHAINS:
            c0, n, r = bulb(P, q)
            pos = m2s(c0 + (r + 0.3) * n)
            mlabs.add(VGroup(Line(m2s(c0 + r * n * 0.9), m2s(c0 + (r + 0.2) * n), color=MAP, stroke_width=2),
                             MathTex(r"%d/%d" % (P, q), font_size=30, color=MAP).move_to(pos)))
        tag = Tex(r"Part 2", font_size=30, color=MUTED).next_to(mim, UP, buff=0.2)
        self.say(r"Part 2 used the very same labels: each bulb of the Mandelbrot set carries a fraction $P/q$, "
                 r"the rotation of its periodic orbit.", anims=[FadeIn(mim), FadeIn(tag)], run_time=1.5)
        self.play(FadeIn(mlabs, lag_ratio=0.3), run_time=1.5)
        hl = VGroup(SurroundingRectangle(labs[2], color=ACCENT, buff=0.08),
                    SurroundingRectangle(mlabs[2][1], color=ACCENT, buff=0.08))
        self.say(r"Same ranking too: between $1/3$ and $1/2$ the biggest bulb, like the biggest island chain, is "
                 r"$2/5 = \frac{1+1}{3+2}$. Resonances are ordered by their denominators.", anims=[Create(hl)])
        self.say(r"Rational rotations resonate; the most irrational ones resist. Keep that in mind: it decides "
                 r"which wall falls last.")
        self.unsay()
        self.play(FadeOut(Group(fr, im1, k0, labs, mim, mlabs, tag, hl, self.chapter_tag)))
        self.chapter_tag = None
