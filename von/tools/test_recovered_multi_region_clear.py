#!/usr/bin/env python3
"""Test the fixed three-region clear sequence at 0x1fe90."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_multi_region_clear.c"


class Region(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("column", "row", "width", "height", "helper")]


class Plan(ctypes.Structure):
    _fields_ = [(name, Region) for name in ("first", "second", "third")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-multi-clear-") as directory:
        library = Path(directory) / "multi-clear.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_multi_region_clear_plan
        plan_fn.argtypes = [ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(ctypes.byref(plan))
        assert (plan.first.column, plan.first.row, plan.first.width,
                plan.first.height, plan.first.helper) == (4, 10, 33, 8, 0x1DF00)
        assert (plan.second.column, plan.second.row, plan.second.width,
                plan.second.height, plan.second.helper) == (22, 10, 38, 8, 0x1DF00)
        assert (plan.third.column, plan.third.row, plan.third.width,
                plan.third.height, plan.third.helper) == (20, 10, 24, 8, 0x1DF00)

    print("PASS: 0x1fe90 multi-region clear")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
