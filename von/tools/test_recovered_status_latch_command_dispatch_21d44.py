#!/usr/bin/env python3
"""Validate the bounded 0x21d44 latch command dispatch."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_command_dispatch_21d44.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "command_helper", "command", "command_source",
        "command_index", "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-command-dispatch-") as directory:
        library = Path(directory) / "dispatch.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        dispatch_fn = recovered.recovered_status_latch_command_dispatch_plan
        dispatch_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                                ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()

        dispatch_fn(56, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.command_helper, plan.command,
                plan.command_source, plan.continuation_target) == (
                    1, 0x2A4E0, 0x1322, 0, 0x21FA4)

        dispatch_fn(56, 7, 0xBEEF, ctypes.byref(plan))
        assert (plan.route, plan.command_helper, plan.command,
                plan.command_source, plan.command_index) == (
                    1, 0x2A4E0, 0xBEEF, 0x21180, 7)

        dispatch_fn(66, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (2, 0x21EF8)

        dispatch_fn(55, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (0, 0x21FA4)

    print("PASS: 0x21d44 status-latch command dispatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
