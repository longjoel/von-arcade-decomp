#!/usr/bin/env python3
"""Check the state-8/9 gate at i960 0x7e0d0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_state89_gate_7e0d0.c"


class Plan(ctypes.Structure):
    _fields_ = [("is_state_8_or_9", ctypes.c_uint32),
                ("float_gate_passed", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-state89.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_state89_gate_7e0d0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    for state in (8, 9):
        plan = Plan()
        function(state, 0, ctypes.byref(plan))
        assert (plan.is_state_8_or_9, plan.route, plan.target) == (1, 1, 0x7E130)
        plan = Plan()
        function(state, 1, ctypes.byref(plan))
        assert (plan.route, plan.target) == (2, 0x81610)
    plan = Plan()
    function(7, 0, ctypes.byref(plan))
    assert (plan.is_state_8_or_9, plan.route, plan.target) == (0, 3, 0x7E144)

print("PASS: 0x7e0d0 state-8/9 gate vectors")
