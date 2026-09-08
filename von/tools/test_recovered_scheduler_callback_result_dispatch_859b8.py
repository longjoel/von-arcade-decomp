#!/usr/bin/env python3
"""Check callback result dispatch at i960 0x859b8."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_result_dispatch_859b8.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_509b8c_low_byte", ctypes.c_uint32),
                ("helper_result", ctypes.c_uint32),
                ("normalized_index", ctypes.c_uint32),
                ("exits_to_85af0", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib859b8.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_result_dispatch_859b8
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    targets = (0x859ec, 0x85a20, 0x85a54, 0x85a88, 0x85abc)
    for helper, target in enumerate(targets, 1):
        result = function(0x1202, helper)
        assert (result.value_509b8c_low_byte, result.normalized_index,
                result.exits_to_85af0, result.target) == (2, helper - 1, 0, target)
    assert function(0, 6).exits_to_85af0 == 1
    assert function(0, 0).exits_to_85af0 == 1

print("recovered 0x859b8 result-dispatch vectors: ok")
