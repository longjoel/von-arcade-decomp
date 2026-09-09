#!/usr/bin/env python3
"""Validate the bounded latch-87 panel route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_panel87_21e7c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "latch", "selector", "first_source", "first_helper",
        "first_width", "first_height", "first_column", "first_row",
        "second_source", "second_helper", "second_column", "second_row",
        "second_command", "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-panel87-") as directory:
        library = Path(directory) / "panel87.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        route_fn = recovered.recovered_status_latch_panel87_plan
        route_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(Plan)]
        plan = Plan()

        route_fn(87, 3, 9, 0xAAA, 0xBBB, ctypes.byref(plan))
        assert (plan.route, plan.first_source, plan.first_helper,
                plan.first_width, plan.first_height, plan.first_column,
                plan.first_row, plan.second_source, plan.second_helper,
                plan.second_column, plan.second_row, plan.second_command,
                plan.continuation_target) == (
                    1, 0xAAA, 0x1DC10, 20, 15, 9, 24, 0xBBB, 0x1D1D0,
                    34, 26, 0x1111, 0x21FA4)

        route_fn(86, 4, 4, 0, 0, ctypes.byref(plan))
        assert plan.route == 0
        route_fn(88, 4, 4, 0, 0, ctypes.byref(plan))
        assert plan.route == 0

    print("PASS: 0x21e7c status-latch panel-87 route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
