#!/usr/bin/env python3
"""Validate the recovered 0x209c0-0x20a18 status route descriptors."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("source", ctypes.c_uint32),
        ("helper", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("column_comes_from_current_position", ctypes.c_uint32),
        ("row_comes_from_current_position", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "routes.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" / "recovered_attributed_status_routes_209c0.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_attributed_status_route_209c0_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    expected = [(0x02FD09A4, 28), (0x02FD07F4, 27)]
    for route, (source, width) in enumerate(expected):
        plan = Plan()
        plan_fn(route, 1, ctypes.byref(plan))
        assert (plan.source, plan.helper, plan.width, plan.height) == (
            source, 0x1DC90, width, 8
        )
        assert plan.column_comes_from_current_position == 1
        assert plan.row_comes_from_current_position == 1

    plan = Plan()
    plan_fn(0, 0, ctypes.byref(plan))
    assert (plan.source, plan.helper) == (0, 0x1DF00)

print("PASS: 0x209c0-0x20a18 attributed status routes")
