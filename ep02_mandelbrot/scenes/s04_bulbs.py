"""Seq 4 — Period map, rotation numbers, antennas, bulb sizes, Farey and Fibonacci."""
from _common import *  # noqa
import cmath
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.fractals import PERIOD_COLORS
from _stages import *

B = {(b["p"], b["q"]): b for b in BULBS["bulbs"]}


def bc(p, q):
    return complex(*B[(p, q)]["centre"])


def label_pos(p, q, extra=0.07):
    b = B[(p, q)]
    root, cen = complex(*b["root"]), complex(*b["centre"])
    u = (cen - root) / abs(cen - root)
    return cen + u * (b["size"] + extra)


class Bulbs(Narrated):
    def cycle_picture(self, zax, c, q, color):
        alpha = (1 - cmath.sqrt(1 - 4 * c)) / 2
        zs = orbit(c, 0j, 400)[-q:]
        # order the cycle in time, starting from the point closest to 0
        k = int(np.argmin([abs(z) for z in zs]))
        cyc = [zs[(k + i) % q] for i in range(q)]
        a = Circle(radius=0.07, color=ORBIT, stroke_width=3).move_to(cpt(zax, alpha))
        al = MathTex(r"\alpha", font_size=26, color=ORBIT).next_to(a, DL, buff=0.05)
        rays = VGroup(*[DashedLine(cpt(zax, alpha), cpt(zax, z), color=MUTED, stroke_width=1.5) for z in cyc])
        edges = VGroup(*[Arrow(cpt(zax, cyc[i]), cpt(zax, cyc[(i + 1) % q]), buff=0.08, color=color,
                               stroke_width=3, max_tip_length_to_length_ratio=0.08) for i in range(q)])
        dots = VGroup(*[Dot(cpt(zax, z), color=color, radius=0.07) for z in cyc])
        return VGroup(rays, edges, dots, a, al)

    def construct(self):
        st = stage()
        self.add(*st.values())
        cax, zax = st["cax"], st["zax"]
        zz = panel_axes((-1.1, 1.1, -0.9167, 0.9167), RIGHT_C)      # zoom x2.2 on the dynamical plane
        zlab = Tex(r"zoom $\times 2.2$", font_size=22, color=MUTED).next_to(RIGHT_C + PANEL_W / 2 * RIGHT + PANEL_H / 2 * DOWN, UL, buff=0.1)
        self.chapter(r"3 \,$\cdot$\, The cardioid is a stability test", animate=False)
        self.chapter(r"4 \,$\cdot$\, Bulbs, rotations and fractions")

        # --- period map
        pm = to_image(m_rgb(periods=True), LEFT_C)
        leg = legend()
        self.add(pm, st["cf"])
        pm.set_opacity(0)
        self.say(r"Colour the inside of $M$ by the \emph{period} of the cycle that the orbit of $0$ falls into: "
                 r"1 in the cardioid, 2 in the disk, and a new period in every bulb.",
                 anims=[pm.animate.set_opacity(1), FadeIn(leg)], run_time=2)
        self.remove(st["m"])

        # --- rotation numbers
        q3 = bc(1, 3)
        cd = Dot(cpt(cax, q3), color=FG, radius=0.07)
        pic = self.cycle_picture(zz, q3, 3, ManimColor(PERIOD_COLORS[2] / 255))
        self.play(FadeIn(cd, scale=2), FadeIn(zlab))
        self.say(r"Pick the bulb attached one third of the way around the cardioid. The orbit of $0$ falls into a "
                 r"cycle of period 3\ldots", anims=[FadeIn(pic[3:]), Create(pic[2])])
        self.say(r"\ldots which turns around the (now unstable) fixed point $\alpha$ by $\tfrac13$ of a turn "
                 r"at each step.", anims=[Create(pic[0]), Create(pic[1], lag_ratio=0.5)], run_time=2, extra=0.3)
        q5 = bc(2, 5)
        cd5 = Dot(cpt(cax, q5), color=FG, radius=0.07)
        pic5 = self.cycle_picture(zz, q5, 5, ManimColor(PERIOD_COLORS[4] / 255))
        self.play(FadeOut(pic), FadeOut(cd), FadeIn(cd5, scale=2))
        self.say(r"The bulb at $\tfrac25$ of a turn: period 5, and each step jumps $\tfrac25$ of a turn — "
                 r"the cycle draws a pentagram.", anims=[FadeIn(pic5[3:]), Create(pic5[2]), Create(pic5[0]),
                                                        Create(pic5[1], lag_ratio=0.5)], run_time=3, extra=0.3)
        rule = MathTex(r"\text{bulb at angle } \tfrac{p}{q} \text{ of a turn} \;\Rightarrow\; "
                       r"\text{period } q,\ \text{rotation } \tfrac{p}{q}", font_size=30)
        rule.scale_to_fit_width(PANEL_W - 0.4).move_to(RIGHT_C + 2.1 * DOWN)
        rbg = BackgroundRectangle(rule, fill_opacity=0.92, buff=0.12)
        self.say(r"In general: the bulb attached at $\tfrac pq$ of a turn has period $q$, and its cycle rotates "
                 r"by $\tfrac pq$ (checked numerically for every $q \le 13$).", anims=[FadeIn(rbg), Write(rule)])
        self.play(FadeOut(pic5), FadeOut(VGroup(rbg, rule)), FadeOut(zlab))

        # --- antenna: zoom into the 2/5 bulb
        b = B[(2, 5)]
        root = complex(*b["root"])
        u = (q5 - root) / abs(q5 - root)
        tgt = q5 + u * 0.06          # frames the bulb and its 5-spoke junction (checked offline)
        zt = ValueTracker(0.0)
        w0 = C_WIN[1] - C_WIN[0]
        w1 = 0.2

        def win(t):
            w = w0 * (w1 / w0) ** t
            h = w * (C_WIN[3] - C_WIN[2]) / w0
            c0 = complex((C_WIN[0] + C_WIN[1]) / 2, 0)
            cen = c0 + (tgt - c0) * (1 - (w / w0 - w1 / w0) / (1 - w1 / w0)) if t > 0 else c0
            return (cen.real - w / 2, cen.real + w / 2, cen.imag - h / 2, cen.imag + h / 2)

        zm = to_image(m_rgb(win(0), periods=True), LEFT_C)
        self.remove(pm)
        self.add(zm, st["cf"])
        self.bring_to_front(cd5)
        cd5.add_updater(lambda m: m.set_opacity(0))
        zm.add_updater(lambda m: m.become(to_image(m_rgb(win(zt.get_value()), maxit=250, periods=True), LEFT_C)))
        self.say(r"Zoom on it. A second way to read the period: its \emph{antenna} branches into exactly 5 spokes.",
                 anims=[zt.animate.set_value(1.0)], run_time=4, extra=1.0)
        self.say(r"Count the spokes, read the period. Small $q$, big bulb: its size is close to "
                 r"$\sin(\pi p/q)/q^2$ (within 2\% here).", anims=[zt.animate.set_value(0.0)], run_time=3)
        zm.clear_updaters()
        cd5.clear_updaters()
        self.remove(cd5)
        self.add(pm)
        self.remove(zm)
        self.bring_to_front(st["cf"])

        # --- Farey
        def lab(p, q, color=FG, size=24):
            t = MathTex(rf"\tfrac{{{p}}}{{{q}}}", font_size=size, color=color).move_to(cpt(cax, label_pos(p, q)))
            return VGroup(BackgroundRectangle(t, fill_opacity=0.85, buff=0.05), t)

        l2, l3 = lab(1, 2), lab(1, 3)
        l2.shift(0.25 * UP)
        self.say(r"Now compare sizes. Between the bulbs $\tfrac13$ and $\tfrac12$, which one is the largest?",
                 anims=[FadeIn(l2), FadeIn(l3)])
        l25 = lab(2, 5, ACCENT, 26)
        far = MathTex(r"\frac13 \oplus \frac12 = \frac{1+1}{3+2} = \frac25", font_size=40, color=FG
                      ).move_to(RIGHT_C + 1.3 * UP)
        self.say(r"It is $\tfrac25$: add the numerators, add the denominators. This \emph{Farey sum} predicts "
                 r"the largest bulb between any two neighbours.", anims=[FadeIn(l25, scale=1.5), Write(far)], extra=0.3)
        l38, l37 = lab(3, 8, ACCENT, 20), lab(3, 7, ACCENT, 20)
        far2 = VGroup(MathTex(r"\frac13 \oplus \frac25 = \frac38", font_size=34),
                      MathTex(r"\frac25 \oplus \frac12 = \frac37", font_size=34)).arrange(DOWN, buff=0.3
                      ).next_to(far, DOWN, buff=0.4)
        self.say(r"Again: between $\tfrac13$ and $\tfrac25$ the largest is $\tfrac38$; between $\tfrac25$ "
                 r"and $\tfrac12$ it is $\tfrac37$ (verified numerically).",
                 anims=[FadeIn(l38), FadeIn(l37), Write(far2)], extra=0.3)

        # --- Fibonacci and the golden point
        self.play(FadeOut(VGroup(far, far2, l37)))
        l513 = lab(5, 13, ACCENT, 18)
        fib = MathTex(r"\tfrac12,\ \tfrac13,\ \tfrac25,\ \tfrac38,\ \tfrac5{13},\ \ldots \;\to\; "
                      r"\tfrac{1}{\varphi^2} \approx 0.382", font_size=34).move_to(RIGHT_C + 1.3 * UP)
        per = Tex(r"periods $2, 3, 5, 8, 13, \ldots$: Fibonacci", font_size=30, color=MUTED).next_to(fib, DOWN, buff=0.3)
        self.say(r"Keep taking the Farey sum of the last two: $\tfrac12, \tfrac13, \tfrac25, \tfrac38, \tfrac5{13}\ldots$ "
                 r"The periods are the Fibonacci numbers.", anims=[FadeIn(l513), Write(fib), FadeIn(per)], extra=0.3)
        g = cardioid(1 - PHI)
        star = Star(n=5, outer_radius=0.13, color=ACCENT, fill_opacity=1).move_to(cpt(cax, g))
        self.say(r"These bulbs close in on one point of the cardioid, at a golden-ratio angle. There, no cycle "
                 r"at all — keep this point in mind for chapter 6.", anims=[FadeIn(star, scale=2)], extra=0.5)
        self.play(FadeOut(VGroup(l2, l3, l25, l38, l513, fib, per, star)))
        self.unsay()
        self.leg = leg
