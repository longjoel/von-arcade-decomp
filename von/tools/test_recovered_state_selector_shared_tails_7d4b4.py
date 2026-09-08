#!/usr/bin/env python3
"""Check shared selector tails at i960 0x7d4b4/0x7d5f4/0x7d644/0x7d654."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_shared_tails_7d4b4.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("writes_selector", ctypes.c_uint32),
        ("selector_value", ctypes.c_uint32),
        ("writes_continuation", ctypes.c_uint32),
        ("continuation_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-tails.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_shared_tail_7d4b4
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    for target, selector in ((0x7D4B4, 3), (0x7D5F4, 2), (0x7D644, 1)):
        plan = Plan()
        function(target, 0x12345678, ctypes.byref(plan))
        assert plan.writes_selector == 1 and plan.selector_value == selector
        assert plan.writes_continuation == 0

    plan = Plan()
    function(0x7D654, 0x12345678, ctypes.byref(plan))
    assert plan.writes_selector == 0
    assert plan.writes_continuation == 1
    assert plan.continuation_value == 0x12345678
    plan = Plan()
    function(0x1234, 9, ctypes.byref(plan))
    assert plan.writes_selector == 0 and plan.writes_continuation == 0

print("PASS: shared 0x7d4b4/0x7d5f4/0x7d644/0x7d654 tail vectors")
