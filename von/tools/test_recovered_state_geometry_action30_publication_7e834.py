#!/usr/bin/env python3
"""Check action-30 publication and the 0x509b34 threshold gate."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_action30_publication_7e834.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("classifier_index", "result_table", "result_value",
                 "status_destination", "action_destination", "action_value",
                 "global_509b34", "threshold", "enters_7e864",
                 "continues_to_7e9f4")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-action30.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_action30_publication_7e834
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(7, 0x12345678, 0x5dd, ctypes.byref(plan))
    assert (plan.classifier_index, plan.result_table, plan.result_value) == (
        7, 0x72660, 0x12345678)
    assert (plan.status_destination, plan.action_destination,
            plan.action_value) == (0x504d94, 0x504db8, 30)
    assert (plan.threshold, plan.enters_7e864, plan.continues_to_7e9f4) == (
        0x5dc, 1, 0)

    for value in (0x5dc, 0):
        plan = Plan()
        function(0, 0, value, ctypes.byref(plan))
        assert plan.enters_7e864 == 0
        assert plan.continues_to_7e9f4 == 1

print("recovered 0x7e834 action30-publication vectors: ok")
