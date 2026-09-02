#!/usr/bin/env python3
"""Validate the 0x9d0d0 persistent countdown prefix."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("frame_value", ctypes.c_uint32),
        ("counter_address", ctypes.c_uint32 * 3),
        ("counter_before", ctypes.c_int32 * 3),
        ("object_flag", ctypes.c_uint32 * 3),
        ("counter_after", ctypes.c_int32 * 3),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "countdowns.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_global_countdowns_9d0d0.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_global_countdowns_plan
    build.argtypes = [
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(Plan),
    ]

    flags = (ctypes.c_uint32 * 3)(1, 0, 0)
    counters = (ctypes.c_int32 * 3)(4, 1, 0)
    plan = Plan()
    build(0x12345678, flags, counters, ctypes.byref(plan))
    assert (plan.frame_value, list(plan.counter_address),
            list(plan.counter_before), list(plan.object_flag),
            list(plan.counter_after)) == (
        0x12345678, [0x562C9C, 0x562CA0, 0x562CA4],
        [4, 1, 0], [1, 0, 0], [0x12345678, 0, 0])

    # Each zero flag decrements only a positive counter; negative and zero
    # values are held by the cmpibge guard.
    flags = (ctypes.c_uint32 * 3)(0, 0, 0)
    counters = (ctypes.c_int32 * 3)(-3, 0, 9)
    plan = Plan()
    build(0xabcdef01, flags, counters, ctypes.byref(plan))
    assert list(plan.counter_after) == [-3, 0, 8]

print("PASS: 0x9d0d0 global countdown prefix")
