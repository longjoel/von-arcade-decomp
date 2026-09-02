#!/usr/bin/env python3
"""Test the 0x1f3b0 press-start message and flag plan."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_press_start_renderer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("message", "text_helper", "column", "row", "flag_address",
                 "flag_set_mask", "flag_clear_mask")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-press-start-") as directory:
        library = Path(directory) / "press-start.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_press_start_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 4, 12, ctypes.byref(plan))
        assert (plan.message, plan.text_helper, plan.column, plan.row,
                plan.flag_address, plan.flag_set_mask, plan.flag_clear_mask) == (0x1F370, 0x1D210, 35, 43, 0x502484, 4, 0)
        plan_fn(0, 0xFFFFFFFF, 0xFFFFFFFE, ctypes.byref(plan))
        assert (plan.message, plan.column, plan.row, plan.flag_set_mask,
                plan.flag_clear_mask) == (0x1F390, 30, 29, 0, 0xFFFB)

    print("PASS: 0x1f3b0 press-start message and flag plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
