"""Sequence 0 — cold open: a continuous zoom into the bifurcation diagram."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import DENSITY_STOPS, FG, ACCENT
from common.logistic import bifurcation_density, density_to_rgb, DELTA, ALPHA, R_INF

LEVELS = 3            # zoom depth: r shrinks by delta, x by |alpha| per level
FRAC_R = 0.64         # keep r_inf at the same relative position on screen


class BifurcationZoom(Scene):
    def window(self, s):
        w = 1.2 / DELTA ** s
        h = 1.0 / abs(ALPHA) ** s
        r0 = R_INF - FRAC_R * w
        return r0, r0 + w, 0.5 - h / 2, 0.5 + h / 2

    def render_image(self, s):
        W, H = config.pixel_width, config.pixel_height
        r0, r1, x0, x1 = self.window(s)
        dens = bifurcation_density(r0, r1, x0, x1, W, H,
                                   transient=1500 + int(1500 * s), samples=int(1.2 * H))
        img = ImageMobject(density_to_rgb(dens, DENSITY_STOPS))
        img.height = config.frame_height
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        return img

    def construct(self):
        s = ValueTracker(0.0)
        img = self.render_image(0)
        self.add(img)
        img.add_updater(lambda m: m.become(self.render_image(s.get_value())))
        self.wait(1.5)
        self.play(s.animate.set_value(LEVELS), run_time=12, rate_func=smooth)
        img.clear_updaters()
        self.wait(0.5)

        line1 = Tex(r"This picture hides a number", color=FG).scale(1.1)
        line2 = Tex(r"that appears \emph{everywhere}.", color=FG).scale(1.1)
        txt = VGroup(line1, line2).arrange(DOWN)
        box = BackgroundRectangle(txt, buff=0.4, fill_opacity=0.75)
        self.play(FadeIn(box), Write(txt), run_time=2)
        self.wait(1.5)
        delta = MathTex(r"\delta = 4.669\,201\,609\,\ldots", color=ACCENT).scale(1.4)
        self.play(FadeOut(txt), img.animate.set_opacity(0.25),
                  box.animate.set_opacity(0), Write(delta), run_time=2)
        self.wait(2)
