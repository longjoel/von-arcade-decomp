#!/usr/bin/env python3
"""Validate the 0x21a1c upper-latch render/clear routes."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("render_selected", ctypes.c_uint32),
                ("clear_selected", ctypes.c_uint32),
                ("downstream_selected", ctypes.c_uint32),
                ("state_update_selected", ctypes.c_uint32),
                ("masked_generator_0", ctypes.c_uint32),
                ("state_504d28_after", ctypes.c_uint32),
                ("state_504d30_after", ctypes.c_uint32),
                ("source", ctypes.c_uint32),
                ("helper", ctypes.c_uint32),
                ("column", ctypes.c_uint32),
                ("row", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32),
                ("clear_count", ctypes.c_uint32),
                ("clear_address", ctypes.c_uint32 * 8)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "routes.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_upper_latch_routes.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_upper_latch_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(21, 0x1f0, 0x1234, 0x2aa, ctypes.byref(plan))
    assert (plan.render_selected, plan.clear_selected, plan.downstream_selected,
            plan.state_update_selected, plan.masked_generator_0,
            plan.state_504d28_after, plan.state_504d30_after, plan.row,
            plan.source, plan.helper, plan.width, plan.height) == (
        1, 0, 0, 1, 0x34, (0x1f0 + 0x34) & 0x1ff, 0xaa, 0,
        0x02FDA1D0, 0x1DC10, 0x40, 4
    )

    plan_fn(32, 0, 0, 0, ctypes.byref(plan))
    assert (plan.render_selected, plan.clear_selected, plan.downstream_selected,
            plan.row) == (1, 0, 0, 44)

    plan_fn(33, 0x123, 0x1aa, 0, ctypes.byref(plan))
    assert (plan.render_selected, plan.clear_selected, plan.downstream_selected,
            plan.state_update_selected, plan.state_504d28_after,
            plan.state_504d30_after, plan.clear_count) == (0, 1, 0, 0, 0x123, 0, 8)
    assert list(plan.clear_address) == [0x504D24, 0x504D2C, 0x504D28,
                                        0x504D30, 0x504D26, 0x504D2E,
                                        0x504D2A, 0x504D32]
    plan_fn(34, 0, 0, 0, ctypes.byref(plan))
    assert (plan.render_selected, plan.clear_selected, plan.downstream_selected) == (0, 0, 1)

print("PASS: 0x21a1c upper-latch routes")
