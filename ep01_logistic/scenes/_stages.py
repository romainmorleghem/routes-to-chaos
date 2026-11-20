"""Shared layouts for episode 1. Scenes build their opening state with these functions so that
the first frame of a scene is identical to the last frame of the previous one."""
import numpy as np
from manim import (Axes, VMobject, VGroup, Dot, MathTex, ImageMobject, Line, config,
                   RESAMPLING_ALGORITHMS, LEFT, RIGHT, UP, DOWN)
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE, DENSITY_STOPS
from common.logistic import orbit, bifurcation_density, density_to_rgb

X0 = 0.2
N_IT = 60

# ---------------------------------------------------------------- cobweb + time series stage

def cobweb_axes():
    return Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=5.0, y_length=5.0,
                axis_config={"color": MUTED, "include_numbers": True, "font_size": 22},
                tips=False).move_to([-3.6, 0.05, 0])


def series_axes():
    return Axes(x_range=[0, N_IT, 10], y_range=[0, 1, 0.5], x_length=6.2, y_length=3.0,
                axis_config={"color": MUTED, "include_numbers": True, "font_size": 20},
                tips=False).move_to([3.4, -0.2, 0])


def series_labels(ts):
    return VGroup(MathTex("n", font_size=28, color=MUTED).next_to(ts.x_axis, RIGHT, buff=0.15),
                  MathTex("x_n", font_size=28, color=MUTED).next_to(ts.y_axis, UP, buff=0.1))


def equation():
    return MathTex(r"x_{n+1} = r\,x_n\,(1 - x_n)", color=FG).move_to([0, 3.35, 0])


def r_label(r, ts):
    return MathTex(f"r = {r:.3f}", color=MAP).next_to(ts, UP, buff=0.45)


def parabola(ax, r, color=MAP, k=1):
    def fk(x):
        for _ in range(k):
            x = r * x * (1 - x)
        return x
    return ax.plot(fk, color=color, x_range=[0, 1, 0.002], stroke_width=3)


def diagonal(ax):
    return ax.plot(lambda x: x, color=DIAG, stroke_width=2.5)


def cobweb_path(ax, r, x0=X0, n=N_IT, color=ORBIT, start=0):
    xs = orbit(r, x0, n)
    pts = [ax.c2p(xs[start], 0 if start == 0 else xs[start])]
    for a, b in zip(xs[start:-1], xs[start + 1:]):
        pts += [ax.c2p(a, b), ax.c2p(b, b)]
    return VMobject(stroke_width=2, stroke_color=color, stroke_opacity=0.85).set_points_as_corners(pts)


def series(ts, r, x0=X0, n=N_IT, color=ORBIT, transient=0):
    xs = orbit(r, x0, n)
    line = VMobject(stroke_color=color, stroke_width=1.5, stroke_opacity=0.45)
    line.set_points_as_corners([ts.c2p(i, v) for i, v in enumerate(xs)])
    dots = VGroup(*[Dot(ts.c2p(i, v), radius=0.035,
                        color=MUTED if i < transient else color) for i, v in enumerate(xs)])
    return VGroup(line, dots)


def fixed_point(r):
    return 1 - 1 / r


def cobweb_stage(r, with_fixed_point=True):
    """Everything on screen at the end of Seq 1 / start of Seq 2 (and Seq 2 end / Seq 3 start)."""
    ax, ts = cobweb_axes(), series_axes()
    g = dict(eq=equation(), ax=ax, ts=ts, ts_lab=series_labels(ts), diag=diagonal(ax),
             f=parabola(ax, r), web=cobweb_path(ax, r), ser=series(ts, r), rlab=r_label(r, ts))
    if with_fixed_point:
        xs = fixed_point(r)
        g["fp"] = Dot(ax.c2p(xs, xs), color=STABLE, radius=0.08)
    return g


# ---------------------------------------------------------------- bifurcation diagram stage

BIF_R = (2.8, 4.0)
BIF_X = (0.0, 1.0)


def bif_axes(x_length=11.6, y_length=5.4, center=(0.35, 0.15, 0), r_range=BIF_R, x_range=BIF_X,
             r_step=0.2):
    ax = Axes(x_range=[r_range[0], r_range[1], r_step], y_range=[x_range[0], x_range[1], 0.5],
              x_length=x_length, y_length=y_length, tips=False,
              axis_config={"color": MUTED, "font_size": 20},
              x_axis_config={"include_numbers": True,
                             "decimal_number_config": {"num_decimal_places": 1}},
              y_axis_config={"include_numbers": True}).move_to(center)
    return ax


def bif_axis_labels(ax):
    return VGroup(MathTex("r", font_size=30, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.15),
                  MathTex("x", font_size=30, color=MUTED).next_to(ax.y_axis, UP, buff=0.1))


def bif_pixels(ax):
    w = int(ax.x_length / config.frame_width * config.pixel_width)
    h = int(ax.y_length / config.frame_height * config.pixel_height)
    return max(w, 64), max(h, 64)


def bif_rgb(ax, r_range=None, x_range=None, fn=None, x0=0.5, transient=1500):
    r_range = r_range or (ax.x_range[0], ax.x_range[1])
    x_range = x_range or (ax.y_range[0], ax.y_range[1])
    w, h = bif_pixels(ax)
    dens = bifurcation_density(*r_range, *x_range, w, h, transient=transient,
                               samples=int(1.3 * h), x0=x0, fn=fn)
    return density_to_rgb(dens, DENSITY_STOPS)


def image_on_axes(rgb, ax):
    img = ImageMobject(rgb)
    img.stretch_to_fit_width(ax.x_length).stretch_to_fit_height(ax.y_length)
    img.move_to(ax.c2p((ax.x_range[0] + ax.x_range[1]) / 2, (ax.y_range[0] + ax.y_range[1]) / 2))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return img


def bif_stage():
    ax = bif_axes()
    return dict(ax=ax, lab=bif_axis_labels(ax), img=image_on_axes(bif_rgb(ax), ax))


def rinf_marker(ax):
    from common.style import ACCENT
    from common.logistic import R_INF
    from manim import DashedLine
    line = DashedLine(ax.c2p(R_INF, ax.y_range[0]), ax.c2p(R_INF, ax.y_range[1]), color=ACCENT,
                      stroke_width=2)
    lab = MathTex(r"r_\infty", font_size=30, color=ACCENT).next_to(line, UP, buff=0.08)
    return VGroup(line, lab)


def delta_badge():
    from common.style import ACCENT
    from manim import UR
    return MathTex(r"\delta = 4.669\,201\ldots", font_size=30, color=ACCENT).to_corner(UR, buff=0.35)


def reveal(rgb, upto_frac, bg=(14, 17, 22)):
    """Copy of an RGB image with the columns right of `upto_frac` blanked (sweep effect)."""
    out = rgb.copy()
    k = int(np.clip(upto_frac, 0, 1) * rgb.shape[1])
    out[:, k:] = bg
    return out
