#!/usr/bin/env python3
"""Validate the recovered 0x1df00 block fill plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("row_addr", ctypes.c_uint32),
        ("col_addr", ctypes.c_uint32),
        ("plane_base", ctypes.c_uint32),
        ("fill_is_caller_link", ctypes.c_uint32),
        ("row_stride_slots", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("rows", ctypes.c_uint32),
        ("total_tiles", ctypes.c_uint32),
        ("start_slot", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "block-fill.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_block_fill_1df00.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_block_fill_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]

    # The 0x1ef70 call shape: 32 wide, 6 rows at cursor (16, 16).
    plan = Plan()
    plan_fn(32, 6, 16, 16, ctypes.byref(plan))
    assert (plan.row_addr, plan.col_addr, plan.plane_base,
            plan.fill_is_caller_link, plan.row_stride_slots) == (
        0x504CE4, 0x504CE0, 0x01000000, 1, 64
    )
    assert (plan.width, plan.rows, plan.total_tiles,
            plan.start_slot) == (32, 6, 192, 16 * 64 + 16)

    # Degenerate shapes fill nothing.
    plan_fn(0, 6, 16, 16, ctypes.byref(plan))
    assert plan.total_tiles == 0
    plan_fn(32, 0, 16, 16, ctypes.byref(plan))
    assert plan.total_tiles == 0

print("PASS: 0x1df00 block fill plan")
