#!/usr/bin/env python3
"""Check the alternate span gate at i960 0x7da54."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_span_gate_7da54.c"


class Plan(ctypes.Structure):
    _fields_ = [("caller_r17", ctypes.c_int32),
                ("divisor", ctypes.c_int32),
                ("frame_quotient", ctypes.c_int32),
                ("frame_target", ctypes.c_int32),
                ("target_difference", ctypes.c_int32),
                ("continues_to_dispatch", ctypes.c_uint32),
                ("falls_to_7db54", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-span.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_span_gate_7da54
    function.argtypes = [ctypes.c_int32] * 3 + [ctypes.c_uint32]
    function.restype = Plan

    result = function(480, 40, -21, 24)
    assert (result.caller_r17, result.divisor) == (-21, 10)
    assert (result.frame_quotient, result.frame_target,
            result.target_difference, result.continues_to_dispatch) == (48, 49, -9, 0)
    assert result.falls_to_7db54 == 0
    result = function(480, 75, -21, 24)
    assert result.target_difference == 26
    assert result.continues_to_dispatch == 1
    result = function(0, 0, -30, 25)
    assert result.falls_to_7db54 == 1

print("PASS: 0x7da54 span-gate vectors")
