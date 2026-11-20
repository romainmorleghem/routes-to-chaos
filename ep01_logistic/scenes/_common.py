import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA = json.loads((ROOT / "ep01_logistic" / "data" / "cascade.json").read_text())

from common import style  # noqa: E402
style.setup()
