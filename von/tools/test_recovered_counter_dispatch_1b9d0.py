#!/usr/bin/env python3
"""Validate the recovered 0x1b9d0 counter dispatch schedule.

Provenance: synthetic (vonj-maincpu.lst 0x1b9d0-0x1ba08); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("counter_addr", ctypes.c_uint32),
        ("call_arg", ctypes.c_uint32),
        ("do_store", ctypes.c_int32),
        ("stored_counter", ctypes.c_uint32),
        ("take_link_block", ctypes.c_int32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "counter-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_counter_dispatch_1b9d0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_counter_dispatch_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint8,
                        ctypes.POINTER(Plan)]

    def run(counter, flag):
        plan = Plan()
        plan_fn(counter, flag, ctypes.byref(plan))
        return plan

    # Masked call argument always reflects bit 5 of the entry counter.
    assert run(0x00000000, 0x00).call_arg == 0
    assert run(0x00000020, 0x00).call_arg == 32
    assert run(0xFFFFFFFF, 0x00).call_arg == 32
    assert run(0x0000001F, 0x00).call_arg == 0

    # Set flag bit bypasses the store and takes the link block.
    plan = run(0x12345678, 0x10)
    assert (plan.do_store, plan.take_link_block) == (0, 1)
    assert plan.stored_counter == 0x12345678
    plan = run(0x1, 0xFF)
    assert (plan.do_store, plan.take_link_block) == (0, 1)

    # Clear flag bit: decrement in place, link only from counter 1.
    plan = run(0x5, 0x00)
    assert (plan.do_store, plan.stored_counter,
            plan.take_link_block) == (1, 0x4, 0)
    assert plan.counter_addr == 0x503A04
    plan = run(0x1, 0x00)
    assert (plan.do_store, plan.stored_counter,
            plan.take_link_block) == (1, 0x0, 1)
    # Wrap-around decrements return, never link.
    plan = run(0x0, 0x00)
    assert (plan.do_store, plan.stored_counter,
            plan.take_link_block) == (1, 0xFFFFFFFF, 0)

print("PASS: 0x1b9d0 counter dispatch schedule")
