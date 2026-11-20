"""Seq 5 — Universality: other one-hump maps give the same delta; a quartic top gives another one."""
import json
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE, ACCENT
from common.narrative import Narrated
from _stages import bif_rgb, image_on_axes

U = json.loads((ROOT / "ep01_logistic" / "data" / "universality.json").read_text())

MAPS = [  # key, vectorised map, parameter range, x range, parameter for the graph, x0, label
    ("logistic", lambda r, x: r * x * (1 - x), (2.8, 4.0), (0, 1), 3.7, 0.5, r"r\,x(1-x)"),
    ("sine", lambda a, x: a * np.sin(np.pi * x), (0.7, 1.0), (0, 1), 0.93, 0.5, r"a\sin(\pi x)"),
    ("ricker", lambda r, x: x * np.exp(r * (1 - x)), (1.8, 3.4), (0, 4), 3.0, 0.5, r"x\,e^{\,r(1-x)}"),
    ("quartic", lambda a, x: 1 - a * x ** 4, (0.6, 2.0), (-1, 1), 1.8, 0.0, r"1-a\,x^{4}"),
]
XS = [-5.3, -1.75, 1.8, 5.35]


class Universality(Narrated):
    def column(self, i):
        key, fn, pr, xr, p_g, x0, tex = MAPS[i]
        cx = XS[i]
        g = Axes(x_range=[xr[0], xr[1], (xr[1] - xr[0]) / 2], y_range=[xr[0], xr[1], (xr[1] - xr[0]) / 2],
                 x_length=2.0, y_length=1.5, tips=False, axis_config={"color": MUTED, "stroke_width": 1.5}
                 ).move_to([cx, 1.95, 0])
        curve = g.plot(lambda x: fn(p_g, x), x_range=[xr[0], xr[1], (xr[1] - xr[0]) / 200],
                       color=MAP if key != "quartic" else ORBIT, stroke_width=3)
        lab = MathTex(tex, font_size=30, color=FG).next_to(g, UP, buff=0.15)
        b = Axes(x_range=[pr[0], pr[1], (pr[1] - pr[0]) / 2], y_range=[xr[0], xr[1], (xr[1] - xr[0]) / 2],
                 x_length=3.2, y_length=2.4, tips=False, axis_config={"color": MUTED, "stroke_width": 1.5}
                 ).move_to([cx, -0.55, 0])
        img = image_on_axes(bif_rgb(b, fn=lambda r, x: fn(r, x), x0=x0, transient=800), b)
        d = U[key]["delta"][-1]
        col = ACCENT if key != "quartic" else ORBIT
        dl = MathTex(rf"\delta \approx {d:.6f}", font_size=32, color=col).next_to(b, DOWN, buff=0.25)
        return dict(g=g, curve=curve, lab=lab, b=b, img=img, dl=dl)

    def construct(self):
        self.chapter(r"4 \,$\cdot$\, Beyond $r_\infty$: chaos", animate=False)
        self.chapter(r"5 \,$\cdot$\, Universality")
        self.say(r"Is $4.669\ldots$ a property of our parabola? Let's change the rule.")
        cols = [self.column(i) for i in range(4)]
        for i in range(3):
            c = cols[i]
            self.play(FadeIn(c["lab"]), Create(c["g"]), Create(c["curve"]), run_time=1)
        self.say(r"A sine arch, or the \emph{Ricker} model used by fishery biologists: "
                 r"different formulas, but each has a single smooth hump.")
        self.say(r"Their bifurcation diagrams: the same cascade, the same chaos, the same windows.",
                 anims=[AnimationGroup(*[FadeIn(Group(cols[i]["b"], cols[i]["img"])) for i in range(3)],
                                       lag_ratio=0.3)], run_time=2)
        self.say(r"And the same $\delta$, to six digits (computed with each map's own cascade).",
                 anims=[AnimationGroup(*[Write(cols[i]["dl"]) for i in range(3)], lag_ratio=0.3)],
                 run_time=2, extra=0.5)

        c = cols[3]
        self.say(r"One exception: a hump with a \emph{flat} top, like $1 - a x^4$.",
                 anims=[FadeIn(c["lab"]), Create(c["g"]), Create(c["curve"])])
        self.play(FadeIn(Group(c["b"], c["img"])), Write(c["dl"]), run_time=1.5)
        tops = VGroup(*[Circle(radius=0.22, color=FG, stroke_width=2).move_to(
            cols[i]["g"].c2p(*self.top(i))) for i in range(4)])
        self.say(r"Only one detail matters: the shape of the very top of the hump. "
                 r"Quadratic top: $4.669\ldots$; quartic top: $7.2847\ldots$, another \emph{universality class}.",
                 anims=[Create(tops)], extra=1.0)
        everything = Group(*[m for c in cols for m in c.values()], tops)
        self.play(FadeOut(everything))

        # --- experiments
        title = Tex(r"Measured in the laboratory (1980s)", font_size=40, color=FG).move_to([0, 2.4, 0])
        items = VGroup(
            Tex(r"$\bullet$ fluid layers heated from below (water, mercury, liquid helium)"),
            Tex(r"$\bullet$ nonlinear electronic circuits (diodes, transistors)"),
            Tex(r"$\bullet$ lasers, acoustic cavities, chemical reactions\ldots"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).scale(0.75).next_to(title, DOWN, buff=0.5)
        res = MathTex(r"\delta_{\text{measured}} \approx 4.3 \text{ -- } 4.8"
                      r"\quad\text{(within error bars of } 4.669\ldots)", color=ACCENT, font_size=36
                      ).next_to(items, DOWN, buff=0.55)
        src = Tex(r"compiled in P.~Cvitanovi\'c, \emph{Universality in Chaos} (1989)", font_size=22,
                  color=MUTED).next_to(res, DOWN, buff=0.35)
        self.say(r"And the same cascade appears in real experiments, where nobody wrote down a parabola.",
                 anims=[FadeIn(title), FadeIn(items, lag_ratio=0.4)], run_time=2)
        self.play(Write(res), FadeIn(src))
        self.wait(2.5)
        self.say(r"Why would a heated liquid know about $4.669\ldots$?", extra=0.8)
        self.play(FadeOut(VGroup(title, items, res, src)))
        self.unsay()

    @staticmethod
    def top(i):
        key, fn, pr, xr, p_g, x0, tex = MAPS[i]
        xc = {"logistic": 0.5, "sine": 0.5, "ricker": 1 / p_g, "quartic": 0.0}[key]
        return xc, fn(p_g, xc)
