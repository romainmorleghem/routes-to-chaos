"""Period-doubling cascade of the Lorenz flow in the window rho ~ 99.5-100.8 (sigma=10, beta=8/3).

Count distinct z-maxima on the attractor: 3 -> 6 -> 12 -> 24 as rho decreases.
Locate each doubling rho_k by bisection, then delta_k = (rho_{k-1}-rho_k)/(rho_k-rho_{k+1}).
Also store the bifurcation diagram (z-maxima vs rho) for the video and the website.
Output: data/bifurcation.json
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.lorenz import z_maxima

OUT = Path(__file__).resolve().parents[1] / "data" / "bifurcation.json"
DT = 0.001


def maxima(r, n=6_000_000, skip=4_000_000):
    return z_maxima(np.array([1.0, 1.0, r + 4.0]), n, DT, skip, r=r)


def count(r, tol):
    s = np.sort(maxima(r))
    return 1 + int(np.sum(np.diff(s) > tol))


def doubling(lo, hi, target, tol, it=18):
    """lo has >= target clusters, hi has fewer."""
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if count(mid, tol) >= target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    rk = []
    brackets = [(99.9, 100.05, 6), (99.6, 99.65, 12), (99.53, 99.56, 24), (99.515, 99.535, 48)]
    for lo, hi, target in brackets:
        # symmetric maxima can merge within tol: accept one cluster fewer
        rk.append(doubling(lo, hi, target - 1, tol=5e-4))
        print("doubling to", target, "at rho =", rk[-1], flush=True)
    deltas = [(rk[i - 1] - rk[i]) / (rk[i] - rk[i + 1]) for i in range(1, len(rk) - 1)]
    print("delta estimates", deltas)
    rhos = np.linspace(99.3, 100.85, 400)
    diag = [[float(r), np.round(maxima(r, 1_200_000, 1_000_000)[-60:], 4).tolist()] for r in rhos]
    wide = np.linspace(20, 220, 500)
    diag_wide = [[float(r), np.round(maxima(r, 400_000, 250_000)[-60:], 3).tolist()] for r in wide]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"sigma": 10, "beta": 8 / 3, "rho_k": rk, "delta_k": deltas,
                               "window": diag, "wide": diag_wide}))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
