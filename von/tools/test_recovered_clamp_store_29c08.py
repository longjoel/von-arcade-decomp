#!/usr/bin/env python3
"""Validate the recovered 0x29c08 clamp-store plan."""
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

    plan_fn(0x200, ctypes.byref(plan))
    assert plan.stored == 0x100
    plan_fn(0x100, ctypes.byref(plan))
    assert plan.stored == 0x100
    plan_fn(-1000, ctypes.byref(plan))
    assert plan.stored == -1000
    plan_fn(-256, ctypes.byref(plan))
    assert plan.stored == -256

print("PASS: 0x29c08 clamp-store plan")
