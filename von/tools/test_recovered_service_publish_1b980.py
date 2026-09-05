#!/usr/bin/env python3
"""Validate the recovered 0x1b980 service-publish leaf.

Provenance: synthetic (vonj-maincpu.lst 0x1b980-0x1b9c4); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("value_addr", ctypes.c_uint32),
        ("value_stored", ctypes.c_int32),
        ("counter_addr", ctypes.c_uint32),
        ("mode_addr", ctypes.c_uint32),
        ("table0_addr", ctypes.c_uint32),
        ("table0_value", ctypes.c_uint32),
        ("table1_addr", ctypes.c_uint32),
        ("table1_value", ctypes.c_uint32),
        ("table2_addr", ctypes.c_uint32),
        ("table2_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "service-publish.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_service_publish_1b980.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_service_publish_plan
    plan_fn.argtypes = [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(ctypes.byref(plan))
    # Fixed g0 = 0 input parks the uploader through the clamp.
    assert (plan.value_addr, plan.value_stored) == (0x51A260, 0)
    assert (plan.counter_addr, plan.mode_addr) == (0x51A264, 0x51A268)
    # Three service-table constants around the sub-calls.
    assert (plan.table0_addr, plan.table0_value) == (0x503A04, 0x14A)
    assert (plan.table1_addr, plan.table1_value) == (0x503A00, 16)
    assert (plan.table2_addr, plan.table2_value) == (0x577170, 0xFFFFFFFF)

print("PASS: 0x1b980 service-publish leaf")
