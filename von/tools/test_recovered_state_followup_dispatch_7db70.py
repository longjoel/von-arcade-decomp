#!/usr/bin/env python3
"""Check the bounded follow-up dispatcher at i960 0x7db70."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_dispatch_7db70.c"


class Plan(ctypes.Structure):
    _fields_ = [("dispatch_allowed", ctypes.c_uint32),
                ("table_index", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_dispatch_7db70
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    expected = [0x7DBA8, 0x7DBB8, 0x7DBA8, 0x7DBB8,
                0x7DBC8, 0x7DBD8, 0x7DBF4, 0x7DC04,
                0x7DC98, 0x7DCA8]
    for selector, target in enumerate(expected):
        plan = Plan()
        function(selector, ctypes.byref(plan))
        assert (plan.dispatch_allowed, plan.table_index, plan.target) == (1, selector, target)
    for selector in (10, 0xffffffff):
        plan = Plan()
        function(selector, ctypes.byref(plan))
        assert plan.dispatch_allowed == 0
        assert plan.target == 0x7DCA8

print("PASS: 0x7db70 follow-up dispatcher vectors")
