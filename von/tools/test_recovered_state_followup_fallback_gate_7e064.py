#!/usr/bin/env python3
"""Check the fallback admission gate at i960 0x7e064."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_fallback_gate_7e064.c"


class Plan(ctypes.Structure):
    _fields_ = [("remainder_480", ctypes.c_uint32),
                ("enters_81610_route", ctypes.c_uint32),
                ("continues_to_7e0d0", ctypes.c_uint32),
                ("writes_continuation", ctypes.c_uint32),
                ("continuation_destination", ctypes.c_uint32),
                ("continuation_value", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("writes_selector", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32),
                ("call_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-fallback.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_fallback_gate_7e064
    function.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(719, 2, 501, 1, 5, 0xA3, 1, 0x1234, ctypes.byref(plan))
    assert (plan.remainder_480, plan.enters_81610_route,
            plan.continues_to_7e0d0) == (239, 1, 0)
    assert (plan.writes_continuation, plan.continuation_destination,
            plan.continuation_value,
            plan.control_destination, plan.control_value,
            plan.call_target) == (1, 0x504DA0, 0x1234, 0x504D9C, 1, 0x81610)
    assert (plan.writes_selector, plan.selector_destination,
            plan.selector_value) == (1, 0x504D98, 1)
    for args in ((720, 2, 501, 1, 5, 0xA3, 1, 0),
                 (719, 3, 501, 1, 5, 0xA3, 1, 0),
                 (719, 2, 500, 1, 5, 0xA3, 1, 0),
                 (719, 2, 501, 0, 5, 0xA3, 1, 0),
                 (719, 2, 501, 1, 4, 0xA3, 1, 0),
                 (719, 2, 501, 1, 5, 0x55, 1, 0)):
        plan = Plan()
        function(*args, ctypes.byref(plan))
        assert plan.enters_81610_route == 0
    plan = Plan()
    function(719, 2, 501, 1, 5, 0xA3, 0, 0, ctypes.byref(plan))
    assert plan.enters_81610_route == 1 and plan.writes_selector == 0

print("PASS: 0x7e064 fallback-gate vectors")
