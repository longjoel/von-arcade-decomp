#!/usr/bin/env python3
"""Validate the common 0x2381c/0x23b3c transform update."""
import ctypes
import pathlib
import struct
import subprocess
import tempfile


def fbits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "base_x", "base_y", "base_z", "scaled_x", "scaled_y",
        "scaled_z", "object_18_after")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "transform-update.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_object_transform_update_2381c.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    update = lib.recovered_geometry_object_transform_update_plan
    update.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Plan)]

    plan = Plan()
    update(fbits(1.0), fbits(2.0), fbits(3.0),
           fbits(4.0), fbits(8.0), fbits(16.0), fbits(0.5),
           ctypes.byref(plan))
    assert (plan.base_x, plan.base_y, plan.base_z) == (
        fbits(1.0), fbits(2.0), fbits(3.0))
    assert (plan.scaled_x, plan.scaled_y, plan.scaled_z,
            plan.object_18_after) == (fbits(3.0), fbits(4.0), fbits(11.0), 1)

print("PASS: 0x2381c/0x23b3c geometry transform update")
