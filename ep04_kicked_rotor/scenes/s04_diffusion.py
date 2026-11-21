"""Seq 4 — Chaos as a random walk: <dp^2> = D n, D ~ K^2/2, Rechester-White, accelerator modes."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _viz import portrait, Frame

AX = {"color": MUTED, "stroke_width": 1.5}


class Diffusion(Narrated):
    def construct(self):
        self.chapter(r"4 \,$\cdot$\, Chaos as a random walk")
        fr = Frame(4.4, 4.4, center=(-4.0, 0.3, 0), fs=22)
        im = portrait(5.0, 4.4, 4.4, n=1200).move_to(fr.c)
        kl = MathTex(r"K = 5", font_size=34, color=FG).next_to(fr, UP, buff=0.15)
        self.say(r"Push to $K = 5$. Chaos is now almost everywhere: only tiny specks of islands remain.",
                 anims=[FadeIn(fr), FadeIn(im), FadeIn(kl)])
        g = np.array(FACTS["growth5"]); n = np.arange(1, g.size + 1)
        ax = Axes(x_range=[0, 200, 50], y_range=[0, 2600, 500], x_length=6.2, y_length=4.2, tips=False,
                  axis_config={**AX, "include_numbers": True, "font_size": 22}).move_to([2.7, 0.45, 0])
        xl = MathTex(r"n", font_size=30, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex(r"\langle (p_n - p_0)^2 \rangle", font_size=30, color=FG).next_to(ax, UP, buff=0.1)
        rw = MathTex(r"p_n - p_0 = K\sum_{j<n} \sin\theta_j \ \Rightarrow\ \langle (p_n-p_0)^2\rangle "
                     r"\approx \frac{K^2}{2}\, n", font_size=34, color=DIAG).move_to([0, 3.1, 0])
        self.say(r"If the angles at successive kicks were independent, each kick would add a random step of "
                 r"variance $K^2/2$: a random walk, like a diffusing molecule.", anims=[FadeIn(rw)])
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeOut(kl), rw.animate.scale(0.75).move_to([2.7, -2.55, 0]))
        cur = ax.plot_line_graph(n, g, add_vertex_dots=False, line_color=ORBIT, stroke_width=4)
        th = ax.plot(lambda x: 12.5 * x, x_range=[0, 200], color=DIAG, stroke_width=2.5)
        th = DashedVMobject(th, num_dashes=40)
        slope = np.polyfit(n, g, 1)[0]
        res = MathTex(r"D = %.2f" % slope, r"\quad\text{vs}\quad", r"\tfrac{K^2}{2} = 12.5", font_size=34
                      ).next_to(ax.c2p(10, 2400), RIGHT, buff=0.1)
        res[0].set_color(ORBIT); res[2].set_color(DIAG)
        self.say(r"Measured over $20\,000$ rotors (red): the spread grows linearly, with slope "
                 r"$D = %.2f$. The naive guess (blue) gives $12.5$." % slope,
                 anims=[Create(cur), Create(th), FadeIn(res)], run_time=3)
        self.say(r"Each rotor is deterministic and unpredictable; the crowd obeys a precise law. "
                 r"The same lesson as Part 3's ink cloud.")
        self.play(FadeOut(Group(fr, im, ax, xl, yl, cur, th, res, rw)))
        d = FACTS["diffusion"]
        K = np.array(d["K"]); r = np.clip(np.array(d["D_over_ql"]), 0, 3.2); w = np.array(d["rw"])
        bx = Axes(x_range=[0, 30, 5], y_range=[0, 3, 1], x_length=11.5, y_length=4.6, tips=False,
                  axis_config={**AX, "include_numbers": True, "font_size": 24}).move_to([0, 0.35, 0])
        bxl = MathTex(r"K", font_size=32, color=FG).next_to(bx.x_axis, RIGHT, buff=0.15)
        byl = MathTex(r"D \big/ \tfrac{K^2}{2}", font_size=32, color=FG).next_to(bx, UP, buff=0.05).align_to(bx, LEFT)
        one = DashedLine(bx.c2p(0, 1), bx.c2p(30, 1), color=MUTED, stroke_width=1.5)
        dots = VGroup(*[Dot(bx.c2p(k, v), radius=0.035, color=ORBIT) for k, v in zip(K, r)])
        self.say(r"Repeat for every $K$ and divide by the naive $K^2/2$ (red dots, $400$ kicks, $4000$ rotors "
                 r"each). The ratio oscillates around 1.", anims=[Create(bx), FadeIn(bxl), FadeIn(byl),
                                                                  Create(one), FadeIn(dots, lag_ratio=0.01)],
                 run_time=3)
        curve = bx.plot_line_graph(K, w, add_vertex_dots=False, line_color=MAP, stroke_width=3)
        frm = MathTex(r"1 - 2J_2(K) - 2J_1^2(K) + 2J_2^2(K) + 2J_3^2(K)", font_size=32, color=MAP
                      ).move_to(bx.c2p(21, 2.6))
        self.say(r"The angles are not quite independent: correlations between kicks a few steps apart. "
                 r"Rechester \& White (1980) summed them into Bessel functions (orange), exact at large $K$.",
                 anims=[Create(curve), FadeIn(frm)], run_time=2.5)
        acc = Tex(r"accelerator modes", font_size=28, color=ACCENT).move_to(bx.c2p(9.6, 2.45))
        arr = VGroup(*[Arrow(acc.get_top() + 0.05 * UP, bx.c2p(k + 0.2, 2.95), buff=0.05, color=ACCENT,
                             stroke_width=3, tip_length=0.15) for k in (2 * np.pi, 4 * np.pi)])
        self.say(r"The spikes near $K = 2\pi, 4\pi, \ldots$ are \emph{accelerator modes}: tiny islands whose "
                 r"orbits gain exactly $2\pi m$ per kick. Rotors stuck near them fly instead of walking.",
                 anims=[FadeIn(arr), FadeIn(acc)])
        self.unsay()
        self.play(FadeOut(VGroup(bx, bxl, byl, one, dots, curve, frm, arr, acc, self.chapter_tag)))
        self.chapter_tag = None
