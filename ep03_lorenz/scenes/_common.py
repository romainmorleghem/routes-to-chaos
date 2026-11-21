import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "ep03_lorenz" / "data"
FACTS = json.loads((DATA / "facts.json").read_text())
EP1 = json.loads((ROOT / "ep01_logistic" / "data" / "cascade.json").read_text())


def bif():
    return json.loads((DATA / "bifurcation.json").read_text())


from common import style  # noqa: E402
style.setup()
from manim import config as _cfg  # noqa: E402
_cfg.disable_caching = True      # updaters hold numba functions, which the hasher cannot serialise
