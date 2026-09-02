#!/usr/bin/env python3
"""Validate the 0x22d30 HUD/reset route."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("fill_destination", ctypes.c_uint32),
                ("fill_group_count", ctypes.c_uint32),
                ("halfwords_per_group", ctypes.c_uint32),
                ("fill_value", ctypes.c_uint32),
                ("cleared_state_count", ctypes.c_uint32),
                ("cleared_state_address", ctypes.c_uint32 * 4),
                ("generator_mask", ctypes.c_uint32),
                ("generator_modulus", ctypes.c_uint32),
                ("generated_value", ctypes.c_uint32),
                ("stored_504d00", ctypes.c_uint32),
                ("uses_fallback_504d00", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "reset.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_hud_reset_22d30.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_hud_reset_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, 0x1002, 0x300, ctypes.byref(plan))
    assert (plan.fill_destination, plan.fill_group_count,
            plan.halfwords_per_group, plan.fill_value) == (
        0x0100C940, 31, 4, 0xFFFF
    )
    assert list(plan.cleared_state_address) == [0x504D26, 0x504CFC,
                                                0x504D08, 0x504D04]
    assert (plan.generated_value, plan.stored_504d00,
            plan.uses_fallback_504d00) == (2, 2, 0)

    plan_fn(7, 0x1003, 0x300, ctypes.byref(plan))
    assert (plan.fill_group_count, plan.generated_value,
            plan.stored_504d00, plan.uses_fallback_504d00) == (38, 3, 3, 0)

    plan_fn(7, 0x1004, 0x300, ctypes.byref(plan))
    assert (plan.generated_value, plan.stored_504d00,
            plan.uses_fallback_504d00) == (4, 0x304, 1)

print("PASS: 0x22d30 HUD/reset route")
