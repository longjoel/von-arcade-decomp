#!/usr/bin/env python3
"""Regression: Lua captures table-3 selection and its one-step cursor cadence."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    motion = ROOT / "von/build/motion-tables/temjin.json"
    if not motion.exists():
        subprocess.run(["python3", str(ROOT / "von/tools/dump_motion_tables.py")], check=True)
    result = subprocess.run([
        "python3", str(ROOT / "von/tools/verify_motion_selector_trace.py"),
        "--motion", str(motion),
        "--log", str(ROOT / "von/tests/fixtures/motion-selector-temjin-table3.log"),
        "--table", "3", "--body-table", "2", "--object", "0x00503ad0", "--prefix", "10",
    ], text=True, capture_output=True, check=True)
    if "PASS: table=3 body-table=2" not in result.stdout:
        raise SystemExit(result.stdout)
    print("PASS: Lua selector tap -> Temjin table 3 and cursor 1..10")
