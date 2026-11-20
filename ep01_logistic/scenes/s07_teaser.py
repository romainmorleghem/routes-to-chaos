"""Seq 7 — Epilogue: the logistic map is z -> z^2 + c; the cascade lines up with the Mandelbrot set."""
from _common import *  # noqa
from manim import *
from matplotlib.colors import LinearSegmentedColormap
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT
from common.narrative import Narrated
from common.logistic import mandelbrot_escape
from _stages import bif_rgb, image_on_axes, bif_pixels

C_RANGE = (-2.05, 0.35)
IM = 0.3


class Teaser(Narrated):
    def construct(self):
        self.chapter(r"6 \,$\cdot$\, Why? Renormalisation", animate=False)
        self.chapter(r"Epilogue \,$\cdot$\, Into the complex plane")
        sub = MathTex(r"z = r\left(\tfrac12 - x\right)", font_size=44).move_to([0, 2.0, 0])
        res = MathTex(r"z_{n+1} = z_n^2 + c", r",\qquad c = \frac r2 - \frac{r^2}{4}", font_size=44
                      ).next_to(sub, DOWN, buff=0.6)
        res[0].set_color(ACCENT)
        self.say(r"One last change of variables: shift and rescale the population, $z = r(\tfrac12 - x)$\ldots",
                 anims=[Write(sub)])
        self.say(r"\ldots and the logistic map becomes the simplest quadratic rule of all, $z \mapsto z^2 + c$. "
                 r"Same dynamics, new coordinates: $r = 1\ldots4$ becomes $c = \tfrac14\ldots{-2}$.",
                 anims=[Write(res)], extra=0.5)
        self.play(FadeOut(sub), res.animate.scale(0.7).to_corner(UR, buff=0.35).shift(0.05 * DOWN))

        top = Axes(x_range=[*C_RANGE, 0.5], y_range=[-2, 2, 1], x_length=12.4, y_length=2.5, tips=False,
                   axis_config={"color": MUTED, "font_size": 18, "stroke_opacity": 0.6}).move_to([0, 1.55, 0])
        img = image_on_axes(bif_rgb(top, fn=lambda c, z: z * z + c, x0=0.0), top)
        cl = MathTex("c", font_size=28, color=MUTED).next_to(top, RIGHT, buff=0.1)
        self.say(r"Here is the bifurcation diagram again, now against $c$ (so $r$ grows to the \emph{left}).",
                 anims=[FadeIn(img), FadeIn(cl)])

        bot = Axes(x_range=[*C_RANGE, 0.5], y_range=[-IM, IM, IM], x_length=12.4,
                   y_length=12.4 * 2 * IM / (C_RANGE[1] - C_RANGE[0]), tips=False,
                   axis_config={"color": MUTED, "font_size": 18}).next_to(top, DOWN, buff=0.15)
        w, h = bif_pixels(bot)
        esc = mandelbrot_escape(*C_RANGE, -IM, IM, w, h, iters=250)
        cmap = LinearSegmentedColormap.from_list("m", ["#0E1116", "#2B2D6E", "#7A3E9D", "#E85D75", "#F2A541"])
        v = np.nan_to_num(np.log1p(np.nan_to_num(esc, nan=0)) / np.log1p(250))
        rgb = (cmap(np.clip(v * 1.6, 0, 1))[..., :3] * 255).astype(np.uint8)
        rgb[np.isnan(esc)] = (255, 244, 214)
        mimg = image_on_axes(rgb, bot)
        self.say(r"Now let $c$ be a \emph{complex} number. Colour each $c$ by whether the orbit of $0$ stays "
                 r"bounded: you get the \emph{Mandelbrot set}.", anims=[FadeIn(mimg)], run_time=2, extra=0.3)

        cs = [(-0.75, r"r_1"), (-1.25, r"r_2"), (-1.401155, r"r_\infty"), (-1.75, r"1+\sqrt8")]
        lines = VGroup(*[DashedLine(top.c2p(c, 2), bot.c2p(c, -IM), color=FG, stroke_width=1.5,
                                    stroke_opacity=0.8, dash_length=0.07) for c, _ in cs])
        labs = VGroup(*[MathTex(t, font_size=24, color=FG).next_to(top.c2p(c, 2), UP, buff=0.05)
                        for c, t in cs])
        labs[2].shift(0.15 * LEFT)
        labs[3].shift(0.1 * LEFT)
        self.say(r"Each fork of the cascade sits exactly where two bulbs touch; $r_\infty$ where the bulbs "
                 r"accumulate; and the period-3 window is a tiny copy of the whole set.",
                 anims=[Create(lines, lag_ratio=0.3), FadeIn(labs)], run_time=2, extra=1.5)
        self.say(r"The real line was only a slice. What happens off it?", extra=0.5)
        self.play(FadeOut(Group(img, mimg, lines, labs, cl, res)))
        self.unsay()
        nxt = Tex(r"Next \,$\cdot$\, Part 2", font_size=40, color=MUTED)
        ttl = Tex(r"The Mandelbrot Set is a Map of Chaos", font_size=56, color=FG).next_to(nxt, DOWN, buff=0.3)
        self.play(FadeIn(nxt), FadeIn(ttl, shift=0.2 * UP), FadeOut(self.chapter_tag))
        self.wait(3)
        self.play(FadeOut(nxt), FadeOut(ttl))
