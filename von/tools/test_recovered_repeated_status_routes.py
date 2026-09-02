#!/usr/bin/env python3
"""Test the repeated 0x204d0-0x20610 status routes."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_repeated_status_routes.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column_advance", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-repeated-status-") as directory:
        library = Path(directory) / "repeated-status.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_repeated_status_route_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        expected_sources = [0x2FCF2C8, 0x2FCF528, 0x2FCF828, 0x2FCF628, 0x2FCF928]
        for route, source in enumerate(expected_sources):
            plan_fn(route, 1, ctypes.byref(plan))
            assert (plan.source, plan.source_helper, plan.fill_helper,
                    plan.column_advance, plan.width, plan.height) == (source, 0x1DC10, 0, 4 if route == 0 else 2, 8 if route == 0 else 12, 4)
        plan_fn(1, 0, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x204d0-0x20610 repeated status routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
