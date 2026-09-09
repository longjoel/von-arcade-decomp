#!/usr/bin/env python3
"""Validate the bounded 0x21af0 record/text route split."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_record_routes_21af0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "record_dispatch", "record_mode", "text_helper",
        "text_call_count", "downstream_target")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-record-routes-") as directory:
        library = Path(directory) / "routes.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        route_fn = recovered.recovered_status_latch_record_route_plan
        route_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(Plan)]
        plan = Plan()

        route_fn(34, ctypes.byref(plan))
        assert (plan.route, plan.record_dispatch, plan.record_mode,
                plan.text_helper, plan.text_call_count) == (0, 0x211F0, 0, 0x1D250, 3)
        route_fn(35, ctypes.byref(plan))
        assert plan.route == 0

        route_fn(36, ctypes.byref(plan))
        assert (plan.route, plan.downstream_target) == (1, 0x21FA4)

        route_fn(37, ctypes.byref(plan))
        assert (plan.route, plan.record_dispatch, plan.record_mode,
                plan.text_helper, plan.text_call_count) == (2, 0x211F0, 1, 0x1D210, 3)
        route_fn(48, ctypes.byref(plan))
        assert plan.route == 2

        route_fn(49, ctypes.byref(plan))
        assert (plan.route, plan.downstream_target) == (3, 0x21CF8)

    print("PASS: 0x21af0 status-latch record/text routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
