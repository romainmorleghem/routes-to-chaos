"""Seq 1 — A very simple rule: the logistic map, how to iterate it graphically, the fixed point."""
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE
from common.narrative import Narrated
from common.logistic import orbit
from _stages import *

R = 2.6


class TheMap(Narrated):
    def construct(self):
        self.chapter(r"1 \,$\cdot$\, A very simple rule")

        # --- the rule, built term by term
        growth = MathTex(r"x_{n+1}", r"=", r"r\,x_n", color=FG).scale(1.4)
        self.say(r"A population that reproduces once a year. "
                 r"Let $x_n$ be its size in year $n$, as a fraction of the maximum ($0\le x_n\le 1$).",
                 anims=[Write(growth)])
        b1 = Brace(growth[2], DOWN, color=MAP)
        t1 = Tex(r"growth: $r$ offspring each", font_size=30, color=MAP).next_to(b1, DOWN)
        self.say(r"Left alone, it is multiplied by a factor $r$ every year\ldots",
                 anims=[GrowFromCenter(b1), FadeIn(t1)])
        full = MathTex(r"x_{n+1}", r"=", r"r\,x_n", r"(1 - x_n)", color=FG).scale(1.4)
        self.play(TransformMatchingTex(growth, full), b1.animate.next_to(full[2], DOWN),
                  t1.animate.next_to(full[2], DOWN, buff=0.75).shift(0.6 * LEFT))
        b2 = Brace(full[3], DOWN, color=DIAG)
        t2 = Tex(r"crowding: less food\\when $x$ is close to 1", font_size=30, color=DIAG
                 ).next_to(b2, DOWN).shift(0.9 * RIGHT)
        self.say(r"\ldots but the closer it gets to the maximum, the less food there is for everyone.",
                 anims=[GrowFromCenter(b2), FadeIn(t2)])
        self.say(r"This is the \emph{logistic map}. One parameter, $r$: the fertility. "
                 r"Everything in this video comes from this single line.", extra=0.5)

        # --- the rule as a graph
        eq = equation()
        self.play(FadeOut(VGroup(b1, t1, b2, t2)), ReplacementTransform(full, eq))
        ax = cobweb_axes()
        f = parabola(ax, R)
        xl = MathTex(r"x_n", font_size=30, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex(r"x_{n+1}", font_size=30, color=MUTED).next_to(ax.y_axis, UP, buff=0.1)
        fl = MathTex(r"f(x) = r\,x(1-x)", font_size=30, color=MAP).next_to(ax.c2p(0.5, 0.65), UP, buff=0.1)
        self.say(r"Think of the rule as a function $f$: this year's population in, next year's out. "
                 rf"Here $r = {R}$.", anims=[Create(ax), FadeIn(xl, yl)])
        self.play(Create(f), FadeIn(fl))

        # --- one step, slowly
        x0 = X0
        x1 = R * x0 * (1 - x0)
        d0 = Dot(ax.c2p(x0, 0), color=ORBIT)
        l0 = MathTex("x_0", font_size=30, color=ORBIT).next_to(d0, DOWN, buff=0.35)
        self.say(rf"Start from $x_0 = {x0}$.", anims=[FadeIn(d0, scale=2), FadeIn(l0)])
        up = DashedLine(ax.c2p(x0, 0), ax.c2p(x0, x1), color=ORBIT)
        left = DashedLine(ax.c2p(x0, x1), ax.c2p(0, x1), color=ORBIT, stroke_opacity=0.6)
        l1 = MathTex("x_1", font_size=30, color=ORBIT).next_to(ax.c2p(0, x1), LEFT, buff=0.15)
        self.say(r"Go up to the curve: its height is next year's population $x_1 = f(x_0)$.",
                 anims=[Create(up), d0.animate.move_to(ax.c2p(x0, x1))])
        self.play(Create(left), FadeIn(l1))
        diag = diagonal(ax)
        dl = MathTex("y = x", font_size=28, color=DIAG).next_to(ax.c2p(0.92, 0.92), RIGHT, buff=0.1)
        self.say(r"To iterate, $x_1$ must become the new input. The trick: the diagonal $y=x$ "
                 r"turns a height into a horizontal position.", anims=[Create(diag), FadeIn(dl)])
        across = Line(ax.c2p(x0, x1), ax.c2p(x1, x1), color=ORBIT)
        down = DashedLine(ax.c2p(x1, x1), ax.c2p(x1, 0), color=ORBIT, stroke_opacity=0.6)
        l1b = MathTex("x_1", font_size=30, color=ORBIT).next_to(ax.c2p(x1, 0), DOWN, buff=0.35)
        self.say(r"Go horizontally to the diagonal: you are now above $x_1$. "
                 r"Then up (or down) to the curve again for $x_2$, and so on.",
                 anims=[Create(across), d0.animate.move_to(ax.c2p(x1, x1))])
        self.play(Create(down), FadeIn(l1b), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(VGroup(left, down, l1, l1b, l0, up, across)), FadeOut(d0))

        # --- the full cobweb + the time series
        ts = series_axes()
        tsl = series_labels(ts)
        web = cobweb_path(ax, R)
        ser = series(ts, R)
        self.say(r"Repeating \emph{vertical to the curve, horizontal to the diagonal} draws a "
                 r"\emph{cobweb}. On the right: the same values as a function of time.",
                 anims=[Create(ts), FadeIn(tsl)])
        self.play(Create(web), Create(ser), run_time=5, rate_func=linear)

        # --- the fixed point
        xs = fixed_point(R)
        fp = Dot(ax.c2p(xs, xs), color=STABLE, radius=0.08)
        self.say(r"The orbit settles where the curve crosses the diagonal: a point that maps to "
                 r"itself, a \emph{fixed point} $x^\ast$.", anims=[FadeIn(fp, scale=3)])
        sol = MathTex(r"r\,x^\ast(1-x^\ast) = x^\ast", r"\;\Rightarrow\;", r"x^\ast = 1 - \tfrac1r",
                      color=FG, font_size=38).move_to([3.4, 2.35, 0])
        sol[2].set_color(STABLE)
        self.play(Write(sol), run_time=1.5)
        self.wait(1.5)
        others = VGroup(*[cobweb_path(ax, R, x0=v, n=25, color=MUTED) for v in (0.05, 0.55, 0.9)])
        others_s = VGroup(*[series(ts, R, x0=v, color=MUTED) for v in (0.05, 0.55, 0.9)])
        self.say(r"Other starting points: same destination. The fixed point \emph{attracts}: "
                 r"the population stabilises at $x^\ast$.", anims=[Create(others), Create(others_s)])
        self.play(FadeOut(others), FadeOut(others_s), FadeOut(sol))
        rl = r_label(R, ts)
        self.play(FadeOut(fl), FadeOut(dl), FadeOut(xl), FadeOut(yl), FadeIn(rl))
        self.say(r"Now let's turn up the fertility $r$\ldots", extra=0.3)
        self.unsay()
