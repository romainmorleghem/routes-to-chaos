"""Numbers quoted in Part 3, computed here (sigma=10, rho=28, beta=8/3 unless stated).

- Lyapunov spectrum (QR method), sum check against the divergence -(sigma+1+beta), Kaplan-Yorke dimension.
- Fixed points and their eigenvalues along rho (pitchfork at 1, Hopf at rho_H).
- Lorenz map: successive z-maxima (z_n, z_{n+1}) and its slope (|F'| > 1 on the attractor).
- Twin trajectories 1e-10 apart: log separation vs time, fitted slope.
Output: data/facts.json
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.lorenz import *

OUT = Path(__file__).resolve().parents[1] / "data" / "facts.json"


def main():
    spec = lyapunov_spectrum(np.array([1.0, 1.0, 1.0]), 5000.0, 0.005)
    ky = 2 + spec[0] / abs(spec[2])
    div = -(SIGMA + 1 + BETA)
    fp = {}
    for r in [0.5, 1.5, 10, 13.926, 20, 24.74, 28]:
        fp[str(r)] = [[p.tolist(), [[e.real, e.imag] for e in np.linalg.eigvals(jacobian(p, r))]]
                      for p in fixed_points(r)]
    m = z_maxima(np.array([1.0, 1.0, 1.0]), 2_000_000, 0.001, 50_000)
    zn, zn1 = m[:-1], m[1:]
    # slope of the map: median z_{n+1} in 40 bins of z_n, then finite differences
    bins = np.linspace(zn.min(), zn.max(), 41)
    cen = 0.5 * (bins[1:] + bins[:-1])
    idx = np.clip(np.digitize(zn, bins) - 1, 0, 39)
    med = np.array([np.median(zn1[idx == i]) for i in range(40)])
    sl = np.abs(np.gradient(med, cen))
    peak = cen[np.argmax(med)]
    a = np.array([1.0, 1.0, 1.0]); a = trajectory(a, 20000, 0.005)[-1]
    b = a + np.array([1e-10, 0, 0])
    ta, tb = trajectory(a, 8000, 0.005), trajectory(b, 8000, 0.005)
    d = np.linalg.norm(ta - tb, axis=1)
    t = np.arange(d.size) * 0.005
    lin = (d > 1e-9) & (d < 1e-1)
    slope = np.polyfit(t[lin], np.log(d[lin]), 1)[0]
    lam = spec[0]
    data = {
        "lyapunov": spec.tolist(), "sum": float(spec.sum()), "divergence": div,
        "kaplan_yorke": float(ky), "rho_hopf": RHO_HOPF, "fixed_points": fp,
        "lorenz_map": {"zn": np.round(zn[:3000], 4).tolist(), "zn1": np.round(zn1[:3000], 4).tolist(),
                       "peak": float(peak), "min_abs_slope": float(np.median(np.sort(sl)[:3]))},
        "twins": {"t": t[::10].tolist(), "log10d": np.log10(d[::10] + 1e-300).tolist(), "slope": float(slope)},
        "horizon_gain_per_decade": float(np.log(10) / lam),
        "doubling_time": float(np.log(2) / lam),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data))
    print({k: v for k, v in data.items() if k not in ("fixed_points", "lorenz_map", "twins")})
    print("map peak", peak, "min|F'| away from peak", data["lorenz_map"]["min_abs_slope"],
          "twin slope", slope)


if __name__ == "__main__":
    main()
