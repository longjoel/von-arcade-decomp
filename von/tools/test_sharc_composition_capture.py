#!/usr/bin/env python3
"""Regression: MAME's paired Temjin packet frame composes within 2.1 degrees."""
import re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
log = ROOT / "von/captures/fifo-program-20260912T/mame.log"
tool = ROOT / "von/tools/validate_sharc_composition.py"
if __name__ == "__main__":
    result = subprocess.run(["python3", str(tool), "--log", str(log),
                             "--t0", "20.323", "--t1", "20.325",
                             "--mat-t0", "20.339", "--mat-t1", "20.340"],
                            text=True, capture_output=True, check=True)
    errors = [float(x) for x in re.findall(r"rot_err=\s*([\d.]+)", result.stdout)]
    if not errors or min(errors) > 2.1: raise SystemExit(result.stdout)
    print(f"PASS: MAME paired SHARC composition best rotation error {min(errors):.2f} deg")
