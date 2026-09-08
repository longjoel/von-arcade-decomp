#!/usr/bin/env python3
"""Check state-31 selector and publication routing at i960 0x7ed34."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_selector_publication_7ed34.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("status_gate_passed", "state_mode_gate_passed",
                 "selector_gate_passed", "enters_route", "state2_publication",
                 "continuation_target", "status_destination", "status_value",
                 "selector_destination", "selector_value", "control_destination",
                 "control_value", "action_destination", "action_value",
                 "continuation_destination", "continuation_value")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-selector-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_selector_publication_7ed34
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(9, 2, 1 << 1, 0, 0xcafe, ctypes.byref(plan))
    assert (plan.status_gate_passed, plan.state_mode_gate_passed,
            plan.selector_gate_passed, plan.enters_route,
            plan.state2_publication) == (1, 1, 1, 1, 1)
    assert plan.continuation_target == 0
    assert (plan.status_destination, plan.status_value,
            plan.selector_destination, plan.selector_value,
            plan.control_destination, plan.control_value) == (
        0x504d94, 0xcafe, 0x504d98, 2, 0x504d9c, 3)
    assert (plan.action_destination, plan.action_value,
            plan.continuation_destination, plan.continuation_value) == (
        0x504db8, 25, 0x504da0, 0x64)

    plan = Plan()
    function(0, 3, 1 << 2, 0, 0, ctypes.byref(plan))
    assert (plan.enters_route, plan.state2_publication,
            plan.continuation_target) == (1, 0, 0x7edc4)

    for args in ((1, 2, 1 << 1, 0, 0), (0, 3, 1 << 1, 0, 0),
                 (0, 2, 1 << 1, 1, 0), (0, 4, 1 << 2, 0, 0)):
        plan = Plan()
        function(*args, ctypes.byref(plan))
        assert plan.enters_route == 0
        assert plan.continuation_target == 0x7ee28

print("recovered 0x7ed34 selector-publication vectors: ok")
