#!/usr/bin/env python3
"""Validate the recovered stateful 0x23410 status renderer."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "eligible", "draws_block", "mode", "mode_table", "helper",
        "source_table", "source_table_selector", "source_table_entry",
        "source_table_index",
        "width", "height", "column", "row", "next_generator_state",
        "next_status_state", "generator_modulus")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "mode-renderer.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_mode_renderer_23410.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_mode_renderer_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, 2, 0x20, 3, 5, 11, ctypes.byref(plan))
    assert (plan.eligible, plan.draws_block, plan.helper,
            plan.source_table, plan.source_table_selector,
            plan.source_table_entry, plan.source_table_index, plan.width,
            plan.height,
            plan.column, plan.row) == (1, 1, 0x1DD80, 0x2EA289C, 3,
                                       0x2EA28B4, 5, 2, 4, 58, 36)
    assert (plan.next_generator_state, plan.next_status_state) == (6, 0x1e)

    plan_fn(0, 9, 0x21, 0, 5, 11, ctypes.byref(plan))
    assert (plan.eligible, plan.draws_block, plan.width,
            plan.next_status_state) == (1, 0, 0, 0x1f)

    for mode in (5, 6, 8, 10):
        plan_fn(0, mode, 0, 0, 0, 11, ctypes.byref(plan))
        assert plan.eligible == 0 and plan.draws_block == 0
    plan_fn(1, 2, 0, 0, 0, 11, ctypes.byref(plan))
    assert plan.eligible == 0 and plan.next_generator_state == 0

print("PASS: 0x23410 stateful status renderer")
