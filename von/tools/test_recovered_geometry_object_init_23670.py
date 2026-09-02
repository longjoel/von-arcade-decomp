#!/usr/bin/env python3
"""Validate the recovered 0x23670 geometry-object initializer prefix."""
import ctypes
import pathlib
import struct
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "fifo_address", "first_command", "first_argument_0",
        "first_argument_1", "second_command", "second_argument_0",
        "second_argument_1", "second_response", "object_8_after",
        "object_94_after", "float_bias", "object_0c_plus_bias",
        "third_command", "third_argument_0", "third_argument_1",
        "third_response", "object_90_after", "object_9c_after",
        "object_a0_after", "object_a1_after")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "geometry-init.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_object_init_23670.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_geometry_object_init_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_int16, ctypes.c_int16, ctypes.c_int32,
                        ctypes.c_int16, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0x3F800000, 0x1000, 0x2000, 12, 5, 0x3F000000,
            -2, 0x20, ctypes.byref(plan))
    assert (plan.fifo_address, plan.first_command, plan.first_argument_0,
            plan.first_argument_1) == (0x884000, 0x0A, 0x3F800000,
                                       0x00800000)
    assert (plan.second_command, plan.second_argument_0,
            plan.second_argument_1, plan.second_response) == (
                0x1D, 5, 0x43200000, 0xFFFFFFFE)
    assert (plan.object_8_after, plan.object_94_after) == (0x1002, 0x1002)
    assert (plan.float_bias, plan.object_0c_plus_bias) == (
        0x40200000, struct.unpack("<I", struct.pack("<f", 3.5))[0])
    assert (plan.third_command, plan.third_argument_0,
            plan.third_argument_1, plan.third_response) == (0x1E, 5, 7, 0x20)
    assert (plan.object_90_after, plan.object_9c_after,
            plan.object_a0_after, plan.object_a1_after) == (0x2020, 0x2020, 0, 0)

print("PASS: 0x23670 geometry-object initializer prefix")
