#!/usr/bin/env python3
"""Check selector-6 publication at i960 0x7fd58."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_selector6_publication_7fd58.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "global_counter", "selector_destination", "selector_value",
        "control_destination", "control_value", "counter_destination",
        "counter_value", "counter_limit_passed", "target", "deeper_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-selector6-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_selector6_publication_7fd58
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for counter, target in ((0, 0x7fdd4), (0x9c4, 0x7fdd4),
                            (0x9c5, 0x7fd90)):
        plan = Plan()
        function(counter, ctypes.byref(plan))
        assert (plan.selector_value, plan.control_value,
                plan.counter_destination, ctypes.c_int32(plan.counter_value).value,
                plan.target) == (6, 0x64, 0x504db4, -1, target)

print("recovered 0x7fd58 selector-6 vectors: ok")
