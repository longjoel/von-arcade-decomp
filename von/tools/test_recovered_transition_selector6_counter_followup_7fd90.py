#!/usr/bin/env python3
"""Check selector-6 counter follow-up at i960 0x7fd90."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_selector6_counter_followup_7fd90.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "control_504e48", "related_state", "object_state",
        "control_zero_gate_passed", "related_state7_gate_passed",
        "object_state8_gate_passed", "status_destination", "published_status",
        "state_destination", "published_state", "target",
        "return_to_selector6_target", "publication_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-selector6-followup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_selector6_counter_followup_7fd90
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for control, related in ((0, 4), (1, 7)):
        plan = Plan()
        function(control, related, 8, ctypes.byref(plan))
        assert (plan.target, plan.published_status) == (0x7fdd4, 0)

    plan = Plan()
    function(1, 4, 8, ctypes.byref(plan))
    assert (plan.target, plan.published_status, plan.published_state,
            plan.state_destination) == (0x7ff28, 1, 1, 0x504d98)

    plan = Plan()
    function(1, 4, 3, ctypes.byref(plan))
    assert (plan.target, plan.published_status, plan.state_destination) == (
        0x7ff28, 22, 0)

print("recovered 0x7fd90 counter-followup vectors: ok")
