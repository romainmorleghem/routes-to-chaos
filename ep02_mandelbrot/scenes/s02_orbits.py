"""Seq 2 — Two planes. The orbit of 0, the escape lemma, the definition of M, building M."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _stages import *

CA, CB, CC = 0.2 + 0.35j, -1.0 + 0.1j, 0.4 + 0.4j


class Orbits(Narrated):
    def construct(self):
        self.chapter(r"1 \,$\cdot$\, Squaring in the plane", animate=False)
        self.chapter(r"2 \,$\cdot$\, Where does $0$ go?")
        st = stage(with_m=False)
        cax, zax = st["cax"], st["zax"]
        self.play(FadeIn(VGroup(cax, zax, st["cf"], st["zf"])), FadeIn(st["tit"]))
        self.say(r"From now on, two planes side by side. On the left, the parameter $c$: which rule we use. "
                 r"On the right, the plane where the orbit $z_0, z_1, z_2, \ldots$ lives.", extra=0.5)
        z0 = Dot(cpt(zax, 0), color=FG, radius=0.06)
        z0l = MathTex("z_0 = 0", font_size=26, color=FG).next_to(z0, DL, buff=0.05)
        self.say(r"We always start from $z_0 = 0$ (we'll see why in chapter 6).", anims=[FadeIn(z0), FadeIn(z0l)])

        def show(c, text, color=ORBIT, n=40, extra=0.0):
            cd = Dot(cpt(cax, c), color=MAP, radius=0.08)
            cl = MathTex(rf"c = {c.real:+.2f} {c.imag:+.2f}i".replace("+", "", 1) if c.real >= 0 else
                         rf"c = {c.real:.2f} {c.imag:+.2f}i", font_size=26, color=MAP).next_to(cd, UR, buff=0.05)
            zs = orbit(c, 0j, n)
            path = orbit_path(zax, zs, color)
            self.play(FadeIn(cd, scale=2), FadeIn(cl))
            self.say(text, anims=[Create(path[0], lag_ratio=1), FadeIn(path[1], lag_ratio=1)], run_time=4, extra=extra)
            return VGroup(cd, cl, path)

        g1 = show(CA, r"For this $c$, the orbit of $0$ spirals into a single point: it settles down.")
        self.play(g1.animate.set_opacity(0.25))
        g2 = show(CB, r"For this one, it ends up jumping back and forth between two points: a cycle of period 2.",
                  color=STABLE)
        self.play(g2.animate.set_opacity(0.25))
        g3 = show(CC, r"And for this one, after a few hesitations, it flies off to infinity.", color=ACCENT, n=12)

        # --- escape lemma
        circ = Circle(radius=2 * zax.x_length / (Z_WIN[1] - Z_WIN[0]), color=DIAG, stroke_width=2
                      ).move_to(cpt(zax, 0))
        lem = VGroup(MathTex(r"|z| > 2,\ |z| \ge |c|", font_size=32),
                     MathTex(r"\Rightarrow\ |z^2 + c| \ \ge\ |z|^2 - |c| \ \ge\ |z|\,(|z| - 1)\ >\ |z|", font_size=32)
                     ).arrange(DOWN, aligned_edge=LEFT)
        lem.scale_to_fit_width(PANEL_W - 0.5).move_to(RIGHT_C + 1.75 * DOWN)
        lbg = BackgroundRectangle(lem, fill_opacity=0.9, buff=0.15)
        self.say(r"A simple test tells them apart: once an orbit leaves the disk of radius $2$, it can never "
                 r"come back.", anims=[Create(circ)])
        self.say(r"Indeed, outside that disk each step multiplies the distance to $0$ by more than $|z| - 1 > 1$: "
                 r"the orbit runs away faster and faster.", anims=[FadeIn(lbg), Write(lem)], run_time=2, extra=1.0)
        self.play(FadeOut(VGroup(lbg, lem, g1, g2, g3)))

        # --- definition and construction of M
        defi = MathTex(r"M = \{\, c \in \mathbb{C} \;:\; \text{the orbit of } 0 \text{ stays bounded} \,\}",
                       font_size=36, color=FG).move_to([0, -2.0, 0])
        dbg = BackgroundRectangle(defi, fill_opacity=0.9, buff=0.15)
        self.say(r"Now colour every $c$ on the left: cream if the orbit of $0$ stays bounded, and a colour "
                 r"that says how fast it escapes otherwise.", anims=[FadeIn(dbg), Write(defi)])
        rgb = m_rgb()
        W = rgb.shape[0]
        t = ValueTracker(0.0)
        bg = np.array([14, 17, 22], np.uint8)

        def partial():
            k = int(t.get_value() * W)
            out = rgb.copy()
            out[k:] = bg
            return to_image(out, LEFT_C)

        img = partial()
        self.add(img)
        self.bring_to_front(st["cf"], dbg, defi)
        img.add_updater(lambda m: m.become(partial()))
        self.say(r"The cream region is the \emph{Mandelbrot set} $M$ (1980): the set of rules "
                 r"for which $0$ never escapes.", anims=[t.animate.set_value(1.0)], run_time=6, wait=0.5)
        img.clear_updaters()
        self.play(FadeOut(VGroup(dbg, defi)))
        self.say(r"Two deep facts: $M$ is all in one piece (Douady \& Hubbard, 1982), and its boundary is so "
                 r"wrinkled that it has dimension $2$ (Shishikura, 1998).")
        self.say(r"Even its area is unknown: about $1.5066$. Yet everything in it follows from $z^2 + c$.")
        self.play(FadeOut(VGroup(z0, z0l, circ)))
        self.unsay()
