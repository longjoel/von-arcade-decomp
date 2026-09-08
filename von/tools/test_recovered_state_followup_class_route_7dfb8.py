#!/usr/bin/env python3
"""Check the classified follow-up state route at i960 0x7dfb8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_class_route_7dfb8.c"


class Plan(ctypes.Structure):
    _fields_ = [("enters_class_route", ctypes.c_uint32),
                ("continues_to_7e064", ctypes.c_uint32),
                ("state_offset", ctypes.c_uint32),
                ("global_le_4", ctypes.c_uint32),
                ("classifier_input", ctypes.c_uint32),
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
    library = pathlib.Path(directory) / "libstate-followup-class.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_class_route_7dfb8
    function.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0xA3, 0x55, 3, 4, 0x111, 2, 0x222, ctypes.byref(plan))
    assert (plan.enters_class_route, plan.continues_to_7e064,
            plan.state_offset, plan.global_le_4) == (1, 0, 0x2000, 1)
    assert (plan.result_table, plan.result_index, plan.result_value) == (0x72780, 2, 0x222)
    assert (plan.selector_destination, plan.selector_value) == (0x504DA0, 0x55)
    assert (plan.control_destination, plan.control_value) == (0x504D9C, 1)
    assert (plan.action_destination, plan.action_value, plan.call_target) == (0x504DB8, 30, 0x79050)
    plan = Plan()
    function(0xA3, 0x55, 6, 5, 0x333, 1, 0x444, ctypes.byref(plan))
    assert (plan.state_offset, plan.global_le_4) == (0xFFFFF800, 0)
    plan = Plan()
    function(0x55, 0x55, 3, 4, 0, 0, 0, ctypes.byref(plan))
    assert plan.continues_to_7e064 == 1

print("PASS: 0x7dfb8 classified-route vectors")
