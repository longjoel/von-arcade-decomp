#!/usr/bin/env python3
"""Validate the 0x218f0 status-loop entry/reset contract."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("fill_value_after_entry", ctypes.c_uint32),
                ("reset_branch_taken", ctypes.c_uint32),
                ("marker_value", ctypes.c_uint32),
                ("marker_address", ctypes.c_uint32 * 4),
                ("shared_clear_address", ctypes.c_uint32),
                ("shared_clear_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "entry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_loop_entry_reset.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_loop_entry_reset_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(Plan)]

    for status, taken in ((-1, 0), (0, 1), (37, 1)):
        plan = Plan()
        plan_fn(status, ctypes.byref(plan))
        assert plan.fill_value_after_entry == 0
        assert plan.reset_branch_taken == taken
        assert plan.marker_value == 0x8000
        assert list(plan.marker_address) == [0x504D2C, 0x504D30,
                                              0x504D2E, 0x504D32]
        assert (plan.shared_clear_address, plan.shared_clear_value) == (
            0x01800000, 0)

print("PASS: 0x218f0 status-loop entry/reset")
