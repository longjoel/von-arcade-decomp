#!/usr/bin/env python3
"""Validate the bounded latch-70 decimal renderer."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_decimal_renderer_222b8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "latch", "first_value", "second_value", "third_value",
        "special_base", "digit_writer", "call_count",
        )] + [("rendered_value", ctypes.c_uint32 * 13),
              ("continuation_target", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-decimal-renderer-") as directory:
        library = Path(directory) / "decimal-renderer.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        render_fn = recovered.recovered_status_latch_decimal_renderer_plan
        render_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.POINTER(Plan)]
        plan = Plan()

        render_fn(70, 1234, 5678, 901, 40, ctypes.byref(plan))
        assert (plan.route, plan.digit_writer, plan.call_count,
                plan.continuation_target) == (1, 0x1D090, 13, 0x223FC)
        assert list(plan.rendered_value) == [
            0x31, 0x32, 0x33, 71, 0x34,
            0x35, 0x36, 0x37, 71, 0x38,
            0x39, 0x30, 0x31]

        render_fn(69, 0, 0, 0, 0, ctypes.byref(plan))
        assert plan.route == 0

    print("PASS: 0x222b8 latch-70 decimal renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
