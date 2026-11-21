"""Seq 5 — Part 1's cascade seen from above: bulbs on the real axis, delta, the period-3 mini-brot."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, ACCENT, DENSITY_STOPS
from common.narrative import Narrated
from common.logistic import bifurcation_density, density_to_rgb
from common.fractals import mandelbrot, colorize, mandelbrot_period, period_rgb
from _stages import *

C_RANGE, IM = (-2.05, 0.35), 0.3
C3 = BULBS["period3_minibrot"]


class RealAxis(Narrated):
    def construct(self):
        st = stage(periods=True)
        leg = legend()
        self.add(*st.values(), leg)
        self.chapter(r"4 \,$\cdot$\, Bulbs, rotations and fractions", animate=False)
        self.chapter(r"5 \,$\cdot$\, Part 1's cascade, seen from above")

        top = Axes(x_range=[*C_RANGE, 0.5], y_range=[-2, 2, 1], x_length=12.4, y_length=2.5, tips=False).move_to([0, 1.55, 0])
        bot = Axes(x_range=[*C_RANGE, 0.5], y_range=[-IM, IM, IM], x_length=12.4,
                   y_length=12.4 * 2 * IM / (C_RANGE[1] - C_RANGE[0]), tips=False).next_to(top, DOWN, buff=0.15)
        px = lambda ax: (int(ax.x_length / config.frame_width * config.pixel_width),
                         int(ax.y_length / config.frame_height * config.pixel_height))

        def img_at(rgb, ax):
            m = ImageMobject(rgb)
            m.stretch_to_fit_width(ax.x_length).stretch_to_fit_height(ax.y_length).move_to(ax.get_center())
            m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
            return m

        def diag_rgb(c0, c1):
            w, h = px(top)
            d = bifurcation_density(c0, c1, -2, 2, w, h, transient=1500, samples=int(1.3 * h), x0=0.0,
                                    fn=lambda c, z: z * z + c)
            return density_to_rgb(d, DENSITY_STOPS)

        def strip_rgb(c0, c1, im):
            w, h = px(bot)
            win = (c0, c1, -im, im)
            return period_rgb(colorize(mandelbrot(*win, w, h, 600), 600, mode="adaptive"), mandelbrot_period(*win, w, h, 3000, 64))

        D = img_at(diag_rgb(*C_RANGE), top)
        S = img_at(strip_rgb(*C_RANGE, IM), bot)
        self.play(FadeOut(Group(*st.values(), leg)), run_time=1)
        self.play(FadeIn(D), FadeIn(S), run_time=1.5)
        self.say(r"Back to Part 1's picture: the bifurcation diagram of $z \mapsto z^2 + c$ for real $c$, above "
                 r"the Mandelbrot set — now with its inside coloured by period.")
        cs = BULBS["real_centres"][:5]
        marks = VGroup()
        for k, c in enumerate(cs[:4]):
            l = DashedLine(top.c2p(c, 2), bot.c2p(c, -IM), color=FG, stroke_width=1.3, stroke_opacity=0.7,
                           dash_length=0.06)
            t = MathTex(str(2 ** k), font_size=26, color=FG).next_to(top.c2p(c, 2), UP, buff=0.06)
            marks.add(VGroup(l, t))
        marks[3][1].shift(0.12 * LEFT)
        self.say(r"Above each bulb of the axis, count the branches of the diagram: 1 over the cardioid, 2 over "
                 r"the disk, then 4, 8\ldots{} Part 1's cascade \emph{is} this chain of bulbs.",
                 anims=[Create(marks, lag_ratio=0.4)], run_time=2, extra=0.5)
        d = BULBS["real_delta"]
        tab = VGroup(MathTex(r"\frac{c_{n-1} - c_n}{c_n - c_{n+1}}", font_size=30, color=MUTED),
                     *[MathTex(f"{v:.5f}", font_size=28, color=ACCENT) for v in (d[0], d[2], d[4], d[-1])],
                     MathTex(r"\to\ \delta = 4.669\ldots", font_size=30, color=ACCENT)
                     ).arrange(RIGHT, buff=0.3)
        tab.scale_to_fit_width(6.2).move_to(top.c2p(-0.3, 1.45))
        tbg = BackgroundRectangle(tab, fill_opacity=0.85, buff=0.1)
        self.say(r"Measure the bulbs' centres $c_n$ along the axis: their gaps shrink by the same factor "
                 r"$\delta = 4.669\ldots$ — Feigenbaum's constant again, read off the Mandelbrot set.",
                 anims=[FadeIn(tbg), FadeIn(tab, lag_ratio=0.2)], run_time=2, extra=0.5)
        self.play(FadeOut(VGroup(tbg, tab, marks)))

        # --- dive into the period-3 window
        t = ValueTracker(0.0)
        w0, w1 = C_RANGE[1] - C_RANGE[0], 0.055
        cmid0 = (C_RANGE[0] + C_RANGE[1]) / 2

        def win(u):
            w = w0 * (w1 / w0) ** u
            f = (1 - w / w0) / (1 - w1 / w0)
            cm = cmid0 + (C3 - cmid0) * f
            return cm - w / 2, cm + w / 2, IM * w / w0

        D.add_updater(lambda m: m.become(img_at(diag_rgb(*win(t.get_value())[:2]), top)))
        S.add_updater(lambda m: m.become(img_at(strip_rgb(*win(t.get_value())), bot)))
        self.say(r"Now dive into Part 1's period-3 window, at $c \approx -1.7549$\ldots",
                 anims=[t.animate.set_value(1.0)], run_time=8, wait=0)
        D.clear_updaters(); S.clear_updaters()
        self.say(r"\ldots a complete mini-Mandelbrot sits on the axis, with its own cardioid (period 3), its own "
                 r"bulbs (6, 12\ldots) and, above it, its own cascade.", extra=1.0)
        self.play(FadeOut(D), FadeOut(S))
        self.unsay()
