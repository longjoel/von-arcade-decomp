#!/usr/bin/env python3
"""Check the mode-5 route at i960 0x7ceb0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_mode5_route_7ceb0.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("coordinate_path", ctypes.c_uint32),
        ("selector_source", ctypes.c_uint32),
        ("selector_index", ctypes.c_uint32),
        ("table_base", ctypes.c_uint32),
        ("wrapper_target", ctypes.c_uint32),
        ("writes_status", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("writes_transition", ctypes.c_uint32),
        ("transition_value", ctypes.c_uint32),
        ("writes_action", ctypes.c_uint32),
        ("action_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-mode5-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_mode5_route_7ceb0
    function.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Plan)]
    function.restype = None

    def run(*values):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        return plan

    plan = run(0, 0, 0, 2, 4, 6)
    assert plan.route == 0 and plan.coordinate_path == 0
    assert plan.selector_index == 6 and plan.table_base == 0x72780
    assert (plan.status_value, plan.action_value) == (1, 30)

    plan = run(0, 0, 0, 3, 9, 6)
    assert plan.coordinate_path == 1 and plan.selector_source == 1
    assert plan.selector_index == 9

    assert run(32, 0, 1, 3, 9, 6).route == 2
    plan = run(32, 1, 0, 3, 9, 6)
    assert plan.route == 1 and plan.table_base == 0x72840
    assert plan.action_value == 10 and plan.writes_transition == 0

    plan = run(32, 1, 1, 3, 9, 6)
    assert (plan.transition_value, plan.action_value) == (2, 25)

print("PASS: 0x7ceb0 transition-mode5 route vectors")
