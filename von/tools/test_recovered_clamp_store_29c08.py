#!/usr/bin/env python3
"""Validate the recovered 0x29c08 clamp-store plan.

Provenance: synthetic (vonj-maincpu.lst 0x29c08-0x29c4c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("value_addr", ctypes.c_uint32),
        ("zero_addr0", ctypes.c_uint32),
        ("zero_addr1", ctypes.c_uint32),
        ("clamp_max", ctypes.c_int32),
        ("stored", ctypes.c_int32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "clamp-store.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_clamp_store_29c08.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_clamp_store_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0x50, ctypes.byref(plan))
    assert (plan.value_addr, plan.zero_addr0, plan.zero_addr1,
            plan.clamp_max) == (0x51A260, 0x51A264, 0x51A268, 0x100)
    assert plan.stored == 0x50

    def stored(value):
        plan_fn(value, ctypes.byref(plan))
        return plan.stored

    # Ceiling arm: anything above 0x100 stores 0x100.
    assert stored(0x200) == 0x100
    assert stored(0x101) == 0x100
    assert stored(0x100) == 0x100
    # Floor arm: the pre-setbit g5 floor clamps below -256.
    assert stored(-255) == -255
    assert stored(-256) == -256
    assert stored(-257) == -256
    assert stored(-1000) == -256
    assert stored(-0x80000000) == -256
    # Interior values pass through, including the extremes' neighbors.
    assert stored(0) == 0
    assert stored(-1) == -1

print("PASS: 0x29c08 clamp-store plan")
