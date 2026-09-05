#!/usr/bin/env python3
"""Validate the recovered 0x1bafc masked call dispatch.

Provenance: synthetic (vonj-maincpu.lst 0x1bafc-0x1bb4c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("counter_addr", ctypes.c_uint32),
        ("masked", ctypes.c_uint32),
        ("dual_call", ctypes.c_int32),
        ("single_call", ctypes.c_int32),
        ("first_call_arg", ctypes.c_uint32),
        ("second_call_arg", ctypes.c_uint32),
        ("bumped_counter", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "masked-call.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_masked_call_1bafc.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_masked_call_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    def run(counter):
        plan = Plan()
        plan_fn(counter, ctypes.byref(plan))
        return plan

    # Zero mask: both calls, then the bump.
    plan = run(0x0)
    assert (plan.masked, plan.dual_call, plan.single_call) == (0, 1, 0)
    assert (plan.first_call_arg, plan.second_call_arg) == (1, 0x1342)
    assert plan.bumped_counter == 0x1
    assert plan.counter_addr == 0x503A04
    plan = run(0x40)
    assert (plan.masked, plan.dual_call, plan.single_call) == (0, 1, 0)
    assert plan.bumped_counter == 0x41

    # 32 mask: the single 0x1ffb0 call with 0, then the bump.
    plan = run(0x20)
    assert (plan.masked, plan.dual_call, plan.single_call) == (32, 0, 1)
    assert (plan.first_call_arg, plan.second_call_arg) == (0, 0x1342)
    assert plan.bumped_counter == 0x21

    # Other masks: bump only, wrapping at the top.
    for counter in (0x1, 0x1F, 0x21, 0x3F, 0x7F, 0xFFFFFFFE, 0xFFFFFFFF):
        plan = run(counter)
        assert plan.masked == counter & 0x3F, hex(counter)
        assert (plan.dual_call, plan.single_call) == (0, 0), hex(counter)
        assert plan.bumped_counter == (counter + 1) & 0xFFFFFFFF, \
            hex(counter)

print("PASS: 0x1bafc masked call dispatch")
