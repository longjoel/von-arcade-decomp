#!/usr/bin/env python3
"""Test the 0x20060 streak-status route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_streak_status_renderer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "initial_column", "initial_row", "initial_clear_width",
                 "initial_clear_height", "message", "message_helper", "digit_helper",
                 "first_tile_source", "first_tile_column_from_g14", "first_tile_width",
                 "first_tile_height", "second_tile_source", "second_tile_column_from_g27",
                 "second_tile_width", "second_tile_height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-streak-status-") as directory:
        library = Path(directory) / "streak-status.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_streak_plan
        plan_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(50, 11, 14, 27, ctypes.byref(plan))
        assert (plan.route, plan.initial_column, plan.initial_row,
                plan.initial_clear_width, plan.initial_clear_height,
                plan.message, plan.message_helper) == (0, 42, 42, 22, 2, 0x20040, 0x1D1F0)
        plan_fn(150, 11, 14, 27, ctypes.byref(plan))
        assert (plan.route, plan.digit_helper, plan.first_tile_source,
                plan.first_tile_column_from_g14, plan.first_tile_width,
                plan.first_tile_height, plan.second_tile_source,
                plan.second_tile_column_from_g27, plan.second_tile_width,
                plan.second_tile_height) == (2, 0x1FF50, 0x2FDFC00, 45, 13, 2,
                                              0x2FDFBFC, 58, 1, 2)
        plan_fn(1, 11, 14, 27, ctypes.byref(plan))
        assert plan.route == 0

    print("PASS: 0x20060 streak-status renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
