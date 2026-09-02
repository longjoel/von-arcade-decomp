#!/usr/bin/env python3
"""Test the 0x207e0/0x20810 status transition routes."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_transition_routes.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper",
                 "column_comes_from_current_position", "row_comes_from_current_position",
                 "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-transition-") as directory:
        library = Path(directory) / "status-transition.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_transition_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(0, 1, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper,
                plan.column_comes_from_current_position, plan.row_comes_from_current_position,
                plan.width, plan.height) == (0x2FCF708, 0x1DC10, 0, 1, 1, 20, 4)
        plan_fn(1, 1, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper, plan.width,
                plan.height) == (0x2FCF988, 0x1DC90, 0, 23, 2)
        plan_fn(1, 0, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x207e0/0x20810 status transition routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
