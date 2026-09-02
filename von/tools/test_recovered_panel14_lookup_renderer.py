#!/usr/bin/env python3
"""Test the masked lookup renderer at 0x1ff50."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel14_lookup_renderer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("helper", "source_table", "source", "table_index", "width",
                 "height", "column_advance", "max_column")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel14-") as directory:
        library = Path(directory) / "panel14.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_panel14_lookup_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(50, 10, 10, ctypes.byref(plan))
        assert (plan.helper, plan.source_table, plan.source, plan.table_index,
                plan.width, plan.height, plan.column_advance, plan.max_column) == (0x1DC10, 0x2EA2090,
                                                                                    0x2EA2098, 2, 1, 2, 1, 41)
        plan_fn(0, 50, 10, ctypes.byref(plan))
        assert (plan.table_index, plan.source, plan.column_advance) == (0, 0x2EA2090, 0)

    print("PASS: 0x1ff50 masked lookup renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
