#!/usr/bin/env python3
"""Check simple follow-up handlers at i960 0x7dba8-0x7dbf4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_simple_handlers_7dba8.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("writes_selector", ctypes.c_uint32),
        ("selector_value", ctypes.c_uint32),
        ("writes_status", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("recognized", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-simple.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_simple_handler_7dba8
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for target in (0x7DBA8, 0x7DBB8):
        plan = Plan()
        function(target, ctypes.byref(plan))
        assert (plan.selector_value, plan.writes_status) == (19, 0)
    for target, selector in ((0x7DBC8, 20), (0x7DBF4, 21)):
        plan = Plan()
        function(target, ctypes.byref(plan))
        assert plan.selector_value == selector and plan.writes_status == 0
    plan = Plan()
    function(0x7DBD8, ctypes.byref(plan))
    assert (plan.selector_value, plan.status_value) == (23, 28)
    plan = Plan()
    function(0x7DC04, ctypes.byref(plan))
    assert plan.recognized == 0

print("PASS: simple 0x7dba8 follow-up handler vectors")
