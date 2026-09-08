#!/usr/bin/env python3
"""Check the state/timing gate at i960 0x7f168."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_timing_publication_gate_7f168.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "related_state", "timing_below_40690000",
        "timing_gate_used", "direct_related_gate_passed",
        "related_object_gate_passed", "final_state_gate_passed",
        "publication_gate_passed", "target", "published_status",
        "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-timing-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_timing_publication_gate_7f168
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for object_state, related_state, timing in ((1, 2, 0), (3, 7, 0),
                                                 (0, 4, 0), (1, 7, 1)):
        plan = Plan()
        function(object_state, related_state, timing, ctypes.byref(plan))
        assert (plan.publication_gate_passed, plan.target,
                plan.published_status) == (1, 0x7f4ac, 7)

    for timing in (0, 1):
        plan = Plan()
        function(0, 2, timing, ctypes.byref(plan))
        assert plan.publication_gate_passed == timing
        assert plan.target == (0x7f4ac if timing else 0x7f1f8)

    plan = Plan()
    function(5, 6, 1, ctypes.byref(plan))
    assert (plan.timing_gate_used, plan.final_state_gate_passed,
            plan.publication_gate_passed, plan.target) == (0, 0, 0, 0x7f1f8)

    plan = Plan()
    function(1, 4, 1, ctypes.byref(plan))
    assert (plan.timing_gate_used, plan.publication_gate_passed,
            plan.target) == (0, 0, 0x7f1f8)

    plan = Plan()
    function(0, 7, 1, ctypes.byref(plan))
    assert (plan.timing_gate_used, plan.publication_gate_passed,
            plan.target) == (0, 0, 0x7f1f8)

print("recovered 0x7f168 timing publication vectors: ok")
