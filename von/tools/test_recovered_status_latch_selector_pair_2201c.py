#!/usr/bin/env python3
"""Validate the bounded 0x2201c selector-pair branch."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_selector_pair_2201c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "selector_gate", "selector", "first_source", "second_source",
        "helper", "call_count", "column", "row", "source_stride",
        "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-selector-pair-") as directory:
        library = Path(directory) / "selector-pair.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        route_fn = recovered.recovered_status_latch_selector_pair_plan
        route_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(Plan)]
        plan = Plan()

        route_fn(0, 7, ctypes.byref(plan))
        assert (plan.route, plan.first_source, plan.second_source, plan.helper,
                plan.call_count, plan.column, plan.row, plan.source_stride,
                plan.continuation_target) == (
                    2, 0x20FD0, 0x20FD8, 0x1D880, 2, 38, 16, 16, 0x22108)

        route_fn(0, 8, ctypes.byref(plan))
        assert (plan.route, plan.first_source, plan.second_source, plan.helper,
                plan.column, plan.row) == (1, 0x20FE0, 0x20FE8, 0x1D7D0, 39, 17)

        route_fn(1, 8, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (0, 0x220B8)

    print("PASS: 0x2201c status-latch selector pair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
