"""Sequence 6 — renormalisation: rescaled f^{2^n} converge to a universal function g."""
from _common import *  # noqa
import numpy as np
from manim import *
from common.style import FG, MUTED, ACCENT, MAP

N_CURVES = 6


class Renormalization(Scene):
    def construct(self):
        title = Tex(r"Zoom on $f^{2^n}$ near $x=\tfrac12$, rescale by $\alpha^n$", color=FG).to_edge(UP)
        ax = Axes(x_range=[-1, 1, 0.5], y_range=[-1.2, 1.2, 0.6], x_length=7, y_length=5.2,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}
                  ).shift(0.4 * DOWN)
        self.play(Write(title), Create(ax))
        ys = np.array(DATA["renorm_y"])
        colors = color_gradient([MAP, ACCENT], N_CURVES)
        prev, lab = None, None
        for n in range(N_CURVES):
            v = np.clip(np.array(DATA["renorm_curves"][n]), -1.2, 1.2)
            curve = VMobject(stroke_color=colors[n], stroke_width=3)
            curve.set_points_smoothly([ax.c2p(a, b) for a, b in zip(ys, v)])
            new_lab = MathTex(rf"n = {n}" + (r"\;(f_{R_0})" if n == 0 else ""), color=colors[n]).to_corner(UR).shift(DOWN)
            anims = [Create(curve) if prev is None else ReplacementTransform(prev.copy(), curve)]
            anims.append(FadeIn(new_lab) if lab is None else ReplacementTransform(lab, new_lab))
            if prev is not None:
                anims.append(prev.animate.set_stroke(opacity=0.25, width=1.5))
            self.play(*anims, run_time=1.6)
            prev, lab = curve, new_lab
        self.wait()
        eq = MathTex(r"g(x) = \alpha\, g\!\left(g\!\left(\tfrac{x}{\alpha}\right)\right)",
                     r",\qquad \alpha = -2.502\,907\,875\ldots", color=ACCENT).to_edge(DOWN)
        self.play(Write(eq), run_time=2)
        self.wait(2)
