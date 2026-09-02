#!/usr/bin/env python3
"""Test the 0x1f010 text-mode setup and helper selection."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_mode_setup.c"


class SetupPlan(ctypes.Structure):
    _fields_ = [
        ("timing_cdc", ctypes.c_uint32),
        ("timing_ce0", ctypes.c_uint32),
        ("timing_ce4", ctypes.c_uint32),
        ("helper", ctypes.c_uint32),
        ("source", ctypes.c_uint32),
        ("tile", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-mode-") as directory:
        library = Path(directory) / "text-mode.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        setup = recovered.recovered_text_mode_setup_plan
        setup.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(SetupPlan)]
        setup.restype = None
        plan = SetupPlan()
        setup(1, 4, 12, ctypes.byref(plan))
        if (plan.timing_cdc, plan.timing_ce0, plan.timing_ce4, plan.helper,
                plan.source, plan.tile, plan.width) != (35, 35, 43, 0x1DC90, 0x2FD0CD4, 19, 2):
            raise SystemExit("nonzero text-mode setup mismatch")
        setup(0, 0xFFFFFFFF, 0xFFFFFFFE, ctypes.byref(plan))
        if (plan.timing_cdc, plan.timing_ce0, plan.timing_ce4, plan.helper, plan.source) != (30, 30, 29, 0x1DF00, 0):
            raise SystemExit("zero text-mode setup mismatch")

    print("PASS: 0x1f010 text-mode timing setup and helper dispatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
