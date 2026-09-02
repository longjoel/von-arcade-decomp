#!/usr/bin/env python3
"""Test the 0x1fc30 two-value scoreboard renderer."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scoreboard_renderer.c"


class Digit(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "helper", "column", "row", "width", "height", "table_index")]


class Plan(ctypes.Structure):
    _fields_ = [("early_return", ctypes.c_uint32),
                ("normalized_first", ctypes.c_uint32),
                ("normalized_second", ctypes.c_uint32),
                ("first_tens", Digit), ("first_units", Digit),
                ("second_tens", Digit), ("second_units", Digit),
                ("first_separator", Digit), ("second_suffix", Digit)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-scoreboard-") as directory:
        library = Path(directory) / "scoreboard.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_scoreboard_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(42, 17, 1, 0, ctypes.byref(plan))
        assert (plan.early_return, plan.normalized_first, plan.normalized_second) == (0, 42, 17)
        assert (plan.first_tens.source, plan.first_tens.column, plan.first_tens.row,
                plan.first_tens.table_index) == (0x2EA1E60, 25, 21, 4)
        assert (plan.first_units.source, plan.first_units.column,
                plan.first_units.table_index) == (0x2EA1E58, 27, 2)
        assert (plan.first_separator.source, plan.first_separator.column,
                plan.first_separator.row, plan.first_separator.width,
                plan.first_separator.height) == (0x2FE158A, 29, 22, 1, 1)
        assert (plan.second_tens.table_index, plan.second_tens.column,
                plan.second_tens.row) == (1, 30, 21)
        assert (plan.second_units.table_index, plan.second_units.column) == (7, 32)
        assert (plan.second_suffix.source, plan.second_suffix.column,
                plan.second_suffix.row, plan.second_suffix.width,
                plan.second_suffix.height) == (0x2FE157A, 34, 21, 4, 2)

        plan_fn(0x8001, 0xFFFF, 0, 4, ctypes.byref(plan))
        assert (plan.early_return, plan.normalized_first, plan.normalized_second) == (1, 0, 0)

    print("PASS: 0x1fc30 scoreboard renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
