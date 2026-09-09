#!/usr/bin/env python3
"""Check follow-up admission at i960 0x7f6b0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_followup_admission_7f6b0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_state", "related_170", "related_172", "published_status",
        "global_status", "r6_compare_equal_zero", "state4_excluded",
        "state4_halfword_checked", "halfword_gate_passed",
        "floating_gate_passed", "status_index", "status_gate_passed",
        "global_index", "global_gate_passed", "admission_passed", "target",
        "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-followup-admission.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_followup_admission_7f6b0
    function.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(3, 3, 0, 8, 8, 1, ctypes.byref(plan))
    assert (plan.admission_passed, plan.target, plan.failure_target) == (
        1, 0x7f708, 0x7f808)

    for values in ((4, 3, 1, 8, 8, 1), (3, 2, 0, 8, 8, 1),
                   (3, 3, 0, 8, 8, 0), (3, 3, 0, 7, 8, 1),
                   (3, 3, 0, 8, 7, 1)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert plan.admission_passed == 0
        assert plan.target == plan.failure_target == 0x7f808

print("recovered 0x7f6b0 follow-up-admission vectors: ok")
