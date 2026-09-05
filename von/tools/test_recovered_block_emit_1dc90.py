#!/usr/bin/env python3
"""Validate the recovered 0x1dc90 block emitter plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("row_addr", ctypes.c_uint32),
        ("col_addr", ctypes.c_uint32),
        ("plane_base", ctypes.c_uint32),
        ("glyph_attr", ctypes.c_uint32),
        ("row_stride_slots", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("rows", ctypes.c_uint32),
        ("total_halfwords", ctypes.c_uint32),
        ("start_slot", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "block-emit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_block_emit_1dc90.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_block_emit_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]

    # The 0x1ef70 call shape: 32 wide, 6 rows at cursor (16, 16).
    plan = Plan()
    plan_fn(32, 6, 16, 16, ctypes.byref(plan))
    assert (plan.row_addr, plan.col_addr, plan.plane_base,
            plan.glyph_attr, plan.row_stride_slots) == (
        0x504CE4, 0x504CE0, 0x01000000, 0xC000, 64
    )
    assert (plan.width, plan.rows, plan.total_halfwords,
            plan.start_slot) == (32, 6, 192, 16 * 64 + 16)

    # Degenerate shapes emit nothing.
    plan_fn(0, 6, 16, 16, ctypes.byref(plan))
    assert plan.total_halfwords == 0
    plan_fn(32, 0, 16, 16, ctypes.byref(plan))
    assert plan.total_halfwords == 0

print("PASS: 0x1dc90 block emitter plan")
