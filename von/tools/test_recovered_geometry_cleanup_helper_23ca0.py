#!/usr/bin/env python3
"""Validate the recovered indirect 0x23ca0 cleanup helper."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("return_stub", ctypes.c_uint32),
        ("cleared_object_byte_count", ctypes.c_uint32),
        ("cleared_object_byte_offset", ctypes.c_uint32 * 3),
        ("published_constant", ctypes.c_uint32),
        ("published_address_count", ctypes.c_uint32),
        ("published_address", ctypes.c_uint32 * 2),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "cleanup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_geometry_cleanup_helper_23ca0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    cleanup = lib.recovered_geometry_cleanup_plan
    cleanup.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    cleanup(ctypes.byref(plan))
    assert (plan.return_stub, plan.cleared_object_byte_count,
            list(plan.cleared_object_byte_offset)) == (0x23CD8, 3, [0xA0, 0xA1, 0xA2])
    assert (plan.published_constant, plan.published_address_count,
            list(plan.published_address)) == (0x41200000, 2, [0x504D54, 0x504D58])

print("PASS: 0x23ca0 geometry cleanup helper")
