#!/usr/bin/env python3
"""Validate the recovered 0x22f0 backup-SRAM record checksum plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("checksum_helper", ctypes.c_uint32),
        ("record_base", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("data_offset", ctypes.c_uint32),
        ("checksum_offset", ctypes.c_uint32),
        ("byte_count", ctypes.c_uint32),
        ("byte_stride", ctypes.c_uint32),
        ("checksum_mask", ctypes.c_uint32),
        ("data_address", ctypes.c_uint32),
        ("checksum_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "record-checksum.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_record_checksum_22f0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_record_checksum_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, ctypes.byref(plan))
    assert (plan.checksum_helper, plan.record_base, plan.record_stride,
            plan.data_offset, plan.checksum_offset, plan.byte_count,
            plan.byte_stride, plan.checksum_mask) == (
        0x3120, 0x01D00000, 524, 0x16, 0x14, 34, 1, 0xFFFF
    )
    assert (plan.data_address, plan.checksum_address) == (
        0x01D00016, 0x01D00014
    )

    # Stride scales linearly: ((i*33)*4-i)*4 == i*524, and the checksum
    # halfword sits two bytes before the checksummed data in each record.
    plan_fn(1, ctypes.byref(plan))
    assert (plan.data_address, plan.checksum_address) == (
        0x01D00016 + 524, 0x01D00014 + 524
    )
    assert plan.data_address - plan.checksum_address == 2

    plan_fn(3, ctypes.byref(plan))
    assert (plan.data_address, plan.checksum_address) == (
        0x01D00016 + 3 * 524, 0x01D00014 + 3 * 524
    )

print("PASS: 0x22f0 record checksum plan")
