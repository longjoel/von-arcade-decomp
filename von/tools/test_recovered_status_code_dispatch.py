#!/usr/bin/env python3
"""Test the 0x1f710 status-code dispatcher and case table."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_code_dispatch.c"


class Block(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("helper", "source", "width", "height")]


class Plan(ctypes.Structure):
    _fields_ = [("blanking_block", Block), ("selected_block", Block),
                ("selected_message", ctypes.c_uint32), ("selected_case", ctypes.c_uint32),
                ("text_column", ctypes.c_uint32), ("text_row", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-dispatch-") as directory:
        library = Path(directory) / "status-dispatch.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_code_dispatch_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(3, 4, 5, 6, 7, ctypes.byref(plan))
        assert (plan.blanking_block.helper, plan.blanking_block.width,
                plan.blanking_block.height) == (0x1DF00, 38, 3)
        assert (plan.selected_case, plan.selected_block.helper, plan.selected_block.source,
                plan.selected_block.width, plan.selected_block.height,
                plan.selected_message, plan.text_column, plan.text_row) == (3, 0x1DC90, 0x02FE343C, 36, 3, 0x1F6B0, 8, 14)
        plan_fn(5, 4, 5, 6, 7, ctypes.byref(plan))
        assert (plan.selected_block.source, plan.selected_block.width,
                plan.selected_block.height) == (0x02FE33B4, 35, 2)
        plan_fn(0xFFFFFFFF, 1, 2, 3, 4, ctypes.byref(plan))
        assert (plan.selected_case, plan.selected_block.helper, plan.selected_block.source,
                plan.selected_block.width, plan.selected_message) == (8, 0x1DF00, 0, 35, 0x1F700)
        for selector in range(8):
            plan_fn(selector, 0, 0, 0, 0, ctypes.byref(plan))
            assert plan.selected_case == selector

    print("PASS: 0x1f710 status-code dispatcher and case table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
