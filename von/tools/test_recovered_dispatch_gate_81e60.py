#!/usr/bin/env python3
"""Validate the recovered 0x81e60 dispatch-gate plan."""
import ctypes
import pathlib
import subprocess
import tempfile


TARGETS = (0x81EDC, 0x81EE8, 0x81EF4, 0x81F00, 0x81F0C,
           0x81F18, 0x81F24, 0x81F30, 0x81F3C, 0x81F48)


class Plan(ctypes.Structure):
    _fields_ = [
        ("mode_match", ctypes.c_uint32),
        ("sub_mode_match", ctypes.c_uint32),
        ("pre_call", ctypes.c_uint32),
        ("calls_pre", ctypes.c_uint32),
        ("state_max", ctypes.c_uint32),
        ("table_base", ctypes.c_uint32),
        ("table_targets", ctypes.c_uint32 * 10),
        ("target", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "dispatch-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_dispatch_gate_81e60.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_dispatch_gate_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]

    # Full gate: mode 4, sub-mode 10, live flag, state 3.
    plan = Plan()
    plan_fn(4, 10, 1, 3, ctypes.byref(plan))
    assert (plan.mode_match, plan.sub_mode_match, plan.pre_call,
            plan.calls_pre, plan.state_max, plan.table_base) == (
        4, 10, 0x84D90, 1, 9, 0x81EB4
    )
    assert list(plan.table_targets) == list(TARGETS)
    assert plan.target == 0x81F00

    # The pre-call needs all three conditions; the table needs flag+bound.
    plan_fn(4, 10, 0, 3, ctypes.byref(plan))
    assert (plan.calls_pre, plan.target) == (0, 0)
    plan_fn(4, 9, 5, 0, ctypes.byref(plan))
    assert (plan.calls_pre, plan.target) == (0, TARGETS[0])
    plan_fn(0, 0, 7, 9, ctypes.byref(plan))
    assert (plan.calls_pre, plan.target) == (0, TARGETS[9])

    # States above 9 exit through the shared return.
    plan_fn(4, 10, 1, 10, ctypes.byref(plan))
    assert (plan.calls_pre, plan.target) == (1, 0)

print("PASS: 0x81e60 dispatch-gate plan")
