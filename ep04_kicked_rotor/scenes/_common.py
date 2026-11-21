import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ep03_lorenz" / "scenes"))
DATA = ROOT / "ep04_kicked_rotor" / "data"
FACTS = json.loads((DATA / "facts.json").read_text())
GREENE = json.loads((DATA / "greene.json").read_text())
DOUBLING = json.loads((DATA / "doubling.json").read_text())

from common import style  # noqa: E402
style.setup()
from manim import config as _cfg  # noqa: E402
_cfg.disable_caching = True
