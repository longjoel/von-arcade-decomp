#!/usr/bin/env python3
"""Check the state-4 publication tail at i960 0x7f7d4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state4_publication_tail_7f7d4.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "classifier_result", "callback_gate", "related_pointer",
        "status_destination", "published_status", "callback_target",
        "callback_argument", "action_destination", "action_value", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state4-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state4_publication_tail_7f7d4
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(6, 1, 0xcafe, ctypes.byref(plan))
    assert (plan.status_destination, plan.published_status,
            plan.callback_target, plan.callback_argument,
            plan.action_destination, plan.action_value, plan.target) == (
        0x504d94, 6, 0x79050, 0xcafe, 0x504db8, 30, 0x7f7fc)

    plan = Plan()
    function(2, 0, 0xcafe, ctypes.byref(plan))
    assert (plan.published_status, plan.callback_target,
            plan.callback_argument, plan.action_value) == (2, 0, 0, 30)

print("recovered 0x7f7d4 publication-tail vectors: ok")
