"""Seq 6 — The quantum kicked rotor: spreading, then dynamical localization; exponential profile; lambda ~ D/hbar^2."""
from _common import *  # noqa
import json
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated

Q = FACTS["qkr"]
CL = json.loads((DATA / "cl_prof.json").read_text())
M = np.array(Q["m"])
AX = {"color": MUTED, "stroke_width": 1.5}
MR, FLOOR = 520, -7.0


def qcurve(ax, t):
    P = np.array(Q["prof"][str(t)])
    sel = np.abs(M) <= MR
    y = np.log10(np.maximum(P[sel], 10 ** FLOOR))
    return ax.plot_line_graph(M[sel] + MR, y - FLOOR, add_vertex_dots=False, line_color=ACCENT, stroke_width=3)


def ccurve(ax, t, bw=8):
    m = np.array(CL[str(t)])
    edges = np.arange(-MR, MR + bw, bw)
    h, _ = np.histogram(m, edges)
    c = (edges[:-1] + edges[1:]) / 2
    P = h / (m.size * bw)
    ok = P > 0
    y = np.where(ok, np.log10(np.where(ok, P, 1)), FLOOR)
    return ax.plot_line_graph(c + MR, np.maximum(y, FLOOR) - FLOOR, add_vertex_dots=False, line_color=ORBIT,
                              stroke_width=3)


class Quantum(Narrated):
    def construct(self):
        self.chapter(r"6 \,$\cdot$\, The quantum rotor")
        psi = MathTex(r"\psi(\theta) = \sum_m \psi_m\, e^{i m\theta}", r",\qquad p = \hbar\, m", font_size=40,
                      color=FG).move_to([0, 2.2, 0])
        self.say(r"Now make the rotor quantum: a molecule, or a cloud of cold atoms kicked by flashes of laser "
                 r"light. Its state is a wave $\psi(\theta)$ on the circle.", anims=[FadeIn(psi[0])])
        self.say(r"Its angular momentum is quantized: $p = \hbar m$, with $m$ an integer.", anims=[FadeIn(psi[1])])
        k1 = MathTex(r"\text{kick:}\quad \psi(\theta) \to e^{-ik\cos\theta}\,\psi(\theta)", font_size=38,
                     color=MAP)
        k2 = MathTex(r"\text{free turn:}\quad \psi_m \to e^{-i\hbar m^2/2}\,\psi_m", font_size=38, color=DIAG)
        ks = VGroup(k1, k2).arrange(DOWN, buff=0.35, aligned_edge=LEFT).next_to(psi, DOWN, buff=0.6)
        self.say(r"The kick multiplies the wave by a phase that depends on the angle; the free rotation, by a "
                 r"phase that depends on the momentum. That is the whole quantum map.", anims=[FadeIn(ks)])
        par = MathTex(r"K = k\hbar = 5,\qquad \hbar = 0.4,\qquad \psi = |m=0\rangle", font_size=36, color=FG
                      ).next_to(ks, DOWN, buff=0.5)
        self.say(r"Same classical strength $K = k\hbar = 5$ as in the random walk, with $\hbar = 0.4$ "
                 r"(quantum effects are strong when $\hbar$ is not small). Start at rest: $m = 0$.",
                 anims=[FadeIn(par)])
        self.play(FadeOut(VGroup(psi, ks, par)))
        ax = Axes(x_range=[0, 2 * MR, 100], y_range=[0, -FLOOR, 1], x_length=11.5, y_length=4.4, tips=False,
                  axis_config=AX).move_to([0, 0.2, 0])
        nums = VGroup(*[MathTex(str(v), font_size=22, color=MUTED).next_to(ax.c2p(v + MR, 0), DOWN, buff=0.12)
                        for v in (-400, -200, 0, 200, 400)],
                      *[MathTex(str(v), font_size=22, color=MUTED).next_to(ax.c2p(0, v - FLOOR), LEFT, buff=0.12)
                        for v in (-6, -4, -2)])
        ax.add(nums)
        xl = MathTex(r"m", font_size=30, color=FG).next_to(ax.c2p(2 * MR, 0), RIGHT, buff=0.15)
        yl = MathTex(r"\log_{10} P(m)", font_size=30, color=FG).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        tl = Tex(r"after 10 kicks", font_size=32, color=FG).move_to(ax.c2p(300 + MR, 6.5))
        leg = VGroup(Tex(r"classical ($20\,000$ rotors)", font_size=28, color=ORBIT),
                     Tex(r"quantum ($|\psi_m|^2$)", font_size=28, color=ACCENT)).arrange(DOWN, aligned_edge=LEFT,
                                                                                    buff=0.1)
        leg.move_to(ax.c2p(-330 + MR, 6.3))
        cc, qc = ccurve(ax, 10), qcurve(ax, 10)
        self.say(r"The momentum distribution after 10 kicks, in log scale. Red: classical rotors. Purple: the "
                 r"quantum wave (averaged over 24 runs).", anims=[Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(leg),
                                                                  FadeIn(tl), Create(cc), Create(qc)], run_time=2)
        for t, txt in ((50, r"At first, quantum and classical spread alike\ldots"),
                       (200, r"\ldots then the classical cloud keeps widening, while the quantum one slows down"),
                       (1000, r"\ldots and freezes. After 1000 kicks the classical rotors are far away; the wave "
                              r"has not moved since a few hundred kicks.")):
            c2, q2 = ccurve(ax, t), qcurve(ax, t)
            t2 = Tex(r"after %d kicks" % t, font_size=32, color=FG).move_to(tl)
            self.say(txt, anims=[Transform(cc, c2), Transform(qc, q2), Transform(tl, t2)], run_time=1.5)
        ex = MathTex(r"|\psi_m|^2 \propto e^{-|m|/\lambda}", font_size=40, color=ACCENT).move_to(ax.c2p(330 + MR, 5.0))
        self.say(r"Not a bell curve like the classical cloud: two straight lines in log scale, an exponential. "
                 r"The wave is \emph{localized} in momentum.", anims=[FadeIn(ex)])
        self.play(FadeOut(VGroup(ax, xl, yl, tl, leg, cc, qc, ex)))
        # <m^2>(t)
        m2c = np.array(Q["m2c"]); m2q = np.array(Q["m2q"])
        n = np.arange(1, m2c.size + 1)
        bx = Axes(x_range=[0, 1000, 200], y_range=[0, 80000, 20000], x_length=10.5, y_length=4.5, tips=False,
                  axis_config={**AX, "include_numbers": True, "font_size": 22}).move_to([0.3, 0.3, 0])
        bxl = MathTex(r"n", font_size=30, color=FG).next_to(bx.x_axis, RIGHT, buff=0.15)
        byl = MathTex(r"\langle m^2 \rangle", font_size=30, color=FG).next_to(bx, UP, buff=0.1).align_to(bx, LEFT)
        lc = bx.plot_line_graph(n[::4], m2c[::4], add_vertex_dots=False, line_color=ORBIT, stroke_width=3)
        lq = bx.plot_line_graph(np.arange(m2q.size)[::4], m2q[::4], add_vertex_dots=False, line_color=ACCENT,
                                stroke_width=3)
        tc = Tex(r"classical: grows forever", font_size=28, color=ORBIT).next_to(bx.c2p(700, 60000), LEFT)
        tq = Tex(r"quantum: saturates", font_size=28, color=ACCENT).next_to(bx.c2p(800, m2q[800]), UP, buff=0.2)
        self.say(r"The spread $\langle m^2\rangle$ tells the story: linear growth forever for the classical rotors, "
                 r"saturation for the quantum one.", anims=[Create(bx), FadeIn(bxl), FadeIn(byl),
                                                            Create(lc), Create(lq), FadeIn(tc), FadeIn(tq)],
                 run_time=3)
        self.say(r"This is \emph{dynamical localization} (Casati, Chirikov, Izrailev \& Ford, 1979): "
                 r"classically chaotic, quantum mechanically frozen.")
        self.play(FadeOut(VGroup(bx, bxl, byl, lc, lq, tc, tq)))
        rows = [[r"%.3f" % s["hbar"], r"%.1f" % s["D_m"], r"%.1f" % s["lam"], r"%.2f" % s["ratio"]]
                for s in FACTS["sweep"]]
        tab = MathTable(rows, col_labels=[MathTex(r"\hbar"), MathTex(r"D/\hbar^2"), MathTex(r"\lambda"),
                                          MathTex(r"\lambda \,/\, (D/\hbar^2)")],
                        include_outer_lines=False, line_config={"stroke_color": MUTED, "stroke_width": 1.2},
                        element_to_mobject_config={"font_size": 32}, v_buff=0.24, h_buff=0.7)
        tab.scale_to_fit_height(3.6).move_to([0, 0.6, 0])
        self.say(r"How wide is the frozen wave? Varying $\hbar$ at fixed $K = 5$: the width $\lambda$ follows the "
                 r"classical diffusion divided by $\hbar^2$, with a ratio between $0.7$ and $0.95$.",
                 anims=[FadeIn(tab)], run_time=1.5)
        self.say(r"Theory (Chirikov, Izrailev \& Shepelyansky) predicts $\lambda \approx D/\hbar^2$, up to "
                 r"fluctuations from run to run. The smaller $\hbar$, the later and wider the freeze, but it always "
                 r"comes.")
        self.unsay()
        self.play(FadeOut(VGroup(tab, self.chapter_tag)))
        self.chapter_tag = None
