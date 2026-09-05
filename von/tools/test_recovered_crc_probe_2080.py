#!/usr/bin/env python3
"""Validate the recovered 0x2080 adjusted CRC probe plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("checksum_helper", ctypes.c_uint32),
        ("pointer_adjust", ctypes.c_uint32),
        ("byte_count", ctypes.c_uint32),
        ("byte_stride", ctypes.c_uint32),
        ("checksum_mask", ctypes.c_uint32),
        ("data_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "crc-probe.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_crc_probe_2080.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_crc_probe_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0x01D00016, ctypes.byref(plan))
    assert (plan.checksum_helper, plan.pointer_adjust, plan.byte_count,
            plan.byte_stride, plan.checksum_mask) == (
        0x3120, 12, 38, 1, 0xFFFF
    )
    assert plan.data_address == 0x01D00016 + 12

    plan_fn(0, ctypes.byref(plan))
    assert plan.data_address == 12

print("PASS: 0x2080 adjusted CRC probe plan")
