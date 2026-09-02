#!/usr/bin/env python3
"""Validate the 0x228f0 16x7 tile pattern writer."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("plane", ctypes.c_uint32),
                ("column", ctypes.c_uint32),
                ("first_row", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32),
                ("tile_count", ctypes.c_uint32),
                ("first_value", ctypes.c_uint32),
                ("attribute_mask", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "pattern.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_tile_pattern_228f0.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_tile_pattern_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    value_fn = lib.recovered_status_tile_pattern_value
    value_fn.argtypes = [ctypes.c_uint32]
    value_fn.restype = ctypes.c_uint32
    destination_fn = lib.recovered_status_tile_pattern_destination
    destination_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    destination_fn.restype = ctypes.c_uint32

    plan = Plan()
    plan_fn(12, 63, ctypes.byref(plan))
    assert (plan.plane, plan.column, plan.first_row, plan.width,
            plan.height, plan.tile_count, plan.first_value,
            plan.attribute_mask) == (0x01000000, 12, 63, 16, 7, 112,
                                     0xD488, 0xC000)
    assert value_fn(0) == 0xD488
    assert value_fn(111) == 0xD4F7
    assert destination_fn(12, 63, 0) == 0x01000000 + ((63 << 6) + 12) * 2
    assert destination_fn(12, 63, 16) == 0x01000000 + (12) * 2

print("PASS: 0x228f0 tile pattern")
