#!/usr/bin/env python3
"""Validate the bounded 0x2241c/0x224e4 render arms."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_render_arms_2241c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "arm", "mode", "column", "row", "record_table", "record_stride",
        "record_source_first", "record_source_second", "record_source_third",
        "record_helper", "matcher", "matcher_source", "matcher_stride",
        "matcher_column", "matcher_row", "record_call_count",
        "matcher_call_count", "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-render-arms-") as directory:
        library = Path(directory) / "arms.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        render_fn = recovered.recovered_status_latch_render_arms_plan
        render_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.POINTER(Plan)]
        plan = Plan()

        render_fn(1, 2, 0x10, 0x20, 0x30, ctypes.byref(plan))
        assert (plan.arm, plan.column, plan.row, plan.record_table,
                plan.record_helper, plan.record_source_third, plan.matcher,
                plan.matcher_source, plan.matcher_column, plan.matcher_row,
                plan.record_call_count, plan.matcher_call_count,
                plan.continuation_target) == (
                    0, 26, 8, 0x20B50 + 2 * 0x68, 0x1DC10, 0x30,
                    0x1D880, 0x20BA8 + 2 * 104, 26, 8, 1, 1, 0x22590)

        render_fn(0, 6, 0x40, 0x50, 0x60, ctypes.byref(plan))
        assert (plan.arm, plan.column, plan.row, plan.record_helper,
                plan.record_source_third, plan.matcher_column) == (
                    1, 23, 11, 0x1DF00, 0, 23)

    print("PASS: 0x2241c/0x224e4 status-latch render arms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
