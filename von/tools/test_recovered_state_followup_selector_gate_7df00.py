#!/usr/bin/env python3
"""Check the selector gate before i960 0x7df58."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_selector_gate_7df00.c"


class Plan(ctypes.Structure):
    _fields_ = [("enters_status7_route", ctypes.c_uint32),
                ("continues_to_7df58", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32),
                ("status_value", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32),
                ("call_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_selector_gate_7df00
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x44, 6, ctypes.byref(plan))
    assert (plan.enters_status7_route, plan.continues_to_7df58) == (0, 1)
    assert plan.call_target == 0
    plan = Plan()
    function(0x55, 0, ctypes.byref(plan))
    assert (plan.enters_status7_route, plan.continues_to_7df58) == (1, 0)
    assert (plan.status_destination, plan.status_value) == (0x504D94, 7)
    assert (plan.control_destination, plan.control_value) == (0x504D9C, 1)
    assert (plan.selector_destination, plan.selector_value,
            plan.call_target) == (0x504DA0, 0x55, 0x79D60)

print("PASS: 0x7df00 selector-gate vectors")
