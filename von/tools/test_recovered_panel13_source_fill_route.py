#!/usr/bin/env python3
"""Test the current-position 0x1ff20 source-or-clear route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel13_source_fill_route.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper",
                 "column_comes_from_current_position", "row_comes_from_current_position",
                 "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel13-") as directory:
        library = Path(directory) / "panel13.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_panel13_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 4, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column_comes_from_current_position,
                plan.row_comes_from_current_position, plan.width,
                plan.height) == (0x2FE0B5C, 0x1DC10, 0, 1, 1, 35, 5)
        plan_fn(0, 4, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x1ff20 panel13 source/fill route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
