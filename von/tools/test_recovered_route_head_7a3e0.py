#!/usr/bin/env python3
"""Validate the recovered 0x7a3e0 routing-head plan."""
import ctypes
import pathlib
import subprocess
import tempfile


A, C, RATIO, D = 0, 1, 2, 3


class Plan(ctypes.Structure):
    _fields_ = [
        ("outcome", ctypes.c_uint32),
        ("mode_value", ctypes.c_uint32),
        ("callee", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "route-head.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_route_head_7a3e0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_route_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    def route(own, peer):
        plan = Plan()
        plan_fn(own, peer, ctypes.byref(plan))
        return plan.outcome, plan.mode_value, plan.callee

    # Own==8 wins over every peer value.
    assert route(8, 5) == (A, 11, 0x78790)
    assert route(8, 0) == (A, 11, 0x78790)
    # Peer 0/3 routes to the 0x7a9f0 arm.
    assert route(2, 0) == (C, 9, 0x7A9F0)
    assert route(2, 3) == (C, 9, 0x7A9F0)
    # Own 1/3/4/5 fall into the ratio computation.
    assert route(1, 2)[0] == RATIO
    assert route(3, 2)[0] == RATIO
    assert route(4, 2)[0] == RATIO
    assert route(5, 9)[0] == RATIO
    # Anything else takes the 0x7a4a8 arm.
    assert route(2, 2)[0] == D
    assert route(6, 9)[0] == D

print("PASS: 0x7a3e0 routing-head plan")
