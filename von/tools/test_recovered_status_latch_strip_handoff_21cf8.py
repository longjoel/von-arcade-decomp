#!/usr/bin/env python3
"""Validate the bounded 0x21cf8 latch-to-strip handoff."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_strip_handoff_21cf8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "strip_builder", "column", "row", "input", "width",
        "scale", "first_value", "second_value", "third_value", "fill_value",
        "continuation_target", "downstream_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-strip-handoff-") as directory:
        library = Path(directory) / "handoff.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        handoff_fn = recovered.recovered_status_latch_strip_handoff_plan
        handoff_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(Plan)]
        plan = Plan()

        for latch in (49, 50):
            handoff_fn(latch, ctypes.byref(plan))
            assert (plan.route, plan.strip_builder, plan.column, plan.row,
                    plan.input, plan.width, plan.scale,
                    plan.continuation_target) == (0, 0x20A20, 7, 8, 1,
                                                   0x118, 0x118, 0x21FA4)
            assert (plan.first_value, plan.second_value, plan.third_value,
                    plan.fill_value) == (0, 0, 0, 0)

        handoff_fn(51, ctypes.byref(plan))
        assert (plan.route, plan.downstream_target) == (1, 0x21D44)

    print("PASS: 0x21cf8 status-latch strip handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
