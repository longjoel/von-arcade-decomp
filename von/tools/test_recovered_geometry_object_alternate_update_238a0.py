#!/usr/bin/env python3
"""Validate the 0x238a0 alternate geometry-object update."""
import ctypes
import pathlib
import struct
import subprocess
import tempfile


def fbits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "fifo_address", "first_command", "first_argument_0",
        "first_argument_1", "first_response", "object_8_after_first",
        "object_0c_after_first", "float_bias", "adjusted_object_0c",
        "object_4_after", "object_10_after", "second_command",
        "second_argument_0", "second_argument_1", "second_response",
        "object_8_after_second", "object_14_after_second",
        "object_18_after", "object_19_after")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "alternate-update.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_object_alternate_update_238a0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    update = lib.recovered_geometry_object_alternate_update_plan
    update.argtypes = [ctypes.c_uint32] * 3 + [ctypes.c_int16,
                         ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]

    plan = Plan()
    update(0x1000, fbits(1.0), 0x2000, 5, -7, 0x20, 0x30,
           ctypes.byref(plan))
    assert (plan.fifo_address, plan.first_command, plan.first_argument_0,
            plan.first_argument_1, plan.first_response) == (
                0x884000, 0x1D, 5, 0x43200000, 0x20)
    assert (plan.object_8_after_first, plan.object_0c_after_first) == (0xFE0, 0xFE0)
    assert (plan.float_bias, plan.adjusted_object_0c,
            plan.object_4_after, plan.object_10_after) == (
                0x40200000, fbits(3.5), fbits(3.5), fbits(3.5))
    assert (plan.second_command, plan.second_argument_0,
            plan.second_argument_1, plan.second_response) == (0x1E, 5, 0xFFFFFFF9, 0x30)
    assert (plan.object_8_after_second, plan.object_14_after_second,
            plan.object_18_after, plan.object_19_after) == (0x2030, 0x2030, 0, 0)

print("PASS: 0x238a0 alternate geometry-object update")
