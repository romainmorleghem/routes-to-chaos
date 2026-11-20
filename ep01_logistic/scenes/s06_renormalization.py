"""Seq 6 — Why? Renormalisation: box-and-rescale, convergence to g, the doubling operator T,
and a (not to scale) picture of function space explaining delta and universality."""
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE, ACCENT
from common.narrative import Narrated
from common.logistic import ALPHA, DELTA

R = DATA["R"]
A = abs(ALPHA)


def fk(r, k):
    def g(x):
        for _ in range(2 ** k):
            x = r * x * (1 - x)
        return x
    return g


class Renormalization(Narrated):
    def construct(self):
        self.chapter(r"5 \,$\cdot$\, Universality", animate=False)
        self.chapter(r"6 \,$\cdot$\, Why? Renormalisation")

        L = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=4.6, y_length=4.6, tips=False,
                 axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}).move_to([-3.6, 0.15, 0])
        Rx = Axes(x_range=[-0.5, 0.5, 0.5], y_range=[-0.5, 0.5, 0.5], x_length=4.6, y_length=4.6, tips=False,
                  axis_config={"color": MUTED, "stroke_opacity": 0.5}).move_to([3.4, 0.15, 0])
        diag = L.plot(lambda x: x, color=DIAG, stroke_width=2)
        f0 = L.plot(fk(R[0], 0), color=MAP, stroke_width=3)
        top = Dot(L.c2p(0.5, 0.5), color=FG)
        t0 = MathTex(r"f_{R_0},\ R_0 = 2", font_size=30, color=MAP).next_to(L, UP, buff=0.15)
        self.play(Create(L), Create(diag))
        self.say(r"To compare the stages fairly, pick at each stage the special $r$ (called $R_n$) for which "
                 r"the top of the hump, $x=\tfrac12$, lies \emph{on} the cycle.",
                 anims=[Create(f0), FadeIn(t0), FadeIn(top, scale=2)])
        ys = np.array(DATA["renorm_y"])
        mask = np.abs(ys) <= 0.5
        def rcurve(n, color, w=3):
            v = np.array(DATA["renorm_curves"][n])[mask]
            return VMobject(stroke_color=color, stroke_width=w).set_points_smoothly(
                [Rx.c2p(a, b) for a, b in zip(ys[mask], v)])
        g0 = rcurve(0, MAP)
        rt = MathTex(r"f_{R_0}", font_size=30, color=MAP).next_to(Rx, UP, buff=0.15)
        self.say(r"Copy it on the right, centred on the top of the hump.",
                 anims=[Create(Rx), TransformFromCopy(f0, g0), FadeIn(rt)])

        colors = [MAP, ACCENT, STABLE, DIAG]
        prev_curve, prev_title = f0, t0
        texts = {
            1: (r"Period 2, at $R_1 = 1+\sqrt5$: draw $f\circ f$. Around $x = \tfrac12$ (box) we find "
                r"the small upside-down copy of chapter 2.",
                r"Rotate it by $180^\circ$ and enlarge it by $|\alpha| \approx 2.5$: it almost matches $f$!"),
            2: (r"Period 4, at $R_2$: draw $f^{4}$ ($f$ applied 4 times). The copy is in a box "
                r"$\alpha^2 \approx 6.3$ times smaller.",
                r"Blow it up by $\alpha^2$: an even better match."),
            3: (r"Period 8, at $R_3$: $f^{8}$, box $|\alpha|^3 \approx 15.7$ times smaller\ldots",
                r"\ldots indistinguishable."),
        }
        for n in (1, 2, 3):
            fn = fk(R[n], n)
            curve = L.plot(fn, x_range=[0, 1, 0.0015], color=colors[n], stroke_width=2.5)
            title = MathTex(rf"f^{{{2**n}}}_{{R_{n}}}", font_size=32, color=colors[n]).next_to(L, UP, buff=0.15)
            side = 1 / A ** n
            box = Square(side_length=side * L.x_length, color=FG, stroke_width=2).move_to(L.c2p(0.5, 0.5))
            self.say(texts[n][0], anims=[ReplacementTransform(prev_curve, curve),
                                         ReplacementTransform(prev_title, title)])
            self.play(Create(box))
            piece = L.plot(fn, x_range=[0.5 - side / 2, 0.5 + side / 2, side / 300],
                           color=colors[n], stroke_width=3)
            grp = VGroup(box.copy(), piece)
            self.add(grp)
            ang = PI * (n % 2) + (TAU if n == 2 else 0)
            target = rcurve(n, colors[n])
            self.say(texts[n][1], anims=[grp.animate.rotate(ang).scale(A ** n).move_to(Rx.c2p(0, 0))],
                     run_time=2.2)
            self.play(FadeOut(grp[0]), ReplacementTransform(grp[1], target), FadeOut(box))
            prev_curve, prev_title = curve, title

        # --- convergence and the universal function g
        self.play(FadeOut(VGroup(L, diag, prev_curve, prev_title, top)), FadeOut(rt))
        big = VGroup(Rx, *[m for m in self.mobjects if isinstance(m, VMobject) and m not in
                           (self.caption, self.chapter_tag)])
        self.play(big.animate.move_to([0, 0.35, 0]))
        gl = MathTex(r"\longrightarrow\; g", font_size=40, color=FG).next_to(Rx, RIGHT, buff=0.3)
        self.say(r"Doubling the period and zooming by $\alpha$ gives, in the limit, one universal "
                 r"curve $g$ — whatever the starting hump.", anims=[FadeIn(gl)])
        self.play(FadeOut(big), FadeOut(gl))

        # --- the doubling operator
        T = MathTex(r"T[f](x)", r"=", r"\alpha", r"\,f\!\big(f(", r"x/\alpha", r")\big)", font_size=56
                    ).move_to([0, 1.3, 0])
        b1 = Brace(T[3:6], DOWN, color=MAP)
        l1 = Tex(r"apply twice:\\ double the period", font_size=30, color=MAP).next_to(b1, DOWN)
        b2 = Brace(T[2], UP, color=ACCENT)
        l2 = Tex(r"zoom by $\alpha$", font_size=30, color=ACCENT).next_to(b2, UP)
        self.say(r"\emph{Apply twice, then zoom}: an operation $T$ that turns a function into another function.",
                 anims=[Write(T)])
        self.play(GrowFromCenter(b1), FadeIn(l1), GrowFromCenter(b2), FadeIn(l2))
        fixed = MathTex(r"T[g] = g", font_size=56, color=ACCENT).move_to([0, -1.4, 0])
        self.say(r"The universal curve does not change under it: $g$ is a \emph{fixed point} of $T$ — "
                 r"exactly like $x^\ast$ was a fixed point of $f$ in chapter 1.", anims=[Write(fixed)], extra=0.5)
        self.play(FadeOut(VGroup(T, b1, l1, b2, l2, fixed)))

        # --- function space cartoon (linearised, not to scale)
        dc = 2.0                                     # cartoon stretching factor (true value: 4.669)
        U = np.array([1.0, 0.18, 0]); U /= np.linalg.norm(U)
        S = np.array([-0.25, 1.0, 0]); S /= np.linalg.norm(S)
        G = np.array([-0.5, 0.3, 0])
        def to_xy(u, s): return G + u * U + s * S
        def Tmap(p):
            d = p - G
            M = np.array([U[:2], S[:2]]).T
            u, s = np.linalg.solve(M, d[:2])
            return to_xy(dc * u, 0.45 * s)
        space = RoundedRectangle(width=12.4, height=5.6, corner_radius=0.3, stroke_color=MUTED,
                                 stroke_width=1.5).move_to([0, 0.15, 0])
        sl = Tex(r"space of all one-hump maps", font_size=26, color=MUTED).next_to(space, UP, buff=-0.45).shift(4.3 * LEFT)
        Ws = Line(to_xy(0, -2.5), to_xy(0, 2.6), color=DIAG, stroke_width=4)
        wl = Tex(r"maps sitting exactly\\at the end of a cascade", font_size=24, color=DIAG).next_to(Ws.get_end(), RIGHT, buff=0.15)
        gd = Dot(G, color=ACCENT, radius=0.1)
        gl = MathTex("g", color=ACCENT, font_size=36).next_to(gd, DL, buff=0.1)
        ua = Arrow(G, to_xy(2.3, 0), color=ORBIT, buff=0.12, stroke_width=4)
        ul = MathTex(r"\times\,\delta", color=ORBIT, font_size=36).next_to(ua.get_end(), UP, buff=0.1)
        self.say(r"Picture every one-hump map as a point in a huge space. $g$ is one point.",
                 anims=[Create(space), FadeIn(sl), FadeIn(gd, scale=2), FadeIn(gl)])
        movers = VGroup(*[Dot(to_xy(0, s), color=DIAG, radius=0.06) for s in (-2.2, -1.4, 1.5, 2.3)])
        self.play(Create(Ws), FadeIn(wl), FadeIn(movers))
        self.say(r"Applying $T$ moves the points. Along a whole surface (blue), maps are pulled toward $g$\ldots",
                 anims=[movers.animate.apply_function(lambda p: G + 0.25 * (p - G))], run_time=2)
        self.play(FadeOut(movers))
        off = Dot(to_xy(0.25, 1.2), color=ORBIT, radius=0.06)
        self.play(FadeIn(off))
        path = [off.get_center()]
        for _ in range(3):
            path.append(Tmap(path[-1]))
        self.say(r"\ldots but in \emph{one single direction} (red) they are pushed away, distances being "
                 r"multiplied by a fixed factor: this factor is $\delta$.",
                 anims=[GrowArrow(ua), FadeIn(ul),
                        Succession(*[off.animate(run_time=0.8).move_to(p) for p in path[1:]])], run_time=2.5)
        self.play(FadeOut(off))

        # family line and the R_n
        Q = to_xy(0, -1.0)
        D = np.array([0.95, -0.55, 0]); D /= np.linalg.norm(D)
        fam = Line(Q - 3.4 * D, Q + 3.6 * D, color=MAP, stroke_width=3)
        fl = Tex(r"logistic maps $f_r$", font_size=26, color=MAP).next_to(fam.get_end(), LEFT, buff=0.1).shift(0.45 * UP)
        q = Dot(Q, color=MAP, radius=0.07)
        ql = MathTex(r"r_\infty", font_size=28, color=MAP).next_to(q, LEFT, buff=0.12)
        u0 = 2.2
        def on_family(u):
            # point of the family line with unstable coordinate u
            M = np.array([U[:2], S[:2]]).T
            uD = np.linalg.solve(M, D[:2])[0]
            return Q + (u / uD) * D
        Rpts = [on_family(u0 / dc ** k) for k in range(4)]
        Rd = VGroup(*[Dot(p, color=FG, radius=0.06) for p in Rpts])
        Rl = VGroup(*[MathTex(f"R_{k+1}", font_size=24, color=FG).next_to(p, UP, buff=0.08)
                      for k, p in enumerate(Rpts[:3])])
        lvl = VGroup(*[DashedLine(p - 2.2 * S, p + 2.2 * S, color=MUTED, stroke_width=1.2, dash_length=0.08)
                       for p in Rpts])
        self.say(r"The logistic maps form a line in this space, crossing the blue surface at $r_\infty$. "
                 r"On it: the special parameters $R_1, R_2, R_3,\ldots$",
                 anims=[Create(fam), FadeIn(fl), FadeIn(q), FadeIn(ql), FadeIn(Rd), FadeIn(Rl)], extra=0.3)
        self.play(Create(lvl))
        new = [Tmap(p) for p in Rpts]
        fam2 = Line(Tmap(fam.get_start()), Tmap(fam.get_end()), color=MAP, stroke_width=3, stroke_opacity=0.5)
        self.say(r"One period doubling is one application of $T$: it sends $R_{n+1}$ onto the level "
                 r"(dashed) where $R_n$ was. So the gaps between the $R_n$ shrink by exactly $\delta$.",
                 anims=[TransformFromCopy(fam, fam2)] + [Rd[k].animate.move_to(new[k]) for k in range(4)],
                 run_time=2.5, extra=0.8)
        self.play(FadeOut(fam2), *[Rd[k].animate.move_to(Rpts[k]) for k in range(4)])
        Q2 = to_xy(0, 1.6)
        D2 = np.array([0.9, 0.35, 0]); D2 /= np.linalg.norm(D2)
        fam_s = Line(Q2 - 3.0 * D2, Q2 + 3.2 * D2, color=STABLE, stroke_width=3)
        fsl = Tex(r"sine maps, Ricker, a heated fluid\ldots", font_size=26, color=STABLE
                  ).next_to(fam_s.get_end(), DOWN, buff=0.15).shift(0.4 * LEFT)
        self.say(r"Any other family crosses the same surface and feels the same $T$ near the same $g$: "
                 r"same $\delta$, same $\alpha$. \emph{That} is universality.",
                 anims=[Create(fam_s), FadeIn(fsl)], extra=0.8)
        nts = Tex(r"(schematic, not to scale)", font_size=22, color=MUTED).next_to(space, DOWN, buff=-0.4).shift(4.6 * RIGHT)
        self.play(FadeIn(nts))
        cartoon = VGroup(space, sl, Ws, wl, gd, gl, ua, ul, fam, fl, q, ql, Rd, Rl, lvl, fam_s, fsl, nts)
        self.play(FadeOut(cartoon))

        summary = VGroup(
            MathTex(r"\delta = 4.669\,201\,609\ldots", color=ACCENT),
            Tex(r"how strongly doubling pushes away from $g$", font_size=32, color=MUTED),
            MathTex(r"\alpha = -2.502\,907\,875\ldots", color=ACCENT),
            Tex(r"the zoom factor that makes $g$ reproduce itself", font_size=32, color=MUTED),
        ).arrange(DOWN, buff=0.25).move_to([0, 0.5, 0])
        summary[2].shift(0.3 * DOWN); summary[3].shift(0.3 * DOWN)
        self.say(r"$\delta$ and $\alpha$ are not properties of a parabola, nor of a fluid: "
                 r"they are properties of \emph{period doubling itself}.",
                 anims=[FadeIn(summary, lag_ratio=0.3)], run_time=2, extra=1.0)
        self.play(FadeOut(summary))
        self.unsay()
