"""Unstable periodic orbits of Lorenz (rho=28): the 'skeleton' of the attractor.

Poincare section z = rho-1 = 27, upward crossings. P: (x,y) -> (x,y). Fixed points of P^n found by
Newton (finite-difference Jacobian) from close returns of a long chaotic orbit. Symbolic label: L/R =
sign of x at each crossing. Keep the shortest distinct words (up to symmetry/cyclic shift).
Output: data/upo.json (orbit points for drawing, period T, word, leading Floquet multiplier).
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.lorenz import section_return, trajectory

OUT = Path(__file__).resolve().parents[1] / "data" / "upo.json"
ZS, DT = 27.0, 0.001


def P(v, n):
    p = np.array([v[0], v[1], ZS]); T = 0.0; word = ""
    for _ in range(n):
        p, t = section_return(p, DT, ZS)
        T += t; word += "R" if p[0] > 0 else "L"
    return p[:2], T, word


def newton(v, n):
    for _ in range(40):
        f, T, w = P(v, n)
        g = f - v
        if not np.all(np.isfinite(g)):
            return None
        if np.linalg.norm(g) < 1e-9:
            J = np.empty((2, 2)); h = 1e-6
            for k in range(2):
                e = np.zeros(2); e[k] = h
                J[:, k] = (P(v + e, n)[0] - P(v - e, n)[0]) / (2 * h)
            return v, T, w, float(max(abs(np.linalg.eigvals(J))))
        J = np.empty((2, 2)); h = 1e-6
        for k in range(2):
            e = np.zeros(2); e[k] = h
            J[:, k] = (P(v + e, n)[0] - f) / h
        v = v - np.linalg.solve(J - np.eye(2), g)
    return None


def canon(w):
    sym = w.translate(str.maketrans("LR", "RL"))
    return min(min(x[i:] + x[:i] for i in range(len(x))) for x in (w, sym))


def main():
    # crossings of a long orbit
    p = np.array([1.0, 1.0, ZS]); pts = []
    for _ in range(4000):
        p, _ = section_return(p, DT, ZS); pts.append(p[:2].copy())
    pts = np.array(pts)
    found = {}
    for n in range(1, 7):
        d = np.linalg.norm(pts[n:] - pts[:-n], axis=1)
        for i in np.argsort(d)[:40]:
            r = newton(pts[i].copy(), n)
            if r is None:
                continue
            v, T, w, mu = r
            c = canon(w)
            if len(w) != n or c in found or len(set(w)) < 2:   # skip L^n (not on attractor)
                continue
            q = trajectory(np.array([v[0], v[1], ZS]), int(T / 0.002) + 1, 0.002)
            found[c] = {"word": w, "T": T, "mu": mu, "pts": np.round(q, 3).tolist()}
            print(n, w, "T=%.4f" % T, "mu=%.3f" % mu, flush=True)
    OUT.write_text(json.dumps(sorted(found.values(), key=lambda o: (len(o["word"]), o["word"]))))
    print("wrote", len(found))


if __name__ == "__main__":
    main()
