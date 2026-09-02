#!/usr/bin/env python3
"""Test the repeated 0x20660-0x206e8 status block routes."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_block_routes_20660.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper",
                 "column_comes_from_current_position", "row_comes_from_current_position",
                 "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-block-") as directory:
        library = Path(directory) / "status-block.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_block_route_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        for route, source, width in ((0, 0x2FCF9E4, 16), (1, 0x2FCF308, 16), (2, 0x2FCF388, 28)):
            plan_fn(route, 1, ctypes.byref(plan))
            assert (plan.source, plan.source_helper, plan.fill_helper,
                    plan.column_comes_from_current_position,
                    plan.row_comes_from_current_position, plan.width,
                    plan.height) == (source, 0x1DC10, 0, 1, 1, width, 4)
        plan_fn(2, 0, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x20660-0x206e8 status block routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
