#!/usr/bin/env python3
"""Test the 0x1f470 insert-coin message and position plan."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_insert_coin_renderer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("message", "text_helper", "column", "row")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-insert-coin-") as directory:
        library = Path(directory) / "insert-coin.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_insert_coin_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 4, 12, ctypes.byref(plan))
        assert (plan.message, plan.text_helper, plan.column, plan.row) == (0x1F440, 0x1D9E0, 35, 43)
        plan_fn(0, 0xFFFFFFFF, 0xFFFFFFFE, ctypes.byref(plan))
        assert (plan.message, plan.column, plan.row) == (0x1F450, 30, 29)

    print("PASS: 0x1f470 insert-coin message and position plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
