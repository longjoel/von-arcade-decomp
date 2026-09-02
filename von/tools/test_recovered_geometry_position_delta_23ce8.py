#!/usr/bin/env python3
"""Validate the instruction-level 0x23ce8 signed position update."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("return_stub", ctypes.c_uint32),
        ("raw_delta", ctypes.c_int32),
        ("signed_limit", ctypes.c_int32),
        ("selected_delta", ctypes.c_int32),
        ("stored_position", ctypes.c_int32),
        ("negative_delta_suppressed", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "position_delta.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_position_delta_23ce8.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    update = lib.recovered_geometry_position_delta_plan
    update.argtypes = [
        ctypes.c_int16, ctypes.c_int16, ctypes.c_int16,
        ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    def run(d0, d2, d4, gate):
        plan = Plan()
        update(d0, d2, d4, gate, ctypes.byref(plan))
        return plan

    # delta >= -limit retains the raw delta; the gate suppresses negatives.
    plan = run(120, 100, 5, 0)
    assert (plan.raw_delta, plan.selected_delta,
            plan.stored_position, plan.negative_delta_suppressed) == (20, 20, 120, 0)
    plan = run(120, 100, 5, 1)
    assert (plan.selected_delta, plan.stored_position) == (20, 120)

    # limit > delta: reload the original positive limit.
    plan = run(103, 100, 5, 1)
    assert (plan.raw_delta, plan.selected_delta, plan.stored_position) == (3, 5, 105)

    # The lower-side input follows the same direct branch shape.
    plan = run(90, 100, 5, 1)
    assert (plan.raw_delta, plan.selected_delta, plan.stored_position) == (-10, 5, 105)

    # A negative limit exercises the negated-limit path and its gate.
    plan = run(90, 100, -5, 0)
    assert (plan.raw_delta, plan.selected_delta,
            plan.stored_position, plan.negative_delta_suppressed) == (-10, 0, 100, 1)
    plan = run(90, 100, -5, 1)
    assert (plan.selected_delta, plan.stored_position) == (-5, 95)

    # STOS retains only the signed halfword result after addition.
    plan = run(0x7ffd, 0x7fff, 5, 1)
    assert plan.stored_position == -32764

    assert plan.return_stub == 0x23D5C

print("PASS: 0x23ce8 geometry position delta")
