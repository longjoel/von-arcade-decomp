#!/usr/bin/env python3
"""Test repeated 0x206f0-0x207d8 status block routes."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_block_routes_206f0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper",
                 "column_comes_from_current_position", "row_comes_from_current_position",
                 "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-block-206f0-") as directory:
        library = Path(directory) / "status-block-206f0.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_block_route_206f0_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        sources = [0x2FCF4A8, 0x2FCF7A8, 0x2FCF688, 0x2FCF588, 0x2FCF888, 0x2FCF708]
        for route, source in enumerate(sources):
            plan_fn(route, 1, ctypes.byref(plan))
            assert (plan.source, plan.source_helper, plan.fill_helper,
                    plan.column_comes_from_current_position,
                    plan.row_comes_from_current_position, plan.width,
                    plan.height) == (source, 0x1DC10, 0, 1, 1, 16 if route < 3 else 20, 4)
        plan_fn(4, 0, ctypes.byref(plan))
        assert (plan.source, plan.source_helper, plan.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x206f0-0x207d8 status block routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
