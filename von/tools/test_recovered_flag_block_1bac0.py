#!/usr/bin/env python3
"""Validate the recovered 0x1bac0 conditional flag block.

Provenance: synthetic (vonj-maincpu.lst 0x1bac0-0x1baf8); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("counter_addr", ctypes.c_uint32),
        ("took_branch", ctypes.c_int32),
        ("flag_addr", ctypes.c_uint32),
        ("flag_value", ctypes.c_uint32),
        ("reg_addr", ctypes.c_uint32),
        ("reg_mask", ctypes.c_uint16),
        ("reg_stored", ctypes.c_uint16),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "flag-block.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_flag_block_1bac0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_flag_block_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint16,
                        ctypes.POINTER(Plan)]

    def run(counter, reg):
        plan = Plan()
        plan_fn(counter, reg, ctypes.byref(plan))
        return plan

    # Equality gate on counter 0x118.
    assert run(0x118, 0xFFFF).took_branch == 1
    assert run(0x117, 0xFFFF).took_branch == 0
    assert run(0x119, 0xFFFF).took_branch == 0
    assert run(0x0, 0xFFFF).took_branch == 0
    assert run(0x118, 0xFFFF).counter_addr == 0x503A04

    # Constant flag store and bit-0-clearing mask.
    for reg, want in ((0x0000, 0x0000), (0x0001, 0x0000),
                      (0xFFFE, 0xFFFE), (0xFFFF, 0xFFFE),
                      (0x8001, 0x8000), (0x1234, 0x1234)):
        plan = run(0x118, reg)
        assert (plan.flag_addr, plan.flag_value) == (0x503A00, 7)
        assert plan.reg_addr == 0x10000000
        assert plan.reg_mask == 0xFFFE
        assert plan.reg_stored == want, hex(reg)

print("PASS: 0x1bac0 conditional flag block")
