#!/usr/bin/env python3
"""Check the classifier-1 bypass route at i960 0x7f098."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_classifier1_bypass_7f098.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "related_state", "selector", "object_state_passed",
        "related_state_passed", "selector_passed", "gate_passed", "target",
        "published_status", "callback_target", "callback_argument",
        "action_destination", "action_value", "control_destination",
        "control_value", "selector_destination", "selector_value",
        "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-classifier1-bypass.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_classifier1_bypass_7f098
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    for selector in (0, 2, 5):
        plan = Plan()
        function(6, 3, selector, 0xcafe, ctypes.byref(plan))
        assert (plan.object_state_passed, plan.related_state_passed,
                plan.selector_passed, plan.gate_passed, plan.target,
                plan.published_status) == (1, 1, 1, 1, 0x7f0bc, 7)
        assert (plan.callback_target, plan.action_destination, plan.action_value,
                plan.control_destination, plan.control_value,
                plan.selector_destination, plan.selector_value) == (
            0x79d60, 0x504db8, 30, 0x504da0, 3, 0x504d9c, 0x64)
        assert plan.callback_argument == 0xcafe

    for object_state, related_state, selector in ((5, 3, 0), (6, 2, 0),
                                                    (6, 3, 1), (6, 3, 4)):
        plan = Plan()
        function(object_state, related_state, selector, 0xcafe, ctypes.byref(plan))
        assert plan.gate_passed == 0
        assert plan.target == plan.failure_target == 0x7f0f8
        assert plan.published_status == plan.callback_target == 0

print("recovered 0x7f098 classifier-1 bypass vectors: ok")
