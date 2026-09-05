#!/usr/bin/env python3
"""Validate the recovered 0x1b940 slot-forward leaf.

Provenance: synthetic (vonj-maincpu.lst 0x1b940-0x1b95c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("copy_src_addr", ctypes.c_uint32),
        ("copy_dst_addr", ctypes.c_uint32),
        ("copy_value", ctypes.c_uint16),
        ("call0_arg", ctypes.c_int32),
        ("call1_arg", ctypes.c_uint32),
    ]


def sign_extend(raw):
    return raw - 0x10000 if raw & 0x8000 else raw


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "slot-forward.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_slot_forward_1b940.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_slot_forward_plan
    plan_fn.argtypes = [ctypes.c_uint16, ctypes.POINTER(Plan)]

    for raw in (0x0000, 0x0001, 0x00FF, 0x7FFF, 0x8000, 0x8001,
                0xFFFE, 0xFFFF, 0x1234):
        plan = Plan()
        plan_fn(raw, ctypes.byref(plan))
        assert (plan.copy_src_addr, plan.copy_dst_addr) == \
            (0x503A80, 0x5032F4), hex(raw)
        assert plan.copy_value == raw, hex(raw)
        assert plan.call0_arg == sign_extend(raw), hex(raw)
        assert plan.call1_arg == 3, hex(raw)

print("PASS: 0x1b940 slot-forward leaf")
