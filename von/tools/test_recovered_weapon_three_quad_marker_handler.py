#!/usr/bin/env python3
"""Validate the 0x21784 three four-marker runs."""
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
                ("run", Run * 3)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "handler.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_weapon_three_quad_marker_handler.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_weapon_three_quad_marker_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(6, 0, 2, 3, 7, 4, 11, 5, ctypes.byref(plan))
    assert (plan.text_helper, plan.text_plane, plan.text_column,
            plan.text_height, plan.marker_table_offset) == (
        0x1DD80, 0x01002000, 2, 37, 0x110)
    for run, x, y in zip(plan.run, (2, 7, 11), (3, 4, 5)):
        assert (run.start, run.count) == (
            0x01002000 + 0x110 + ((y << 6) + x) * 2, 4
        )

    plan_fn(6, 1, 2, 3, 7, 4, 11, 5, ctypes.byref(plan))
    assert (plan.text_helper, plan.text_plane) == (0x1DC10, 0x01000000)

print("PASS: 0x21784 three-quad marker handler")
