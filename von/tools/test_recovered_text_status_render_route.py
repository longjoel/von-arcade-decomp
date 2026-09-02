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

    print("PASS: 0x1e030 stable status-render route and frame contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
