"""Facts about the Mandelbrot set used in episode 2, computed rather than quoted.

- p/q bulbs: root on the main cardioid at angle 2*pi*p/q, centre (superstable c), size ~ |centre - root|,
  rotation number of the attracting q-cycle.
- Farey check: between the p/q and p'/q' bulbs, the largest bulb is the mediant (p+p')/(q+q').
- Real axis: period-doubling centres c_n and the ratio of gaps -> Feigenbaum delta.
Output: data/bulbs.json
"""
import json
from fractions import Fraction
from pathlib import Path
import numpy as np
import mpmath as mp

mp.mp.dps = 40
OUT = Path(__file__).resolve().parents[1] / "data" / "bulbs.json"


def cardioid(theta):
    w = mp.e ** (1j * theta) / 2
    return w - w * w                       # c such that the fixed point z* = w has multiplier e^{i theta}


def centre(q, guess):
    """Newton on P(c) = f_c^q(0) = 0 (superstable q-cycle)."""
    c = mp.mpc(guess)
    for _ in range(200):
        z, dz = mp.mpc(0), mp.mpc(0)
        for _ in range(q):
            dz = 2 * z * dz + 1
            z = z * z + c
        step = z / dz
        c -= step
        if abs(step) < mp.mpf(10) ** -30:
            return c
    raise RuntimeError


def rotation_number(c, q):
    """Rotation of the superstable cycle around the alpha fixed point."""
    alpha = (1 - mp.sqrt(1 - 4 * c)) / 2
    z, angles = mp.mpc(0), []
    for _ in range(q):
        angles.append(mp.arg(z - alpha))
        z = z * z + c
    steps = [((angles[(i + 1) % q] - angles[i]) / (2 * mp.pi)) % 1 for i in range(q)]
    return float(sum(steps) / q)


def bulb(p, q):
    th = 2 * mp.pi * p / q
    root = cardioid(th)
    normal = root - cardioid(th + mp.mpf("1e-6"))
    normal = 1j * normal / abs(normal)
    # pick the outward normal (pointing away from the cardioid's centre ~ c = 0)
    if abs(root + normal * 0.01) < abs(root):
        normal = -normal
    c = centre(q, root + normal * (mp.sin(mp.pi * p / q) / q ** 2))
    return dict(p=p, q=q, root=[float(root.real), float(root.imag)], centre=[float(c.real), float(c.imag)],
                size=float(abs(c - root)), rotation=rotation_number(c, q))


def main():
    out = {"bulbs": []}
    fr = sorted({Fraction(p, q) for q in range(2, 14) for p in range(1, q) if np.gcd(p, q) == 1 and p / q <= 0.5})
    for f in fr:
        out["bulbs"].append(bulb(f.numerator, f.denominator))
    by = {(b["p"], b["q"]): b for b in out["bulbs"]}
    # Farey: largest bulb strictly between 1/3 and 1/2 should be 2/5; between 2/5 and 1/2: 3/7, ...
    checks = []
    for a, b in [((1, 3), (1, 2)), ((2, 5), (1, 2)), ((1, 3), (2, 5)), ((1, 4), (1, 3))]:
        lo, hi = Fraction(*a), Fraction(*b)
        inside = [k for k in by if lo < Fraction(*k) < hi]
        big = max(inside, key=lambda k: by[k]["size"])
        med = (a[0] + b[0], a[1] + b[1])
        checks.append(dict(between=[a, b], largest=big, mediant=med, ok=big == med))
    out["farey_checks"] = checks
    # real-axis cascade (superstable centres), periods 1, 2, 4, ...
    cs = [mp.mpf(0), mp.mpf(-1)]
    for n in range(2, 11):
        g = cs[-1] + (cs[-1] - cs[-2]) / mp.mpf("4.6692")
        cs.append(centre(2 ** n, g).real)
    gaps = [cs[i] - cs[i + 1] for i in range(len(cs) - 1)]
    out["real_centres"] = [float(c) for c in cs]
    out["real_delta"] = [float(gaps[i] / gaps[i + 1]) for i in range(len(gaps) - 1)]
    out["period3_minibrot"] = float(centre(3, -1.75).real)
    OUT.write_text(json.dumps(out, indent=1))
    for b in out["bulbs"]:
        if b["q"] <= 8:
            print(f"{b['p']}/{b['q']}: centre {b['centre'][0]:+.6f}{b['centre'][1]:+.6f}i  size {b['size']:.5f}"
                  f"  q^2*size {b['q']**2*b['size']:.3f}  rot {b['rotation']:.4f}")
    for ch in checks:
        print("Farey", ch)
    print("real delta:", ["%.5f" % d for d in out["real_delta"][-4:]], " period-3 centre:", out["period3_minibrot"])


if __name__ == "__main__":
    main()
