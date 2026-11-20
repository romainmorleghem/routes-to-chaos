"""Sequences 1-2 — the logistic map, cobweb diagram and time series as r varies."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT
from common.logistic import orbit

N_IT = 60
X0 = 0.2


class Cobweb(Scene):
    def construct(self):
        eq = MathTex(r"x_{n+1} = r\,x_n\,(1 - x_n)", color=FG).to_edge(UP)
        self.play(Write(eq))

        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=5.2, y_length=5.2,
                  axis_config={"color": MUTED, "include_numbers": True,
                               "font_size": 22}).to_edge(LEFT, buff=0.8).shift(0.4 * DOWN)
        ts = Axes(x_range=[0, N_IT, 10], y_range=[0, 1, 0.5], x_length=6, y_length=3,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}
                  ).to_edge(RIGHT, buff=0.6).shift(0.2 * DOWN)
        ts_lab = VGroup(MathTex("n", font_size=28).next_to(ts.x_axis, DOWN, buff=0.1).align_to(ts, RIGHT),
                        MathTex("x_n", font_size=28).next_to(ts.y_axis, UP, buff=0.1))
        diag = ax.plot(lambda x: x, color=DIAG)

        r = ValueTracker(2.6)
        r_lab = always_redraw(lambda: MathTex(f"r = {r.get_value():.3f}", color=MAP)
                              .next_to(ts, UP, buff=0.5))

        def parabola():
            rv = r.get_value()
            return ax.plot(lambda x: rv * x * (1 - x), color=MAP)

        def cobweb():
            xs = orbit(r.get_value(), X0, N_IT)
            pts = [ax.c2p(xs[0], 0)]
            for a, b in zip(xs[:-1], xs[1:]):
                pts += [ax.c2p(a, b), ax.c2p(b, b)]
            path = VMobject(stroke_width=2).set_points_as_corners(pts)
            # older segments fade, so the attractor stands out
            path.set_stroke(color=[ORBIT, ORBIT], opacity=0.85)
            return path

        def series():
            xs = orbit(r.get_value(), X0, N_IT)
            line = VMobject(stroke_color=ORBIT, stroke_width=1.5, stroke_opacity=0.5)
            line.set_points_as_corners([ts.c2p(i, v) for i, v in enumerate(xs)])
            dots = VGroup(*[Dot(ts.c2p(i, v), radius=0.03, color=ORBIT) for i, v in enumerate(xs)])
            return VGroup(line, dots)

        f_graph = always_redraw(parabola)
        self.play(Create(ax), Create(diag), Create(ts), FadeIn(ts_lab))
        self.play(Create(f_graph), FadeIn(r_lab))

        # first cobweb, drawn step by step
        web0, ser0 = cobweb(), series()
        self.play(Create(web0), Create(ser0), run_time=4, rate_func=linear)
        self.remove(web0, ser0)
        web = always_redraw(cobweb)
        ser = always_redraw(series)
        self.add(web, ser)

        captions = [
            (3.2, r"$r=3.2$: the fixed point is unstable — a 2-cycle appears"),
            (3.5, r"$r=3.5$: period 4"),
            (3.83, r"$r\approx 3.83$: a window of period 3"),
            (3.97, r"$r=3.97$: chaos"),
        ]
        cap = Tex(r"$r<3$: every orbit settles on a fixed point", font_size=34, color=FG).to_edge(DOWN)
        self.play(FadeIn(cap))
        self.wait(1.5)
        for target, text in captions:
            new = Tex(text, font_size=34, color=FG).to_edge(DOWN)
            self.play(r.animate.set_value(target), FadeTransform(cap, new), run_time=3)
            cap = new
            self.wait(1.5)
