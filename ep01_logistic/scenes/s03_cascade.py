"""Seq 3 — From one orbit to the bifurcation diagram; the cascade r_n and Feigenbaum's delta."""
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, MAP, DIAG, ORBIT, STABLE, ACCENT
from common.narrative import Narrated
from common.logistic import orbit, R_INF
from _stages import *

R = 3.5
TRANS = 30


class Cascade(Narrated):
    def construct(self):
        st = cobweb_stage(R, with_fixed_point=False)
        fp_dot = Dot(st["ax"].c2p(fixed_point(R), fixed_point(R)), color=ORBIT, radius=0.08)
        self.add(*st.values(), fp_dot)
        self.chapter(r"2 \,$\cdot$\, When a fixed point breaks", animate=False)
        self.chapter(r"3 \,$\cdot$\, The period-doubling cascade")
        ts = st["ts"]

        # --- from a time series to a column of points
        ser_t = series(ts, R, transient=TRANS)
        self.say(r"We only care about the long run. Forget the first steps (the \emph{transient}, in grey)\ldots",
                 anims=[Transform(st["ser"], ser_t)])
        tail = VGroup(*[d.copy() for d in st["ser"][1][TRANS:]])
        col_x = ts.c2p(N_IT, 0)[0] + 0.55
        self.add(tail)
        self.say(r"\ldots and keep the values the orbit returns to forever. Here: 4 values, the 4-cycle.",
                 anims=[AnimationGroup(*[d.animate.set_x(col_x) for d in tail], lag_ratio=0.03)],
                 run_time=2)

        # --- new graph: long-term values against r
        ax = bif_axes()
        lab = bif_axis_labels(ax)
        old = VGroup(*[v for k, v in st.items()], fp_dot)
        self.play(FadeOut(old), FadeOut(self.caption), run_time=1)
        self.caption = None
        self.play(Create(ax), FadeIn(lab))
        xs = orbit(R, X0, 400)[-64:]
        self.play(*[d.animate.move_to(ax.c2p(R, x)) for d, x in zip(tail, xs[: len(tail)])], run_time=1.5)
        rtick = MathTex(r"r=3.5", font_size=28, color=MAP).next_to(ax.c2p(R, 1), UP, buff=0.1)
        self.say(r"Plot those values above $r = 3.5$ on a new graph.", anims=[FadeIn(rtick)])
        extra = VGroup()
        for rv in (2.9, 3.2, 3.3):
            ys = np.unique(np.round(orbit(rv, X0, 600)[-32:], 4))
            extra.add(*[Dot(ax.c2p(rv, y), radius=0.05, color=ORBIT) for y in ys])
        self.say(r"Same for $r = 2.9$ (one value: a fixed point), $r = 3.2$ and $3.3$ (two values)\ldots",
                 anims=[FadeIn(extra, lag_ratio=0.2)])

        # --- sweep
        rgb = bif_rgb(ax)
        t = ValueTracker(0.0)
        img = image_on_axes(reveal(rgb, 0), ax)
        img.add_updater(lambda m: m.become(image_on_axes(reveal(rgb, t.get_value()), ax)))
        sweep = always_redraw(lambda: Line(ax.c2p(2.8 + 1.2 * t.get_value(), 0),
                                           ax.c2p(2.8 + 1.2 * t.get_value(), 1),
                                           color=FG, stroke_width=1.5, stroke_opacity=0.6))
        self.add(img, sweep)
        self.bring_to_front(tail, extra)
        self.say(r"\ldots and for every $r$. This is the \emph{bifurcation diagram}: "
                 r"the long-term behaviour of the population, for every fertility $r$.",
                 anims=[t.animate.set_value(1.0), FadeOut(rtick)], run_time=7, wait=1.0)
        self.play(FadeOut(tail), FadeOut(extra), FadeOut(sweep))
        img.clear_updaters()
        self.remove(sweep)
        self.say(r"Read it from left to right: one branch (fixed point), then 2, 4, 8\ldots "
                 r"and then a dark cloud. Chapters 1 and 2 were the left part.")

        # --- the forks r_n
        rn = DATA["r"][:5]
        lines = VGroup(*[DashedLine(ax.c2p(v, 0), ax.c2p(v, 1), color=FG, stroke_width=1.5,
                                    stroke_opacity=0.7) for v in rn])
        labs = VGroup(*[MathTex(f"r_{i+1}", font_size=26, color=FG).next_to(ax.c2p(v, 0), DOWN, buff=0.45)
                        for i, v in enumerate(rn[:3])])
        self.say(r"Each fork is a period doubling: $1\to2$ at $r_1 = 3$, $2\to4$ at "
                 r"$r_2 \approx 3.449$, $4\to8$ at $r_3 \approx 3.544$, $8 \to 16$ at $r_4\approx 3.5644$\ldots",
                 anims=[Create(lines, lag_ratio=0.3), FadeIn(labs)], run_time=2)
        braces = VGroup(*[BraceBetweenPoints(ax.c2p(rn[i], 1.0), ax.c2p(rn[i + 1], 1.0), UP,
                                             color=MAP, buff=0.05) for i in range(3)])
        blabs = VGroup(*[MathTex(rf"\Delta_{i+1}", font_size=26, color=MAP).next_to(b, UP, buff=0.05)
                         for i, b in enumerate(braces)])
        blabs[2].shift(0.15 * RIGHT)
        self.say(r"The forks come faster and faster. Measure the gaps between them: "
                 r"$\Delta_n = r_{n+1} - r_n$.", anims=[GrowFromCenter(b) for b in braces] + [FadeIn(blabs)])
        d = DATA["delta_r"]
        ratios = VGroup(MathTex(rf"\Delta_1 / \Delta_2 \approx {d[0]:.2f}", font_size=34, color=MAP),
                        MathTex(rf"\Delta_2 / \Delta_3 \approx {d[1]:.2f}", font_size=34, color=MAP)
                        ).arrange(DOWN, aligned_edge=LEFT).move_to(ax.c2p(3.0, 0.88))
        self.say(r"Each gap is roughly $4.7$ times shorter than the previous one.",
                 anims=[FadeIn(ratios, lag_ratio=0.5)], run_time=1.5)

        # --- the table
        diagram = Group(ax, lab, img, lines, labs, braces, blabs)
        self.play(FadeOut(ratios), diagram.animate.scale(0.5).to_edge(LEFT, buff=0.3).shift(0.3 * UP))
        rows = []
        rs = DATA["r_str"]
        for n in range(2, 10):
            ratio = f"{d[n-2]:.7f}"
            rows.append([MathTex(str(n)), MathTex(rf"{2**(n-1)}\to{2**n}"), MathTex(rs[n - 1][:12]),
                         MathTex(ratio, color=ACCENT)])
        head = [MathTex(s, color=MUTED) for s in (r"n", r"\text{period}", r"r_n",
                                                    r"\Delta_{n-1}/\Delta_{n}")]
        table = MobjectTable([head] + rows, include_outer_lines=False,
                             line_config={"stroke_color": MUTED, "stroke_width": 1},
                             v_buff=0.16, h_buff=0.55)
        table.scale_to_fit_width(6.6).move_to([3.55, 0.45, 0])
        self.play(Create(table.get_horizontal_lines()[0]), *[Write(m) for m in table.get_rows()[0]])
        self.say(r"Push the computation further (here with 60-digit precision): the ratio settles "
                 r"down to a precise number.",
                 anims=[AnimationGroup(*[FadeIn(r, shift=0.1 * LEFT) for r in table.get_rows()[1:]],
                                       lag_ratio=0.35)], run_time=4)
        dl = MathTex(r"\delta = \lim_{n\to\infty}\frac{\Delta_{n-1}}{\Delta_{n}} = 4.669\,201\,609\,102\,990\ldots",
                     color=ACCENT, font_size=36).next_to(table, DOWN, buff=0.3)
        self.say(r"This is \emph{Feigenbaum's constant} $\delta$, discovered in 1975 with a pocket calculator.",
                 anims=[Write(dl)], run_time=2)
        self.play(Circumscribe(dl, color=ACCENT))

        # --- r_inf
        self.play(FadeOut(table), FadeOut(dl), FadeOut(braces), FadeOut(blabs))
        diagram = Group(ax, lab, img, lines, labs)
        self.play(diagram.animate.scale(2).move_to(ORIGIN).shift(ax.get_center() * 0), run_time=1.2)
        self.play(Group(ax, lab, img, lines, labs).animate.shift(bif_axes().get_center() - ax.get_center()),
                  run_time=0.01)
        geo = MathTex(r"r_\infty = r_1 + \Delta_1 + \Delta_2 + \cdots \approx r_1 + \Delta_1\left(1 + \tfrac1\delta + \tfrac1{\delta^2} + \cdots\right)",
                      font_size=32, color=FG).move_to(ax.c2p(3.12, 0.9))
        mk = rinf_marker(ax)
        self.say(r"Since the gaps shrink geometrically, their sum is finite: infinitely many doublings "
                 r"fit before a limit $r_\infty = 3.569\,945\,6\ldots$", anims=[Write(geo)], run_time=2)
        self.play(FadeOut(lines), FadeOut(labs), Create(mk), FadeIn(delta_badge()))
        self.say(r"And beyond $r_\infty$?", extra=0.3)
        self.play(FadeOut(geo))
        self.unsay()
