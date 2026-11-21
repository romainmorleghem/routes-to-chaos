"""Seq 1 — From kicks to a map: the standard map, the torus, area preservation (vs Part 3)."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _viz import Frame
from _stages import raster_points

K = 1.2


def blob(n=6000, c=(2.0, 0.6), r=0.32, seed=3):
    rng = np.random.default_rng(seed)
    a = rng.random(n) * 2 * np.pi; s = r * np.sqrt(rng.random(n))
    return c[0] + s * np.cos(a), c[1] + s * np.sin(a)


def step(th, p):
    p = p + K * np.sin(th)
    th = (th + p) % (2 * np.pi)
    return th, (p + np.pi) % (2 * np.pi) - np.pi


class StandardMap(Narrated):
    def construct(self):
        self.chapter(r"1 \,$\cdot$\, From kicks to a map")
        e1 = MathTex(r"p_{n+1}", r"=", r"p_n + K\sin\theta_n", font_size=46, color=FG)
        e2 = MathTex(r"\theta_{n+1}", r"=", r"\theta_n + p_{n+1}", font_size=46, color=FG)
        eqs = VGroup(e1, e2).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([0, 1.6, 0])
        e1[2].set_color(MAP); e2[2].set_color(DIAG)
        l1 = Tex(r"kick", font_size=30, color=MAP).next_to(e1, RIGHT, buff=0.6)
        l2 = Tex(r"free turn for one second", font_size=30, color=DIAG).next_to(e2, RIGHT, buff=0.6)
        self.say(r"Two lines say everything. The kick changes the speed by $K\sin\theta$\ldots",
                 anims=[Write(e1), FadeIn(l1)], run_time=1.5)
        self.say(r"\ldots then the rod turns by an angle equal to its new speed (unit time, unit inertia).",
                 anims=[Write(e2), FadeIn(l2)], run_time=1.5)
        name = Tex(r"the \emph{standard map} (Chirikov, 1969)", font_size=34, color=ACCENT
                   ).next_to(eqs, DOWN, buff=0.45)
        self.say(r"This is the \emph{standard map}. As with Part 1's logistic map, we simply iterate. "
                 r"But now there are two variables, and no friction anywhere.", anims=[FadeIn(name)])
        # torus
        self.play(VGroup(eqs, l1, l2, name).animate.scale(0.7).to_edge(UP, buff=0.75))
        sq = Square(3.2, color=MUTED, stroke_width=2).move_to([0, -0.9, 0])
        arr = VGroup(
            Arrow(sq.get_corner(DL), sq.get_corner(UL), buff=0, color=MAP, stroke_width=4, tip_length=0.2),
            Arrow(sq.get_corner(DR), sq.get_corner(UR), buff=0, color=MAP, stroke_width=4, tip_length=0.2),
            Arrow(sq.get_corner(DL), sq.get_corner(DR), buff=0, color=DIAG, stroke_width=4, tip_length=0.2),
            Arrow(sq.get_corner(UL), sq.get_corner(UR), buff=0, color=DIAG, stroke_width=4, tip_length=0.2))
        lt = MathTex(r"\theta \bmod 2\pi", font_size=30, color=DIAG).next_to(sq, DOWN, buff=0.15)
        lp = MathTex(r"p \bmod 2\pi", font_size=30, color=MAP).next_to(sq, LEFT, buff=0.15)
        self.say(r"Only $\theta$ modulo $2\pi$ matters. And adding $2\pi$ to the speed just adds one full turn "
                 r"between kicks: $p$ modulo $2\pi$ is enough too.", anims=[Create(sq), FadeIn(lt), FadeIn(lp)])
        self.say(r"So the state lives on a square whose opposite edges are glued: a torus. "
                 r"Every picture in this episode is drawn on it.", anims=[Create(arr)])
        self.play(FadeOut(VGroup(sq, arr, lt, lp)))
        # area preservation
        jac = MathTex(r"\det\frac{\partial(\theta_{n+1},p_{n+1})}{\partial(\theta_n,p_n)} = "
                      r"\det\begin{pmatrix}1+K\cos\theta & 1\\ K\cos\theta & 1\end{pmatrix} = 1",
                      font_size=34, color=FG).move_to([0, 1.3, 0])
        self.say(r"One more property, the crucial one. The Jacobian determinant of the map is exactly 1:",
                 anims=[FadeIn(jac)])
        self.play(FadeOut(jac), FadeOut(VGroup(eqs, l1, l2, name)))
        fr = Frame(5.0, 5.0, center=(-2.9, 0.45, 0), fs=24)
        th, p = blob()
        imgs = []
        for i in range(7):
            imgs.append(raster_points(th, p, (0, 2 * np.pi), (-np.pi, np.pi), 5.0, 5.0, color_hex="#C792EA",
                                      gain=1.6).move_to(fr.c))
            th, p = step(th, p)
        cnt = Tex(r"kick 0", font_size=32, color=MUTED).next_to(fr, UP, buff=0.15)
        self.say(r"Take a small blob of $6000$ nearby states and kick them all, with $K = 1.2$.",
                 anims=[FadeIn(fr), FadeIn(imgs[0]), FadeIn(cnt)])
        for i in range(1, 7):
            c2 = Tex(r"kick %d" % i, font_size=32, color=MUTED).move_to(cnt)
            self.play(FadeTransform(imgs[i - 1], imgs[i]), Transform(cnt, c2), run_time=1.1)
            self.wait(0.3)
        p3 = VGroup(Tex(r"Part 3:", font_size=32, color=MUTED),
                    MathTex(r"\text{volume} \times e^{-13.67\,t}", font_size=36, color=ORBIT),
                    Tex(r"\ $\Rightarrow$ attractor", font_size=32, color=ORBIT)).arrange(DOWN, buff=0.15)
        p4 = VGroup(Tex(r"Part 4:", font_size=32, color=MUTED),
                    MathTex(r"\text{area} \times 1", font_size=36, color=STABLE),
                    Tex(r"\ $\Rightarrow$ no attractor", font_size=32, color=STABLE)).arrange(DOWN, buff=0.15)
        cmp_ = VGroup(p3, p4).arrange(DOWN, buff=0.6).move_to([3.4, 0.45, 0])
        self.say(r"The blob is stretched and folded, as in Part 3, but its area never changes: no state is "
                 r"ever lost. This is Liouville's theorem for a system without friction.", anims=[FadeIn(p4)])
        self.say(r"In Part 3, volumes shrank and every motion fell onto an attractor. Here nothing can "
                 r"attract: each orbit keeps its own character forever.", anims=[FadeIn(p3)])
        self.unsay()
        self.play(FadeOut(Group(fr, imgs[-1], cnt, cmp_, self.chapter_tag)))
        self.chapter_tag = None
