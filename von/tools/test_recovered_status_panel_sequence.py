#!/usr/bin/env python3
"""Test the three-stage status-panel sequence at 0x1f540."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_panel_sequence.c"


class Stage(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("helper", "source", "fill_value", "column", "row", "width", "height")]


class Plan(ctypes.Structure):
    _fields_ = [("first", Stage), ("second", Stage), ("third", Stage)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-sequence-") as directory:
        library = Path(directory) / "status-sequence.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_panel_sequence_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(4, 20, 1, 0, ctypes.byref(plan))
        assert (plan.first.helper, plan.first.source, plan.first.column,
                plan.first.row, plan.first.width, plan.first.height) == (0x1DC10, 0x02FDE9D0, 6, 19, 55, 8)
        assert (plan.second.helper, plan.second.source, plan.second.column,
                plan.second.row, plan.second.width, plan.second.height) == (0x1DC10, 0x02FE1606, 18, 12, 34, 2)
        assert (plan.third.helper, plan.third.source, plan.third.column,
                plan.third.row, plan.third.width, plan.third.height) == (0x1DC90, 0x02FE158E, 18, 12, 30, 2)
        plan_fn(0xFFFFFFFF, 0, 0, 1, ctypes.byref(plan))
        assert (plan.first.column, plan.first.row, plan.second.column,
                plan.second.row, plan.third.helper, plan.third.source) == (1, 0xFFFFFFFF, 13, 0xFFFFFFF8, 0x1DF00, 0)

    print("PASS: 0x1f540 three-stage status-panel sequence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
