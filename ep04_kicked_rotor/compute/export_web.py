import json
from pathlib import Path
D = Path(__file__).resolve().parents[1] / "data"
W = Path(__file__).resolve().parents[2] / "web" / "data" / "ep4.json"
f = json.loads((D / "facts.json").read_text())
g = json.loads((D / "greene.json").read_text())
d = json.loads((D / "doubling.json").read_text())
r = lambda v, k=4: [round(x, k) for x in v]
out = {"greene": g, "a_k": d["a_k"], "delta_k": d["delta_k"], "periods": d["periods"],
       "diff": {"K": f["diffusion"]["K"], "ratio": r(f["diffusion"]["D_over_ql"]), "rw": r(f["diffusion"]["rw"])},
       "sweep": f["sweep"]}
W.write_text(json.dumps(out, separators=(",", ":")))
print(W.stat().st_size)
