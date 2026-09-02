#!/usr/bin/env python3
"""Validate the 0x23980 geometry-object variant preamble."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("fifo_address", ctypes.c_uint32),
        ("command", ctypes.c_uint32),
        ("argument_0", ctypes.c_uint32),
        ("object_parent_delta", ctypes.c_uint32),
        ("first_response", ctypes.c_uint32),
        ("object_172", ctypes.c_int32),
        ("object_172_fixed", ctypes.c_int32),
        ("response_delta", ctypes.c_int32),
        ("response_delta_fixed", ctypes.c_int32),
        ("object_84_minus_504baa", ctypes.c_int32),
        ("transform_path", ctypes.c_uint32),
        ("alternate_path", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "variant.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_object_variant_23980.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_geometry_object_variant_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.c_int16] * 4 + [
        ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0x2000, 0x1000, 0x3000, 23, 40, 5, 10, 8010,
            ctypes.byref(plan))
    assert (plan.fifo_address, plan.command, plan.argument_0,
            plan.object_parent_delta) == (0x884000, 0x0A, 0x3000, 0x1000)
    assert (plan.object_172, plan.object_172_fixed,
            plan.response_delta, plan.response_delta_fixed,
            plan.object_84_minus_504baa) == (23, 0x170000, 8000, 0x1f400000, 35)
    assert (plan.transform_path, plan.alternate_path) == (1, 0)

    plan_fn(0x2000, 0x1000, 0x3000, 21, 40, 5, 10, 8010,
            ctypes.byref(plan))
    assert (plan.transform_path, plan.alternate_path) == (0, 1)

print("PASS: 0x23980 geometry-object variant preamble")
