#!/usr/bin/env python3
"""Validate the recovered 0x6ede0 command-6 float-pair plan."""
import ctypes
import pathlib
import struct
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("opcode", ctypes.c_uint32),
        ("table_base", ctypes.c_uint32),
        ("record_size", ctypes.c_uint32),
        ("trunc_x", ctypes.c_int32),
        ("trunc_y", ctypes.c_int32),
        ("valid", ctypes.c_uint32),
        ("index", ctypes.c_uint32),
        ("reject_value", ctypes.c_uint32),
        ("packet", ctypes.c_uint32 * 8),
        ("out_halfwords", ctypes.c_uint32 * 2),
    ]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "command6-pair.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_command6_pair_6ede0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_command6_pair_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Plan)]

    # In-range pair: asymmetric index ty*512 + tx/2, ordered packet.
    plan = Plan()
    plan_fn(bits(100.0), bits(200.0), 11, 22,
            0xA1, 0xA2, 0xA3, 0xA4, ctypes.byref(plan))
    assert (plan.opcode, plan.table_base, plan.record_size,
            plan.reject_value) == (0x41, 0x0051BB28, 20, 0x47C34F80)
    assert (plan.trunc_x, plan.trunc_y, plan.valid) == (100, 200, 1)
    assert plan.index == 200 * 512 + 50
    assert list(plan.packet) == [53, 0xA1, bits(100.0), 0xA3,
                                 bits(200.0), 0xA2 ^ 0x80000000,
                                 0xA4, 0xA2]
    assert list(plan.out_halfwords) == [11, 22]

    # Upper boundary stays valid; just above it rejects.
    plan_fn(bits(1023.9), bits(0.0), 0, 0, 0, 0, 0, 0,
            ctypes.byref(plan))
    assert (plan.trunc_x, plan.valid, plan.index) == (
        1023, 1, 1023 >> 1)
    plan_fn(bits(1024.0), bits(0.0), 0, 0, 0, 0, 0, 0,
            ctypes.byref(plan))
    assert (plan.trunc_x, plan.valid, plan.index) == (1024, 0, 0)

    # Negative inputs truncate toward zero but fail the halved mask.
    plan_fn(struct.unpack("<I", struct.pack("<f", -1.5))[0],
            bits(10.0), 0, 0, 0, 0, 0, 0, ctypes.byref(plan))
    assert (plan.trunc_x, plan.valid) == (-1, 0)

print("PASS: 0x6ede0 command-6 pair plan")
