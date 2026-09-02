#!/usr/bin/env python3
"""Test the attributed 0x20840-0x209b8 status routes."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_attributed_status_routes_20840.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "helper", "width", "height",
                 "column_comes_from_current_position", "row_comes_from_current_position")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-attributed-status-") as directory:
        library = Path(directory) / "attributed-status.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_attributed_status_route_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        sources = [0x2FCFA64, 0x2FCFBE4, 0x2FCFDD4, 0x2FD0014,
                   0x2FD0124, 0x2FD02E4, 0x2FD0464, 0x2FD0634]
        widths = [24, 31, 45, 43, 28, 24, 29, 29]
        heights = [8, 8, 8, 4, 8, 8, 8, 8]
        for route, source in enumerate(sources):
            plan_fn(route, 1, 14, 12, ctypes.byref(plan))
            assert (plan.source, plan.helper, plan.width, plan.height,
                    plan.column_comes_from_current_position,
                    plan.row_comes_from_current_position) == (source, 0x1DC90,
                                                               widths[route], heights[route], 1, 1)
        plan_fn(2, 0, 14, 12, ctypes.byref(plan))
        assert (plan.source, plan.helper) == (0, 0x1DF00)

    print("PASS: 0x20840-0x209b8 attributed status routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
