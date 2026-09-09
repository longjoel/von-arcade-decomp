#!/usr/bin/env python3
"""Check dual threshold routing at i960 0x7fd24."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_dual_threshold_route_7fd24.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "first_threshold_above_current",
        "second_threshold_above_current", "first_threshold_gate_passed",
        "second_threshold_gate_passed", "state0_or6_passed",
        "state6_second_arm", "publication_route", "target",
        "publication_target", "alternate_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-dual-threshold.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_dual_threshold_route_7fd24
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for values in ((0, 0, 1), (6, 1, 1), (5, 1, 0)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert (plan.publication_route, plan.target) == (1, 0x7fd58)

    for values in ((6, 1, 0), (5, 0, 1), (3, 0, 1)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert (plan.publication_route, plan.target) == (0, 0x7fed0)

print("recovered 0x7fd24 dual-threshold vectors: ok")
