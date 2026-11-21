"""Seq 5 — Part 1 hidden inside: Lorenz's map of successive maxima, the cobweb, and Feigenbaum's delta
measured again in the rho ~ 100 window."""
from _common import *  # noqa
import json
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.lorenz import trajectory
from _stages import raster_points

DELTA = 4.669201609


class LorenzMap(Narrated):
    def construct(self):
        self.chapter(r"5 \,$\cdot$\, Part 1, hidden inside")
        dt = 0.005
        P = trajectory(np.array([1.0, 1.0, 1.0]), 6400, dt)[400:]
        z = P[:, 2]
        t = np.arange(z.size) * dt
        ax = Axes(x_range=[0, 30, 5], y_range=[0, 50, 10], x_length=12, y_length=2.6, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_numbers": True, "font_size": 20}
                  ).move_to([0, 1.6, 0])
        zl = MathTex(r"z(t)", font_size=30, color=FG).next_to(ax, LEFT, buff=0.15).shift(0.8 * UP)
        gr = ax.plot_line_graph(t[::3], z[::3], add_vertex_dots=False, line_color=DIAG, stroke_width=2)
        self.say(r"In 1963, Lorenz himself found a way back to one dimension. He watched only $z(t)$\ldots",
                 anims=[Create(ax), FadeIn(zl), Create(gr)], run_time=4)
        im = [i for i in range(1, z.size - 1) if z[i] > z[i - 1] and z[i] >= z[i + 1]]
        dots = VGroup(*[Dot(ax.c2p(t[i], z[i]), radius=0.05, color=MAP) for i in im])
        labs = VGroup(*[MathTex(r"z_{%d}" % (j + 1), font_size=22, color=MAP).next_to(dots[j], UP, buff=0.06)
                        for j in range(4)])
        self.say(r"\ldots and recorded its successive peaks $z_1, z_2, z_3, \ldots$ Then he asked: does "
                 r"each peak predict the next?", anims=[FadeIn(dots, lag_ratio=0.05), FadeIn(labs)], run_time=2.5)
        self.play(FadeOut(VGroup(ax, zl, gr, dots, labs)))
        # the map
        lm = FACTS["lorenz_map"]
        zn, zn1 = np.array(lm["zn"]), np.array(lm["zn1"])
        mx = Axes(x_range=[29, 49, 5], y_range=[29, 49, 5], x_length=5.6, y_length=5.6, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_numbers": True, "font_size": 20}
                  ).move_to([-2.6, 0.35, 0])
        xl = MathTex(r"z_n", font_size=30, color=FG).next_to(mx.x_axis, DOWN, buff=0.45)
        yl = MathTex(r"z_{n+1}", font_size=30, color=FG).next_to(mx.y_axis, LEFT, buff=0.35)
        diag = mx.plot(lambda v: v, x_range=[29, 49], color=DIAG, stroke_width=2.5)
        pts = VGroup(*[Dot(mx.c2p(a, b), radius=0.022, color=MAP) for a, b in zip(zn[:1500], zn1[:1500])])
        self.play(Create(mx), FadeIn(xl), FadeIn(yl))
        self.say(r"Plot each peak against the next. Not a cloud: a thin curve, a \emph{function} "
                 r"$z_{n+1} = F(z_n)$, with a single sharp maximum.",
                 anims=[FadeIn(pts, lag_ratio=0.002)], run_time=4)
        note = VGroup(Tex(r"Part 1:", font_size=30, color=MUTED),
                      MathTex(r"x_{n+1} = r\,x_n(1-x_n)", font_size=34, color=MAP)).arrange(DOWN, buff=0.15)
        note.move_to([3.6, 1.8, 0])
        self.say(r"A hump, a diagonal: this is the picture of Part 1. The continuous flow hides a "
                 r"one-dimensional map.", anims=[Create(diag), FadeIn(note)], run_time=1.5)
        # cobweb with the true successive maxima
        cw = VGroup()
        for i in range(14):
            a, b = zn[i], zn1[i]
            cw.add(Line(mx.c2p(a, a), mx.c2p(a, b), color=ORBIT, stroke_width=2.5))
            cw.add(Line(mx.c2p(a, b), mx.c2p(b, b), color=ORBIT, stroke_width=2.5))
        self.say(r"So we can cobweb it, exactly as in Part 1: up to the curve, across to the diagonal, repeat. "
                 r"These are the real peaks of the flow.", anims=[Create(cw, lag_ratio=1)], run_time=7)
        slope = MathTex(r"|F'(z)| > 1 \ \text{everywhere}\ \ (\min \approx %.2f)" % lm["min_abs_slope"],
                        font_size=32, color=FG).move_to([3.6, 0.2, 0])
        conc = MathTex(r"\Rightarrow\ \text{every cycle is unstable}", font_size=32, color=ORBIT
                       ).next_to(slope, DOWN, buff=0.3)
        self.say(r"Now Part 1's stability test: a cycle is stable if $|F'| < 1$ along it. Here the slope is "
                 r"steeper than 1 everywhere\ldots", anims=[Write(slope)], run_time=1.5)
        self.say(r"\ldots so no cycle can ever attract. Lorenz concluded in 1963 that the motion "
                 r"must be aperiodic. Chaos, proven from a hump.", anims=[Write(conc)], run_time=1.2)
        self.play(FadeOut(VGroup(mx, xl, yl, diag, pts, cw, slope, conc, note)))
        # window around rho = 100: period doubling
        self.chapter(r"5 \,$\cdot$\, Turn the heat to $\rho \approx 100$")
        B = bif()
        xs, ys = [], []
        for r, m in B["window"]:
            for v in m:
                if v > 138:
                    xs.append(r); ys.append(v)
        xr, yr = (99.3, 100.85), (140.5, 146.5)
        bx = Axes(x_range=[99.3, 100.8, 0.25], y_range=[141, 146, 1], x_length=11, y_length=4.2, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "font_size": 20},
                  x_axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 2}},
                  ).move_to([0, 0.5, 0])
        img = raster_points(xs, ys, xr, yr, bx.c2p(xr[1], 0)[0] - bx.c2p(xr[0], 0)[0],
                            bx.c2p(0, yr[1])[1] - bx.c2p(0, yr[0])[1], color_hex="#F2A541", gain=2.0)
        img.move_to(bx.c2p(np.mean(xr), np.mean(yr)))
        lab = MathTex(r"\text{peaks of } z \text{ (top branch)}", font_size=28, color=FG).next_to(bx, UP, buff=0.1)
        rl = MathTex(r"\rho", font_size=30, color=FG).next_to(bx.x_axis, RIGHT, buff=0.15)
        self.say(r"Something even more striking. Far above $\rho = 28$, near $\rho = 100$, the flow settles on "
                 r"a periodic orbit again. Record its peaks as $\rho$ \emph{decreases}:",
                 anims=[Create(bx), FadeIn(lab), FadeIn(rl)], run_time=1.5)
        self.play(FadeIn(img), run_time=2.5)
        PR = json.loads((DATA / "doubling_floquet.json").read_text())["0.001"]
        rk, dk = PR["rho_k"], PR["delta_k"]
        tks = VGroup(*[DashedLine(bx.c2p(r, 141), bx.c2p(r, 146), color=ACCENT, stroke_width=2) for r in rk])
        self.say(r"Each branch splits in two, then again, then again\ldots{} A period-doubling cascade, "
                 r"in a three-dimensional flow.", anims=[Create(tks, lag_ratio=0.4)], run_time=3)
        self.play(FadeOut(img), FadeOut(tks), FadeOut(VGroup(bx, lab, rl)))
        rows = []
        for i, r in enumerate(rk):
            d = r"" if i == 0 or i == len(rk) - 1 else r"%.4f" % dk[i - 1]
            rows.append([str(i + 1), r"%d" % PR["crossings"][i], r"%.9f" % r, d])
        tab = MathTable(rows, col_labels=[MathTex(c) for c in (r"k", r"\text{loops}", r"\rho_k", r"\delta_k")],
                        include_outer_lines=False, line_config={"stroke_color": MUTED, "stroke_width": 1.5},
                        element_to_mobject_config={"font_size": 34}, v_buff=0.32, h_buff=0.7)
        tab.scale_to_fit_width(7.4).move_to([-2.85, 0.45, 0])
        dl = MathTex(r"\delta_k = \frac{\rho_{k-1} - \rho_k}{\rho_k - \rho_{k+1}}", font_size=36, color=FG
                     ).move_to([3.75, 1.4, 0])
        self.say(r"Measure where the doublings happen and take the ratios of successive gaps, "
                 r"as in Part 1:", anims=[FadeIn(tab), Write(dl)], run_time=1.5)
        lim = MathTex(r"\longrightarrow\ \delta = %.4f\ldots" % DELTA, font_size=40, color=ACCENT
                      ).next_to(dl, DOWN, buff=0.6)
        self.say(r"Each $\rho_k$ is located where the orbit's Floquet multiplier crosses $-1$ (Newton on a "
                 r"Poincar\'e section; stable to $10^{-7}$ when the time step is halved).")
        self.say(r"%s\ldots{} converging to Feigenbaum's $\delta = 4.6692$, the constant of Part 1."
                 % ", ".join("%.3f" % d for d in dk), anims=[Write(lim)], run_time=1.5)
        self.say(r"A fluid model, three equations, nothing like $rx(1-x)$\ldots{} and the same constant. "
                 r"Because the flow hides a one-hump map, universality applies to it.")
        self.unsay()
        self.play(FadeOut(VGroup(tab, dl, lim)))
