#!/usr/bin/env python3
"""Validate the bounded 0x22108 timing/status gate."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_timing_gate_22108.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "status_mode", "latch", "compare_value", "base_54",
        "base_58", "raw_timing", "timing_after", "word_4c_before",
        "word_4c_after", "word_50_before", "word_50_after", "fallback_g14",
        "timing_address", "word_4c_address", "word_50_address",
        "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-timing-gate-") as directory:
        library = Path(directory) / "timing-gate.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        gate_fn = recovered.recovered_status_latch_timing_gate_plan
        gate_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(Plan)]
        plan = Plan()

        gate_fn(1, 63, 32, 4, 12, 7, 8, 99, ctypes.byref(plan))
        assert (plan.route, plan.compare_value, plan.raw_timing,
                plan.timing_after, plan.word_4c_after, plan.word_50_after,
                plan.continuation_target) == (2, 63, 3000, 3000, 7, 8, 0x223FC)

        gate_fn(2, 63, 32, 4, 12, 7, 8, 99, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (0, 0x223FC)
        gate_fn(1, 64, 32, 4, 12, 7, 8, 99, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (1, 0x221B8)

        gate_fn(1, 63, 32, 0, 12, 0xFFFFFFFF, 8, 99, ctypes.byref(plan))
        assert (plan.timing_after, plan.word_4c_after) == (99, 99)
        gate_fn(1, 63, 32, 4, 12, 7, 0xFFFFFFFF, 99, ctypes.byref(plan))
        assert plan.word_50_after == 99

    print("PASS: 0x22108 status-latch timing gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
