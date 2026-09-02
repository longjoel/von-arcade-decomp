#!/usr/bin/env python3
"""Validate the 0x219a8-0x21a18 status route."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("selected", ctypes.c_uint32),
                ("special_latch_9", ctypes.c_uint32),
                ("masked_generator_0", ctypes.c_uint32),
                ("state_504d28_after", ctypes.c_uint32),
                ("state_504d30_after", ctypes.c_uint32),
                ("source", ctypes.c_uint32),
                ("helper", ctypes.c_uint32),
                ("column", ctypes.c_uint32),
                ("row", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_mid_latch_route.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_mid_latch_route_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(9, 0x1f0, 0x1234, 0x2aa, ctypes.byref(plan))
    assert (plan.selected, plan.special_latch_9, plan.masked_generator_0,
            plan.state_504d28_after, plan.state_504d30_after, plan.row) == (
        1, 1, 0x34, (0x1f0 + 0x34) & 0x1ff, 0xaa, 0
    )
    assert (plan.source, plan.helper, plan.column, plan.width, plan.height) == (
        0x02FEAB34, 0x1DE00, 0, 0x40, 4
    )

    plan_fn(20, 0, 0, 0x3ff, ctypes.byref(plan))
    assert (plan.selected, plan.special_latch_9, plan.row,
            plan.state_504d30_after) == (1, 0, 44, 0x1ff)

    plan_fn(21, 0, 0, 0, ctypes.byref(plan))
    assert plan.selected == 0

print("PASS: 0x219a8 mid-latch route")
