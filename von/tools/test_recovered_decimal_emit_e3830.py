#!/usr/bin/env python3
"""Validate the recovered 0xe3830 decimal emitter plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("saturate_limit", ctypes.c_uint32),
        ("saturated", ctypes.c_uint32),
        ("saturate_string", ctypes.c_uint32),
        ("string_walker", ctypes.c_uint32),
        ("tens_char", ctypes.c_uint32),
        ("ones_char", ctypes.c_uint32),
        ("digit_walker", ctypes.c_uint32),
        ("digit_mode0", ctypes.c_uint32),
        ("digit_mode1", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "decimal-emit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_decimal_emit_e3830.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_decimal_emit_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    # 42 renders as the '4'/'2' pair through the digit walker.
    plan = Plan()
    plan_fn(42, ctypes.byref(plan))
    assert (plan.saturate_limit, plan.saturated, plan.saturate_string,
            plan.string_walker, plan.digit_walker, plan.digit_mode0,
            plan.digit_mode1) == (
        99, 0, 0xE3824, 0x1D9E0, 0x1D310, 3, 0
    )
    assert (plan.tens_char, plan.ones_char) == (0x34, 0x32)

    # Single digits keep a '0' tens place.
    plan_fn(7, ctypes.byref(plan))
    assert (plan.saturated, plan.tens_char, plan.ones_char) == (
        0, 0x30, 0x37)

    # Anything above 99 saturates to the shared "99" string.
    plan_fn(100, ctypes.byref(plan))
    assert (plan.saturated, plan.tens_char, plan.ones_char) == (1, 0, 0)
    plan_fn(0xFFFFFFFF, ctypes.byref(plan))
    assert plan.saturated == 1

print("PASS: 0xe3830 decimal emitter plan")
