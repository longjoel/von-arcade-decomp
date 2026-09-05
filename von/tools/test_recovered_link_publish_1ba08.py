#!/usr/bin/env python3
"""Validate the recovered 0x1ba08 link-publish block.

Provenance: synthetic (vonj-maincpu.lst 0x1ba08-0x1ba24); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("call_arg", ctypes.c_uint32),
        ("flag_addr", ctypes.c_uint32),
        ("flag_value", ctypes.c_uint32),
        ("link_addr", ctypes.c_uint32),
        ("link_stored", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "link-publish.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_link_publish_1ba08.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_link_publish_plan
    plan_fn.argtypes = [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(ctypes.byref(plan))
    assert plan.call_arg == 2
    assert (plan.flag_addr, plan.flag_value) == (0x5039F4, 1)
    # The stored link is the call's own resume address, not the entry link.
    assert (plan.link_addr, plan.link_stored) == (0x503A00, 0x1BA10)

print("PASS: 0x1ba08 link-publish block")
