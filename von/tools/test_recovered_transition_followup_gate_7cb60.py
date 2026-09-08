#!/usr/bin/env python3
"""Check the dispatch prefix at i960 0x7cb60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_followup_gate_7cb60.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("fallback_target", ctypes.c_uint32),
        ("followup_target", ctypes.c_uint32),
        ("state_handler_target", ctypes.c_uint32),
        ("selector", ctypes.c_uint32),
        ("stores_state_handler_result", ctypes.c_uint32),
        ("state_handler_result_destination", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-followup-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_followup_gate_7cb60
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    def run(timing_passed, selector, final_compare_passed):
        plan = Plan()
        function(timing_passed, selector, final_compare_passed,
                 ctypes.byref(plan))
        return plan

    for selector in (0, 7):
        plan = run(1, selector, 1)
        assert plan.route == 0
        assert plan.fallback_target == 0x783C8
        assert plan.stores_state_handler_result == 0

    assert run(0, 8, 1).route == 0
    assert run(1, 8, 1).route == 1
    plan = run(1, 0xFFFFFFFF, 0)
    assert plan.route == 2
    assert plan.state_handler_target == 0x82800
    assert plan.stores_state_handler_result == 1
    assert plan.state_handler_result_destination == 0x504D80

print("PASS: 0x7cb60 transition-followup gate vectors")
