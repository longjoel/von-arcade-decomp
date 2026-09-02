#!/usr/bin/env python3
"""Test the signed 0x1fbe0 status-value renderer route."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_value_renderer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "block_helper", "block_source", "block_width", "block_height",
                 "block_uses_current_position", "column_advance", "glyph_helper",
                 "glyph_source_table", "glyph_index", "glyph_width", "glyph_height",
                 "clear_helper", "clear_width", "clear_height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-value-") as directory:
        library = Path(directory) / "status-value.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_status_value_plan
        plan_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(Plan)]
        plan = Plan()

        plan_fn(-0x31, ctypes.byref(plan))
        assert (plan.route, plan.block_helper, plan.block_source, plan.block_width,
                plan.block_height, plan.block_uses_current_position, plan.column_advance,
                plan.glyph_helper, plan.glyph_source_table, plan.glyph_index,
                plan.glyph_width, plan.glyph_height) == (0, 0x1DC10, 0x2FE17EC, 20, 3, 1, 21,
                                                          0x1DC10, 0x2EA1FD0, 15, 4, 3)

        plan_fn(0, ctypes.byref(plan))
        assert (plan.route, plan.clear_helper, plan.clear_width, plan.clear_height) == (1, 0x1DF00, 25, 3)

    print("PASS: 0x1fbe0/0x1e7c0 signed status-value renderer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
