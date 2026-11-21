"""Diffusion of the standard map and dynamical localization of the quantum kicked rotor."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.special import jv
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.kicked import spread, lift_step, qkr, TWO_PI

D = Path(__file__).resolve().parents[1] / "data"
rng = np.random.default_rng(0)

# ---- classical diffusion coefficient D(K) = <dp^2>/n, n = 400 kicks, 4000 particles
NP, NKICK = 4000, 400
Ks = np.round(np.arange(1.5, 30.01, 0.1), 2)
Dm = []
for K in Ks:
    th0 = rng.random(NP) * TWO_PI; p0 = rng.random(NP) * TWO_PI
    Dm.append(spread(th0, p0, K, NKICK, NKICK)[0] / NKICK)
Dm = np.array(Dm)
rw = 1 - 2 * jv(2, Ks) - 2 * jv(1, Ks) ** 2 + 2 * jv(2, Ks) ** 2 + 2 * jv(3, Ks) ** 2
# <dp^2>(n) at K=5 (linear growth) and at K = 2 pi + 0.3 (accelerator modes: anomalous)
K5 = 5.0
th0 = rng.random(20000) * TWO_PI; p0 = rng.random(20000) * TWO_PI
g5 = spread(th0, p0, K5, 200, 1)
gA = spread(th0, p0, 2 * np.pi + 0.3, 200, 1)

# ---- quantum kicked rotor: k = 12.5, tau = hbar = 0.4  ->  K = k tau = 5
k, tau, N, NQ = 12.5, 0.4, 4096, 1000
rec = (10, 50, 200, 1000)
m2q = np.zeros(NQ + 1); prof = {t: 0 for t in rec}
NB = 24
for b in rng.random(NB) - 0.5:
    m2, sn, mm = qkr(k, tau, NQ, N, beta=b, record=rec)
    m2q += m2 / NB
    for t in rec:
        prof[t] = prof[t] + sn[t] / NB
# classical rotor with the same K, all particles starting at p = 0 (like psi = |m=0>)
thc = rng.random(20000) * TWO_PI
m2c = spread(thc, np.zeros(20000), k * tau, NQ, 1) / tau ** 2
cl_prof = {}
for t in rec:
    ths, ps = thc.copy(), np.zeros(20000)
    for i in range(20000):
        ths[i], ps[i] = lift_step(thc[i], 0.0, k * tau, t)
    cl_prof[t] = (ps / tau).tolist()
# localization length from the exponential tail of the final profile: P ~ exp(-2|m|/xi)
P = prof[NQ]; sel = (np.abs(mm) > 20) & (np.abs(mm) < 200) & (P > 0)
slope = np.polyfit(np.abs(mm[sel]), np.log(P[sel]), 1)[0]
xi = -2 / slope
Dq = Dm[np.argmin(abs(Ks - K5))] / tau ** 2          # classical diffusion in m units
# localization length vs classical diffusion: K = 5 fixed, hbar = tau = K/k varied.
# stationary profile |psi_m|^2 ~ exp(-|m|/lam)  ->  <m^2>_sat = 2 lam^2
sweep = []
for kk in (6.0, 8.0, 10.0, 12.5, 15.0):
    tt = K5 / kk; T = int(min(40 * kk * kk / 2, 4500)); acc = np.zeros(T + 1)
    for b in rng.random(24) - 0.5:
        acc += qkr(kk, tt, T, 8192, beta=b)[0] / 24
    Dmk = kk * kk / 2 * rw[np.argmin(abs(Ks - K5))]
    lam = float(np.sqrt(acc[-T // 4:].mean() / 2))
    sweep.append({"k": kk, "hbar": tt, "D_m": Dmk, "lam": lam, "ratio": lam / Dmk})
    print(sweep[-1], flush=True)
# quantum resonance: tau = 4 pi -> free phases = 1 -> ballistic <m^2> = k^2 n^2 / 2
m2r, _, _ = qkr(1.0, 4 * np.pi, 200, 2048)

out = {
    "diffusion": {"K": Ks.tolist(), "D_over_ql": (Dm / (Ks ** 2 / 2)).tolist(), "rw": rw.tolist(),
                  "n": NKICK, "particles": NP},
    "growth5": g5.tolist(), "growthA": gA.tolist(), "K_acc": 2 * np.pi + 0.3,
    "qkr": {"k": k, "tau": tau, "K": k * tau, "N": N, "beta_avg": NB, "m2q": m2q.tolist(), "m2c": m2c.tolist(),
            "m": mm.tolist(), "prof": {str(t): prof[t].tolist() for t in rec},
            "xi_fit": xi, "D_m": Dq, "xi_theory": Dq / 2, "m2_sat": float(m2q[-200:].mean())},
    "sweep": sweep,
    "resonance": {"m2": m2r.tolist(), "k": 1.0},
}
(D / "facts.json").write_text(json.dumps(out))
(D / "cl_prof.json").write_text(json.dumps(cl_prof))
print("D/ql at K=5:", Dm[np.argmin(abs(Ks - 5))] / 12.5, "rw:", rw[np.argmin(abs(Ks - 5))])
print("xi_fit", xi, "D_m", Dq, "D_m/2", Dq / 2, "m2_sat", m2q[-200:].mean(), "2 xi^2", 2 * xi ** 2)
print("resonance m2(200)", m2r[-1], "k^2 n^2/2", 200 ** 2 / 2)
