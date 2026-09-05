#!/usr/bin/env python3
"""Validate the recovered 0x1ef70 cursor-home dispatch plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("home_addrs", ctypes.c_uint32 * 3),
        ("home_values", ctypes.c_uint32 * 3),
        ("use_fill", ctypes.c_uint32),
        ("fill_width", ctypes.c_uint32),
        ("fill_rows", ctypes.c_uint32),
        ("fill_callee", ctypes.c_uint32),
        ("emit_string", ctypes.c_uint32),
        ("emit_width", ctypes.c_uint32),
        ("emit_rows", ctypes.c_uint32),
        ("emit_callee", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "home-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_home_dispatch_1ef70.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_home_dispatch_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, ctypes.byref(plan))
    assert list(plan.home_addrs) == [0x504CDC, 0x504CE0, 0x504CE4]
    assert list(plan.home_values) == [16, 16, 18]
    assert (plan.use_fill, plan.fill_width, plan.fill_rows,
            plan.fill_callee) == (1, 32, 6, 0x1DF00)
    assert (plan.emit_string, plan.emit_width, plan.emit_rows,
            plan.emit_callee) == (0x2FD6D20, 32, 6, 0x1DC90)

    plan_fn(9, ctypes.byref(plan))
    assert plan.use_fill == 0

print("PASS: 0x1ef70 cursor-home dispatch plan")
