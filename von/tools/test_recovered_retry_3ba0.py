#!/usr/bin/env python3
"""Validate the recovered 0x3ba0 retry controller plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("outcome", ctypes.c_uint32),
        ("calls_copy", ctypes.c_uint32),
        ("copy_adjust", ctypes.c_uint32),
        ("service_arg", ctypes.c_uint32),
        ("calls_service", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "retry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_retry_3ba0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_retry_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    def retry(counter, limit, mode, flag):
        plan = Plan()
        plan_fn(counter, limit, mode, flag, ctypes.byref(plan))
        return (plan.outcome, plan.calls_copy, plan.copy_adjust,
                plan.service_arg, plan.calls_service)

    # Limit inside the stepped counter with a zero mode returns early.
    assert retry(5, 0, 0, 0x10) == (0, 0, 0, 0, 0)
    # A set mode without the flag bit also returns early.
    assert retry(5, 10, 1, 0x00) == (0, 0, 0, 0, 0)
    # Set mode plus flag bit advances straight to the service call.
    assert retry(5, 10, 1, 0x10) == (1, 0, 0, 0x111C, 1)
    # Equality is not the cmpobl branch: zero mode is accepted at the limit.
    assert retry(5, 6, 0, 0x00) == (1, 0, 0, 0x111C, 1)
    # A normal zero-mode step also skips the copy helper.
    assert retry(5, 10, 0, 0x00) == (1, 0, 0, 0x111C, 1)
    # Only the sign-extended 0xffff counter wraps to zero and reaches 0x2330.
    assert retry(-1, 10, 0, 0x00) == (1, 1, 10, 0x111C, 1)

print("PASS: 0x3ba0 retry controller plan")
