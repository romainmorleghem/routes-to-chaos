"""Period doublings of the Lorenz flow near rho = 100, located precisely.

Poincare section z = Z0 (upward). For each k, the orbit with n_k = n_0 * 2^k crossings is tracked
by Newton on P^{n_k}(v) = v; its Floquet multiplier mu(rho) (eigenvalue of DP^{n_k}, the one near -1)
is computed, and rho_k solves mu(rho) = -1 (secant). The doubled orbit (2 n_k crossings) is then
seeded from the eigenvector of the multiplier -1 to start the next k.
Convergence is checked by halving dt. Output: data/doubling_floquet.json
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.lorenz import return_map, z_maxima, trajectory

S, B = 10.0, 8.0 / 3.0
Z0 = 98.0
OUT = Path(__file__).resolve().parents[1] / "data" / "doubling_floquet.json"


def P(v, n, r, dt):
    return np.array(return_map(v[0], v[1], Z0, n, dt, S, r, B))


def jac(v, n, r, dt, h=1e-7):
    J = np.empty((2, 2))
    for k in range(2):
        e = np.zeros(2); e[k] = h * max(1.0, abs(v[k]))
        J[:, k] = (P(v + e, n, r, dt) - P(v - e, n, r, dt)) / (2 * e[k])
    return J


def fixed(v, n, r, dt):
    for _ in range(30):
        g = P(v, n, r, dt) - v
        J = jac(v, n, r, dt)
        dv = np.linalg.solve(J - np.eye(2), -g)
        v = v + dv
        if np.linalg.norm(dv) < 1e-11 * (1 + np.linalg.norm(v)):
            break
    return v, jac(v, n, r, dt)


def mu_minus(J):
    ev = np.linalg.eigvals(J)
    return ev[np.argmin(np.abs(ev + 1))].real


def locate(v, n, r_hi, r_lo, dt):
    """Brent's method on mu(rho) + 1 = 0 in [r_lo, r_hi]; the orbit is tracked from the last good point."""
    from scipy.optimize import brentq
    state = {"v": v}
    def g(r):
        w, J = fixed(state["v"], n, r, dt)
        if not np.all(np.isfinite(J)):
            w, J = track(state["v"], n, state.get("r", r_hi), r, dt, steps=8)
        state["v"], state["r"], state["J"] = w, r, J
        return mu_minus(J) + 1
    rk = brentq(g, r_lo, r_hi, xtol=1e-12, rtol=1e-14)
    g(rk)
    return rk, state["v"], state["J"]


def track(v, n, r_from, r_to, dt, steps=12):
    """continuation of the n-orbit from r_from to r_to"""
    for r in np.linspace(r_from, r_to, steps + 1)[1:]:
        v, J = fixed(v, n, r, dt)
    return v, J


def seed_double(v, n, r, J, dt):
    """the 2n-orbit exists just below the doubling, at v +- c * eigenvector(-1): try amplitudes until
    Newton lands on a genuine 2n-orbit (not back on the n-orbit, which is also fixed by P^{2n})"""
    ev, V = np.linalg.eig(J)
    e = V[:, np.argmin(np.abs(ev + 1))].real
    for c in (0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2):
        w, _ = fixed(v + c * e, 2 * n, r, dt)
        if np.all(np.isfinite(w)) and np.linalg.norm(P(w, n, r, dt) - w) > 1e-4:
            return w
    raise RuntimeError("could not seed the doubled orbit")


def run(dt, rho_guess):
    r = 100.3
    # land on the stable orbit by brute force (linear-interpolated crossings), then polish by Newton
    tr = trajectory(np.array([1.0, 1.0, r + 4.0]), 4_000_000, 0.0005, S, r, B)[3_000_000:]
    z = tr[:, 2]
    idx = np.where((z[:-1] < Z0) & (z[1:] >= Z0))[0]
    pts = tr[idx, :2]
    n0 = next(n for n in range(1, 10) if np.linalg.norm(pts[-1] - pts[-1 - n]) < 0.05)
    v, _ = fixed(pts[-1].copy(), n0, r, dt)
    v, _ = track(v, n0, r, rho_guess[0][1], dt)
    out, n = [], n0
    for k, (lo, hi) in enumerate(rho_guess):
        rk, v, J = locate(v, n, hi, lo, dt)
        out.append((rk, n))
        print("dt=%g k=%d crossings=%d rho_k=%.10f mu=%.8f" % (dt, k + 1, n, rk, mu_minus(J)), flush=True)
        if k + 1 == len(rho_guess):
            break
        rs = rk - 0.02 * (rk - rho_guess[k + 1][1])
        v, J = fixed(v, n, rs, dt)
        v = seed_double(v, n, rs, J, dt)
        n *= 2
        v, _ = track(v, n, rs, rho_guess[k + 1][1], dt)
    return n0, out


def main():
    guess = [(99.97, 99.99), (99.62, 99.64), (99.543, 99.551), (99.5275, 99.5295), (99.5245, 99.5265),
             (99.5236, 99.5246)]
    res = {}
    for dt in (0.002, 0.001):
        n0, out = run(dt, guess)
        rk = [r for r, _ in out]
        d = [(rk[i - 1] - rk[i]) / (rk[i] - rk[i + 1]) for i in range(1, len(rk) - 1)]
        print("dt", dt, "delta_k", d, flush=True)
        res[str(dt)] = {"n0": n0, "rho_k": rk, "crossings": [n for _, n in out], "delta_k": d}
        # refine the guesses for the next dt
        guess = [(r - 2e-4, r + 2e-4) for r in rk]
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
