#!/usr/bin/env python3
"""Validate the bounded 0x223fc convergence gate."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_convergence_gate_223fc.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "selector_gate", "latch", "latch_minus_87", "bit3_set",
        "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-convergence-gate-") as directory:
        library = Path(directory) / "gate.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        gate_fn = recovered.recovered_status_latch_convergence_gate_plan
        gate_fn.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32,
                            ctypes.POINTER(Plan)]
        plan = Plan()

        gate_fn(1, 155, 1, ctypes.byref(plan))
        assert (plan.route, plan.latch_minus_87, plan.continuation_target) == (
            1, 68, 0x2241C)
        gate_fn(1, 155, 0, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (2, 0x224E4)
        gate_fn(0, 155, 1, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (0, 0x22590)
        gate_fn(1, 156, 1, ctypes.byref(plan))
        assert plan.route == 0

    print("PASS: 0x223fc status-latch convergence gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
