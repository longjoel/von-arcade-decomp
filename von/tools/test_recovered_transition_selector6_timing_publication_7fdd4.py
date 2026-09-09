#!/usr/bin/env python3
"""Check selector-6 timing publication at i960 0x7fdd4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_selector6_timing_publication_7fdd4.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "related_state", "related_17a_shifted",
        "object_state_gate_passed", "related_state_gate_passed",
        "timing_gate_passed", "publication_gate_passed", "state_destination",
        "state_value", "action_destination", "action_value", "target",
        "alternate_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-selector6-timing.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_selector6_timing_publication_7fdd4
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for object_state, related_state in ((0, 0), (0, 6), (6, 0), (6, 6)):
        plan = Plan()
        function(object_state, related_state, 0x90000, ctypes.byref(plan))
        assert (plan.publication_gate_passed, plan.state_value,
                plan.action_value, plan.target) == (1, 6, 20, 0x7fe20)

    plan = Plan()
    function(0, 0, 0x90001, ctypes.byref(plan))
    assert (plan.timing_gate_passed, plan.publication_gate_passed) == (0, 0)
    for values in ((1, 0, 0x100), (0, 2, 0x100), (6, 5, 0x100)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert plan.publication_gate_passed == 0
        assert plan.target == plan.alternate_target == 0x7fe24

print("recovered 0x7fdd4 selector-6 publication vectors: ok")
