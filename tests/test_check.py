"""The check script itself: it loads, runs on this folder and writes a file Darsi can read."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_check_writes_darsi_check_json():
    subprocess.run([sys.executable, str(ROOT / "check.py")], check=True, cwd=ROOT, capture_output=True)
    out = json.loads((ROOT / "darsi-check.json").read_text(encoding="utf-8"))
    assert out["darsi"] == 1
    assert set(out["milestones"]) == {"m1", "m2", "m3", "m4", "m5"}
    for m in out["milestones"].values():
        assert all({"id", "ok", "en", "ar"} <= set(c) for c in m["checks"])
