"""Seq 5 — Period doubling without friction: the main island at K=4; area-preserving Henon cascade; delta=8.7210."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated
from _viz import portrait, henon_portrait
from _stages import raster_points

P = np.pi
BOX = ((P - 1.8, P + 1.8), (-2.7, 2.7))
HV = ((0.0, 0.6), (-0.6, 0.0))


class Doubling(Narrated):
    def construct(self):
        self.chapter(r"5 \,$\cdot$\, Period doubling without friction")
        M = MathTex(r"M(\pi, 0) = \begin{pmatrix}1-K & 1\\ -K & 1\end{pmatrix},\qquad \mathrm{tr}\,M = 2 - K",
                    font_size=36, color=FG).move_to([0, 2.7, 0])
        self.say(r"Islands are not eternal either. At the centre of the main island, $(\theta,p)=(\pi,0)$, "
                 r"the trace of the stability matrix is $2-K$\ldots", anims=[FadeIn(M)])
        st = MathTex(r"\text{stable} \iff |\mathrm{tr}\,M| < 2 \iff K < 4", font_size=36, color=STABLE
                     ).next_to(M, DOWN, buff=0.3)
        self.say(r"\ldots and a point of an area-preserving map is stable only while $|\mathrm{tr}\,M|<2$: "
                 r"here, while $K<4$.", anims=[FadeIn(st)])
        w, h = 2.4, 3.6
        a = portrait(3.8, w, h, box=BOX, m=150).move_to([-2.0, -0.6, 0])
        b = portrait(4.3, w, h, box=BOX, m=150).move_to([2.0, -0.6, 0])
        la = MathTex(r"K = 3.8", font_size=30, color=FG).next_to(a, LEFT, buff=0.2)
        lb = MathTex(r"K = 4.3", font_size=30, color=FG).next_to(b, RIGHT, buff=0.2)
        self.play(VGroup(M, st).animate.scale(0.75).move_to([0, 2.75, 0]))
        self.say(r"Zoom on the centre. Past $K=4$ it turns unstable and two islands appear, visited "
                 r"alternately: a period doubling, exactly like $r=3$ in Part 1.",
                 anims=[FadeIn(a), FadeIn(b), FadeIn(la), FadeIn(lb)], run_time=1.5)
        self.play(FadeOut(Group(a, b, la, lb, M, st)))
        hen = MathTex(r"(x, y) \mapsto (1 - a x^2 + y,\ -x)", font_size=44, color=MAP).move_to([0, 2.3, 0])
        p1 = MathTex(r"\text{Part 1: } x \mapsto 1 - a x^2", font_size=32, color=MUTED).next_to(hen, DOWN, buff=0.3)
        self.say(r"To follow the whole cascade, zoom on the simplest model of an island losing stability: the "
                 r"area-preserving H\'enon map, the frictionless cousin of Part 1's map.",
                 anims=[Write(hen), FadeIn(p1)], run_time=1.5)
        h1 = henon_portrait(2.5, 3.0, 3.0, view=HV).move_to([-2.0, -0.85, 0])
        h2 = henon_portrait(3.3, 3.0, 3.0, view=HV).move_to([2.0, -0.85, 0])
        l1 = MathTex(r"a = 2.5", font_size=30, color=FG).next_to(h1, LEFT, buff=0.2)
        l2 = MathTex(r"a = 3.3", font_size=30, color=FG).next_to(h2, RIGHT, buff=0.2)
        self.play(VGroup(hen, p1).animate.scale(0.8).move_to([0, 2.9, 0]))
        self.say(r"Its determinant is exactly 1. One island at $a = 2.5$; past $a = 3$ it splits into two, "
                 r"visited alternately.", anims=[FadeIn(h1), FadeIn(h2), FadeIn(l1), FadeIn(l2)], run_time=1.5)
        self.play(FadeOut(Group(h1, h2, l1, l2)))
        T = DOUBLING["tree"]
        A = DOUBLING["a_k"]
        bx = Axes(x_range=[2.4, 4.2, 0.2], y_range=[-0.1, 0.55, 0.1], x_length=11.5, y_length=4.4, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 1.5}, x_axis_config={"include_numbers": True,
                  "font_size": 22, "numbers_to_include": [2.6, 3.0, 3.4, 3.8, 4.2]}).move_to([0, 0.05, 0])
        im = VGroup()
        groups = {}
        for t in T:
            if t[0] >= 2.4:
                groups.setdefault(len(t[1]), []).append((t[0], sorted(t[1])))
        for q, G in sorted(groups.items()):
            aa = np.array([g[0] for g in G]); X = np.array([g[1] for g in G])
            o = np.argsort(aa); aa, X = aa[o], X[o]
            for j in range(q):
                pts = [bx.c2p(u, v) for u, v in zip(aa, X[:, j])]
                if q > 1:   # start each new branch at the bifurcation point of its parent
                    par = groups[q // 2]; pa = max(par, key=lambda g: g[0])
                    pts.insert(0, bx.c2p(A[int(np.log2(q)) - 1], min(pa[1], key=lambda v: abs(v - X[0, j]))))
                im.add(VMobject(stroke_color=MAP, stroke_width=2.5).set_points_as_corners(pts))
        al = MathTex(r"a", font_size=30, color=FG).next_to(bx.x_axis, RIGHT, buff=0.15)
        tk = VGroup(*[DashedLine(bx.c2p(v, -0.1), bx.c2p(v, 0.55), color=ACCENT, stroke_width=1.5) for v in A[:4]])
        self.say(r"Follow the stable orbit as $a$ grows: period 1, 2, 4, 8, 16, 32, 64. Each $a_k$ is located "
                 r"where the multipliers reach $-1$, with exact derivatives: no time step, no approximation.",
                 anims=[FadeOut(VGroup(hen, p1)), Create(bx), FadeIn(al), FadeIn(im), Create(tk)], run_time=2)
        self.play(FadeOut(Group(bx, im, al, tk)))
        d = DOUBLING["delta_k"]
        rows = []
        for i, v in enumerate(A):
            rows.append([str(i + 1), str(DOUBLING["periods"][i]), r"%.12f" % v,
                         "" if i == 0 or i == len(A) - 1 else r"%.5f" % d[i - 1]])
        tab = MathTable(rows, col_labels=[MathTex(c) for c in (r"k", r"\text{period}", r"a_k", r"\delta_k")],
                        include_outer_lines=False, line_config={"stroke_color": MUTED, "stroke_width": 1.2},
                        element_to_mobject_config={"font_size": 32}, v_buff=0.22, h_buff=0.6)
        tab.scale_to_fit_width(7.2).move_to([-2.6, 0.35, 0])
        self.say(r"The gaps shrink by a constant factor, as in Part 1: $%s$\ldots" %
                 r",\ ".join("%.4f" % v for v in d), anims=[FadeIn(tab)], run_time=1.5)
        c1 = VGroup(Tex(r"Part 1, with friction", font_size=30, color=MUTED),
                    MathTex(r"\delta = 4.6692\ldots", font_size=42, color=MUTED)).arrange(DOWN, buff=0.15)
        c4 = VGroup(Tex(r"Part 4, without friction", font_size=30, color=FG),
                    MathTex(r"\delta = 8.7210\ldots", font_size=42, color=ACCENT)).arrange(DOWN, buff=0.15)
        cmp_ = VGroup(c1, c4).arrange(DOWN, buff=0.6).move_to([4.0, 0.35, 0])
        self.say(r"But they converge to $8.7210$, not $4.6692$! Greene, MacKay, Vivaldi \& Feigenbaum (1981): "
                 r"every area-preserving cascade shares $\delta = 8.721097\ldots$", anims=[FadeIn(cmp_)])
        self.say(r"Two universality classes: one for systems that lose energy, one for systems that keep it.")
        self.unsay()
        self.play(FadeOut(Group(tab, cmp_, self.chapter_tag)))
        self.chapter_tag = None
