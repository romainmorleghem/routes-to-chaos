"""Seq 7 — Why: the hidden disordered crystal (Fishman-Grempel-Prange), experiment, quantum resonance."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated

OMEGA = 0.7
MS = np.arange(-24, 25)


def sites(hbar, y0=0.6, w=11.5, h=1.3, col=MAP):
    T = np.tan(0.5 * (OMEGA - hbar * MS ** 2 / 2))
    T = np.clip(T, -3, 3) / 3 * h
    dx = w / (MS.size - 1)
    g = VGroup()
    for i, t in enumerate(T):
        x = -w / 2 + i * dx
        g.add(Line([x, y0, 0], [x, y0 + t, 0], color=col, stroke_width=5))
    base = Line([-w / 2 - 0.2, y0, 0], [w / 2 + 0.2, y0, 0], color=MUTED, stroke_width=1.5)
    return VGroup(base, g)


class Anderson(Narrated):
    def construct(self):
        self.chapter(r"7 \,$\cdot$\, Why: a hidden crystal")
        chain = VGroup(*[Dot([x, 0.6, 0], radius=0.06, color=FG) for x in np.linspace(-5.75, 5.75, MS.size)])
        hop = VGroup(*[CurvedArrow([x, 0.75, 0], [x + 0.24, 0.75, 0], color=DIAG, tip_length=0.08)
                       for x in np.linspace(-5.75, 5.5, 12)])
        ml = MathTex(r"m = -24 \quad \cdots \quad 0 \quad \cdots \quad 24", font_size=30, color=MUTED
                     ).move_to([0, -1.05, 0])
        self.say(r"Why does the wave stop? Fishman, Grempel \& Prange (1982) found an exact rewriting: the rotor "
                 r"behaves like an electron hopping along a chain of sites $m$\ldots",
                 anims=[FadeIn(chain, lag_ratio=0.02), FadeIn(ml)], run_time=2)
        T = MathTex(r"T_m = \tan\!\Big(\tfrac12\big(\omega - \tfrac{\hbar m^2}{2}\big)\Big)", font_size=40,
                    color=MAP).move_to([0, 2.6, 0])
        s1 = sites(0.4)
        self.say(r"\ldots where site $m$ has energy $T_m$. With $\hbar = 0.4$, these energies jump around as if "
                 r"they were random: a disordered crystal.", anims=[Write(T), FadeOut(chain), FadeIn(s1)],
                 run_time=2)
        env = FunctionGraph(lambda x: 0.6 - 2.2 * np.exp(-abs(x) / 1.4), x_range=[-5.75, 5.75],
                            color=ACCENT, stroke_width=4)
        envl = MathTex(r"|\psi_m| \sim e^{-|m|/2\lambda}", font_size=34, color=ACCENT).move_to([3.6, -1.3, 0])
        self.say(r"In a disordered chain, waves scattered by the irregular sites interfere destructively and stay "
                 r"trapped: Anderson localization (1958). Here nobody added disorder: chaos made it.",
                 anims=[Create(env), FadeIn(envl)], run_time=2)
        self.say(r"And it was seen: Moore, Robinson, Bharucha, Sundaram \& Raizen (1995) kicked cold sodium atoms "
                 r"with pulses of a standing light wave, and measured exactly this exponential momentum profile.")
        T2 = MathTex(r"\hbar = 4\pi:\quad e^{-i\hbar m^2/2} = e^{-2\pi i m^2} = 1", font_size=40, color=STABLE
                     ).move_to(T)
        s2 = sites(4 * np.pi, col=STABLE)
        self.say(r"Now choose $\hbar = 4\pi$. The free phases all become 1, and every site has the same energy: "
                 r"a perfect crystal, with nothing to scatter the wave.",
                 anims=[Transform(T, T2), Transform(s1, s2), FadeOut(env), FadeOut(envl)], run_time=2)
        self.play(FadeOut(VGroup(T, s1, ml)))
        r = np.array(FACTS["resonance"]["m2"]); n = np.arange(r.size)
        q = np.array(FACTS["qkr"]["m2q"])[:201]
        ax = Axes(x_range=[0, 200, 50], y_range=[0, 20000, 5000], x_length=10.5, y_length=4.4, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 1.5, "include_numbers": True, "font_size": 22}
                  ).move_to([0.3, 0.4, 0])
        xl = MathTex(r"n", font_size=30, color=FG).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex(r"\langle m^2\rangle", font_size=30, color=FG).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        dots = VGroup(*[Dot(ax.c2p(i, r[i]), radius=0.045, color=STABLE) for i in range(0, 201, 8)])
        th = ax.plot(lambda x: x * x / 2, x_range=[0, 200], color=STABLE, stroke_width=2)
        lt = MathTex(r"\hbar = 4\pi,\ k = 1:\ \langle m^2\rangle = \tfrac{k^2 n^2}{2}", font_size=32, color=STABLE
                     ).next_to(ax.c2p(120, 15000), LEFT)
        lq = ax.plot_line_graph(n, q, add_vertex_dots=False, line_color=ACCENT, stroke_width=3)
        llq = MathTex(r"\hbar = 0.4,\ k = 12.5:\ \text{localized}", font_size=32, color=ACCENT).next_to(ax.c2p(200, q[200]),
                                                                                       UL, buff=0.1)
        self.say(r"The wave then accelerates without limit: $\langle m^2 \rangle = k^2 n^2/2$ exactly (dots: "
                 r"simulation with $k = 1$). A \emph{quantum resonance}, faster than any random walk.",
                 anims=[Create(ax), FadeIn(xl), FadeIn(yl), Create(th), FadeIn(dots, lag_ratio=0.1), FadeIn(lt),
                        Create(lq), FadeIn(llq)], run_time=3)
        self.say(r"$\hbar/4\pi$ rational: resonance. Irrational: localization. Once again, arithmetic draws "
                 r"the line, as it did for the island chains and the golden curve.")
        self.unsay()
        self.play(FadeOut(VGroup(ax, xl, yl, dots, th, lt, lq, llq, self.chapter_tag)))
        self.chapter_tag = None
