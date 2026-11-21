"""Seq 2 — Turning up the heat: rho from 0.5 to 28. Rest, steady rolls, transient chaos, Hopf, attractor."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.lorenz import fixed_points, jacobian, RHO_HOPF
from _stages import lorenz_points, curve, project, glow_image, TRAIL

STARTS = [(-8, 6, 12), (9, -4, 30), (2, 12, 5), (-12, -10, 40), (5, 5, 20), (-3, -9, 8)]
SCR = dict(scale=0.095, screen=np.array([0.6, -0.35, 0]))


def rho_bar():
    nl = NumberLine(x_range=[0, 30, 5], length=5.2, color=MUTED, include_numbers=True,
                    font_size=22).to_corner(UR, buff=0.55).shift(0.25 * DOWN)
    lab = MathTex(r"\rho", font_size=34, color=MAP).next_to(nl, LEFT, buff=0.2)
    ticks = VGroup()
    for v, c in [(1, STABLE), (13.93, ORBIT), (24.06, ORBIT), (RHO_HOPF, ACCENT)]:
        ticks.add(Line(nl.n2p(v) + 0.12 * UP, nl.n2p(v) + 0.12 * DOWN, color=c, stroke_width=3))
    return nl, lab, ticks


def fp_dots(r, z_center=25.0):
    g = VGroup()
    for i, p in enumerate(fixed_points(r)):
        ev = np.linalg.eigvals(jacobian(p, r))
        stable = np.all(ev.real < 0)
        g.add(Dot(project(p, **SCR, center=np.array([0, 0, z_center]))[0], radius=0.09,
                  color=STABLE if stable else ORBIT))
    return g


class Journey(Narrated):
    def construct(self):
        self.chapter(r"2 \,$\cdot$\, Turning up the heat")
        nl, lab, ticks = rho_bar()
        rv = ValueTracker(0.5)
        mark = always_redraw(lambda: Triangle(color=MAP, fill_opacity=1).scale(0.09).rotate(PI)
                             .move_to(nl.n2p(rv.get_value()) + 0.2 * UP))
        val = always_redraw(lambda: MathTex(r"\rho = %.2f" % rv.get_value(), font_size=30, color=MAP)
                            .next_to(nl, DOWN, buff=0.45))
        self.play(FadeIn(nl), FadeIn(lab), FadeIn(mark), FadeIn(val))
        self.say(r"$\rho$ is the heating, the knob of this episode, exactly like $r$ in Part 1. "
                 r"($\sigma = 10$ and $\beta = 8/3$ stay fixed.) Let's turn it up slowly.")

        def bundle(r, T, zc=25.0, skip=0.0, opacity=0.9):
            g = VGroup()
            for j, s in enumerate(STARTS):
                P = lorenz_points(s, T=T, dt=0.004, r=r, skip=skip)
                g.add(curve(P, width=2.0, colors=TRAIL[j % 4], opacity=opacity, **SCR,
                            center=np.array([0, 0, zc])))
            return g

        b = bundle(0.5, 8, zc=20)
        d = fp_dots(0.5, 20)
        self.say(r"$\rho = 0.5$: no convection. Wherever it starts, the fluid comes to rest: "
                 r"every trajectory falls into the origin.", anims=[Create(b, lag_ratio=0.1), FadeIn(d)],
                 run_time=4)
        self.play(FadeOut(b), FadeOut(d), rv.animate.set_value(10), run_time=1.5)
        self.add(ticks[0])
        b = bundle(10, 12, zc=20)
        d = fp_dots(10, 20)
        self.say(r"At $\rho = 1$ rest becomes unstable and two new equilibria $C_\pm$ appear: steady rolls, "
                 r"turning one way or the other. The same event as $r = 1$ in Part 1.",
                 anims=[Create(b, lag_ratio=0.1), FadeIn(d)], run_time=4)
        self.say(r"Trajectories now spiral into $C_+$ or $C_-$. Which one depends on where they start, "
                 r"but the outcome is boring and predictable.")
        self.play(FadeOut(b), FadeOut(d), rv.animate.set_value(22), run_time=1.5)
        self.add(ticks[1])
        P = lorenz_points((-3.0, -9.0, 8.0), T=60, dt=0.004, r=22)
        tr = curve(P, width=1.6, **SCR)
        d = fp_dots(22)
        self.say(r"Past $\rho \approx 13.93$ something new appears: trajectories wander chaotically, "
                 r"sometimes for a long time\ldots", anims=[FadeIn(d), Create(tr)], run_time=9, wait=0.5)
        self.say(r"\ldots before settling into a roll anyway. \emph{Transient chaos}: the strange set is "
                 r"already there, but it is still a trap with an exit.")
        self.play(FadeOut(tr), FadeOut(d), rv.animate.set_value(RHO_HOPF), run_time=1.5)
        self.add(ticks[2], ticks[3])
        eq = MathTex(r"\rho_H = \frac{\sigma(\sigma+\beta+3)}{\sigma-\beta-1} = 24.74", font_size=36,
                     color=ACCENT).to_corner(UL, buff=0.6).shift(0.6 * DOWN)
        self.say(r"At $\rho_H$ the rolls themselves become unstable: their eigenvalues cross into the right "
                 r"half-plane (a Hopf bifurcation).", anims=[Write(eq)], run_time=1.5)
        self.say(r"(Between 24.06 and 24.74, the rolls and the chaos coexist: the same heating, two possible "
                 r"climates.)")
        self.play(FadeOut(eq), rv.animate.set_value(28), run_time=1.5)
        ev = np.linalg.eigvals(jacobian(fixed_points(28)[1], 28))
        ev = sorted(ev, key=lambda e: e.imag)
        evt = MathTex(r"\text{eigenvalues at } C_\pm:\ \ %.2f,\ \ %.3f \pm %.2f\,i" % (ev[1].real, ev[2].real,
                      ev[2].imag), font_size=30, color=FG).to_corner(UL, buff=0.6).shift(0.5 * DOWN)
        trc = curve(lorenz_points(T=40, dt=0.004, skip=2), width=1.3, opacity=0.8, **SCR)
        d = fp_dots(28)
        self.say(r"$\rho = 28$. Nothing is stable any more: the origin and both rolls repel. "
                 r"Near $C_\pm$, a slow outward spiral (real part $+0.094$), fast attraction elsewhere.",
                 anims=[FadeIn(evt), FadeIn(d), Create(trc)], run_time=8, wait=1.0)
        self.say(r"Repelled by everything, yet confined in a bounded region (and squeezed to zero volume): "
                 r"the motion has nowhere to settle. It must be chaotic.")
        self.unsay()
        self.play(FadeOut(VGroup(nl, lab, mark, val, ticks, evt, d)), trc.animate.set_stroke(opacity=0.35))
        self.play(FadeOut(trc))
