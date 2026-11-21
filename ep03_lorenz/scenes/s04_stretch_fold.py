"""Seq 4 — Stretch and fold: an ink drop of 40 000 initial conditions; Part 1's fold; dimension 2.06."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.lorenz import trajectory, cloud
from _stages import glow_image, lorenz_points, curve

N = 40000
NSNAP = 240
TMAX = 7.0
INK = ["#0E1116", "#123A5A", "#2F7FC1", "#5DA9E9", "#BDE3FF", "#FFFFFF"]


def snapshots():
    rng = np.random.default_rng(3)
    c0 = trajectory(np.array([1.0, 1.0, 1.0]), 6000, 0.005)[-1]
    v = rng.normal(size=(N, 3))
    v = v / np.linalg.norm(v, axis=1)[:, None] * rng.random(N)[:, None] ** (1 / 3)
    Pc = c0 + 0.6 * v
    out = [Pc.copy()]
    dt = 0.0025
    steps = int(TMAX / NSNAP / dt)
    for _ in range(NSNAP):
        Pc = cloud(Pc, steps, dt)
        out.append(Pc.copy())
    return out


class StretchFold(Narrated):
    def construct(self):
        self.chapter(r"4 \,$\cdot$\, Stretch and fold")
        bg = curve(lorenz_points(T=60, dt=0.004, skip=2), width=0.8, opacity=0.18, colors=MUTED)
        self.play(FadeIn(bg))
        self.say(r"Exponential separation inside a bounded region: how is that even possible? "
                 r"Let us drop some ink: 40\,000 starting points in a tiny ball.")
        S = snapshots()
        k = ValueTracker(0)
        cache = {}
        def img():
            i = int(round(k.get_value()))
            if i not in cache:
                cache.clear()
                cache[i] = glow_image(S[i], stops=INK, gain=1.5)
            return cache[i]
        ink = always_redraw(img)
        self.add(ink)
        self.say(r"First the drop is \emph{stretched}: along the unstable direction it lengthens into a thread, "
                 r"while it is crushed in the other.", anims=[k.animate(rate_func=linear).set_value(70)],
                 run_time=9, wait=0.3)
        self.say(r"The thread cannot grow forever in a bounded box: at the top of the attractor it is "
                 r"\emph{folded} back onto itself, half to each wing.",
                 anims=[k.animate(rate_func=linear).set_value(150)], run_time=9, wait=0.3)
        self.say(r"Stretch, fold, stretch, fold\ldots{} The ink spreads over the whole attractor: "
                 r"two neighbours end up anywhere.", anims=[k.animate(rate_func=linear).set_value(NSNAP)],
                 run_time=9, wait=0.5)
        self.play(FadeOut(ink), FadeOut(bg))
        # Part 1 callback: the logistic map does the same to an interval
        self.chapter(r"4 \,$\cdot$\, The same recipe as Part 1")
        x = np.linspace(0, 1, 300)
        L = 6.0
        top = VGroup(*[Line([-L / 2 + L * a, 1.7, 0], [-L / 2 + L * b, 1.7, 0], stroke_width=10,
                            color=interpolate_color(ManimColor(DIAG), ManimColor(ORBIT), a))
                       for a, b in zip(x[:-1], x[1:])])
        tl = MathTex(r"x \in [0,1]", font_size=32, color=FG).next_to(top, LEFT, buff=0.3)
        fx = 4 * x * (1 - x)
        def folded(t):
            g = VGroup()
            for i in range(len(x) - 1):
                y0, y1 = (0.0 if x[i] < 0.5 else -0.35), (0.0 if x[i + 1] < 0.5 else -0.35)
                ax_, bx_ = fx[i], fx[i + 1]
                p0 = np.array([-L / 2 + L * ((1 - t) * x[i] + t * ax_), 0.2 + t * y0, 0])
                p1 = np.array([-L / 2 + L * ((1 - t) * x[i + 1] + t * bx_), 0.2 + t * y1, 0])
                g.add(Line(p0, p1, stroke_width=10, color=interpolate_color(ManimColor(DIAG),
                                                                           ManimColor(ORBIT), x[i])))
            return g
        tt = ValueTracker(0)
        bot = always_redraw(lambda: folded(tt.get_value()))
        bl = MathTex(r"f(x) = 4x(1-x)", font_size=32, color=MAP).next_to(top, LEFT, buff=0.3).shift(1.5 * DOWN)
        self.play(FadeIn(top), FadeIn(tl))
        self.add(bot)
        self.say(r"Part 1's map does exactly this to the interval: it stretches it to twice its length "
                 r"and folds it in half. Each half covers everything.", anims=[tt.animate.set_value(1), FadeIn(bl)],
                 run_time=4)
        self.say(r"Stretching creates sensitivity; folding keeps it bounded. Every strange attractor is a "
                 r"machine that does both, forever.")
        self.play(FadeOut(VGroup(top, tl, bl)), FadeOut(bot))
        # fractal dimension
        self.chapter(r"4 \,$\cdot$\, A book of infinitely many pages")
        Pg = lorenz_points(T=600, dt=0.002, skip=5)
        glow = glow_image(Pg, yaw=0.3, pitch=-0.2)
        self.play(FadeIn(glow))
        self.say(r"Each fold lays a sheet on top of another. Zoom in on what looks like a surface, and it splits "
                 r"into two sheets, then four\ldots{} an infinite stack.")
        l1, l3 = FACTS["lyapunov"][0], FACTS["lyapunov"][2]
        ky = MathTex(r"D = 2 + \frac{\lambda_1}{|\lambda_3|} = 2 + \frac{%.3f}{%.2f} = %.3f" % (l1, abs(l3),
                     FACTS["kaplan_yorke"]), font_size=40, color=ACCENT)
        box = BackgroundRectangle(ky, fill_opacity=0.85, buff=0.2)
        g = Group(box, ky).to_edge(UP, buff=0.8)
        self.say(r"Its dimension is not 2, not 3. The Kaplan--Yorke formula weighs stretching against "
                 r"crushing:", anims=[FadeIn(g)], run_time=1.2)
        self.say(r"A little more than a surface: volume zero, area infinite. That is a \emph{strange attractor}.")
        self.unsay()
        self.play(FadeOut(g), FadeOut(glow))
