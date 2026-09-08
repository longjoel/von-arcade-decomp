#!/usr/bin/env python3
"""Check connected high-confidence gates in producer 0x7d920."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_gate_chain_7d920.c"


class Plan(ctypes.Structure):
    _fields_ = [("ratio_gate_passed", ctypes.c_uint32),
                ("span_gate_passed", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-chain.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_gate_chain_7d920
    function.argtypes = [ctypes.c_float, ctypes.c_int32,
                         ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0.4, -1, 10, 3, ctypes.byref(plan))
    assert (plan.ratio_gate_passed, plan.route, plan.target) == (1, 1, 0x7DB70)
    plan = Plan()
    function(0.8, 25, 10, 3, ctypes.byref(plan))
    assert (plan.span_gate_passed, plan.route, plan.target) == (1, 1, 0x7DB70)
    plan = Plan()
    function(0.8, 24, 25, 3, ctypes.byref(plan))
    assert (plan.route, plan.target) == (3, 0x7DB54)
    plan = Plan()
    function(0.8, 24, 24, 3, ctypes.byref(plan))
    assert (plan.route, plan.target, plan.selector) == (2, 0x7DA8C, 3)

print("PASS: 0x7d920 connected gate-chain vectors")
