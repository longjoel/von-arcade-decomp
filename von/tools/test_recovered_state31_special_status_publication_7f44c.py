#!/usr/bin/env python3
"""Check special status publication at i960 0x7f44c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_special_status_publication_7f44c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "incoming_status", "related_state", "accepted", "admission_arm",
        "selector_destination", "selector_value", "status_destination",
        "status_value", "control_destination", "control_value",
        "callback_target", "callback_argument", "action_destination",
        "action_value", "target", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-special-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_special_status_publication_7f44c
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for status, related, arm in ((0x92, 6, 1), (0x44, 0, 2),
                                 (0x56, 7, 3), (0x57, 7, 4)):
        plan = Plan()
        function(status, related, 0xcafe, ctypes.byref(plan))
        assert (plan.accepted, plan.admission_arm, plan.selector_value,
                plan.status_value, plan.control_value, plan.action_value,
                plan.target) == (1, arm, 3, 7, status, 30, 0x7f4c0)
        assert (plan.callback_target, plan.callback_argument) == (0x79d60, 0xcafe)

    for status, related in ((0x92, 5), (0x56, 6), (0x57, 6), (0x55, 7)):
        plan = Plan()
        function(status, related, 0xcafe, ctypes.byref(plan))
        assert (plan.accepted, plan.target, plan.failure_target) == (0, 0x7f4c4, 0x7f4c4)

print("recovered 0x7f44c special-publication vectors: ok")
