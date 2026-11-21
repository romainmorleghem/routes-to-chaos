"""Seq 0 — from Part 1's last picture to the whole plane, then a dive into seahorse valley."""
from _common import *  # noqa
import numpy as np
from manim import *
from matplotlib.colors import LinearSegmentedColormap
from common.style import FG, MUTED, ACCENT
from common.narrative import Narrated
from common.logistic import mandelbrot_escape
from common.fractals import mandelbrot, colorize

E1 = load_ep1_stages()
C_RANGE, IM = (-2.05, 0.35), 0.3                     # exactly Part 1, seq 7
FULL = (-2.6, 1.0, -1.25, 1.25)                      # whole set, aspect 1.44
FULL_W, FULL_H, FULL_C = 8.64, 6.0, np.array([0, 0.25, 0])
TARGET = complex(-0.7436423016578859, 0.13182651981259472)  # period-39 mini-brot, seahorse valley (Newton)
DEPTH = 5.45                                         # decades of zoom (final width 1.3e-5)


def ep1_strip_rgb(bot):
    w, h = E1.bif_pixels(bot)
    esc = mandelbrot_escape(*C_RANGE, -IM, IM, w, h, iters=250)
    cmap = LinearSegmentedColormap.from_list("m", ["#0E1116", "#2B2D6E", "#7A3E9D", "#E85D75", "#F2A541"])
    v = np.nan_to_num(np.log1p(np.nan_to_num(esc, nan=0)) / np.log1p(250))
    rgb = (cmap(np.clip(v * 1.6, 0, 1))[..., :3] * 255).astype(np.uint8)
    rgb[np.isnan(esc)] = (255, 244, 214)
    return rgb


class ColdOpen(Narrated):
    def construct(self):
        # --- Part 1's final picture, rebuilt with the same code
        top = Axes(x_range=[*C_RANGE, 0.5], y_range=[-2, 2, 1], x_length=12.4, y_length=2.5, tips=False,
                   axis_config={"color": MUTED, "font_size": 18, "stroke_opacity": 0.6}).move_to([0, 1.55, 0])
        diag = E1.image_on_axes(E1.bif_rgb(top, fn=lambda c, z: z * z + c, x0=0.0), top)
        bot = Axes(x_range=[*C_RANGE, 0.5], y_range=[-IM, IM, IM], x_length=12.4,
                   y_length=12.4 * 2 * IM / (C_RANGE[1] - C_RANGE[0]), tips=False,
                   axis_config={"color": MUTED, "font_size": 18}).next_to(top, DOWN, buff=0.15)
        strip = E1.image_on_axes(ep1_strip_rgb(bot), bot)
        cs = [(-0.75, r"r_1"), (-1.25, r"r_2"), (-1.401155, r"r_\infty"), (-1.75, r"1+\sqrt8")]
        lines = VGroup(*[DashedLine(top.c2p(c, 2), bot.c2p(c, -IM), color=FG, stroke_width=1.5,
                                    stroke_opacity=0.8, dash_length=0.07) for c, _ in cs])
        labs = VGroup(*[MathTex(t, font_size=24, color=FG).next_to(top.c2p(c, 2), UP, buff=0.05) for c, t in cs])
        labs[2].shift(0.15 * LEFT); labs[3].shift(0.1 * LEFT)
        self.chapter(r"Previously, in Part 1", animate=False)
        self.remove(self.chapter_tag)
        self.play(FadeIn(Group(diag, strip, lines, labs)), FadeIn(self.chapter_tag), run_time=1.5)
        self.say(r"Part 1 ended here: the period-doubling cascade of the logistic map, lined up with the "
                 r"Mandelbrot set along the real line.")
        self.say(r"But the real line was only a slice. Today: the whole plane.")

        # --- the strip becomes part of the whole set
        self.play(FadeOut(diag), FadeOut(lines), FadeOut(labs))
        sw = (C_RANGE[1] - C_RANGE[0]) / (FULL[1] - FULL[0]) * FULL_W
        sh = 2 * IM / (FULL[3] - FULL[2]) * FULL_H
        sx = FULL_C[0] - FULL_W / 2 + ((C_RANGE[0] + C_RANGE[1]) / 2 - FULL[0]) / (FULL[1] - FULL[0]) * FULL_W
        W = int(FULL_W / config.frame_width * config.pixel_width)
        H = int(FULL_H / config.frame_height * config.pixel_height)

        def full_image(rgb):
            m = ImageMobject(rgb)
            m.stretch_to_fit_width(FULL_W).stretch_to_fit_height(FULL_H).move_to(FULL_C)
            m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
            return m

        e0 = mandelbrot(*FULL, W, H, 250)
        base = colorize(e0, 250, mode="ep1")
        whole = full_image(base)
        self.play(strip.animate.stretch_to_fit_width(sw).stretch_to_fit_height(sh).move_to([sx, FULL_C[1], 0]),
                  run_time=2)
        self.add(whole, strip)
        self.play(FadeIn(whole), FadeOut(strip), run_time=1.5)
        self.chapter(r"Part 2")

        # --- the dive
        u = ValueTracker(0.0)
        lo_hi = {}

        def frame_rgb(t):
            w = (FULL[1] - FULL[0]) * 10 ** (-DEPTH * t)
            h = w * (FULL[3] - FULL[2]) / (FULL[1] - FULL[0])
            c0 = complex((FULL[0] + FULL[1]) / 2, 0)
            cen = TARGET + (c0 - TARGET) * 10 ** (-DEPTH * t)
            maxit = int(250 + 450 * DEPTH * t)
            e = mandelbrot(cen.real - w / 2, cen.real + w / 2, cen.imag - h / 2, cen.imag + h / 2, W, H, maxit)
            ad = colorize(e, maxit, mode="adaptive")
            a = min(1.0, t * 12)                    # blend from Part 1's colouring to adaptive contrast
            if a < 1:
                ep1 = colorize(e, maxit, mode="ep1")
                ad = ((1 - a) * ep1 + a * ad).astype(np.uint8)
            return ad

        img = full_image(base)
        self.remove(whole)
        self.add(img)
        img.add_updater(lambda m: m.become(full_image(frame_rgb(u.get_value()))))
        self.say(r"Each point of this picture is a different rule, $z \mapsto z^2 + c$. "
                 r"Its colour tells what that rule does to the number $0$.", wait=0)
        self.play(u.animate.set_value(1.0), run_time=16, rate_func=smooth)
        img.clear_updaters()
        self.say(r"300\,000 times closer: a complete copy of the whole set. "
                 r"Why this shape? And what does it have to do with chaos?", extra=0.3)
        self.unsay()
        series = Tex(r"Routes to Chaos", font_size=72, color=FG)
        part = Tex(r"Part 2 \,$\cdot$\, The Mandelbrot Set is a Map of Chaos", font_size=36,
                   color=MUTED).next_to(series, DOWN, buff=0.4)
        self.play(img.animate.set_opacity(0.15), run_time=1)
        self.play(FadeIn(series, shift=0.2 * UP), FadeIn(part), run_time=1.5)
        self.wait(2.5)
        self.play(FadeOut(series), FadeOut(part), FadeOut(img), FadeOut(self.chapter_tag), run_time=1)
