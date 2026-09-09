#!/usr/bin/env python3
"""Validate the bounded latch-86 glyph/record route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_glyph_record_21d98.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "latch", "selector", "mode", "column", "row", "matcher",
        "matcher_source", "matcher_stride", "glyph_index", "record_table",
        "record_stride", "source_first", "source_second", "source_third",
        "transfer_helper", "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-glyph-record-") as directory:
        library = Path(directory) / "glyph-record.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        route_fn = recovered.recovered_status_latch_glyph_record_plan
        route_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()

        route_fn(86, 0, 2, 17, 0x10, 0x20, 0x30, ctypes.byref(plan))
        assert (plan.route, plan.column, plan.row, plan.matcher,
                plan.matcher_source, plan.matcher_stride,
                plan.glyph_index, plan.record_table, plan.record_stride,
                plan.source_first, plan.source_second, plan.source_third,
                plan.transfer_helper) == (
                    1, 26, 8, 0x1D880, 0x20BA8 + 2 * 104, 104, 17,
                    0x20B50, 0x68, 0x10, 0x20, 0x30, 0x1DC10)

        route_fn(86, 0, 6, 4, 0, 0, 0, ctypes.byref(plan))
        assert plan.column == 23
        route_fn(86, 0, 5, 4, 0, 0, 0, ctypes.byref(plan))
        assert plan.column == 25

        route_fn(86, 1, 2, 4, 0, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (0, 0x21FA4)
        route_fn(85, 0, 2, 4, 0, 0, 0, ctypes.byref(plan))
        assert plan.route == 0

    print("PASS: 0x21d98 status-latch glyph/record route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
