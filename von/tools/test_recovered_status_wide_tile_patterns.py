#!/usr/bin/env python3
"""Validate the 0x22970 and 0x229e0 wide tile-pattern writers."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("base", ctypes.c_uint32),
                ("column", ctypes.c_uint32),
                ("row", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32),
                ("tile_count", ctypes.c_uint32),
                ("first_value", ctypes.c_uint32),
                ("attribute_mask", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "patterns.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_wide_tile_patterns.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_wide_tile_pattern_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]
    value_fn = lib.recovered_status_wide_tile_pattern_value
    value_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    value_fn.restype = ctypes.c_uint32
    destination_fn = lib.recovered_status_wide_tile_pattern_destination
    destination_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_uint32, ctypes.c_uint32]
    destination_fn.restype = ctypes.c_uint32

    for variant, width, base, first in ((0, 23, 0x01000000, 0xFFB0),
                                        (1, 29, 0x01000034, 0xFD10),
                                        (2, 19, 0x01000034, 0xFF40)):
        plan = Plan()
        plan_fn(variant, 5, 7, ctypes.byref(plan))
        assert (plan.base, plan.column, plan.row, plan.width, plan.height,
                plan.tile_count, plan.first_value, plan.attribute_mask) == (
            base, 5, 7, width, 2, width * 2, first, 0xC000
        )
        source = 0x3DB0 if variant == 0 else 0x3D10 if variant == 1 else 0x3F40
        assert value_fn(variant, 0) == 0xC000 + source
        assert value_fn(variant, width * 2 - 1) == 0xC000 + source + width * 2 - 1
        assert destination_fn(variant, 5, 7, width) == base + ((8 << 6) + 5) * 2

print("PASS: 0x22970/0x229e0 wide tile patterns")
