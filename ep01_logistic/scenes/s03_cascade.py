"""Sequence 3 — the period-doubling cascade and the convergence of the ratios to delta."""
from _common import *  # noqa
from manim import *
from common.style import FG, MUTED, ACCENT

ROWS = 9


class Cascade(Scene):
    def construct(self):
        title = Tex(r"Where the period doubles", color=FG).to_edge(UP)
        self.play(Write(title))
        r = DATA["r_str"][:ROWS]
        dr = DATA["delta_r"]
        head = [MathTex(s, color=MUTED) for s in
                (r"n", r"\text{period}", r"r_n",
                 r"\dfrac{r_{n}-r_{n-1}}{r_{n+1}-r_{n}}")]
        rows = []
        for n in range(ROWS):
            ratio = f"{dr[n-1]:.7f}" if 1 <= n <= len(dr) and n < ROWS - 1 else ""
            rows.append([MathTex(str(n + 1)), MathTex(rf"{2**n}\to{2**(n+1)}"),
                         MathTex(r[n][:12]), MathTex(ratio, color=ACCENT) if ratio else MathTex("")])
        table = MobjectTable([head] + rows, include_outer_lines=False,
                             line_config={"stroke_color": MUTED, "stroke_width": 1},
                             v_buff=0.18, h_buff=0.7).scale(0.72).next_to(title, DOWN)
        self.play(Create(table.get_horizontal_lines()[0]),
                  *[Write(m) for m in table.get_rows()[0]])
        for i, row in enumerate(table.get_rows()[1:]):
            self.play(*[FadeIn(m, shift=0.1 * LEFT) for m in row],
                      run_time=0.9 if i < 4 else 0.45)
        self.wait()
        delta = MathTex(r"\delta = \lim_{n\to\infty}\frac{r_{n}-r_{n-1}}{r_{n+1}-r_{n}}"
                        r" = 4.669\,201\,609\,102\,990\ldots", color=ACCENT).scale(0.9)
        delta.to_edge(DOWN)
        self.play(Write(delta), run_time=2)
        self.play(Circumscribe(delta, color=ACCENT))
        self.wait(2)
