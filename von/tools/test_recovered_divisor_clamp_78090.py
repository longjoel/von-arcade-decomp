#!/usr/bin/env python3
"""Validate the recovered 0x78090 divisor/saturation plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("divisor", ctypes.c_uint32),
        ("divisor_wide", ctypes.c_uint32),
        ("divisor_narrow", ctypes.c_uint32),
        ("quotient_raw", ctypes.c_int32),
        ("quotient_sat", ctypes.c_int32),
        ("saturate_max", ctypes.c_uint32),
        ("flag_threshold", ctypes.c_uint32),
        ("flag", ctypes.c_int32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "divisor-clamp.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_divisor_clamp_78090.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_divisor_clamp_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_int32,
                        ctypes.POINTER(Plan)]

    # Narrow path with saturation: 10000/100 = 100 clamps to 90,
    # and a dividend above 120 reports the plain flag 1.
    plan = Plan()
    plan_fn(3, 10000, ctypes.byref(plan))
    assert (plan.divisor, plan.divisor_wide, plan.divisor_narrow,
            plan.saturate_max, plan.flag_threshold) == (
        0x64, 0xBB8, 0x64, 90, 120
    )
    assert (plan.quotient_raw, plan.quotient_sat, plan.flag) == (
        100, 90, 1)

    # Mode 4 takes the wide divisor: 6000/3000 = 2, but a dividend
    # above 120 still reports the plain flag 1.
    plan_fn(4, 6000, ctypes.byref(plan))
    assert (plan.divisor, plan.quotient_raw, plan.quotient_sat,
            plan.flag) == (0xBB8, 2, 2, 1)

    # Mode 7 reaches its own check despite comparing above 4.
    plan_fn(7, 90, ctypes.byref(plan))
    assert (plan.divisor, plan.quotient_raw, plan.flag) == (0xBB8, 0, 0)

    # Small dividends keep the raw quotient on both divisors.
    plan_fn(0, 50, ctypes.byref(plan))
    assert (plan.divisor, plan.quotient_raw, plan.flag) == (0x64, 0, 0)

print("PASS: 0x78090 divisor/saturation plan")
