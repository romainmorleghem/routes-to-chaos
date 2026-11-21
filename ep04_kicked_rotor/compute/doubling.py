"""Period-doubling cascade in the area-preserving Henon map  T(x, y) = (1 - a x^2 + y, -x)  (det = 1).
It is the generic local model of an elliptic orbit losing stability in any area-preserving map
(the conservative cousin of Part 1's x -> 1 - a x^2). Fixed point doubles at a = 3.
a_k = value where the residue R = (2 - tr M)/4 of the 2^(k-1)-orbit reaches 1.
Exact tangent maps: no time step, precision limited by double arithmetic only."""
import json
from pathlib import Path
import numpy as np
from numba import njit
from scipy.optimize import brentq

OUT = Path(__file__).resolve().parents[1] / "data" / "doubling.json"
NK = 10


@njit(cache=True)
def mono(x, y, a, q):
    m00, m01, m10, m11 = 1.0, 0.0, 0.0, 1.0
    for i in range(q):
        j = -2.0 * a * x
        m00, m01, m10, m11 = j * m00 + m10, j * m01 + m11, -m00, -m01
        x, y = 1.0 - a * x * x + y, -x
    return x, y, m00, m01, m10, m11


def periodic(x, y, a, q, it=60):
    for _ in range(it):
        X, Y, m00, m01, m10, m11 = mono(x, y, a, q)
        J = np.array([[m00 - 1, m01], [m10, m11 - 1]])
        try:
            d = np.linalg.solve(J, [x - X, y - Y])
        except np.linalg.LinAlgError:
            return None
        x, y = x + d[0], y + d[1]
        if not np.isfinite(x):
            return None
        if abs(d).max() < 1e-15 * (1 + abs(x)):
            break
    X, Y, m00, m01, m10, m11 = mono(x, y, a, q)
    if abs(X - x) + abs(Y - y) > 1e-9:
        return None
    return x, y, (2 - (m00 + m11)) / 4, np.array([[m00, m01], [m10, m11]])


def distinct(t, a, half):
    X, Y, *_ = mono(t[0], t[1], a, half)
    return np.hypot(X - t[0], Y - t[1]) > 1e-7


TREE = []


def orbit_x(x, y, a, q):
    xs = []
    for _ in range(q):
        x, y = 1 - a * x * x + y, -x
        xs.append(x)
    return xs


def run():
    for a in np.linspace(1.0, 3.0, 60):
        xf = (-1 + np.sqrt(1 + a)) / a
        TREE.append([a, [xf]])
    a0 = 3.0
    x = (-1 + np.sqrt(1 + a0)) / a0
    v, q, A, gap = np.array([x, -x]), 1, [a0], 1.0
    for k in range(1, NK):
        ak = A[-1]
        eta = 1e-4 * gap
        s = periodic(*v, ak + eta, q)
        ev, V = np.linalg.eig(s[3])
        e = V[:, np.argmin(np.abs(ev + 1))].real
        w = None
        for c in np.geomspace(1e-3, 30, 40) * np.sqrt(eta):
            for sg in (1, -1):
                t = periodic(*(np.array(s[:2]) + sg * c * e), ak + eta, 2 * q)
                if t is not None and distinct(t, ak + eta, q) and 0 <= t[2] < 1:
                    w = t; break
            if w is not None:
                break
        if w is None:
            print("seed failed after", A); break
        q *= 2
        aa, cur, prev, j = ak + eta, w, None, 0
        while cur[2] < 1:
            prev = (aa, cur)
            TREE.append([aa, orbit_x(cur[0], cur[1], aa, q)])
            j += 1
            aa = ak + eta * 1.05 ** j
            cur = periodic(cur[0], cur[1], aa, q)
            if cur is None or not distinct(cur, aa, q // 2):
                print("stop: orbit lost (double precision limit)"); return A
                raise RuntimeError("lost orbit q=%d a=%.15f" % (q, aa))
        st = {"x": prev[1][:2]}

        def f(b):
            r = periodic(*st["x"], b, q)
            st["x"] = r[:2]
            return r[2] - 1
        an = brentq(f, prev[0], aa, xtol=1e-16, rtol=1e-15)
        r = periodic(*st["x"], an, q)
        v, gap = np.array(r[:2]), an - ak
        A.append(an)
        d = (A[-2] - A[-3]) / (A[-1] - A[-2]) if len(A) > 2 else float("nan")
        print("k=%d period=%d a=%.15f R=%.12f delta=%.6f" % (k + 1, q, an, r[2], d), flush=True)
    return A


A = run()
d = [(A[i] - A[i - 1]) / (A[i + 1] - A[i]) for i in range(1, len(A) - 1)]
OUT.write_text(json.dumps({"a_k": A, "periods": [2 ** i for i in range(len(A))], "delta_k": d, "tree": TREE}, indent=1))
