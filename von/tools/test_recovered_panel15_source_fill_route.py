#!/usr/bin/env python3
"""Test the explicit-position 0x1ffb0 source-or-clear route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel15_source_fill_route.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column", "row", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel15-") as directory:
        library = Path(directory) / "panel15.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_panel15_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 23, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column, plan.row, plan.width, plan.height) == (0x2FE0F54, 0x1DD10, 0, 4, 17, 54, 5)
        plan_fn(0, 23, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column, plan.row, plan.width, plan.height) == (0, 0, 0x1DF70, 4, 17, 54, 5)

    print("PASS: 0x1ffb0 panel15 source/fill route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
