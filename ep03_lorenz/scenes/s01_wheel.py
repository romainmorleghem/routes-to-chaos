"""Seq 1 — What the equations mean: Malkus' leaky water wheel; volume contraction."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _stages import lorenz_points

NCUP = 12
R = 1.9
WC = np.array([-3.6, 0.35, 0])


def wheel_state(P, dt):
    """Wheel angle from x (angular velocity) integrated in time; cup fill from (y, z): the mass
    distribution m(phi) = m0 + a1 cos(phi) + b1 sin(phi), with b1 ~ y (left/right) and a1 ~ z (top-heavy)."""
    theta = np.cumsum(P[:, 0]) * dt * 0.35
    return theta


def cup_fill(phi, y, z):
    # phi measured from the top; top-heavy when z is small (water still at the top), lopsided with y
    m = 0.5 + 0.022 * (27 - z) * np.cos(phi) + 0.03 * y * np.sin(phi)
    return float(np.clip(m, 0.04, 1.0))


def wheel(theta, y, z):
    g = VGroup()
    g.add(Circle(radius=R, color=MUTED, stroke_width=3).move_to(WC))
    for j in range(NCUP):
        phi = theta + 2 * np.pi * j / NCUP
        pos = WC + R * np.array([np.sin(phi), np.cos(phi), 0])
        g.add(Line(WC, pos, color=MUTED, stroke_width=1.2))
        f = cup_fill(phi, y, z)
        cup = Rectangle(width=0.36, height=0.42, color=FG, stroke_width=2).move_to(pos)
        water = Rectangle(width=0.36, height=0.42 * f, stroke_width=0, fill_color=DIAG, fill_opacity=0.85)
        water.align_to(cup, DOWN).align_to(cup, LEFT)
        g.add(water, cup)
    g.add(Dot(WC, color=FG, radius=0.06))
    return g


class Wheel(Narrated):
    def construct(self):
        self.chapter(r"1 \,$\cdot$\, What the equations mean")
        self.say(r"Before any mathematics, a machine that obeys these equations \emph{exactly}: "
                 r"a leaky water wheel (Malkus, 1970s).")
        dt = 0.01
        P = lorenz_points(T=60, dt=dt, skip=1.0)
        th = wheel_state(P, dt)
        k = ValueTracker(0)
        live = always_redraw(lambda: wheel(th[int(k.get_value())], *P[int(k.get_value()), 1:]))
        tap = VGroup(Line(WC + [0, R + 1.1, 0], WC + [0, R + 0.35, 0], color=DIAG, stroke_width=6),
                     Tex(r"water in", font_size=26, color=DIAG).move_to(WC + [0.85, R + 0.85, 0]))
        self.play(FadeIn(live), FadeIn(tap))
        self.say(r"Water pours in at the top; every cup leaks through a hole at its bottom. "
                 r"The wheel turns, and the cups carry their water around.")
        # x(t) plot on the right
        ax = Axes(x_range=[0, 60, 10], y_range=[-25, 25, 10], x_length=6.0, y_length=2.6,
                  axis_config={"color": MUTED, "stroke_width": 2}, tips=False).move_to([3.4, 1.3, 0])
        lab = MathTex(r"x(t)", font_size=30, color=ORBIT).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        lab2 = Tex(r"= speed of the wheel", font_size=26, color=MUTED).next_to(lab, RIGHT, buff=0.15)
        graph = always_redraw(lambda: ax.plot_line_graph(
            np.arange(0, int(k.get_value()) + 1, 4) * dt, P[:int(k.get_value()) + 1:4, 0],
            add_vertex_dots=False, line_color=ORBIT, stroke_width=2.5))
        self.play(Create(ax), FadeIn(lab), FadeIn(lab2))
        self.add(graph)
        self.say(r"Watch it: it speeds up, slows down, reverses\ldots{} with no rule we can see. "
                 r"Its speed is $x$.", anims=[k.animate.set_value(1500)], run_time=15, wait=0.3)
        dic = VGroup(
            Tex(r"$x$ \ : how fast the wheel turns", font_size=30, color=FG),
            Tex(r"$y$ \ : how lopsided it is (left vs right)", font_size=30, color=FG),
            Tex(r"$z$ \ : how top-heavy it is", font_size=30, color=FG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([3.4, -1.3, 0])
        self.say(r"Three numbers describe the whole wheel, and Newton's law plus the leaks give exactly "
                 r"the Lorenz equations.", anims=[FadeIn(dic, lag_ratio=0.3), k.animate.set_value(2400)],
                 run_time=8, wait=1.0)
        self.say(r"Why reversals? If the wheel turns too fast, cups pass under the tap too quickly to fill. "
                 r"The heavy side overshoots the bottom and starts rising\ldots{} and pulls the wheel back.",
                 anims=[k.animate.set_value(4000)], run_time=12, wait=1.5)
        self.say(r"Lorenz himself was modelling \emph{convection}: air heated from below rolls one way, "
                 r"then the other. $\rho$ measures how strongly it is heated.",
                 anims=[k.animate.set_value(5200)], run_time=8, wait=1.5)
        self.play(FadeOut(VGroup(ax, lab, lab2, dic)), FadeOut(tap), FadeOut(live), FadeOut(graph))
        # volume contraction
        self.chapter(r"1 \,$\cdot$\, Every volume shrinks")
        div = MathTex(r"\nabla\!\cdot\!\mathbf F", r"= \frac{\partial \dot x}{\partial x} + \frac{\partial \dot y}"
                      r"{\partial y} + \frac{\partial \dot z}{\partial z}", r"= -\sigma - 1 - \beta",
                      r"= -13.67", font_size=40, color=FG).move_to([0, 1.9, 0])
        div[3].set_color(ACCENT)
        self.say(r"One more property, and it is decisive. Take a small blob of starting points: "
                 r"how does its volume change?", anims=[Write(div[:2])], run_time=2)
        self.say(r"The divergence of the velocity field is its rate of change. For Lorenz it is a constant, "
                 r"the same everywhere:", anims=[Write(div[2:])], run_time=2)
        # cube shrinking along e^{-13.67 t}
        cube = Square(side_length=2.0, color=DIAG, fill_opacity=0.25).move_to([-3.2, -0.9, 0])
        tt = ValueTracker(0.0)
        cube.add_updater(lambda m: m.set_width(2.0 * np.exp(-13.67 * tt.get_value() / 3) + 1e-3)
                         .move_to([-3.2, -0.9, 0]))
        vol = always_redraw(lambda: MathTex(r"V(t) = V_0\,e^{-13.67\,t}", r"\quad t = %.2f" % tt.get_value(),
                                            font_size=36, color=FG).move_to([2.3, -0.9, 0]))
        self.add(cube, vol)
        self.say(r"so every volume shrinks like $e^{-13.67\,t}$: after one unit of time, a millionth "
                 r"of it is left ($e^{-13.67} \approx 1.2\times10^{-6}$).",
                 anims=[tt.animate.set_value(1.0)], run_time=5)
        self.say(r"The attractor therefore has \emph{zero volume}. Yet it is not a point, nor a loop. "
                 r"That is what makes it \emph{strange}, and the leaks (the friction) are what make it possible.")
        self.unsay()
        cube.clear_updaters()
        self.play(FadeOut(VGroup(div, cube, vol)))
