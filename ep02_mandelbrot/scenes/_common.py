import json, sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
BULBS = json.loads((ROOT / "ep02_mandelbrot" / "data" / "bulbs.json").read_text())
EP1 = json.loads((ROOT / "ep01_logistic" / "data" / "cascade.json").read_text())

from common import style  # noqa: E402
style.setup()
from manim import config as _cfg  # noqa: E402
_cfg.disable_caching = True      # updaters hold numba functions, which the hasher cannot serialise


def load_ep1_stages():
    """Part 1's layout helpers (used to rebuild its last picture exactly)."""
    spec = importlib.util.spec_from_file_location("ep1_stages", ROOT / "ep01_logistic" / "scenes" / "_stages.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
