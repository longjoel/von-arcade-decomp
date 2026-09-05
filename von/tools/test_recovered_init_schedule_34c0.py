#!/usr/bin/env python3
"""Validate the recovered 0x34c0 fixed init schedule."""
import ctypes
import pathlib
import subprocess
import tempfile


STORE8, STORE16, STORE32, CALL = 1, 2, 4, 0

EXPECTED = [
    (STORE8, 0x5024CD), (STORE8, 0x5024CC), (STORE16, 0x5024CE),
    (STORE8, 0x5024D1), (STORE8, 0x5024D0), (STORE16, 0x5024D2),
    (STORE16, 0x5024C0), (STORE16, 0x5024C2),
    (CALL, 0x22F0), (CALL, 0x2330),
    (STORE16, 0x5023F2), (STORE16, 0x5024C4), (STORE16, 0x5024C6),
    (STORE16, 0x5024C8), (STORE32, 0x5023E4),
]


class Op(ctypes.Structure):
    _fields_ = [("kind", ctypes.c_uint32), ("address", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "init-schedule.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_init_schedule_34c0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    lib.recovered_init_op_count.restype = ctypes.c_uint32
    op_at = lib.recovered_init_op_at
    op_at.argtypes = [ctypes.c_uint32, ctypes.POINTER(Op)]

    assert lib.recovered_init_op_count() == len(EXPECTED)
    for index, (kind, address) in enumerate(EXPECTED):
        op = Op()
        op_at(index, ctypes.byref(op))
        assert (op.kind, op.address) == (kind, address), index
    op = Op()
    op_at(99, ctypes.byref(op))
    assert (op.kind, op.address) == (0, 0)

print("PASS: 0x34c0 fixed init schedule")
