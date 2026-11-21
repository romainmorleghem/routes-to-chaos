"""Seq 0 — Cold open: a kicked rod, its stroboscopic portrait (Part 3's teaser), title."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT
from common.narrative import Narrated
from _viz import portrait, Frame

K0, TH0, P0 = 1.2, 2.3, 0.35
PIV, R = np.array([-3.9, 0.35, 0]), 1.75


def kicks(n):
    th, p = [TH0], [P0]
    for _ in range(n):
        p.append(p[-1] + K0 * np.sin(th[-1]))
        th.append(th[-1] + p[-1])
    return np.array(th), np.array(p)


class ColdOpen(Narrated):
    def construct(self):
        N = 16
        TH, PP = kicks(N)
        T = ValueTracker(0.0)

        def angle(t):
            n = min(int(np.floor(t)), N - 1)
            return TH[n] + PP[n + 1] * (t - n) if t >= 0 else TH[0]

        ring = DashedVMobject(Circle(radius=R, color=MUTED, stroke_width=1.5).move_to(PIV), num_dashes=60)
        piv = Dot(PIV, color=FG, radius=0.07)

        def rod():
            t = T.get_value()
            a = angle(t)
            tip = PIV + R * np.array([np.sin(a), np.cos(a), 0])
            hot = (t - np.floor(t)) < 0.12 and t > 0.5
            col = MAP if hot else FG
            g = VGroup(Line(PIV, tip, color=col, stroke_width=6), Dot(tip, radius=0.13, color=col))
            if hot:
                g.add(Circle(radius=0.32, color=MAP, stroke_width=3).move_to(tip))
            return g
        live = always_redraw(rod)
        self.say(r"Part 3 ended with a question: can chaos survive without friction? Here is the simplest "
                 r"system to test it.", anims=[FadeIn(ring), FadeIn(piv), FadeIn(live)])
        fr = Frame(4.9, 4.9, center=(2.9, 0.45, 0), fs=24)

        def dots():
            n = int(np.floor(T.get_value()))
            g = VGroup()
            for i in range(min(n, N) + 1):
                th = TH[i] % (2 * np.pi)
                p = (PP[i] + np.pi) % (2 * np.pi) - np.pi
                g.add(Dot(fr.c2p(th, p), radius=0.06, color=ORBIT))
            return g
        pts = always_redraw(dots)
        self.say(r"A rod turns freely on an axle. Once per second it gets a brief kick, like a flash of gravity: "
                 r"strong when the rod is horizontal, zero when it is vertical.",
                 anims=[T.animate(rate_func=linear).set_value(3.0)], run_time=6, wait=0)
        self.play(FadeIn(fr), run_time=0.6)
        self.add(pts)
        self.say(r"Between kicks it spins at constant speed. Mark its angle $\theta$ and speed $p$ at each kick: "
                 r"the speed jumps up, down, with no visible pattern.",
                 anims=[T.animate(rate_func=linear).set_value(float(N))], run_time=13, wait=0.5)
        im = portrait(0.971635, 4.9, 4.9, n=1500).move_to(fr.c)
        self.say(r"Now repeat for many starting states, thousands of kicks each: islands of order inside a "
                 r"sea of chaos (red). This is where Part 3 left us.", anims=[FadeIn(im), FadeOut(pts)],
                 run_time=2.5)
        self.say(r"This picture, a kicked rod seen once per kick, is the whole episode: its smooth curves, "
                 r"its chaos, and what quantum mechanics does to that chaos.")
        self.unsay()
        self.remove(live)
        part = Tex(r"Part 4", font_size=40, color=MUTED)
        ttl = Tex(r"The Kicked Rotor", font_size=64, color=FG).next_to(part, DOWN, buff=0.25)
        sub = Tex(r"Order, Chaos, and a Quantum Brake", font_size=36, color=MUTED).next_to(ttl, DOWN, buff=0.25)
        card = VGroup(part, ttl, sub).move_to([0, -2.55, 0])
        bgr = BackgroundRectangle(card, fill_opacity=0.85, buff=0.25)
        self.play(FadeOut(VGroup(ring, piv, rod())), FadeIn(bgr), FadeIn(card, shift=0.2 * UP), run_time=1.2)
        self.wait(3)
        self.play(FadeOut(Group(bgr, card, im, fr)), run_time=1.2)
