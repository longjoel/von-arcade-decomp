#!/usr/bin/env python3
"""Check the mode-5 dispatch at i960 0x7cfe0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_mode5_dispatch_7cfe0.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("wrapper_target", ctypes.c_uint32),
        ("secondary_target", ctypes.c_uint32),
        ("table_base", ctypes.c_uint32),
        ("writes_status", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("writes_transition", ctypes.c_uint32),
        ("transition_value", ctypes.c_uint32),
        ("writes_action", ctypes.c_uint32),
        ("action_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-mode5-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_mode5_dispatch_7cfe0
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    def run(*values):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        return plan

    plan = run(32, 0, 1)
    assert plan.route == 2 and plan.secondary_target == 0x79D60
    assert plan.status_value == 1

    plan = run(0, 0, 1)
    assert plan.route == 0 and plan.wrapper_target == 0x78408

    plan = run(0, 1, 0)
    assert plan.route == 1 and plan.table_base == 0x72840
    assert plan.action_value == 10 and plan.writes_transition == 0

    plan = run(0, 1, 1)
    assert plan.transition_value == 2 and plan.action_value == 25

print("PASS: 0x7cfe0 transition-mode5 dispatch vectors")
