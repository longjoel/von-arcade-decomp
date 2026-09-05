#!/usr/bin/env python3
"""Validate the recovered 0x7a438/0x7a4a8 ratio-duel plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("obj_ratio", ctypes.c_float),
        ("peer_ratio", ctypes.c_float),
        ("flag_live", ctypes.c_uint32),
        ("wins", ctypes.c_uint32),
        ("win_mode", ctypes.c_uint32),
        ("win_callee", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "ratio-duel.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_ratio_duel_7a438.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_ratio_duel_plan
    plan_fn.argtypes = [ctypes.c_int32 * 4, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    def duel(halves, flag, mode, callee):
        raw = (ctypes.c_int32 * 4)(*halves)
        plan = Plan()
        plan_fn(raw, flag, mode, callee, ctypes.byref(plan))
        return plan

    # 1/2 < 3/4 with a live flag wins the mode-10 arm.
    plan = duel([1, 2, 3, 4], 1, 10, 0x7AD90)
    assert abs(plan.obj_ratio - 0.5) < 1e-6
    assert abs(plan.peer_ratio - 0.75) < 1e-6
    assert (plan.flag_live, plan.wins, plan.win_mode,
            plan.win_callee) == (1, 1, 10, 0x7AD90)

    # Equal ratios never win; a dead flag never wins.
    assert duel([1, 2, 2, 4], 1, 10, 0x7AD90).wins == 0
    assert duel([1, 2, 3, 4], 0, 10, 0x7AD90).wins == 0
    assert duel([1, 2, 3, 4], 2, 10, 0x7AD90).wins == 0

    # The 0x7a4a8 arm shares the predicate with mode 9.
    plan = duel([1, 4, 1, 2], 1, 9, 0x7A9F0)
    assert (plan.wins, plan.win_mode, plan.win_callee) == (1, 9, 0x7A9F0)
    assert duel([3, 4, 1, 2], 1, 9, 0x7A9F0).wins == 0

print("PASS: 0x7a438 ratio-duel plan")
