"""Feigenbaum's delta for several one-hump maps -> data/universality.json.

Superstable parameters R_n solve f_r^{2^n}(x_c(r)) = x_c(r), x_c = critical point.
Quadratic maxima should all give delta = 4.6692..., the quartic one 7.2846...
"""
import json
from pathlib import Path
import mpmath as mp

mp.mp.dps = 50
OUT = Path(__file__).resolve().parents[1] / "data" / "universality.json"

MAPS = {
    "logistic": dict(f=lambda r, x: r * x * (1 - x), xc=lambda r: mp.mpf(1) / 2,
                     R=[2, 1 + mp.sqrt(5)], n0=0, tex=r"r\,x(1-x)"),
    "sine": dict(f=lambda a, x: a * mp.sin(mp.pi * x), xc=lambda a: mp.mpf(1) / 2,
                 R=[0.5, 0.7777], n0=0, tex=r"a\sin(\pi x)"),
    "ricker": dict(f=lambda r, x: x * mp.exp(r * (1 - x)), xc=lambda r: 1 / r,
                   R=[1, 2.5], n0=0, tex=r"x\,e^{\,r(1-x)}"),
    "quartic": dict(f=lambda a, x: 1 - a * x ** 4, xc=lambda a: mp.mpf(0),
                    R=[1, 1.6], n0=1, tex=r"1-a\,x^4"),
}


def F(m, n, r):
    x = m["xc"](r)
    y = x
    for _ in range(2 ** n):
        y = m["f"](r, y)
    return y - x


def newton(m, n, r, steps=80):
    """Newton with complex-step derivative (F is analytic in r)."""
    h = mp.mpf(10) ** -30
    r = mp.mpf(r)
    for _ in range(steps):
        Fr = F(m, n, r)
        dF = mp.im(F(m, n, mp.mpc(r, h))) / h
        step = Fr / dF
        r -= step
        if abs(step) < mp.mpf(10) ** -40:
            return r
    raise RuntimeError(f"no convergence n={n}")


def cascade(m, n_max):
    n0 = m["n0"]
    R = [newton(m, n0, m["R"][0]), newton(m, n0 + 1, m["R"][1])]
    d = 4.67 if m is not MAPS["quartic"] else 7.3
    for k in range(2, n_max + 1):
        g = R[-1] + (R[-1] - R[-2]) / d
        R.append(newton(m, n0 + k, g))
        d = (R[-2] - R[-3]) / (R[-1] - R[-2])
    deltas = [(R[i - 1] - R[i - 2]) / (R[i] - R[i - 1]) for i in range(2, len(R))]
    return R, deltas


def main():
    out = {}
    for name, m in MAPS.items():
        R, d = cascade(m, 10)
        out[name] = {"tex": m["tex"], "R": [float(v) for v in R], "delta": [float(v) for v in d]}
        print(f"{name:9s} R0={float(R[0]):.6f} delta -> " + "  ".join(f"{float(v):.6f}" for v in d[-4:]))
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
