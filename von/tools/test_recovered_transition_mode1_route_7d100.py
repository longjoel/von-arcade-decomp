#!/usr/bin/env python3
"""Check the mode-1 route at i960 0x7d100."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_mode1_route_7d100.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("entry_target", ctypes.c_uint32),
        ("wrapper_target", ctypes.c_uint32),
        ("table_base", ctypes.c_uint32),
        ("writes_status", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("writes_transition", ctypes.c_uint32),
        ("transition_value", ctypes.c_uint32),
        ("writes_action", ctypes.c_uint32),
        ("action_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-mode1-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_mode1_route_7d100
    function.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Plan)]
    function.restype = None

    def run(*values):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        return plan

    plan = run(2, 0, 1, 0, 3, 0)
    assert plan.route == 0 and plan.entry_target == 0x7A3E0

    plan = run(0, 1, 1, 2, 3, 0)
    assert plan.route == 1 and plan.wrapper_target == 0x78408
    assert (plan.transition_value, plan.action_value, plan.status_value) == (2, 30, 1)

    plan = run(0, 1, 1, 2, 7, 0)
    assert plan.writes_status == 0

    plan = run(0, 0, 0, 0, 3, 0)
    assert plan.route == 2 and plan.table_base == 0x72840
    assert plan.action_value == 10 and plan.writes_action == 1
    assert plan.writes_transition == 0

    plan = run(0, 0, 0, 0, 3, 1)
    assert (plan.transition_value, plan.action_value, plan.status_value) == (2, 30, 1)
    plan = run(0, 0, 1, 0, 7, 0)
    assert plan.writes_transition == 1 and plan.writes_status == 0

print("PASS: 0x7d100 transition-mode1 route vectors")
