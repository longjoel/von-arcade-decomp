#!/usr/bin/env python3
"""Test the fixed attributed panel transfer at 0x1f640."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_fixed_panel_transfer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("helper", "source", "width", "height", "uses_current_position")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-fixed-panel-") as directory:
        library = Path(directory) / "fixed-panel.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_fixed_panel_transfer_plan
        plan_fn.argtypes = [ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(ctypes.byref(plan))
        assert (plan.helper, plan.source, plan.width, plan.height,
                plan.uses_current_position) == (0x1DC90, 0x02FDED40, 6, 8, 1)

    print("PASS: 0x1f640 fixed attributed panel transfer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
