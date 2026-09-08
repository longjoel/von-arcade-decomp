#!/usr/bin/env python3
"""Check the mode/timing gate at i960 0x7cc50."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_mode_gate_7cc50.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("entry_target", ctypes.c_uint32),
        ("timing_target", ctypes.c_uint32),
        ("writes_status", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("writes_transition", ctypes.c_uint32),
        ("transition_value", ctypes.c_uint32),
        ("writes_action", ctypes.c_uint32),
        ("action_value", ctypes.c_uint32),
        ("writes_selector", ctypes.c_uint32),
        ("selector_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-mode-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_mode_gate_7cc50
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    def run(*values):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        return plan

    plan = run(0, 1, 1, 1, 1)
    assert plan.route == 0 and plan.entry_target == 0x7A3E0

    plan = run(2, 0, 1, 1, 1)
    assert plan.route == 1
    assert (plan.status_value, plan.action_value) == (1, 30)
    assert plan.writes_transition == 0
    assert plan.writes_selector == 1 and plan.selector_value == 3

    plan = run(2, 1, 0, 0, 1)
    assert plan.route == 2 and plan.timing_target == 0x78408
    assert plan.writes_selector == 0

    plan = run(2, 1, 1, 1, 1)
    assert plan.writes_selector == 1 and plan.selector_value == 3
    assert run(2, 1, 1, 1, 0).writes_selector == 0

print("PASS: 0x7cc50 transition-mode gate vectors")
