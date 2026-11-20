"""Seq 4 — Beyond r_inf: sensitivity, Lyapunov exponent (link to Seq 2), windows, self-similarity."""
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE, ACCENT, DENSITY_STOPS
from common.narrative import Narrated
from common.logistic import orbit, lyapunov, R_INF, bifurcation_density, density_to_rgb
from _stages import *

RC = 3.9
EPS = 1e-8
N = 50
WIN = (3.8284, 3.8572, 0.455, 0.555)    # period-3 window, middle branch


class Chaos(Narrated):
    def construct(self):
        st = bif_stage()
        ax = st["ax"]
        mk, badge = rinf_marker(ax), delta_badge()
        self.add(st["ax"], st["lab"], st["img"], mk, badge)
        self.chapter(r"3 \,$\cdot$\, The period-doubling cascade", animate=False)
        self.chapter(r"4 \,$\cdot$\, Beyond $r_\infty$: chaos")

        zone = Rectangle(width=ax.c2p(4, 0)[0] - ax.c2p(R_INF, 0)[0], height=ax.y_length,
                         stroke_width=0, fill_color=ORBIT, fill_opacity=0.12
                         ).move_to(ax.c2p((R_INF + 4) / 2, 0.5))
        self.say(r"Beyond $r_\infty$ the long-term values fill entire bands. "
                 r"Has the population become random?", anims=[FadeIn(zone)])
        rl = Line(ax.c2p(RC, 0), ax.c2p(RC, 1), color=ORBIT, stroke_width=3)
        self.say(r"Let's look at a single orbit, at $r = 3.9$.", anims=[Create(rl)])
        self.play(FadeOut(Group(st["ax"], st["lab"], st["img"], mk, zone, rl)))

        # --- two orbits
        top = Axes(x_range=[0, N, 10], y_range=[0, 1, 0.5], x_length=11, y_length=2.4, tips=False,
                   axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}).move_to([0.3, 1.55, 0])
        bot = Axes(x_range=[0, N, 10], y_range=[-9, 0, 3], x_length=11, y_length=2.2, tips=False,
                   axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}).move_to([0.3, -1.55, 0])
        tl = MathTex("x_n", font_size=28, color=MUTED).next_to(top.y_axis, UP, buff=0.05)
        bl = MathTex(r"\log_{10}|\varepsilon_n|", font_size=28, color=MUTED).next_to(bot.y_axis, UP, buff=0.05)
        a, b = orbit(RC, 0.2, N), orbit(RC, 0.2 + EPS, N)

        def trace(ax_, vals, color, w=2):
            m = VMobject(stroke_color=color, stroke_width=w).set_points_as_corners(
                [ax_.c2p(i, v) for i, v in enumerate(vals)])
            return VGroup(m, *[Dot(ax_.c2p(i, v), radius=0.03, color=color) for i, v in enumerate(vals)])

        ta, tb = trace(top, a, ORBIT), trace(top, b, DIAG, 1.5)
        self.play(Create(top), FadeIn(tl))
        self.say(r"Nothing random here: the rule is exact, and $x_0$ determines the whole future.",
                 anims=[Create(ta, run_time=3)])
        self.say(r"Now start a second orbit (blue) at $x_0 + 10^{-8}$ — a difference far below any "
                 r"possible measurement.", anims=[Create(tb, run_time=3)])
        sep = int(np.argmax(np.abs(a - b) > 0.05))
        hl = Rectangle(width=top.c2p(N, 0)[0] - top.c2p(sep, 0)[0], height=top.y_length,
                       stroke_width=0, fill_color=FG, fill_opacity=0.08).move_to(top.c2p((sep + N) / 2, 0.5))
        self.say(rf"For about {sep} steps they are indistinguishable. Then they have nothing in common.",
                 anims=[FadeIn(hl)])

        eps = np.log10(np.abs(a - b) + 1e-300)
        eps[0] = -8
        de = VGroup(*[Dot(bot.c2p(i, max(v, -9)), radius=0.035, color=ACCENT) for i, v in enumerate(eps)])
        fit_n = np.arange(0, sep)
        slope, icpt = np.polyfit(fit_n, eps[:sep], 1)
        lam = slope * np.log(10)
        fit = Line(bot.c2p(0, icpt), bot.c2p(sep + 4, icpt + slope * (sep + 4)), color=MAP)
        self.play(Create(bot), FadeIn(bl))
        self.say(r"Plot the gap $\varepsilon_n = |x_n - x_n'|$ on a logarithmic scale\ldots",
                 anims=[FadeIn(de, lag_ratio=0.05)], run_time=2.5)
        self.say(rf"\ldots it grows along a straight line: multiplied by the same factor at every step, "
                 rf"$\varepsilon_n \approx \varepsilon_0\, e^{{\lambda n}}$ with $\lambda \approx {lam:.2f}$.",
                 anims=[Create(fit)])
        self.say(r"This is \emph{sensitive dependence on initial conditions}: any error, however tiny, "
                 r"ends up as large as the signal. Long-term prediction is impossible.", extra=0.5)
        self.play(FadeOut(VGroup(top, bot, tl, bl, ta, tb, hl, de, fit)))

        # --- link with Seq 2: Lyapunov exponent
        steps = VGroup(
            MathTex(r"\varepsilon_{n+1} \approx |f'(x_n)|\;\varepsilon_n"),
            MathTex(r"\varepsilon_{n} \approx |f'(x_{n-1})|\cdots|f'(x_1)|\,|f'(x_0)|\;\varepsilon_0"),
            MathTex(r"\lambda = \lim_{n\to\infty}\frac1n\sum_{k=0}^{n-1}\ln|f'(x_k)|", color=ACCENT),
        ).arrange(DOWN, buff=0.55).move_to([0, 0.6, 0])
        self.say(r"Why exponential? Remember chapter 2: one step multiplies a small error by "
                 r"the slope $|f'(x_n)|$ of the curve where the orbit is.", anims=[Write(steps[0])])
        self.say(r"After $n$ steps the factors multiply. Unlike the fixed point, the orbit visits "
                 r"places where the slope is steep and places where it is flat.", anims=[Write(steps[1])])
        self.say(r"The average growth rate is the \emph{Lyapunov exponent} $\lambda$: "
                 r"the mean of $\ln|f'|$ along the orbit.", anims=[Write(steps[2])])
        signs = VGroup(Tex(r"$\lambda < 0$: errors die out $\to$ stable cycle", color=STABLE),
                       Tex(r"$\lambda > 0$: errors explode $\to$ chaos", color=ORBIT)
                       ).arrange(DOWN, aligned_edge=LEFT).scale(0.8).next_to(steps, DOWN, buff=0.5)
        self.play(FadeIn(signs, lag_ratio=0.4))
        self.wait(2.5)
        self.play(FadeOut(steps), FadeOut(signs))

        # --- lambda(r) under the diagram
        ax2 = bif_axes(y_length=3.5, center=(0.35, 1.2, 0))
        img2 = image_on_axes(bif_rgb(ax2), ax2)
        lax = Axes(x_range=[2.8, 4, 0.2], y_range=[-1.5, 0.75, 0.75], x_length=ax2.x_length, y_length=1.9,
                   tips=False, axis_config={"color": MUTED, "font_size": 20},
                   y_axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 2}}
                   ).move_to([0.35, -1.7, 0])
        lax.shift((ax2.c2p(2.8, 0)[0] - lax.c2p(2.8, 0)[0]) * RIGHT)
        llab = MathTex(r"\lambda", font_size=32, color=MUTED).next_to(lax.y_axis, LEFT, buff=0.6)
        rs = np.linspace(2.8, 4, 900)
        lv = np.clip(lyapunov(rs, transient=600, n=1500), -1.5, 0.75)
        segs = VGroup(*[Line(lax.c2p(r0, l0), lax.c2p(r1, l1), stroke_width=2,
                             color=ORBIT if (l0 + l1) > 0 else STABLE)
                        for r0, r1, l0, l1 in zip(rs[:-1], rs[1:], lv[:-1], lv[1:])])
        zero = DashedLine(lax.c2p(2.8, 0), lax.c2p(4, 0), color=MUTED, stroke_width=1)
        mk2 = rinf_marker(ax2)
        self.play(FadeIn(Group(ax2, img2, mk2)), Create(lax), FadeIn(llab), Create(zero))
        self.say(r"Compute $\lambda$ for every $r$, aligned with the diagram: negative before $r_\infty$ "
                 r"(touching 0 at each fork), mostly positive after.", anims=[Create(segs, run_time=3)])
        rw = 1 + np.sqrt(8)
        arr = Arrow(lax.c2p(rw + 0.08, -1.2), lax.c2p(rw + 0.01, -0.9), color=FG, buff=0, stroke_width=3)
        self.say(r"But inside the chaos there are \emph{windows} where $\lambda < 0$: order is back. "
                 r"The widest one starts at $r = 1+\sqrt8 \approx 3.828$, with a cycle of period 3.",
                 anims=[GrowArrow(arr)])

        # --- zoom into the window
        self.play(FadeOut(VGroup(lax, llab, segs, zero, arr)), FadeOut(mk2), FadeOut(ax2))
        frame = Rectangle(width=ax2.x_length, height=ax2.y_length, stroke_color=MUTED, stroke_width=1
                          ).move_to(ax2.get_center())
        W, H = bif_pixels(ax2)
        s = ValueTracker(0.0)

        def win(u):
            g = lambda a0, a1: a0 + (a1 - a0) * (1 - (1 - u) ** 3) if False else None  # noqa
            # geometric interpolation of the window size, centred on the target window
            r0, r1, x0, x1 = 2.8, 4.0, 0.0, 1.0
            R0, R1, X0_, X1 = WIN
            k = u
            w = (r1 - r0) * ((R1 - R0) / (r1 - r0)) ** k
            h = (x1 - x0) * ((X1 - X0_) / (x1 - x0)) ** k
            cr = r0 + (r1 - r0) / 2 + ((R0 + R1) / 2 - (r0 + r1) / 2) * (1 - ((R1 - R0) / (r1 - r0)) ** k) / (1 - (R1 - R0) / (r1 - r0))
            cx = 0.5 + ((X0_ + X1) / 2 - 0.5) * (1 - ((X1 - X0_) / (x1 - x0)) ** k) / (1 - (X1 - X0_) / (x1 - x0))
            return cr - w / 2, cr + w / 2, cx - h / 2, cx + h / 2

        def zimg():
            r0, r1, x0, x1 = win(s.get_value())
            dens = bifurcation_density(r0, r1, x0, x1, W, H, transient=3000, samples=int(1.3 * H))
            m = ImageMobject(density_to_rgb(dens, DENSITY_STOPS))
            m.stretch_to_fit_width(ax2.x_length).stretch_to_fit_height(ax2.y_length).move_to(ax2.get_center())
            m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            return m

        zi = zimg()
        self.remove(img2)
        self.add(zi, frame)
        zi.add_updater(lambda m: m.become(zimg()))
        self.say(r"Zoom into the middle branch of this window\ldots",
                 anims=[s.animate.set_value(1.0)], run_time=8)
        zi.clear_updaters()
        self.say(r"\ldots a miniature copy of the whole diagram: period doubling $3\to6\to12\to\cdots$, "
                 r"chaos, windows. And its forks shrink by the same factor $\delta = 4.669\ldots$", extra=1.0)
        self.say(r"Why the same number, again and again?", extra=0.5)
        self.play(FadeOut(zi), FadeOut(frame), FadeOut(badge))
        self.unsay()
