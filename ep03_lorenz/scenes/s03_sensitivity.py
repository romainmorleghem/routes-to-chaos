"""Seq 3 — Sensitivity, measured: twins 1e-10 apart, log-error is a straight line, horizon law, spectrum."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.lorenz import trajectory
from _stages import project, comet, curve

SCR = dict(scale=0.105, screen=np.array([-3.7, 0.4, 0]))
LAM = FACTS["lyapunov"][0]


class Sensitivity(Narrated):
    def construct(self):
        self.chapter(r"3 \,$\cdot$\, How fast does it forget?")
        a0 = trajectory(np.array([1.0, 1.0, 1.0]), 20000, 0.005)[-1]
        b0 = a0 + np.array([1e-10, 0, 0])
        A = trajectory(a0, 8000, 0.005)
        B = trajectory(b0, 8000, 0.005)
        self.say(r"Everybody quotes the butterfly. Let us \emph{measure} it. Two starting points, "
                 r"$10^{-10}$ apart: a distance far below any instrument.")
        ax = Axes(x_range=[0, 40, 10], y_range=[-14, 2, 2], x_length=5.6, y_length=4.4, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_numbers": True, "font_size": 22}
                  ).move_to([3.3, 0.55, 0])
        ylab = MathTex(r"\log_{10} |\delta(t)|", font_size=28, color=FG).next_to(ax, UP, buff=0.15)
        xlab = MathTex(r"t", font_size=28, color=FG).next_to(ax.x_axis, RIGHT, buff=0.1)
        self.play(Create(ax), FadeIn(ylab), FadeIn(xlab))
        k = ValueTracker(2)
        t = np.arange(A.shape[0]) * 0.005
        d = np.log10(np.linalg.norm(A - B, axis=1) + 1e-300)
        live = always_redraw(lambda: VGroup(
            comet(A[max(0, int(k.get_value()) - 300):int(k.get_value()) + 1], color=DIAG, width=3, **SCR),
            comet(B[max(0, int(k.get_value()) - 300):int(k.get_value()) + 1], color=ORBIT, width=3, **SCR)))
        graph = always_redraw(lambda: ax.plot_line_graph(t[:int(k.get_value()) + 1:8],
                                                         d[:int(k.get_value()) + 1:8],
                                                         add_vertex_dots=False, line_color=MAP, stroke_width=2.5))
        self.add(live, graph)
        self.say(r"For a long time they are indistinguishable: one curve. Meanwhile, on the right, "
                 r"the logarithm of their distance climbs steadily\ldots",
                 anims=[k.animate(rate_func=linear).set_value(4200)], run_time=14, wait=0.3)
        self.say(r"\ldots until, around $t \approx 25$, they separate and live independent lives.",
                 anims=[k.animate(rate_func=linear).set_value(6000)], run_time=7, wait=0.5)
        line = ax.plot(lambda x: -10 + LAM * x / np.log(10), x_range=[0, 24], color=ACCENT, stroke_width=3)
        lam = MathTex(r"|\delta(t)| \approx \delta_0\, e^{\lambda t},\quad \lambda = %.3f" % LAM, font_size=34,
                      color=ACCENT).next_to(ax, DOWN, buff=0.45)
        self.say(r"A straight line on a log scale means exponential growth: the error is multiplied by $e$ "
                 r"every $1/\lambda$ units of time, and doubles every $\ln 2/\lambda \approx %.2f$." %
                 FACTS["doubling_time"], anims=[Create(line), Write(lam)], run_time=1.5)
        self.say(r"$\lambda$ is the \emph{Lyapunov exponent}: the same number as in Part 1, where we averaged "
                 r"$\ln|f'(x_n)|$ along an orbit. Here, averaged over the whole attractor.")
        self.remove(live)
        self.play(FadeOut(graph))
        # horizon law
        self.chapter(r"3 \,$\cdot$\, The prediction horizon")
        hz = MathTex(r"T_{\text{pred}} \approx \frac{1}{\lambda}\ln\frac{\text{tolerance}}{\delta_0}",
                     font_size=40, color=FG).move_to([-3.6, 1.2, 0])
        self.say(r"So how far ahead can we predict? Until the error reaches our tolerance:",
                 anims=[Write(hz)], run_time=1.5)
        lines = VGroup()
        for j, e in enumerate([-10, -11, -12, -13]):
            lines.add(ax.plot(lambda x, e=e: e + LAM * x / np.log(10), x_range=[0, (e * -1) * np.log(10) / LAM],
                              color=[ACCENT, STABLE, DIAG, MAP][j], stroke_width=2.5))
        gain = MathTex(r"\times 10 \text{ precision } \Rightarrow \ + \frac{\ln 10}{\lambda} = +%.2f"
                       % FACTS["horizon_gain_per_decade"], font_size=36, color=STABLE).move_to([-3.6, -0.6, 0])
        self.say(r"Measure ten times better, the line shifts right by only $\ln 10/\lambda$. A thousand times "
                 r"better buys three such steps.", anims=[Create(lines[1:], lag_ratio=0.5), Write(gain)],
                 run_time=3)
        self.say(r"Precision gets you \emph{logarithmically} little. That is the real content of the butterfly "
                 r"effect, and why weather forecasts stop at about two weeks.")
        self.play(FadeOut(VGroup(lines, line, hz, gain, lam)))
        # spectrum
        l1, l2, l3 = FACTS["lyapunov"]
        sp = MathTex(r"\lambda_1 = %.3f" % l1, r",\quad \lambda_2 = 0", r",\quad \lambda_3 = %.2f" % l3,
                     font_size=38, color=FG).move_to([-3.2, 1.3, 0])
        sm = MathTex(r"\lambda_1 + \lambda_2 + \lambda_3 = %.3f = \nabla\!\cdot\!\mathbf F" % (l1 + l2 + l3),
                     font_size=36, color=ACCENT).next_to(sp, DOWN, buff=0.45)
        self.say(r"In three dimensions there are three exponents: one direction stretches, one is neutral "
                 r"(along the flow), one is crushed.", anims=[Write(sp)], run_time=2)
        self.say(r"And their sum is exactly the volume contraction rate of Chapter 1: a check, computed "
                 r"independently, to four digits.", anims=[Write(sm)], run_time=1.5)
        self.unsay()
        self.play(FadeOut(VGroup(sp, sm, ax, ylab, xlab)))
