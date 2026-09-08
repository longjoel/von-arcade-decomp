#!/usr/bin/env python3
"""Check distinct primary-table follow-up handler effects."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_primary_handlers_7daf0.c"


class Plan(ctypes.Structure):
    _fields_ = [("writes_selector", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32),
                ("writes_status", ctypes.c_uint32),
                ("status_value", ctypes.c_uint32),
                ("writes_continuation", ctypes.c_uint32),
                ("continuation_value", ctypes.c_uint32),
                ("decrements_counter", ctypes.c_uint32),
                ("counter_destination", ctypes.c_uint32),
                ("counter_after", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32),
                ("continuation_destination", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-primary-handlers.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_primary_handler_7daf0
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x7DAF0, 0, 0, 0, ctypes.byref(plan))
    assert (plan.selector_value, plan.writes_status) == (20, 0)
    assert plan.selector_destination == 0x504D98
    plan = Plan()
    function(0x7DB00, 0, 0, 0, ctypes.byref(plan))
    assert (plan.selector_value, plan.status_value) == (23, 28)
    assert (plan.selector_destination, plan.status_destination) == (0x504D98, 0x504D94)
    plan = Plan()
    function(0x7DB1C, 0, 0, 0, ctypes.byref(plan))
    assert (plan.selector_value, plan.status_value) == (21, 0)
    plan = Plan()
    function(0x7DB2C, 4, 9, 0x1234, ctypes.byref(plan))
    assert plan.writes_status and plan.status_value == 0x1234
    assert plan.status_destination == 0x504D94
    assert plan.decrements_counter == 1
    assert (plan.counter_destination, plan.counter_after) == (0x51C930, 8)
    plan = Plan()
    function(0x7DB54, 6, 0, 0x5678, ctypes.byref(plan))
    assert plan.writes_continuation == 0
    plan = Plan()
    function(0x7DB54, 5, 0, 0x5678, ctypes.byref(plan))
    assert plan.writes_continuation and plan.continuation_value == 0x5678
    assert (plan.status_destination, plan.continuation_destination) == (0x504D94, 0x51C930)

print("PASS: primary follow-up handler vectors")
