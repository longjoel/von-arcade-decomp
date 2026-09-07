#!/usr/bin/env python3
"""Test the I/O self-test failure-dispatch routing plan at 0x2768-0x2788."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_io.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("calls_failure_service", ctypes.c_uint32),
        ("calls_queue_initialize", ctypes.c_uint32),
        ("result", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-io-dispatch-") as directory:
        library = Path(directory) / "io_dispatch.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_io_self_test_dispatch_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan_fn.restype = None

        cases = [
            # (failed, latched, calls_failure_service, calls_queue_initialize)
            (0x00000000, 0x00000000, 0, 0),
            (0x00000000, 0xDEADBEEF, 0, 0),
            (0x00000001, 0x00000001, 1, 1),
            (0x00000001, 0x00000000, 1, 1),
            (0xFFFFFFFF, 0x00000001, 1, 1),
        ]
        for failed, latched, want_service, want_queue in cases:
            plan = Plan()
            plan_fn(failed, latched, ctypes.byref(plan))
            observed = (plan.calls_failure_service, plan.calls_queue_initialize, plan.result)
            if observed != (want_service, want_queue, latched):
                raise SystemExit(
                    f"dispatch plan mismatch for failed={failed:#x}: {observed}"
                )

    print("PASS: 0x2768 I/O self-test failure dispatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
