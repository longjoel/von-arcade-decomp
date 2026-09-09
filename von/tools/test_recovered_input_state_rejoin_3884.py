#!/usr/bin/env python3
"""Validate the 0x3884 input-state rejoin route."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "g0_input", "g7_marker", "combined_value", "route",
        "reset_tail_called", "checksum_helper", "table_copy_helper",
        "reset_tail_return", "state_body_entry")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "rejoin.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_state_rejoin_3884.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    fn = lib.recovered_input_state_rejoin_plan_3884
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    for g0, g7, expected_route in ((0, 0, 0), (1, 0, 1), (0, 1, 1), (0xFFFFFFFF, 0, 1)):
        plan = Plan()
        fn(g0, g7, ctypes.byref(plan))
        assert plan.combined_value == (g0 | g7)
        assert plan.route == expected_route
        assert plan.reset_tail_called == (1 if expected_route == 0 else 0)
        assert (plan.checksum_helper, plan.table_copy_helper,
                plan.reset_tail_return, plan.state_body_entry) == (0x22f0, 0x2330, 0x3a20, 0x388c)

print("PASS: 0x3884 input-state rejoin plan")
