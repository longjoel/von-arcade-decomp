#!/usr/bin/env python3
"""Test the two-block panel plan at 0x1f4c0."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_panel_builder.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("first_source", "first_column", "first_row", "first_width",
                 "first_height", "second_table_entry", "second_selector",
                 "second_column", "second_row", "second_width", "second_height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-panel-builder-") as directory:
        library = Path(directory) / "status-panel-builder.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_panel_builder_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(0x130, ctypes.byref(plan))
        assert (plan.first_source, plan.first_column, plan.first_row,
                plan.first_width, plan.first_height) == (0x02FE01D4, 4, 10, 5, 5)
        assert (plan.second_selector, plan.second_table_entry, plan.second_column,
                plan.second_row, plan.second_width, plan.second_height) == (0, 0x02EA2010, 28, 20, 8, 5)
        plan_fn(0x13F, ctypes.byref(plan))
        assert (plan.second_selector, plan.second_table_entry) == (0xF, 0x02EA204C)
        plan_fn(0x00000000, ctypes.byref(plan))
        assert plan.second_selector == 0

    print("PASS: 0x1f4c0 two-block status-panel plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
