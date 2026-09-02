#!/usr/bin/env python3
"""Test the third protected source/fill renderer route at 0x1f290."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_status_panel3_route.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("helper", "source", "fill_value", "column", "row", "width",
                 "height", "stack_frame_bytes")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-panel3-") as directory:
        library = Path(directory) / "status-panel3.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_status_panel3_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 4, 12, ctypes.byref(plan))
        assert (plan.helper, plan.source, plan.column, plan.row, plan.width,
                plan.height) == (0x1DD10, 0x02FD848A, 2, 35, 43, 3)
        plan_fn(0, 0xFFFFFFFF, 0xFFFFFFFE, ctypes.byref(plan))
        assert (plan.helper, plan.source, plan.fill_value, plan.row, plan.width,
                plan.height, plan.stack_frame_bytes) == (0x1DF70, 0, 0, 30, 29, 3, 0x50)

    print("PASS: 0x1f290/0x1f2a0 status-panel source/fill route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
