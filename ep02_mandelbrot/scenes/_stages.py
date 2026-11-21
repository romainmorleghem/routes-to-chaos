"""Episode 2 layout: parameter plane (c, left) and dynamical plane (z, right), on screen throughout."""
import cmath
import numpy as np
from manim import (Axes, VGroup, Tex, MathTex, Rectangle, Dot, Line, VMobject, ImageMobject, config,
                   RESAMPLING_ALGORITHMS, UP, DOWN, LEFT, RIGHT)
from common.style import FG, MUTED, MAP, ORBIT, DIAG, ACCENT
from common.fractals import mandelbrot, julia, colorize, mandelbrot_period, period_rgb

C_WIN = (-2.25, 0.75, -1.25, 1.25)
Z_WIN = (-2.46, 2.46, -2.05, 2.05)
PANEL_W, PANEL_H = 6.3, 5.25
LEFT_C, RIGHT_C = np.array([-3.45, 0.15, 0]), np.array([3.45, 0.15, 0])

PHI = (np.sqrt(5) - 1) / 2


def cardioid(t):
    w = cmath.exp(2j * np.pi * t) / 2
    return w - w * w


GALLERY = [  # name, c, caption fragment
    ("cauliflower", 0.25),
    ("San Marco", -0.75),
    ("basilica", -1.0),
    ("Douady's rabbit", -0.122561166876654 + 0.744861766619744j),
    ("Siegel disk", cardioid(1 - PHI)),
    ("dendrite", 1j),
    ("airplane", -1.754877666246693),
    ("dragon", -0.8 + 0.156j),
    ("dust", 0.45 + 0.35j),
]


def panel_axes(win, center):
    ax = Axes(x_range=[win[0], win[1], 1], y_range=[win[2], win[3], 1], x_length=PANEL_W, y_length=PANEL_H,
              tips=False, axis_config={"color": MUTED, "stroke_width": 1, "stroke_opacity": 0.35})
    ax.shift(center - ax.get_center())
    return ax


def panel_px():
    return (int(PANEL_W / config.frame_width * config.pixel_width),
            int(PANEL_H / config.frame_height * config.pixel_height))


def to_image(rgb, center):
    img = ImageMobject(rgb)
    img.stretch_to_fit_width(PANEL_W).stretch_to_fit_height(PANEL_H).move_to(center)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
    return img


def frame(center):
    return Rectangle(width=PANEL_W, height=PANEL_H, stroke_color=MUTED, stroke_width=1.2).move_to(center)


def titles():
    l = Tex(r"parameter plane: the rule $z\mapsto z^2+c$", font_size=26, color=MUTED)
    r = Tex(r"dynamical plane: the orbit $z_0, z_1, z_2, \ldots$", font_size=26, color=MUTED)
    l.next_to(LEFT_C + PANEL_H / 2 * UP, UP, buff=0.12)
    r.next_to(RIGHT_C + PANEL_H / 2 * UP, UP, buff=0.12)
    return VGroup(l, r)


def m_rgb(win=C_WIN, maxit=250, periods=False, mode="ep1"):
    w, h = panel_px()
    e = mandelbrot(*win, w, h, maxit)
    rgb = colorize(e, maxit, mode=mode)
    if periods:
        rgb = period_rgb(rgb, mandelbrot_period(*win, w, h, max(2000, maxit), 64))
    return rgb


def j_rgb(c, win=Z_WIN, maxit=300, mode="ep1"):
    w, h = panel_px()
    return colorize(julia(*win, w, h, c.real, c.imag, maxit), maxit, mode=mode)


def stage(with_m=True, periods=False):
    """Two empty panels (+ the Mandelbrot set on the left). The standard opening/closing state."""
    cax, zax = panel_axes(C_WIN, LEFT_C), panel_axes(Z_WIN, RIGHT_C)
    g = dict(cax=cax, zax=zax, cf=frame(LEFT_C), zf=frame(RIGHT_C), tit=titles())
    if with_m:
        g["m"] = to_image(m_rgb(periods=periods), LEFT_C)
    return g


def cpt(ax, c):
    return ax.c2p(c.real, c.imag)


def orbit(c, z0=0j, n=40):
    zs = [z0]
    for _ in range(n):
        z = zs[-1] ** 2 + c
        if abs(z) > 50:
            break
        zs.append(z)
    return zs


def orbit_path(ax, zs, color=ORBIT, win=Z_WIN):
    """Dots + segments of an orbit, clipped to the panel window."""
    inside = lambda z: win[0] <= z.real <= win[1] and win[2] <= z.imag <= win[3]
    pts = [cpt(ax, z) for z in zs if inside(z)]
    def clip(a, b):           # shorten a segment that leaves the window
        if inside(b):
            return b
        lo, hi = 0.0, 1.0
        for _ in range(30):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if inside(a + m * (b - a)) else (lo, m)
        return a + lo * (b - a)
    segs = VGroup(*[Line(cpt(ax, a), cpt(ax, clip(a, b)), stroke_width=1.6, color=color, stroke_opacity=0.55)
                    for a, b in zip(zs[:-1], zs[1:]) if inside(a)])
    dots = VGroup(*[Dot(p, radius=0.045, color=color) for p in pts])
    return VGroup(segs, dots)


def legend():
    from manim import Square, ManimColor
    from common.fractals import PERIOD_COLORS
    chips = VGroup()
    for k in range(8):
        sq = Square(0.22, fill_color=ManimColor(PERIOD_COLORS[k] / 255), fill_opacity=1, stroke_width=0)
        chips.add(VGroup(sq, MathTex(str(k + 1), font_size=22, color=FG).next_to(sq, RIGHT, buff=0.06)))
    chips.arrange(RIGHT, buff=0.22)
    return VGroup(Tex("period:", font_size=22, color=MUTED), chips).arrange(RIGHT, buff=0.15
                  ).next_to(LEFT_C + PANEL_H / 2 * DOWN, DOWN, buff=0.12)
