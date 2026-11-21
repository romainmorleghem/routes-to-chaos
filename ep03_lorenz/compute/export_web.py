"""Compact JSON for web/ep3 (bifurcation diagrams, unstable periodic orbits, key numbers)."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "ep03_lorenz" / "data"
b = json.loads((D / "bifurcation.json").read_text())
fl = json.loads((D / "doubling_floquet.json").read_text())["0.001"]
f = json.loads((D / "facts.json").read_text())
u = json.loads((D / "upo.json").read_text())
prim = lambda w: all(w != w[:d] * (len(w) // d) for d in range(1, len(w)) if len(w) % d == 0)
out = {
    "rho_k": fl["rho_k"], "delta_k": fl["delta_k"], "crossings": fl["crossings"],
    "window": [[r, [round(v, 2) for v in m[-40:]]] for r, m in b["window"]],
    "wide": [[round(r, 2), [round(v, 1) for v in m[-40:]]] for r, m in b["wide"]],
    "lyapunov": f["lyapunov"], "kaplan_yorke": f["kaplan_yorke"], "rho_hopf": f["rho_hopf"],
    "upo": [{"word": o["word"], "T": round(o["T"], 4), "mu": round(o["mu"], 2),
             "pts": [[round(c, 2) for c in p] for p in o["pts"][::max(1, len(o["pts"]) // 500)]]}
            for o in u if prim(o["word"])],
}
(ROOT / "web" / "data" / "ep3.json").write_text(json.dumps(out, separators=(",", ":")))
print((ROOT / "web" / "data" / "ep3.json").stat().st_size)
