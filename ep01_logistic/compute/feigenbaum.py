"""Compute the period-doubling cascade of the logistic map and Feigenbaum's constants.

Outputs ep01_logistic/data/cascade.json with
  - bifurcation points r_n  (period 2^(n-1) -> 2^n loses stability)
  - superstable points R_n  (x = 1/2 lies on the 2^n-cycle)
  - ratio estimates delta_n and alpha_n
  - rescaled curves f_{R_n}^{2^n} around x = 1/2 for the renormalisation scene.
Uses mpmath at 60 digits so that ratios stay accurate deep in the cascade.
"""
import json
from pathlib import Path
import mpmath as mp

mp.mp.dps = 60
OUT = Path(__file__).resolve().parents[1] / "data" / "cascade.json"


def iterate(r, x, n):
    """Return f^n(x) and its derivatives d/dx and d/dr."""
    dx, dr = mp.mpf(1), mp.mpf(0)
    for _ in range(n):
        dr = x * (1 - x) + r * (1 - 2 * x) * dr
        dx = r * (1 - 2 * x) * dx
        x = r * x * (1 - x)
    return x, dx, dr


def superstable(n_max=13):
    R = [mp.mpf(2), 1 + mp.sqrt(5)]
    for n in range(2, n_max + 1):
        guess = R[-1] + (R[-1] - R[-2]) / (mp.mpf("4.6692") if n > 2 else 4)
        r = guess
        for _ in range(100):
            g, _, dg = iterate(r, mp.mpf("0.5"), 2 ** n)
            step = (g - mp.mpf("0.5")) / dg
            r -= step
            if abs(step) < mp.mpf(10) ** (-50):
                break
        R.append(r)
    return R


def bifurcations(R):
    """r_n lies between R_{n-1} and R_n: solve f^p(x)=x, (f^p)'(x)=-1 with p=2^(n-1)."""
    out = [mp.mpf(3)]
    for n in range(2, len(R)):
        p = 2 ** (n - 1)
        r = (R[n - 1] + 2 * R[n]) / 3
        x, _, _ = iterate(r, mp.mpf("0.5"), 50 * p)  # land on the cycle
        for _ in range(200):
            # Newton in (x, r) on F = (f^p(x)-x, (f^p)'(x)+1); Jacobian by finite differences
            h = mp.mpf(10) ** (-30)
            def F(x, r):
                y, d, _ = iterate(r, x, p)
                return mp.matrix([y - x, d + 1])
            F0 = F(x, r)
            J = mp.matrix(2, 2)
            Fx, Fr = F(x + h, r), F(x, r + h)
            for i in range(2):
                J[i, 0] = (Fx[i] - F0[i]) / h
                J[i, 1] = (Fr[i] - F0[i]) / h
            s = mp.lu_solve(J, -F0)
            x, r = x + s[0], r + s[1]
            if mp.norm(s) < mp.mpf(10) ** (-40):
                break
        out.append(r)
    return out


def main():
    R = superstable()
    r = bifurcations(R)
    delta_R = [(R[n - 1] - R[n - 2]) / (R[n] - R[n - 1]) for n in range(2, len(R))]
    delta_r = [(r[n - 1] - r[n - 2]) / (r[n] - r[n - 1]) for n in range(2, len(r))]
    # d_n = f^{2^(n-1)}(1/2) - 1/2 at R_n : distance to the nearest cycle point
    d = [iterate(R[n], mp.mpf("0.5"), 2 ** (n - 1))[0] - mp.mpf("0.5") for n in range(1, len(R))]
    alpha = [d[i] / d[i + 1] for i in range(len(d) - 1)]

    # Renormalisation curves: g_n(y) = alpha^n [ f_{R_n}^{2^n}(1/2 + y/alpha^n) - 1/2 ]
    a = mp.mpf("-2.502907875095892822283902873218")
    ys = [mp.mpf(i) / 200 - 1 for i in range(401)]
    curves = []
    for n in range(0, 7):
        s = a ** n
        curves.append([float(s * (iterate(R[n], mp.mpf("0.5") + y / s, 2 ** n)[0] - mp.mpf("0.5")))
                       for y in ys])

    data = {
        "R": [float(v) for v in R],
        "r": [float(v) for v in r],
        "R_str": [mp.nstr(v, 16) for v in R],
        "r_str": [mp.nstr(v, 16) for v in r],
        "delta_R": [float(v) for v in delta_R],
        "delta_r": [float(v) for v in delta_r],
        "alpha": [float(v) for v in alpha],
        "renorm_y": [float(y) for y in ys],
        "renorm_curves": curves,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print("n   r_n                  delta(r)      R_n                  delta(R)      alpha")
    for n in range(len(R)):
        dr_ = f"{delta_r[n-2]:.10f}" if 2 <= n < len(delta_r) + 2 else ""
        dR = f"{delta_R[n-2]:.10f}" if n >= 2 else ""
        al = f"{alpha[n-1]:.10f}" if 1 <= n <= len(alpha) else ""
        rn = data["r_str"][n - 1] if 1 <= n <= len(r) else ""
        print(f"{n:<3} {rn:<20} {dr_:<13} {data['R_str'][n]:<20} {dR:<13} {al}")


if __name__ == "__main__":
    main()
