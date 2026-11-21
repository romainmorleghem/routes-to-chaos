"""Seq 3 — The last wall: KAM curves break; the golden curve; Greene's residues -> K_c; unbounded wandering."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _viz import portrait, Frame, golden_orbit, lift_p
from _stages import raster_points

FR = dict(width=4.8, height=4.8, center=(-3.1, 0.25, 0), fs=24)


class Golden(Narrated):
    def construct(self):
        self.chapter(r"3 \,$\cdot$\, The last wall")
        fr = Frame(**FR)
        Ks = [0.6, 0.8, 0.9]
        ims = [portrait(k, 4.8, 4.8, n=1800).move_to(fr.c) for k in Ks]
        kl = MathTex(r"K = 0.6", font_size=36, color=FG).next_to(fr, UP, buff=0.2).shift(1.2 * RIGHT)
        self.say(r"Kick harder. Islands grow, their chaotic layers merge, and the walls between them "
                 r"dissolve one after another.", anims=[FadeIn(fr), FadeIn(ims[0]), FadeIn(kl)])
        for i in (1, 2):
            self.play(FadeTransform(ims[i - 1], ims[i]),
                      Transform(kl, MathTex(r"K = %.1f" % Ks[i], font_size=36, color=FG).move_to(kl)), run_time=2)
            self.wait(0.8)
        g = golden_orbit(0.9)
        gi = raster_points(g[:, 0], g[:, 1], (0, 2 * np.pi), (-np.pi, np.pi), 4.8, 4.8, color_hex="#FFF4D6",
                           gain=3.0).move_to(fr.c)
        gold = MathTex(r"\omega = \frac{\sqrt5 - 1}{2} = \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1+\cdots}}}",
                       font_size=36, color=FG).move_to([3.3, 1.6, 0])
        self.say(r"Which wall resists longest? The one whose rotation is the hardest to approximate by fractions: "
                 r"the golden ratio (white curve).", anims=[ims[2].animate.set_opacity(0.35), FadeIn(gi),
                                                             Write(gold)], run_time=2)
        fib = MathTex(r"\tfrac12,\ \tfrac23,\ \tfrac35,\ \tfrac58,\ \tfrac{8}{13},\ \ldots,\ "
                      r"\tfrac{F_n}{F_{n+1}} \to \omega", font_size=36, color=MAP).next_to(gold, DOWN, buff=0.5)
        self.say(r"Its best fractions are ratios of Fibonacci numbers, and each one has a periodic orbit "
                 r"that hugs the golden curve.", anims=[FadeIn(fib)])
        self.play(FadeOut(gold), FadeOut(fib))
        rows = [[r"%d/%d" % (e["P"], e["q"]), r"%.9f" % e["K"]] for e in GREENE[3:]]
        tab = MathTable(rows, col_labels=[MathTex(r"P/q"), MathTex(r"K_n")], include_outer_lines=False,
                        line_config={"stroke_color": MUTED, "stroke_width": 1.2},
                        element_to_mobject_config={"font_size": 30}, v_buff=0.16, h_buff=0.6)
        tab.scale_to_fit_height(4.6).move_to([3.3, 0.5, 0])
        self.say(r"Greene (1979): the curve exists as long as these orbits stay stable enough, until their "
                 r"residue $R = (2 - \mathrm{tr}\,M)/4$ reaches $1/4$. The threshold $K_n$ for each:",
                 anims=[FadeIn(tab)], run_time=1.5)
        kc = MathTex(r"K_c = 0.971635\ldots", font_size=40, color=ACCENT).next_to(tab, DOWN, buff=0.15)
        self.say(r"The thresholds converge to $K_c = 0.971635$, in agreement with the accepted $0.9716354$. "
                 r"This is the $K$ of Part 3's teaser: the moment the last wall breaks.", anims=[Write(kc)])
        self.play(FadeOut(Group(tab, kc, gi, ims[2], fr, kl)))
        # unbounded wandering above K_c
        a = lift_p(0.1, 0.0, 0.95, 200000)[::250]
        b = lift_p(0.1, 0.0, 1.2, 200000)[::250]
        ax = Axes(x_range=[0, 200000, 50000], y_range=[-20, 12, 5], x_length=11, y_length=4.6, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 1.5, "include_numbers": False},
                  y_axis_config={"include_numbers": True, "font_size": 24, "numbers_to_include": [-20, -10, 10]}
                  ).move_to([0, 0.3, 0])
        xl = Tex(r"$0 \to 200\,000$ kicks", font_size=28, color=MUTED).next_to(ax, DOWN, buff=0.1).align_to(ax, RIGHT)
        yl = MathTex(r"p", font_size=32, color=FG).next_to(ax.y_axis, UP, buff=0.1)
        n = np.arange(a.size) * 250
        ca = ax.plot_line_graph(n, a, add_vertex_dots=False, line_color=MUTED, stroke_width=2)
        cb = ax.plot_line_graph(n, b, add_vertex_dots=False, line_color=ORBIT, stroke_width=2)
        la = MathTex(r"K = 0.95", font_size=30, color=MUTED).next_to(ax.c2p(200000, 2.6), UP, buff=0.1).shift(0.4 * LEFT)
        lb = MathTex(r"K = 1.2", font_size=30, color=ORBIT).next_to(ax.c2p(200000, b[-1]), DOWN, buff=0.15).shift(0.4 * LEFT)
        self.say(r"Follow the speed of one chaotic orbit, without the modulo. Below $K_c$ (grey) it stays "
                 r"trapped between two walls, forever.", anims=[Create(ax), FadeIn(xl), FadeIn(yl),
                                                            Create(ca), FadeIn(la)], run_time=3)
        self.say(r"Above $K_c$ (red), nothing stops it any more: its speed wanders up and down without limit.",
                 anims=[Create(cb), FadeIn(lb)], run_time=4)
        self.unsay()
        self.play(FadeOut(VGroup(ax, xl, yl, ca, cb, la, lb, self.chapter_tag)))
        self.chapter_tag = None
