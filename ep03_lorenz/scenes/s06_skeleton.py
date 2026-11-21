"""Seq 6 — The skeleton: unstable periodic orbits labelled by L/R words; other strange attractors."""
from _common import *  # noqa
import json
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from common.lorenz import trajectory_any
from _stages import lorenz_points, curve, glow_image, fit_view

COLS = [MAP, DIAG, ORBIT, STABLE, ACCENT]


def primitive(w):
    return all(w != w[:d] * (len(w) // d) for d in range(1, len(w)) if len(w) % d == 0)


class Skeleton(Narrated):
    def construct(self):
        self.chapter(r"6 \,$\cdot$\, The skeleton")
        U = [o for o in json.loads((DATA / "upo.json").read_text()) if primitive(o["word"])]
        bg = curve(lorenz_points(T=80, dt=0.004, skip=2), width=0.7, opacity=0.2, colors=MUTED)
        self.play(FadeIn(bg))
        self.say(r"A chaotic orbit never closes. But the attractor is densely threaded with orbits that "
                 r"\emph{do}: periodic, and all unstable.")
        picks = [o for o in U if o["word"] in ("RL", "RLL", "RLLR", "RLLLR", "RLLRL")][:5]
        shown = VGroup()
        legend = VGroup()
        for j, o in enumerate(picks):
            c = curve(np.array(o["pts"]), width=3.2, colors=COLS[j])
            lab = MathTex(r"\texttt{%s}" % o["word"], r"\ \ T = %.3f" % o["T"], font_size=28, color=COLS[j])
            legend.add(lab)
            shown.add(c)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UR, buff=0.6).shift(0.4 * DOWN)
        self.say(r"Each is named by its itinerary: \texttt{L} for a loop around the left hole, \texttt{R} "
                 r"for the right. \texttt{RL}: once around each.", anims=[Create(shown[0]), FadeIn(legend[0])],
                 run_time=2)
        for j in range(1, len(picks)):
            self.play(Create(shown[j]), FadeIn(legend[j]), run_time=1.6)
        self.say(r"\texttt{RLL}, \texttt{RLLR}, \ldots{} one orbit for (almost) every word: the map of Part 1 "
                 r"again, where a symbolic itinerary labels every cycle.")
        mu = picks[0]["mu"]
        self.say(r"Each is unstable: a neighbour of \texttt{RL} is pushed away by a factor %.1f per lap. "
                 r"So the chaotic orbit shadows one cycle, is ejected, shadows another\ldots" % mu)
        self.say(r"That is the skeleton of chaos: averages over the attractor (even $\lambda$) can be "
                 r"computed from these few cycles alone (periodic-orbit theory, Cvitanovi\'c).")
        self.unsay()
        self.play(FadeOut(VGroup(shown, legend, bg)))
        # gallery
        self.chapter(r"6 \,$\cdot$\, Other strange attractors")
        names = [("R\\\"ossler", 0, 0.03, 600, (0.1, 0.0, 0.1), 0.4, -0.5, "one fold, like a sheet of paper"),
                 ("Thomas", 1, 0.05, 4000, (0.1, 0.0, 0.1), 0.6, 0.6, "a random walk with no randomness"),
                 ("Aizawa", 2, 0.01, 600, (0.1, 0.0, 0.1), 0.4, -0.3, "a sphere with a tube through it"),
                 ("Halvorsen", 3, 0.005, 600, (-1.48, -1.51, 2.04), 0.8, 0.5, "three-fold symmetric wings")]
        tiles = Group()
        for j, (nm, kind, dt, T, p0, yaw, pitch, cap) in enumerate(names):
            P = trajectory_any(kind, np.array(p0), int(T / dt), dt)[2000:]
            P = P[:: max(1, len(P) // 400000)]
            v = fit_view(P, yaw, pitch, 5.0, 2.2)
            im = glow_image(P, yaw, pitch, width=5.6, height=2.45, **v,
                            screen=np.array([0, 0, 0.0]))
            t = Tex(nm, font_size=28, color=FG)
            c = Tex(cap, font_size=22, color=MUTED)
            tiles.add(Group(im, VGroup(t, c).arrange(DOWN, buff=0.06)).arrange(DOWN, buff=0.05))
        tiles.arrange_in_grid(2, 2, buff=(0.6, 0.12)).move_to([0, 0.45, 0])
        self.say(r"Other equations, other shapes, same recipe: a flow that stretches, folds, and loses volume.",
                 anims=[FadeIn(tiles, lag_ratio=0.3)], run_time=3)
        self.wait(2)
        self.unsay()
        self.play(FadeOut(tiles))
