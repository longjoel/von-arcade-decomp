#!/usr/bin/env python3
"""Check the result publication handoff at i960 0x7fabc."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_result_publication_handoff_7fabc.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "result_value", "status_destination", "published_status", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-result-handoff.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_result_publication_handoff_7fabc
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for value in (0, 1, 6, 0xffffffff):
        plan = Plan()
        function(value, ctypes.byref(plan))
        assert (plan.status_destination, plan.published_status,
                plan.target) == (0x504d94, value, 0x7fc84)

print("recovered 0x7fabc result-handoff vectors: ok")
