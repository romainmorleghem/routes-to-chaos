"""Seq 3 — The main cardioid is Part 1's stability test; the period-2 disk."""
from _common import *  # noqa
import cmath
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _stages import *

CA = 0.2 + 0.35j
CB = -1.0 + 0.1j


def overlay(lines, size=32):
    g = VGroup(*[MathTex(t, font_size=size) for t in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    if g.width > PANEL_W - 0.4:
        g.scale_to_fit_width(PANEL_W - 0.4)
    g.move_to(RIGHT_C + (PANEL_H / 2 - g.height / 2 - 0.3) * DOWN)
    return VGroup(BackgroundRectangle(g, fill_opacity=0.92, buff=0.15), g)


class Cardioid(Narrated):
    def construct(self):
        st = stage()
        self.add(*st.values())
        cax, zax = st["cax"], st["zax"]
        self.chapter(r"2 \,$\cdot$\, Where does $0$ go?", animate=False)
        self.chapter(r"3 \,$\cdot$\, The cardioid is a stability test")

        cd = Dot(cpt(cax, CA), color=MAP, radius=0.08)
        path = orbit_path(zax, orbit(CA, 0j, 40), ORBIT)
        zs = (1 - cmath.sqrt(1 - 4 * CA)) / 2
        zsd = Dot(cpt(zax, zs), color=STABLE, radius=0.09)
        zsl = MathTex(r"z^\ast", font_size=30, color=STABLE).next_to(zsd, UR, buff=0.05)
        self.play(FadeIn(cd, scale=2))
        self.say(r"Take $c$ in the big central region: the orbit of $0$ settles on a \emph{fixed point} "
                 r"$z^\ast$, a point such that $z^{\ast 2} + c = z^\ast$.",
                 anims=[Create(path[0], lag_ratio=1), FadeIn(path[1], lag_ratio=1)], run_time=3)
        self.play(FadeIn(zsd, scale=2), FadeIn(zsl))
        ov = overlay([r"f_c'(z) = 2z", r"|f_c'(z^\ast)| = |2z^\ast| < 1 \;\Rightarrow\; \text{stable}"])
        self.say(r"Is it stable? Exactly the test of Part 1, chapter 2: near $z^\ast$ a small error is "
                 r"multiplied by $f_c'(z^\ast) = 2z^\ast$ at each step. Stable if $|2z^\ast| < 1$.",
                 anims=[FadeIn(ov[0]), Write(ov[1])], run_time=2, extra=0.5)
        self.play(FadeOut(path), FadeOut(cd))

        # --- the boundary: |2z*| = 1
        ov2 = overlay([r"2z^\ast = e^{i\theta}", r"c = z^\ast - z^{\ast 2} = \tfrac12 e^{i\theta} - \tfrac14 e^{2i\theta}"])
        self.say(r"The boundary of the stable region: $|2z^\ast| = 1$, i.e. $2z^\ast = e^{i\theta}$. "
                 r"Solve for $c$\ldots", anims=[FadeTransform(ov, ov2)], extra=0.3)
        th = ValueTracker(0.001)
        half = Circle(radius=0.5 * zax.x_length / (Z_WIN[1] - Z_WIN[0]), color=STABLE, stroke_width=2
                      ).move_to(cpt(zax, 0))
        hl = MathTex(r"|z| = \tfrac12", font_size=24, color=STABLE).next_to(half, DR, buff=-0.1)
        card = always_redraw(lambda: ParametricFunction(
            lambda t: cpt(cax, cmath.exp(1j * t) / 2 - cmath.exp(2j * t) / 4),
            t_range=[0, th.get_value()], color=ACCENT, stroke_width=4))
        cdot = always_redraw(lambda: Dot(cpt(cax, cmath.exp(1j * th.get_value()) / 2 - cmath.exp(2j * th.get_value()) / 4),
                                         color=ACCENT, radius=0.07))
        zdot = always_redraw(lambda: Dot(cpt(zax, cmath.exp(1j * th.get_value()) / 2), color=STABLE, radius=0.08))
        self.play(FadeOut(zsd), FadeOut(zsl), Create(half), FadeIn(hl))
        self.add(card, cdot, zdot)
        self.say(r"\ldots and let $\theta$ turn: while $z^\ast$ goes around the circle $|z| = \tfrac12$ (right), "
                 r"$c$ draws a \emph{cardioid} (left) — exactly the edge of the main body of $M$.",
                 anims=[th.animate.set_value(TAU)], run_time=6, extra=0.5)
        cm = Dot(cpt(cax, -0.75), color=FG, radius=0.07)
        cml = MathTex(r"c = -\tfrac34", font_size=28, color=FG).next_to(cm, DOWN, buff=0.15)
        self.play(th.animate.set_value(PI), run_time=1.5)
        self.say(r"At $\theta = \pi$: $c = -\tfrac34$. With $c = r/2 - r^2/4$ (Part 1's change of variables), "
                 r"that is $r = 3$: the very first period doubling, $r_1$.", anims=[FadeIn(cm), FadeIn(cml)])
        self.play(th.animate.set_value(TAU), run_time=1.5)

        # --- the 2-cycle disk
        self.play(FadeOut(VGroup(half, hl)), FadeOut(zdot), FadeOut(cdot))
        self.remove(zdot, cdot)
        cd2 = Dot(cpt(cax, CB), color=MAP, radius=0.08)
        p2 = orbit_path(zax, orbit(CB, 0j, 40), STABLE)
        self.play(FadeIn(cd2, scale=2))
        ov3 = overlay([r"z_1 z_2 = c + 1", r"(f_c \circ f_c)'(z_1) = 2z_1 \cdot 2z_2 = 4(c+1)",
                       r"\text{stable} \iff |c + 1| < \tfrac14"])
        self.say(r"Same test for the 2-cycle $z_1 \leftrightarrow z_2$. Its two points solve "
                 r"$z^2 + z + c + 1 = 0$, so their product is $c + 1$\ldots",
                 anims=[FadeTransform(ov2, ov3[:1] if False else ov3), Create(p2[0], lag_ratio=1),
                        FadeIn(p2[1], lag_ratio=1)], run_time=3)
        disk = Circle(radius=0.25 * cax.x_length / (C_WIN[1] - C_WIN[0]), color=DIAG, stroke_width=4
                      ).move_to(cpt(cax, -1))
        self.say(r"\ldots and the error after two steps is multiplied by $4(c+1)$. Stable inside the disk "
                 r"$|c+1| < \tfrac14$: the second bulb, exactly.", anims=[Create(disk)], extra=0.5)
        self.say(r"So the shape of $M$ is not arbitrary: each region is where one particular cycle is stable.")
        self.play(FadeOut(VGroup(ov3, disk, card, cm, cml, cd2, p2)))
        self.remove(card)
        self.unsay()
