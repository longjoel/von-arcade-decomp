#!/usr/bin/env python3
"""Validate the recovered 0x23954 object lifecycle tail."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_18", "state_19_before", "state_19_after",
        "increments_state_19")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "lifecycle-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_object_lifecycle_tail_23954.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_geometry_object_lifecycle_plan
    plan_fn.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, 31, ctypes.byref(plan))
    assert (plan.state_19_after, plan.increments_state_19) == (32, 1)
    plan_fn(0, 32, ctypes.byref(plan))
    assert (plan.state_19_after, plan.increments_state_19) == (32, 0)
    plan_fn(1, 31, ctypes.byref(plan))
    assert (plan.state_19_after, plan.increments_state_19) == (31, 0)

print("PASS: 0x23954 geometry-object lifecycle tail")
