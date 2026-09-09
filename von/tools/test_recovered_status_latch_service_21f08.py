#!/usr/bin/env python3
"""Validate the bounded 0x21f08 latch service routes."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_service_21f08.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "helper", "command_helper", "command",
        "first_state_helper", "second_state_helper", "state_before",
        "state_first_result", "state_after", "second_state_result",
        "counter_before", "counter_after", "continuation_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-latch-service-") as directory:
        library = Path(directory) / "service.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        service_fn = recovered.recovered_status_latch_service_plan
        service_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.POINTER(Plan)]
        plan = Plan()

        service_fn(156, 0, 0, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.helper, plan.command_helper, plan.command) == (
            1, 0x22C78, 0x2A4E0, 0x133F)
        service_fn(157, 0, 0, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.helper) == (2, 0x20AE8)

        service_fn(158, 0x1F0, 0x234, 0x345, 0, ctypes.byref(plan))
        assert (plan.route, plan.first_state_helper, plan.second_state_helper,
                plan.state_first_result, plan.state_after,
                plan.second_state_result) == (3, 0xF5058, 0xF5058,
                                               0x34, 0x24, 0x145)
        service_fn(185, 0, 0, 0, 0, ctypes.byref(plan))
        assert plan.route == 3

        service_fn(186, 0, 0, 0, 0, ctypes.byref(plan))
        assert (plan.route, plan.helper) == (2, 0x22CB8)
        service_fn(187, 0, 0, 0, 0x100, ctypes.byref(plan))
        assert (plan.route, plan.counter_after) == (4, 0xFF)
        service_fn(100, 0, 0, 0, 4, ctypes.byref(plan))
        assert plan.route == 0

    print("PASS: 0x21f08 status-latch service routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
