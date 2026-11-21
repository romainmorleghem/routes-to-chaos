"""Seq 1 — Squaring in the plane: lengths square, angles double; then shift by c."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE
from common.narrative import Narrated


class Squaring(Narrated):
    def construct(self):
        self.chapter(r"1 \,$\cdot$\, Squaring in the plane")
        pl = ComplexPlane(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=9, y_length=6,
                          background_line_style={"stroke_color": MUTED, "stroke_opacity": 0.25, "stroke_width": 1},
                          axis_config={"stroke_color": MUTED}).move_to([0, 0.2, 0])
        pl.add_coordinates(font_size=18)
        unit = Circle(radius=pl.get_x_unit_size(), color=DIAG, stroke_width=2).move_to(pl.n2p(0))
        ul = MathTex(r"|z| = 1", font_size=26, color=DIAG).next_to(pl.n2p(0.72 + 0.72j), UR, buff=0.05)
        self.play(Create(pl), run_time=1.2)
        r, th = ValueTracker(1.25), ValueTracker(0.45)
        z = lambda: r.get_value() * np.exp(1j * th.get_value())
        az = always_redraw(lambda: Arrow(pl.n2p(0), pl.n2p(z()), buff=0, color=MAP, stroke_width=5,
                                         max_tip_length_to_length_ratio=0.12))
        lz = always_redraw(lambda: MathTex("z", color=MAP, font_size=34).next_to(pl.n2p(z()), UR, buff=0.05))
        self.say(r"A complex number $z = x + iy$ is a point of the plane — or an arrow from $0$, "
                 r"with a length $|z|$ and an angle $\arg z$.", anims=[GrowArrow(az), FadeIn(lz)])
        self.add(az, lz)
        a1 = always_redraw(lambda: Arc(radius=0.55, start_angle=0, angle=th.get_value() % TAU,
                                       arc_center=pl.n2p(0), color=MAP, stroke_width=2))
        az2 = always_redraw(lambda: Arrow(pl.n2p(0), pl.n2p(z() ** 2), buff=0, color=ORBIT, stroke_width=5,
                                          max_tip_length_to_length_ratio=0.12))
        lz2 = always_redraw(lambda: MathTex("z^2", color=ORBIT, font_size=34).next_to(pl.n2p(z() ** 2), UR, buff=0.05))
        a2 = always_redraw(lambda: Arc(radius=0.85, start_angle=0, angle=(2 * th.get_value()) % TAU,
                                       arc_center=pl.n2p(0), color=ORBIT, stroke_width=2))
        rule = MathTex(r"|z^2| = |z|^2", r"\qquad", r"\arg z^2 = 2\arg z", font_size=36).to_corner(UR, buff=0.5).shift(0.3 * DOWN)
        rule.add_background_rectangle(opacity=0.85, buff=0.15)
        self.say(r"Multiplying two complex numbers multiplies their lengths and \emph{adds} their angles. "
                 r"So $z^2$ has the length squared and \emph{twice} the angle.",
                 anims=[Create(a1), GrowArrow(az2), FadeIn(lz2), Create(a2), FadeIn(rule)])
        self.add(a1, az2, lz2, a2)
        self.play(Create(unit), FadeIn(ul))
        self.say(r"Turn $z$ once around: $z^2$ goes around twice. Outside the unit circle $z^2$ is "
                 r"farther out; inside, closer to $0$; on the circle, it stays on the circle.",
                 anims=[th.animate.set_value(0.45 + TAU)], run_time=6, wait=0.5)
        self.play(r.animate.set_value(0.8), th.animate.set_value(0.45 + TAU + 0.6), run_time=2)
        self.play(r.animate.set_value(1.0), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(VGroup(az, lz, a1, az2, lz2, a2)))
        self.remove(az, lz, a1, az2, lz2, a2)

        # --- the whole plane at once
        u = pl.get_x_unit_size()
        grid = VGroup(*[Circle(radius=rr * u, color=c, stroke_width=2 if rr == 1 else 1.3).move_to(pl.n2p(0))
                        for rr, c in [(0.4, STABLE), (0.7, STABLE), (1.0, DIAG), (1.2, ORBIT), (1.35, ORBIT)]],
                      *[Line(pl.n2p(0), pl.n2p(1.35 * np.exp(1j * a)), color=MUTED, stroke_width=1.3)
                        for a in np.linspace(0, TAU, 12, endpoint=False)])
        grid.set_z_index(2)
        for m in grid:
            m.insert_n_curves(80)
        self.play(FadeOut(unit), FadeOut(ul), Create(grid), run_time=1.5)
        self.say(r"Apply it to the whole plane at once: angles double, the unit circle (blue) is mapped onto "
                 r"itself, the inside (green) shrinks toward $0$, the outside (red) is flung away.",
                 anims=[ApplyPointwiseFunction(lambda p: pl.n2p(pl.p2n(p) ** 2), grid)], run_time=3.5)
        c = -0.6 + 0.35j
        ca = Arrow(pl.n2p(0), pl.n2p(c), buff=0, color=ACCENT, stroke_width=5, max_tip_length_to_length_ratio=0.15)
        cl = MathTex("c", color=ACCENT, font_size=34).next_to(ca.get_end(), UL, buff=0.05)
        self.say(r"Then add a fixed number $c$: everything is shifted by the same arrow.",
                 anims=[GrowArrow(ca), FadeIn(cl)])
        self.play(grid.animate.shift(pl.n2p(c) - pl.n2p(0)), run_time=2)
        rule2 = MathTex(r"f_c(z) = z^2 + c", font_size=44, color=FG)
        sub = Tex(r"stretch-and-turn, then shift", font_size=30, color=MUTED).next_to(rule2, DOWN, buff=0.15)
        box = VGroup(rule2, sub).to_corner(UR, buff=0.5).shift(0.3 * DOWN)
        bg = BackgroundRectangle(box, fill_opacity=0.85, buff=0.2)
        self.play(FadeOut(rule), FadeIn(bg), Write(rule2), FadeIn(sub))
        self.say(r"That is the whole rule. Repeat it forever: $z_0 \to z_1 \to z_2 \to \cdots$ "
                 r"Which starting points survive, and which fly off to infinity?", extra=0.5)
        self.play(FadeOut(VGroup(grid, ca, cl, pl, bg, rule2, sub)))
        self.unsay()
