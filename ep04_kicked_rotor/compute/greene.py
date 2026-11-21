"""Greene's residue criterion for the golden KAM torus of the standard map  p'=p+K sin th, th'=th+p'.
T = I2 o I1 with involutions I1(th,p) = (-th, p + K sin th), I2(th,p) = (p - th, p):
Fix(I1) = {th = 0, pi}, Fix(I2) = {p = 2 th}.  A symmetric orbit of type P/q starts at th0 in {0, pi};
q even -> after q/2 steps it is back on Fix(I1);  q odd -> after (q+1)/2 steps it lies on Fix(I2).
1-D Newton on p0, then residue R = (2 - tr M)/4 of the full period. The elliptic orbit (R > 0) is
continued in K; K_n solves R = 1/4 (Greene). K_n -> K_c, the break-up of the golden torus."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.kicked import monodromy, TWO_PI

OUT = Path(__file__).resolve().parents[1] / "data" / "greene.json"


def shoot(th0, p0, K, q, P):
    m = q // 2 if q % 2 == 0 else (q + 1) // 2
    for _ in range(50):
        t, p, a, b, c, d = monodromy(th0, p0, K, m)
        if q % 2 == 0:
            g, dg = t - th0 - np.pi * P, b
        else:
            g, dg = 2 * t - p - 2 * th0 - TWO_PI * P, 2 * b - d
        step = -g / dg
        p0 += step
        if abs(step) < 1e-14:
            break
    t, p, a, b, c, d = monodromy(th0, p0, K, q)
    err = abs(t - th0 - TWO_PI * P) + abs(p - p0)
    return p0, (2 - (a + d)) / 4, err


def K_n(P, q):
    """continue both symmetric orbits (th0 = 0 and pi) from small K; keep the one with R > 0"""
    Ks = np.concatenate([np.linspace(0.05, 0.9, 30 + q), np.linspace(0.9005, 1.03, 260 + q)])
    for th0 in (0.0, np.pi):
        p0, prev = TWO_PI * P / q, None
        for K in Ks:
            p0, R, err = shoot(th0, p0, K, q, P)
            if err > 1e-6 or (K > 0.96 and R < 0):
                break
            if R > 0.25:
                st = {"p": prev[1]}

                def f(k):
                    st["p"], r, _ = shoot(th0, st["p"], k, q, P)
                    return r - 0.25
                return th0, brentq(f, prev[0], K, xtol=1e-15)
            prev = (K, p0)
    raise RuntimeError("no elliptic orbit %d/%d" % (P, q))


fib = [1, 2]
while fib[-1] < 987:
    fib.append(fib[-1] + fib[-2])
out = []
for P, q in zip(fib[:-1], fib[1:]):
    th0, k = K_n(P, q)
    print(P, q, th0, "%.12f" % k, flush=True)
    out.append({"P": P, "q": q, "th0": th0, "K": k})
OUT.write_text(json.dumps(out, indent=1))
