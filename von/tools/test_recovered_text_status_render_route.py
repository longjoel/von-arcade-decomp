#!/usr/bin/env python3
"""Test the recovered stable entry route and frame contract at 0x1e030."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_status_render_route.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "source", "column", "row", "width", "height",
                 "saved_general_register_words", "saved_special_register_words",
                 "saved_fp_registers", "stack_frame_bytes")]


class SecondaryPairPlan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("secondary_word", "source", "source_width", "blank_width",
                 "column", "row", "height", "source_helper", "blank_helper")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-render-") as directory:
        library = Path(directory) / "status-render.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_status_render_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 0xFFFFFFF5, ctypes.byref(plan))
        assert (plan.route, plan.source, plan.column, plan.row, plan.width, plan.height) == (0, 0x02FD81EC, 1, 20, 19, 2)
        assert (plan.saved_general_register_words, plan.saved_special_register_words,
                plan.saved_fp_registers, plan.stack_frame_bytes) == (8, 2, 4, 0x50)
        plan_fn(0, 12, ctypes.byref(plan))
        assert (plan.route, plan.source, plan.width, plan.height) == (1, 0, 0, 0)
        gate_fn = recovered.recovered_text_status_render_gate_plan
        gate_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Plan)]
        gate_fn(0, 0, 0, 12, ctypes.byref(plan))
        assert (plan.route, plan.source, plan.column, plan.row,
                plan.width, plan.height) == (2, 0, 1, 43, 21, 2)
        gate_fn(0, 1, 0, 12, ctypes.byref(plan))
        assert plan.route == 1
        gate_fn(0, 0, 1, 12, ctypes.byref(plan))
        assert plan.route == 1
        pair_fn = recovered.recovered_text_status_secondary_pair_plan
        pair_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(SecondaryPairPlan)]
        pair = SecondaryPairPlan()
        pair_fn(1, 12, ctypes.byref(pair))
        assert (pair.source, pair.source_width, pair.blank_width,
                pair.column, pair.row, pair.height,
                pair.source_helper, pair.blank_helper) == (
            0x02FD8170, 14, 15, 1, 43, 2, 0x1DD10, 0x1DF70)
        pair_fn(0xFFFFFFFF, 12, ctypes.byref(pair))
        assert (pair.source, pair.source_width, pair.blank_width) == (
            0x02FD81A8, 16, 17)

    print("PASS: 0x1e030 stable status-render route and frame contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
