#!/usr/bin/env python3
"""Check the initial state-31 admission gates at i960 0x7f0f8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_zero_frame_admission_7f0f8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "frame_is_zero", "related_state", "object_state", "selector",
        "frame_gate_passed", "related_object_exclusion_passed",
        "selector_set_passed", "primary_gate_passed",
        "secondary_selector_passed", "target", "failure_target",
        "secondary_failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-zero-frame.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_zero_frame_admission_7f0f8
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    for selector in (3, 6):
        plan = Plan()
        function(1, 2, 0, selector, ctypes.byref(plan))
        assert (plan.primary_gate_passed, plan.secondary_selector_passed,
                plan.target) == (1, 1, 0x7f168)

    for selector in (1, 4, 7):
        plan = Plan()
        function(1, 2, 0, selector, ctypes.byref(plan))
        assert (plan.selector_set_passed, plan.primary_gate_passed,
                plan.secondary_selector_passed, plan.target) == (1, 1, 0, 0x7f1f8)

    for values in ((0, 2, 0, 3), (1, 7, 5, 3), (1, 2, 0, 8)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert plan.primary_gate_passed == 0
        assert plan.target == plan.failure_target == 0x7f32c

print("recovered 0x7f0f8 zero-frame admission vectors: ok")
