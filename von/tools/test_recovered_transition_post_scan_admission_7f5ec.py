#!/usr/bin/env python3
"""Check post-scan admission at i960 0x7f5ec."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_post_scan_admission_7f5ec.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_170", "related_172", "related_state", "published_status",
        "r6_compare_equal_zero", "halfword_gate_passed", "state_gate_passed",
        "status_index", "status_gate_passed", "floating_gate_passed",
        "admission_passed", "target", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-post-scan-admission.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_post_scan_admission_7f5ec
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    for values in ((3, 0, 3, 8, 1), (0, 1, 8, 9, 1),
                   (3, 0, 8, 0, 1)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert (plan.admission_passed, plan.target) == (1, 0x7f634)

    for values in ((0, 0, 3, 8, 1), (3, 0, 4, 8, 1),
                   (3, 0, 3, 7, 1), (3, 0, 3, 8, 0)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert plan.admission_passed == 0
        assert plan.target == plan.failure_target == 0x7f6b0

    plan = Plan()
    function(3, 0, 3, 0, 1, ctypes.byref(plan))
    assert plan.status_index == 0xfffffffe
    assert plan.status_gate_passed == 1

print("recovered 0x7f5ec post-scan admission vectors: ok")
