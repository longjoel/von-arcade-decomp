#!/usr/bin/env python3
"""Regression: a retained MAME packet prefix resolves to Temjin ROM table 3."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
tool = ROOT / "von/tools/verify_motion_packet_mapping.py"
motion = ROOT / "von/build/motion-tables/temjin.json"
capture = ROOT / "von/captures/fifo-program-20260912T/mame.log"

if __name__ == "__main__":
    if not motion.exists():
        subprocess.run(["python3", str(ROOT / "von/tools/dump_motion_tables.py")], check=True)
    result = subprocess.run(["python3", str(tool), "--motion", str(motion), "--log", str(capture),
                             "--expect", "3,0,7", "--expect", "2,0,1,11",
                             "--expect-run", "3,0,16"], text=True, capture_output=True, check=True)
    if "PASS: table=3 frame=0" not in result.stdout or "PASS: table=2 frame=0" not in result.stdout: raise SystemExit(result.stdout)
    print("PASS: MAME emitter packet prefix -> Temjin paired ROM tables 3 (7 skeleton) + 2 (body 1..11), 16-frame cadence")
