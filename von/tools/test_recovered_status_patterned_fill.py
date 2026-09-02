#!/usr/bin/env python3
"""Validate the 0x22840 patterned fill and 0x228b0 state update."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("fill_selected", ctypes.c_uint32),
                ("destination", ctypes.c_uint32),
                ("repetition_count", ctypes.c_uint32),
                ("fill_repetitions_per_group", ctypes.c_uint32),
                ("solid_repetitions_per_group", ctypes.c_uint32),
                ("fill_value", ctypes.c_uint32),
                ("solid_value", ctypes.c_uint32),
                ("state_504d28_after", ctypes.c_uint32),
                ("state_504d2a_after", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "fill.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_patterned_fill.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_patterned_fill_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(1, 1, 0x1f0, 0x20, 0x2aa, 0x1234, ctypes.byref(plan))
    assert (plan.fill_selected, plan.destination, plan.repetition_count,
            plan.fill_repetitions_per_group, plan.solid_repetitions_per_group,
            plan.fill_value, plan.solid_value) == (
        1, 0x0100d002, 192, 4, 4, 0x1234, 0xffff
    )
    assert (plan.state_504d28_after, plan.state_504d2a_after) == (
        (0x1f0 + 0xaa) & 0x1ff, (0x2aa - 0x20) & 0x1ff
    )

    plan_fn(192, 1, 0, 0, 0, 0, ctypes.byref(plan))
    assert plan.fill_selected == 0
    plan_fn(1, 2, 0, 0, 0, 0, ctypes.byref(plan))
    assert plan.fill_selected == 0

print("PASS: 0x22840 patterned fill")
