#!/usr/bin/env python3
"""Validate the bounded 0x221b8 text schedule."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_text_schedule_221b8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "latch", "first_row_base", "second_row_base", "separator_base",
        "character_writer", "numeric_helper", "numeric_call_count",
        "character_call_count")] + [
            ("rendered_value", ctypes.c_uint32 * 12),
            ("first_column", ctypes.c_uint32),
            ("second_column", ctypes.c_uint32),
            ("continuation_target", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-text-schedule-") as directory:
        library = Path(directory) / "schedule.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        schedule_fn = recovered.recovered_status_latch_text_schedule_plan
        schedule_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                                ctypes.POINTER(Plan)]
        plan = Plan()
        results = (ctypes.c_uint32 * 10)(1, 12, 23, 34, 45, 56, 67, 78, 89, 90)

        schedule_fn(69, 11, 13, 40, results, ctypes.byref(plan))
        assert (plan.route, plan.character_writer, plan.numeric_helper,
                plan.numeric_call_count, plan.character_call_count,
                plan.first_column, plan.second_column,
                plan.continuation_target) == (0, 0x1CD18, 0xF5058, 10, 12,
                                               13, 13, 0x223FC)
        assert list(plan.rendered_value) == [
            0x31, 0x32, 0x33, 71, 0x34, 0x35, 0x36, 0x37,
            71, 0x38, 0x39, 0x30]

        schedule_fn(70, 11, 13, 40, results, ctypes.byref(plan))
        assert (plan.route, plan.continuation_target) == (1, 0x222B8)

    print("PASS: 0x221b8 status-latch text schedule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
