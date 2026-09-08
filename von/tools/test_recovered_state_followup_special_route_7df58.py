#!/usr/bin/env python3
"""Check the special follow-up route at i960 0x7df58."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_special_route_7df58.c"


class Plan(ctypes.Structure):
    _fields_ = [("enters_table_route", ctypes.c_uint32),
                ("continues_to_7dfb8", ctypes.c_uint32),
                ("result_table", ctypes.c_uint32),
                ("result_index", ctypes.c_uint32),
                ("result_value", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("action_destination", ctypes.c_uint32),
                ("action_value", ctypes.c_uint32),
                ("call_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-special.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_special_route_7df58
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x55, 0x44, 2, 0x1234, ctypes.byref(plan))
    assert (plan.enters_table_route, plan.continues_to_7dfb8) == (1, 0)
    assert (plan.result_table, plan.result_index, plan.result_value) == (0x72780, 2, 0x1234)
    assert (plan.selector_destination, plan.selector_value) == (0x504DA0, 0x44)
    assert (plan.control_destination, plan.control_value) == (0x504D9C, 1)
    assert (plan.action_destination, plan.action_value, plan.call_target) == (0x504DB8, 30, 0x79050)
    plan = Plan()
    function(0x55, 0x56, 2, 0, ctypes.byref(plan))
    assert plan.continues_to_7dfb8 == 1
    plan = Plan()
    function(0xA3, 0x56, 6, 0x22, ctypes.byref(plan))
    assert plan.enters_table_route == 1
    plan = Plan()
    function(0xA3, 0x56, 5, 0, ctypes.byref(plan))
    assert plan.continues_to_7dfb8 == 1

print("PASS: 0x7df58 special-route vectors")
