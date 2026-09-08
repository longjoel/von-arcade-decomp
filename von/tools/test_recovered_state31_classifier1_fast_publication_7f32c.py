#!/usr/bin/env python3
"""Check classifier-result-1 fast publication at i960 0x7f32c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_classifier1_fast_publication_7f32c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "classifier_result", "r6_compare_equal_zero", "classifier_gate_passed",
        "selector_written", "selector_destination", "selector_value",
        "control_written", "control_destination", "control_value", "target",
        "alternate_target", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-classifier1-fast.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_classifier1_fast_publication_7f32c
    function.argtypes = [ctypes.c_uint32] * 2 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(1, 1, ctypes.byref(plan))
    assert (plan.classifier_gate_passed, plan.selector_written,
            plan.selector_destination, plan.selector_value, plan.control_written,
            plan.control_destination, plan.control_value, plan.target) == (
        1, 1, 0x504d9c, 3, 1, 0x504da0, 0x64, 0x7f360)

    plan = Plan()
    function(1, 0, ctypes.byref(plan))
    assert (plan.selector_written, plan.selector_value, plan.control_written,
            plan.target) == (1, 3, 0, 0x7f364)

    plan = Plan()
    function(2, 1, ctypes.byref(plan))
    assert (plan.classifier_gate_passed, plan.selector_written,
            plan.control_written, plan.target) == (0, 0, 0, 0x7f44c)

print("recovered 0x7f32c classifier-1 fast-publication vectors: ok")
