#!/usr/bin/env python3
"""Test the fixed continuation-message renderer at 0x1fa00."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_continued_renderer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("message", "text_helper", "column", "row", "writes_position")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-continued-") as directory:
        library = Path(directory) / "continued.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_continued_renderer_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(0x12, ctypes.byref(plan))
        assert (plan.message, plan.text_helper, plan.column, plan.row,
                plan.writes_position) == (0x1F9E0, 0x1DA90, 0x12, 20, 1)

        plan_fn(0xFFFFFFFF, ctypes.byref(plan))
        assert plan.column == 0xFFFFFFFF

    print("PASS: 0x1fa00 continuation-message renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
