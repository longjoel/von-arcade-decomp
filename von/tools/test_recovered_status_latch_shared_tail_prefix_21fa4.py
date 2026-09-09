#!/usr/bin/env python3
"""Validate the bounded 0x21fa4 shared-tail prefix."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_shared_tail_prefix_21fa4.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "latch", "bit1_set", "helper", "source",
        "position_register", "position_offset", "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-shared-prefix-") as directory:
        library = Path(directory) / "prefix.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        prefix_fn = recovered.recovered_status_latch_shared_tail_prefix_plan
        prefix_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                              ctypes.POINTER(Plan)]
        plan = Plan()

        prefix_fn(155, 1, ctypes.byref(plan))
        assert (plan.route, plan.helper, plan.source, plan.position_register,
                plan.position_offset, plan.continuation_target) == (
                    1, 0x1DC10, 0x2FE8EC2, 12, 31, 0x2201C)
        prefix_fn(155, 0, ctypes.byref(plan))
        assert (plan.route, plan.helper, plan.source,
                plan.continuation_target) == (2, 0x1DF00, 0, 0x2201C)
        prefix_fn(156, 1, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (0, 0x22108)

    print("PASS: 0x21fa4 shared-tail prefix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
