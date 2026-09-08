#!/usr/bin/env python3
"""Check the action-25 publication tail at i960 0x7e230."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_action25_publication_7e230.c"


class Plan(ctypes.Structure):
    _fields_ = [("classifier_index", ctypes.c_uint32),
                ("result_table", ctypes.c_uint32),
                ("result_value", ctypes.c_uint32),
                ("derived_value", ctypes.c_uint32),
                ("derived_destination", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("action_destination", ctypes.c_uint32),
                ("action_value", ctypes.c_uint32),
                ("continuation_destination", ctypes.c_uint32),
                ("continuation_value", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-action25.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_action25_publication_7e230
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(7, 0x12345678, 0xCAFEBABE, ctypes.byref(plan))
    assert (plan.classifier_index, plan.result_table, plan.result_value,
            plan.derived_value, plan.derived_destination) == (7, 0x72660, 0x12345678, 6, 0x504DB4)
    assert (plan.control_destination, plan.control_value) == (0x504D9C, 1)
    assert (plan.action_destination, plan.action_value) == (0x504DB8, 25)
    assert (plan.continuation_destination, plan.continuation_value,
            plan.status_destination) == (0x504DA0, 0xCAFEBABE, 0x504D94)
    plan = Plan()
    function(0, 0, 0, ctypes.byref(plan))
    assert plan.derived_value == 0xFFFFFFFF

print("PASS: 0x7e230 action-25 publication vectors")
