#!/usr/bin/env python3
"""Test the fixed 0x1fba0 panel transfer contract."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel10_transfer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("helper", "source", "column", "row", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel10-") as directory:
        library = Path(directory) / "panel10.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_panel10_transfer_plan
        plan_fn.argtypes = [ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(ctypes.byref(plan))
        assert (plan.helper, plan.source, plan.column, plan.row,
                plan.width, plan.height) == (0x1DC10, 0x2FE0404, 10, 20, 31, 5)

    print("PASS: 0x1fba0 fixed panel transfer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
