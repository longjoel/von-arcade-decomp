#!/usr/bin/env python3
"""Check selector-6/status-7 routing at i960 0x7fed4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_selector6_status7_route_7fed4.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_172", "global_counter", "callback_argument",
        "related_172_gate_passed", "counter_gate_passed", "admission_passed",
        "selector_destination", "selector_value", "control_destination",
        "control_value", "counter_destination", "counter_value",
        "status_destination", "status_value", "callback_target",
        "action_destination", "action_value", "target", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-selector6-status7.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_selector6_status7_route_7fed4
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for value in (27, 30):
        plan = Plan()
        function(value, 0x5dd, 0xcafe, ctypes.byref(plan))
        assert (plan.admission_passed, plan.selector_value,
                plan.control_value, plan.status_value,
                ctypes.c_int32(plan.counter_value).value,
                plan.callback_target, plan.callback_argument,
                plan.action_value) == (1, 6, 0x64, 7, -1, 0x79d60,
                                       0xcafe, 30)

    for values in ((26, 0x5dd), (27, 0x5dc), (30, 0x5dc)):
        plan = Plan()
        function(*values, 0, ctypes.byref(plan))
        assert (plan.admission_passed, plan.target,
                plan.failure_target) == (0, 0x7ff34, 0x7ff34)

print("recovered 0x7fed4 selector6/status7 vectors: ok")
