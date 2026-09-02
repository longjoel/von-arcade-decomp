#!/usr/bin/env python3
"""Validate the 0x214bc five-marker handler."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("text_helper", ctypes.c_uint32),
                ("text_plane", ctypes.c_uint32),
                ("text_column", ctypes.c_uint32),
                ("text_row", ctypes.c_uint32),
                ("text_width", ctypes.c_uint32),
                ("text_height", ctypes.c_uint32),
                ("marker_table_offset", ctypes.c_uint32),
                ("marker_start", ctypes.c_uint32),
                ("marker_value", ctypes.c_uint32),
                ("marker_count", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "handler.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_weapon_five_marker_handler.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_weapon_five_marker_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(4, 0, 6, 9, ctypes.byref(plan))
    assert (plan.text_helper, plan.text_plane, plan.text_column,
            plan.text_row, plan.text_height) == (0x1DD80, 0x01002000, 1, 8, 35)
    assert (plan.marker_start, plan.marker_value, plan.marker_count) == (
        0x01002000 + 0x114 + ((9 << 6) + 6) * 2, 0x2674, 5
    )

    plan_fn(4, 1, 6, 9, ctypes.byref(plan))
    assert plan.text_helper == 0x1DC10
    assert plan.text_plane == 0x01000000

print("PASS: 0x214bc five-marker handler")
