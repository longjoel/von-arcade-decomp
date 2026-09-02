#!/usr/bin/env python3
"""Test the 0x1fff0 source-or-clear route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel16_source_fill_route.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column", "row", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel16-") as directory:
        library = Path(directory) / "panel16.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_panel16_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 9, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column, plan.row, plan.width, plan.height) == (0x2FDFF54, 0x1DC90, 0, 11, 21, 40, 8)
        plan_fn(0, 9, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column, plan.row, plan.width, plan.height) == (0, 0, 0x1DF00, 11, 21, 40, 8)

    print("PASS: 0x1fff0 panel16 source/fill route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
