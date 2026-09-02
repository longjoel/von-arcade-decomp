#!/usr/bin/env python3
"""Validate the 0x21580 and 0x21674 handler contracts."""
import ctypes
import pathlib
import subprocess
import tempfile


class Run(ctypes.Structure):
    _fields_ = [("start", ctypes.c_uint32), ("count", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("text_helper", ctypes.c_uint32),
                ("text_plane", ctypes.c_uint32),
                ("text_column", ctypes.c_uint32),
                ("text_row", ctypes.c_uint32),
                ("text_width", ctypes.c_uint32),
                ("text_height", ctypes.c_uint32),
                ("marker_table_offset", ctypes.c_uint32),
                ("marker_value", ctypes.c_uint32),
                ("marker_run_count", ctypes.c_uint32),
                ("run", Run * 3)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "handlers.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_weapon_irregular_handlers.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_weapon_irregular_handler_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 9 + [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, 5, 1, 2, 3, 7, 4, 11, 5, ctypes.byref(plan))
    assert (plan.text_helper, plan.text_plane, plan.text_column,
            plan.text_height, plan.marker_run_count) == (
        0x1DC10, 0x01000000, 3, 36, 3)
    for run, x, y, count in zip(plan.run, (2, 7, 11), (3, 4, 5), (2, 4, 4)):
        assert (run.start, run.count) == (
            0x01000000 + 0x114 + ((y << 6) + x) * 2, count
        )

    plan_fn(1, 6, 0, 2, 3, 7, 4, 11, 5, ctypes.byref(plan))
    assert (plan.text_helper, plan.text_plane, plan.text_column,
            plan.text_height, plan.marker_run_count) == (
        0x1DD80, 0x01002000, 3, 37, 0)
    assert [run.count for run in plan.run] == [0, 0, 0]

print("PASS: 0x21580/0x21674 irregular handlers")
