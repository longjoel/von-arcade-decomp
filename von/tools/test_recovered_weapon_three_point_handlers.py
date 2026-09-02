#!/usr/bin/env python3
"""Validate shared three-point weapon-handler geometry."""
import ctypes
import pathlib
import subprocess
import tempfile


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_uint32), ("y", ctypes.c_uint32),
                ("destination", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("text_helper", ctypes.c_uint32),
                ("text_plane", ctypes.c_uint32),
                ("text_column", ctypes.c_uint32),
                ("text_row", ctypes.c_uint32),
                ("text_width", ctypes.c_uint32),
                ("text_height", ctypes.c_uint32),
                ("marker_table_offset", ctypes.c_uint32),
                ("point", Point * 3)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "handlers.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_weapon_three_point_handlers.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_weapon_three_point_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 10 + [ctypes.POINTER(Plan)]

    for kind, table in ((0, 0x114), (1, 0x118), (4, 0x110)):
        plan = Plan()
        plan_fn(kind, 5, 0, 0x1234, 2, 3, 7, 4, 11, 5, ctypes.byref(plan))
        assert (plan.text_helper, plan.text_plane, plan.text_height,
                plan.marker_table_offset) == (0x1DD80, 0x01002000, 36, table)
        for point, x, y in zip(plan.point, (2, 7, 11), (3, 4, 5)):
            assert (point.x, point.y, point.destination) == (
                x, y, 0x01002000 + table + ((y << 6) + x) * 2
            )

        plan_fn(kind, 0, 1, 0x1234, 2, 3, 7, 4, 11, 5, ctypes.byref(plan))
        assert (plan.text_helper, plan.text_plane, plan.text_height) == (
            0x1DC10, 0x01000000, 31
        )

print("PASS: 0x21240/0x21314/0x213e8 three-point handlers")
