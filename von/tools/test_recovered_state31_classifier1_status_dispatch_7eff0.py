#!/usr/bin/env python3
"""Check classifier-1 status dispatch at i960 0x7eff0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_classifier1_status_dispatch_7eff0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("classifier_result", "classifier_gate_passed", "original_status",
                 "normalized_index", "table_target", "published_status",
                 "common_callback_target", "callback_argument",
                 "common_tail_target", "bypass_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-classifier1-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_classifier1_status_dispatch_7eff0
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    expected = [(0x7f040, 1), (0x7f068, 4), (0x7f070, 5),
                (0x7f080, 6), (0x7f08c, 12), (0x7f08c, 13),
                (0x7f08c, 14), (0x7f08c, 15), (0x7f08c, 16),
                (0x7f08c, 17), (0x7f050, 2), (0x7f058, 3)]
    for index, (target, status) in enumerate(expected):
        plan = Plan()
        function(1, index + 8, 0xcafe, ctypes.byref(plan))
        assert (plan.classifier_gate_passed, plan.normalized_index,
                plan.table_target, plan.published_status) == (1, index, target, status)
        assert (plan.common_callback_target, plan.callback_argument,
                plan.common_tail_target, plan.bypass_target) == (
            0x79050, 0xcafe, 0x7f08c, 0)

    plan = Plan()
    function(2, 8, 0, ctypes.byref(plan))
    assert (plan.classifier_gate_passed, plan.bypass_target) == (0, 0x7f098)
    plan = Plan()
    function(1, 7, 0, ctypes.byref(plan))
    assert (plan.normalized_index, plan.table_target,
            plan.published_status) == (0xffffffff, 0x7f08c, 7)

print("recovered 0x7eff0 classifier-1 dispatch vectors: ok")
