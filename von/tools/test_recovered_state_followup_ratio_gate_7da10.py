#!/usr/bin/env python3
"""Check the zero-extended ratio gate at i960 0x7da10."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_ratio_gate_7da10.c"


class Plan(ctypes.Structure):
    _fields_ = [("object_1d0_zero_extended", ctypes.c_uint32),
                ("object_1d8_zero_extended", ctypes.c_uint32),
                ("ratio", ctypes.c_float),
                ("threshold", ctypes.c_float),
                ("continues_to_dispatch", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-ratio.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_ratio_gate_7da10
    function.argtypes = [ctypes.c_uint16, ctypes.c_uint16]
    function.restype = Plan

    result = function(1, 4)
    assert (result.object_1d0_zero_extended,
            result.object_1d8_zero_extended) == (1, 4)
    assert abs(result.ratio - 0.25) < 1e-6
    assert result.continues_to_dispatch == 1
    assert function(2, 4).continues_to_dispatch == 0
    # ldos followed by shlo/shri preserves the low half as unsigned.
    result = function(0xffff, 0xffff)
    assert (result.object_1d0_zero_extended,
            result.object_1d8_zero_extended) == (0xffff, 0xffff)
    assert result.continues_to_dispatch == 0

print("PASS: 0x7da10 ratio-gate vectors")
