#!/usr/bin/env python3
"""Test the 0x1d570 status-glyph normalization and source selection."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_status_glyph.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("glyph_index", "source_kind", "source", "descriptor", "rows", "adjustment")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-glyph-") as directory:
        library = Path(directory) / "status-glyph.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_status_glyph_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
        plan = Plan()
        adjustment = ctypes.c_uint32(1)

        plan_fn(0x61, ctypes.byref(adjustment), ctypes.byref(plan))
        assert (plan.glyph_index, plan.source_kind, plan.source, plan.descriptor, plan.rows, plan.adjustment) == (65, 0, 0, 0x02EA16D8, 2, 1)
        plan_fn(0x49, None, ctypes.byref(plan))
        assert (plan.glyph_index, plan.source_kind, plan.source) == (41, 1, 0x02FD7C90)
        plan_fn(0x4A, None, ctypes.byref(plan))
        assert (plan.glyph_index, plan.source_kind, plan.source) == (42, 1, 0x02FD7C98)
        plan_fn(0x00, None, ctypes.byref(plan))
        assert plan.glyph_index == 0
        plan_fn(0xFF, None, ctypes.byref(plan))
        assert plan.glyph_index == 95

    print("PASS: 0x1d570 status-glyph normalization and source selection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
