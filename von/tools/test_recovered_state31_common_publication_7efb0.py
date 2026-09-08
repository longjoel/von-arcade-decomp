#!/usr/bin/env python3
"""Check the common state-31 publication tail at i960 0x7efb0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_common_publication_7efb0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("classifier_band", "result_table", "result_value",
                 "status_destination", "callback_target", "callback_argument",
                 "action_destination", "action_value", "control_destination",
                 "control_value", "selector_destination", "selector_value",
                 "returns")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-common-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_common_publication_7efb0
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(6, 0x12345678, 0xcafe, ctypes.byref(plan))
    assert (plan.classifier_band, plan.result_table, plan.result_value,
            plan.status_destination) == (6, 0x72780, 0x12345678, 0x504d94)
    assert (plan.callback_target, plan.callback_argument,
            plan.action_destination, plan.action_value) == (
        0x79050, 0xcafe, 0x504db8, 30)
    assert (plan.control_destination, plan.control_value,
            plan.selector_destination, plan.selector_value, plan.returns) == (
        0x504d9c, 3, 0x504da0, 0x64, 1)

print("recovered 0x7efb0 common-publication vectors: ok")
