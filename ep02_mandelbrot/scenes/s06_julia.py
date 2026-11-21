"""Seq 6 — Julia sets: one world per point. Tour, dust, theorem, mosaic, Tan Lei."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.fractals import julia, mandelbrot, colorize, julia_mosaic
from _stages import *

G = dict(GALLERY)


class Julia(Narrated):
    def construct(self):
        self.chapter(r"5 \,$\cdot$\, Part 1's cascade, seen from above", animate=False)
        self.chapter(r"6 \,$\cdot$\, Julia sets: one world per point")
        st = stage()
        cax, zax = st["cax"], st["zax"]
        self.play(FadeIn(Group(*st.values())), run_time=1.2)

        cr, ci, it = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(300)
        c = lambda: complex(cr.get_value(), ci.get_value())
        J = to_image(j_rgb(0j), RIGHT_C)
        cur = always_redraw(lambda: Dot(cpt(cax, c()), color=FG, radius=0.075).set_stroke(ORBIT, 3))
        crit = always_redraw(lambda: (lambda g: (g[0].set_stroke(opacity=0.25), g[1].set_opacity(0.9), g)[-1])(orbit_path(zax, orbit(c(), 0j, 30), FG)))
        self.say(r"So far we followed one orbit per $c$: the orbit of $0$. Now fix $c$, and colour \emph{every} "
                 r"starting point $z_0$ on the right by the same rule: cream if its orbit stays bounded.")
        self.add(J, st["zf"], cur)
        self.play(FadeIn(J), run_time=1)
        J.add_updater(lambda m: m.become(to_image(j_rgb(c(), maxit=int(it.get_value())), RIGHT_C)))
        self.say(r"The cream set is the \emph{filled Julia set} $K_c$. For $c = 0$ it is the unit disk: "
                 r"chapter 1, squaring keeps the inside, flings away the outside.")
        self.add(crit)
        self.say(r"The white dots: the orbit of $0$, the one that decides the colour of $c$ on the left.")

        name = Tex("", font_size=30)
        self.add(name)

        def stop(key, text, run_time=2.5, extra=0.3, label=None):
            nonlocal name
            v = G[key]
            new = Tex(label or key, font_size=30, color=ACCENT).next_to(RIGHT_C + PANEL_H / 2 * UP, DOWN, buff=0.15)
            new = VGroup(BackgroundRectangle(new, fill_opacity=0.8, buff=0.08), new)
            self.play(cr.animate.set_value(v.real), ci.animate.set_value(v.imag), FadeTransform(name, new),
                      run_time=run_time)
            name = new
            self.say(text, extra=extra)

        stop("cauliflower", r"$c = \tfrac14$, the cusp of the cardioid: the \emph{cauliflower}. Inside the cardioid, "
                            r"$K_c$ stays one round-ish blob.")
        stop("San Marco", r"$c = -\tfrac34$, where the cardioid meets the disk: pinched everywhere, "
                          r"the \emph{San Marco} set.")
        stop("basilica", r"$c = -1$, centre of the period-2 bulb: the \emph{basilica}. Its orbit of $0$ is the "
                         r"2-cycle $0 \to -1 \to 0$.")
        stop("Douady's rabbit", r"Centre of the $\tfrac13$ bulb: \emph{Douady's rabbit}. Three ears meet at every "
                                r"junction, and the dynamics rotates them by $\tfrac13$ of a turn — chapter 4.")
        stop("Siegel disk", r"The golden point of chapter 4: no cycle. Around a hidden centre, the orbits turn "
                            r"forever by an irrational angle: a \emph{Siegel disk}.")
        stop("dendrite", r"$c = i$, on the boundary: $0 \to i \to -1+i \to -i \to -1+i \ldots$ never returns to $0$. "
                         r"$K_c$ has no inside at all: a \emph{dendrite}, a tree of curves.", label=r"dendrite ($c = i$)")
        self.play(cr.animate.set_value(0.0), ci.animate.set_value(0.0), run_time=2)
        stop("airplane", r"Chapter 5's mini-Mandelbrot, $c \approx -1.7549$: the \emph{airplane}. Its orbit of $0$ "
                         r"is a 3-cycle, like the main period-3 bulb.", run_time=3)
        stop("dragon", r"Now step \emph{just outside} $M$: $c = -0.8 + 0.156i$. It looks solid\ldots", run_time=3, extra=0)
        self.say(r"\ldots but the orbit of $0$ escapes after 252 steps. Let the computer iterate longer: "
                 r"the cream evaporates. $K_c$ is a cloud of disconnected dust.",
                 anims=[it.animate.set_value(3000)], run_time=5, extra=0.5)
        it.set_value(300)
        stop("dust", r"Farther out, the dust is obvious: a \emph{Cantor set}, infinitely many points, no two connected.")

        # --- the theorem
        thm = MathTex(r"c \in M", r"\iff", r"K_c \text{ is connected}", font_size=40)
        sub = Tex(r"(Fatou, Julia, 1919)", font_size=24, color=MUTED).next_to(thm, DOWN, buff=0.12)
        box = VGroup(thm, sub).move_to([0, -1.9, 0])
        bb = BackgroundRectangle(box, fill_opacity=0.92, buff=0.18)
        self.say(r"This is the theorem behind the whole picture: $c$ is in $M$ exactly when its Julia set is in "
                 r"one piece.", anims=[FadeIn(bb), Write(thm), FadeIn(sub)], extra=0.3)
        self.say(r"Why the orbit of $0$? Because $0$ is the only \emph{critical point} of $z^2 + c$ "
                 r"($f'(0) = 0$), like $x = \tfrac12$ in Part 1. If it escapes, the Julia set shatters; if not, "
                 r"it holds together.", extra=0.8)
        self.play(FadeOut(VGroup(bb, thm, sub)))

        # --- the mosaic
        self.play(cr.animate.set_value(-1.0), ci.animate.set_value(0.0), FadeOut(name), run_time=2)
        J.clear_updaters()
        self.remove(crit, cur)
        w, h = panel_px()

        def mosaic(n):
            ny = max(1, round(n * (C_WIN[3] - C_WIN[2]) / (C_WIN[1] - C_WIN[0])))
            e = julia_mosaic(*C_WIN, w, h, n, ny, 120, 1.9)
            return to_image(colorize(e, 120), LEFT_C)

        mos = mosaic(6)
        self.say(r"One last picture. Draw, at each point $c$ of the left plane, a tiny copy of its Julia set\ldots",
                 anims=[FadeIn(mos)], run_time=1.5)
        for n in (12, 24, 48, 96):
            new = mosaic(n)
            self.play(FadeIn(new), run_time=1.6)
            self.remove(mos)
            mos = new
        self.say(r"\ldots the connected ones draw the Mandelbrot set. $M$ is an \emph{index} of all Julia sets: "
                 r"a map of every possible dynamics of $z^2 + c$.", extra=1.0)

        # --- Tan Lei
        self.play(FadeOut(mos), FadeIn(st["m"]))
        self.play(cr.animate.set_value(0.0), ci.animate.set_value(1.0), run_time=1)
        J.become(to_image(j_rgb(1j), RIGHT_C))
        cd = Dot(cpt(cax, 1j), color=FG, radius=0.075).set_stroke(ORBIT, 3)
        zd = Dot(cpt(zax, 1j), color=FG, radius=0.075).set_stroke(ORBIT, 3)
        self.play(FadeIn(cd), FadeIn(zd))
        zt = ValueTracker(0.0)
        Mi = to_image(m_rgb(), LEFT_C)
        self.add(Mi, st["cf"], cd)

        def wins(u, base):
            wd = (base[1] - base[0]) * (0.016 / (base[1] - base[0])) ** u
            hd = wd * (base[3] - base[2]) / (base[1] - base[0])
            cen0 = complex((base[0] + base[1]) / 2, (base[2] + base[3]) / 2)
            cen = cen0 + (1j - cen0) * min(1.0, u * 3)
            return cen.real - wd / 2, cen.real + wd / 2, cen.imag - hd / 2, cen.imag + hd / 2

        Mi.add_updater(lambda m: m.become(to_image(m_rgb(wins(zt.get_value(), C_WIN), maxit=1200, mode="adaptive"), LEFT_C)))
        J.add_updater(lambda m: m.become(to_image(j_rgb(1j, wins(zt.get_value(), Z_WIN), maxit=1200, mode="adaptive"), RIGHT_C)))
        cd.add_updater(lambda m: m.set_opacity(max(0, 1 - 3 * zt.get_value())))
        zd.add_updater(lambda m: m.set_opacity(max(0, 1 - 3 * zt.get_value())))
        self.say(r"A last surprise. Zoom into $M$ near $c = i$ (left), and into the Julia set of $c = i$ near "
                 r"the point $i$ (right)\ldots", anims=[zt.animate.set_value(1.0)], run_time=7, wait=0.3)
        Mi.clear_updaters(); J.clear_updaters()
        self.say(r"\ldots the same branching, up to a rotation (Tan Lei, 1990). Near such points, $M$ looks like "
                 r"the Julia set it indexes: the map resembles the territory.", extra=1.0)
        self.play(FadeOut(Group(Mi, J, cd, zd, *st.values())))
        self.unsay()
