#!/usr/bin/env python3
"""Validate the recovered 0xe3a70 three-byte emitter plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("callee", ctypes.c_uint32),
        ("byte_count", ctypes.c_uint32),
        ("offsets", ctypes.c_uint32 * 3),
        ("bytes", ctypes.c_int32 * 3),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "tribyte-emit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_tribyte_emit_e3a70.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_tribyte_emit_plan
    plan_fn.argtypes = [ctypes.c_uint32 * 3, ctypes.POINTER(Plan)]

    raw = (ctypes.c_uint32 * 3)(0x41, 0x80, 0xFF)
    plan = Plan()
    plan_fn(raw, ctypes.byref(plan))
    assert (plan.callee, plan.byte_count) == (0x1D570, 3)
    assert list(plan.offsets) == [0, 1, 2]
    assert list(plan.bytes) == [0x41, -128, -1]

print("PASS: 0xe3a70 three-byte emitter plan")
