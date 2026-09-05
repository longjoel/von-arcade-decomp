#!/usr/bin/env python3
"""Validate the recovered 0x1ba70 threshold dispatch tail.

Provenance: synthetic (vonj-maincpu.lst 0x1ba70-0x1babc); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("counter_addr", ctypes.c_uint32),
        ("call_made", ctypes.c_int32),
        ("call_arg", ctypes.c_uint32),
        ("do_store", ctypes.c_int32),
        ("stored_counter", ctypes.c_uint32),
        ("store_final", ctypes.c_int32),
        ("final_addr", ctypes.c_uint32),
        ("final_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "threshold-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_threshold_dispatch_1ba70.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_threshold_dispatch_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint8,
                        ctypes.POINTER(Plan)]

    def run(counter, flag):
        plan = Plan()
        plan_fn(counter, flag, ctypes.byref(plan))
        return plan

    # Threshold gate: the 0x1317 call issues only at counter 480.
    assert run(480, 0x00).call_made == 1
    assert run(480, 0x00).call_arg == 0x1317
    assert run(479, 0x00).call_made == 0
    assert run(481, 0x00).call_made == 0
    assert run(0, 0x00).call_made == 0

    # Set flag bit: no counter store, terminal 22-store always.
    plan = run(0x77, 0x10)
    assert (plan.do_store, plan.store_final) == (0, 1)
    assert plan.stored_counter == 0x77
    assert (plan.final_addr, plan.final_value) == (0x503A00, 22)
    assert plan.counter_addr == 0x503A04

    # Clear flag bit: decrement, terminal store only from counter 1.
    plan = run(0x9, 0x00)
    assert (plan.do_store, plan.stored_counter,
            plan.store_final) == (1, 0x8, 0)
    plan = run(0x1, 0x00)
    assert (plan.do_store, plan.stored_counter,
            plan.store_final) == (1, 0x0, 1)
    plan = run(0x0, 0x00)
    assert (plan.do_store, plan.stored_counter,
            plan.store_final) == (1, 0xFFFFFFFF, 0)
    # Threshold and dispatch compose: call at 480 still decrements.
    plan = run(480, 0x00)
    assert (plan.call_made, plan.do_store, plan.stored_counter,
            plan.store_final) == (1, 1, 479, 0)

print("PASS: 0x1ba70 threshold dispatch tail")
