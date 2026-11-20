"""Seq 2 — When a fixed point breaks: linear stability, f'(x*) = 2 - r, f∘f and the 2-cycle."""
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE, ACCENT
from common.narrative import Narrated
from _stages import *

R0 = 2.6
R2 = 1 + np.sqrt(6)


class Stability(Narrated):
    def construct(self):
        st = cobweb_stage(R0)
        self.add(*st.values())
        self.chapter(r"1 \,$\cdot$\, A very simple rule", animate=False)
        ax, ts = st["ax"], st["ts"]

        r = ValueTracker(R0)
        f = always_redraw(lambda: parabola(ax, r.get_value()))
        web = always_redraw(lambda: cobweb_path(ax, r.get_value()))
        ser = always_redraw(lambda: series(ts, r.get_value()))
        rl = always_redraw(lambda: r_label(r.get_value(), ts))
        fp = always_redraw(lambda: Dot(ax.c2p(fixed_point(r.get_value()), fixed_point(r.get_value())),
                                       color=STABLE if r.get_value() < 3 else ORBIT, radius=0.08))
        self.remove(st["f"], st["web"], st["ser"], st["rlab"], st["fp"])
        self.add(f, web, ser, rl, fp)
        self.chapter(r"2 \,$\cdot$\, When a fixed point breaks")

        self.say(r"At $r = 2.9$ the orbit still converges, but it now \emph{overshoots}: "
                 r"above $x^\ast$, below, above\ldots",
                 anims=[r.animate.set_value(2.9)], run_time=3)

        # --- why: linearisation (replaces the time series)
        side = VGroup(ts, st["ts_lab"])
        self.play(FadeOut(side), FadeOut(ser), FadeOut(rl))
        self.remove(ser, rl)
        lin = VGroup(
            MathTex(r"x_{n+1} - x^\ast", r"= f(x_n) - f(x^\ast)"),
            MathTex(r"\approx f'(x^\ast)\,(x_n - x^\ast)"),
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.9).move_to([3.3, 1.7, 0])
        lin[1].align_to(lin[0][1], LEFT)
        self.say(r"Why? Close to $x^\ast$ the curve is nearly a straight line, of slope $f'(x^\ast)$.",
                 anims=[Write(lin[0])])
        self.say(r"So each step multiplies the distance to $x^\ast$ by the same number, $f'(x^\ast)$.",
                 anims=[Write(lin[1])])
        cases = VGroup(
            Tex(r"$|f'(x^\ast)| < 1$: the distance shrinks \;$\to$ stable", color=STABLE),
            Tex(r"$|f'(x^\ast)| > 1$: the distance grows \;$\to$ unstable", color=ORBIT),
            Tex(r"$f'(x^\ast) < 0$: the sign flips \;$\to$ zig-zag", color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.62).next_to(lin, DOWN, buff=0.4)
        self.say(r"If its size is below 1, the population returns to $x^\ast$; above 1, it is pushed "
                 r"away. A negative slope explains the zig-zag.", anims=[FadeIn(cases, lag_ratio=0.3)])
        slope = MathTex(r"f'(x^\ast) = r\,(1 - 2x^\ast) = 2 - r", color=ACCENT).scale(0.85
                       ).next_to(cases, DOWN, buff=0.4)
        self.play(Write(slope))

        # number line for f'(x*)
        nl = NumberLine(x_range=[-1.6, 1.2, 0.5], length=5, color=MUTED, include_numbers=True,
                        font_size=20, numbers_to_include=[-1, 0, 1]).next_to(slope, DOWN, buff=0.55)
        band = Line(nl.n2p(-1), nl.n2p(1), color=STABLE, stroke_width=8, stroke_opacity=0.5)
        cursor = always_redraw(lambda: Triangle(color=ACCENT, fill_opacity=1).scale(0.09).rotate(PI)
                               .next_to(nl.n2p(2 - r.get_value()), UP, buff=0.02))
        nl_lab = MathTex(r"f'(x^\ast)", font_size=26, color=ACCENT).next_to(nl, LEFT)
        self.say(r"With $x^\ast = 1 - 1/r$, the slope is $2 - r$. It leaves the stable zone "
                 r"$[-1, 1]$ exactly at $r = 3$.", anims=[Create(nl), FadeIn(band, nl_lab), FadeIn(cursor)])
        self.play(r.animate.set_value(3.0), run_time=3)
        self.wait(0.5)
        self.play(r.animate.set_value(3.2), run_time=2.5)
        self.say(r"Beyond $r = 3$, $x^\ast$ repels. But the orbit does not explode: "
                 r"it settles on a \emph{cycle of period 2}, alternating between two values.")
        self.play(FadeOut(VGroup(lin, cases, slope, nl, band, nl_lab)), FadeOut(cursor))
        self.remove(cursor)
        rl = always_redraw(lambda: r_label(r.get_value(), ts))
        ser = always_redraw(lambda: series(ts, r.get_value()))
        self.play(FadeIn(side), FadeIn(ser), FadeIn(rl))

        # --- f∘f
        f2 = always_redraw(lambda: parabola(ax, r.get_value(), color=ACCENT, k=2))
        f2l = MathTex(r"f\!\circ\! f", font_size=32, color=ACCENT).next_to(ax.c2p(0.98, 0.5), RIGHT, buff=0.1)
        self.say(r"A 2-cycle $a \to b \to a$ means $f(f(a)) = a$: the cycle points are fixed points "
                 r"of $f\circ f$, the rule applied twice.", anims=[Create(f2), FadeIn(f2l)])
        self.say(r"$f\circ f$ crosses the diagonal three times: the old $x^\ast$ (unstable) and the "
                 r"two points of the cycle.")
        # the seed of renormalisation
        rv = 3.2
        def f2v(x):
            return rv * (rv * x * (1 - x)) * (1 - rv * x * (1 - x))
        box = Square(side_length=ax.x_length * 0.42, color=FG, stroke_width=2
                     ).move_to(ax.c2p(0.5, f2v(0.5) + 0.04))
        self.play(Create(box))
        self.say(r"Look closely at the middle: $f\circ f$ looks like a \emph{small, upside-down copy} "
                 r"of $f$. Keep this in mind: it is the key to the whole story.", extra=1.0)
        self.play(FadeOut(box))

        # --- next doubling
        self.say(r"So the same reasoning applies to $f\circ f$: when \emph{its} slope at the cycle "
                 r"reaches $-1$, at $r = 1+\sqrt6 \approx 3.449$, the 2-cycle breaks into a 4-cycle.",
                 anims=[r.animate.set_value(R2)], run_time=3)
        self.play(FadeOut(f2), FadeOut(f2l))
        self.remove(f2)
        self.play(r.animate.set_value(3.5), run_time=2)
        self.say(r"Period 4\ldots and it keeps going. Where does this end?", extra=0.5)
        self.unsay()
        # leave a clean stage (static copies) for the hand-off
        end = cobweb_stage(3.5, with_fixed_point=False)
        self.remove(f, web, ser, rl, fp)
        self.add(end["f"], end["web"], end["ser"], end["rlab"])
        self.add(Dot(ax.c2p(fixed_point(3.5), fixed_point(3.5)), color=ORBIT, radius=0.08))
