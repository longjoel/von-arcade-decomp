#!/usr/bin/env python3
"""Test the 0x1fa30 source-or-clear route contract."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel5_source_fill_route.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column", "row", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel5-") as directory:
        library = Path(directory) / "panel5.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_panel5_source_fill_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()

        plan_fn(1, 7, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column, plan.row, plan.width, plan.height) == (0x2FE053A, 0x1DC10, 0, 2, 20, 38, 5)

        plan_fn(0, 7, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column, plan.row, plan.width, plan.height) == (0, 0, 0x1DF00, 2, 20, 38, 5)

    print("PASS: 0x1fa30 panel5 source/fill route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
