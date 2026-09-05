#!/usr/bin/env python3
"""Validate the recovered 0x1b960 park-and-publish leaf.

Provenance: synthetic (vonj-maincpu.lst 0x1b960-0x1b97c); no
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
        ("publish_addr", ctypes.c_uint32),
        ("publish_value", ctypes.c_uint32),
        ("link_addr", ctypes.c_uint32),
        ("link_stored", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "park-store.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_park_store_1b960.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_park_store_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    for link in (0x00000000, 0x00001B97C, 0xDEADBEEF):
        plan = Plan()
        plan_fn(link, ctypes.byref(plan))
        assert plan.value_addr == 0x51A260, hex(link)
        # Fixed g0 = 0 input: the clamp stores exactly 0, which parks
        # the uploader (counter slot zeroed below the sub-3 guard).
        assert plan.value_stored == 0, hex(link)
        assert (plan.counter_addr, plan.mode_addr) == (0x51A264, 0x51A268)
        assert (plan.publish_addr, plan.publish_value) == (0x503A00, 25)
        assert (plan.link_addr, plan.link_stored) == (0x5024C6, link)

print("PASS: 0x1b960 park-and-publish leaf")
