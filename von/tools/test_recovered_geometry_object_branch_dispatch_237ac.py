#!/usr/bin/env python3
"""Validate the 0x237ac fixed-point branch dispatcher."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("object_flag_18", ctypes.c_uint32),
        ("first_window", ctypes.c_uint32),
        ("first_response", ctypes.c_int32),
        ("first_window_pass", ctypes.c_uint32),
        ("first_response_pass", ctypes.c_uint32),
        ("second_window", ctypes.c_uint32),
        ("second_response", ctypes.c_int32),
        ("second_window_pass", ctypes.c_uint32),
        ("second_response_pass", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "branch-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_object_branch_dispatch_237ac.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    dispatch = lib.recovered_geometry_object_branch_dispatch_plan
    dispatch.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]

    plan = Plan()
    dispatch(0, 0, 0, ctypes.byref(plan))
    assert (plan.route, plan.first_window, plan.first_response,
            plan.first_window_pass, plan.first_response_pass) == (0, 0x17ff, 0, 1, 1)
    dispatch(1, 0, 0, ctypes.byref(plan))
    assert (plan.route, plan.second_window, plan.second_response,
            plan.second_window_pass, plan.second_response_pass) == (2, 0x1ff, 0, 1, 1)
    dispatch(0, 0, 0xf201, ctypes.byref(plan))
    assert (plan.first_response, plan.second_response,
            plan.first_response_pass, plan.second_response_pass) == (-0xdff, -0xdff, 1, 0)
    dispatch(0, 0, 0xe000, ctypes.byref(plan))
    assert plan.route == 2
    dispatch(0, 0xffff, 0, ctypes.byref(plan))
    assert plan.first_window == 0x17fe and plan.first_window_pass == 1
    assert plan.route == 0

print("PASS: 0x237ac geometry-object branch dispatcher")
