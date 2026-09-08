#!/usr/bin/env python3
"""Check callback alignment at i960 0x8558c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_alignment_8558c.c"

class Plan(ctypes.Structure):
    _fields_ = [("incoming_value", ctypes.c_uint32),
                ("aligned_value", ctypes.c_uint32),
                ("alignment_delta", ctypes.c_int32),
                ("uses_fallback_8", ctypes.c_uint32),
                ("continues_with_decoded_dimensions", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib8558c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_alignment_8558c
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    result = function(5)
    assert (result.aligned_value, result.alignment_delta,
            result.uses_fallback_8, result.continues_with_decoded_dimensions) == (8, -3, 1, 0)
    result = function(ctypes.c_uint32(-5).value)
    assert (result.aligned_value, result.alignment_delta,
            result.uses_fallback_8, result.continues_with_decoded_dimensions) == (
        ctypes.c_uint32(-8).value, 3, 0, 1)
    assert function(4).uses_fallback_8 == 1
    assert function(0).uses_fallback_8 == 1

print("recovered 0x8558c alignment vectors: ok")
