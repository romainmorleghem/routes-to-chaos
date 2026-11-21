"""Seq 0 — Cold open: Part 2's last equations come alive; the butterfly; the promise; title."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, ORBIT, DIAG
from common.narrative import Narrated
from _stages import lorenz_points, project, comet, glow_image, curve, TRAIL


def equations():
    return MathTex(r"\dot x = \sigma(y - x)", r"\quad \dot y = x(\rho - z) - y", r"\quad \dot z = xy - \beta z",
                   font_size=32, color=FG).to_edge(UP, buff=0.7)


class ColdOpen(Narrated):
    def construct(self):
        eqs = equations()
        self.say(r"Part 2 ended on three equations. A point $(x, y, z)$ moves in space; "
                 r"they give its velocity at every instant.", anims=[FadeIn(eqs)])
        P = lorenz_points(T=30, dt=0.004)
        yaw = ValueTracker(0.0)
        k = ValueTracker(2)
        tail = 220
        def draw():
            i = int(k.get_value())
            return comet(P[max(0, i - tail):i + 1], yaw=yaw.get_value(), color=ORBIT, width=3.2)
        live = always_redraw(draw)
        self.add(live)
        self.say(r"With $\sigma = 10,\ \rho = 28,\ \beta = 8/3$, start at $(1,1,1)$ and simply follow the arrows.",
                 anims=[k.animate.set_value(1800)], run_time=7, wait=0.5, )
        trace = always_redraw(lambda: curve(P[:int(k.get_value()) + 1:2], yaw=yaw.get_value(), width=1.3,
                                            opacity=0.55))
        self.add(trace)
        self.say(r"It loops around one hole, jumps to the other, comes back\ldots{} never twice the same way.",
                 anims=[k.animate.set_value(7400), yaw.animate.set_value(0.0)], run_time=12, wait=0.5,
                 )
        self.remove(live)
        trace.clear_updaters()
        Pg = lorenz_points(T=600, dt=0.002, skip=5)
        glow = glow_image(Pg)
        self.say(r"Run it long enough and the path paints a shape: the \emph{Lorenz attractor}. "
                 r"You have seen this butterfly before.", anims=[FadeOut(trace), FadeIn(glow)], run_time=2.5)
        self.say(r"This episode is about what it \emph{hides}: its physical meaning, the speed at which it "
                 r"forgets, and, folded inside it, the map of Part 1.")
        self.unsay()
        part = Tex(r"Part 3", font_size=40, color=MUTED)
        ttl = Tex(r"Strange Attractors", font_size=64, color=FG).next_to(part, DOWN, buff=0.25)
        sub = Tex(r"Chaos Without Energy Conservation", font_size=36, color=MUTED).next_to(ttl, DOWN, buff=0.25)
        card = VGroup(part, ttl, sub).move_to([0, -2.55, 0])
        bgr = BackgroundRectangle(card, fill_opacity=0.85, buff=0.25)
        self.play(FadeOut(eqs), FadeIn(bgr), FadeIn(card, shift=0.2 * UP), run_time=1.2)
        self.wait(3)
        self.play(FadeOut(Group(bgr, card, glow)), run_time=1.2)
