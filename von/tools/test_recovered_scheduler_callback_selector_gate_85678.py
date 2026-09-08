#!/usr/bin/env python3
"""Check the callback selector gate at i960 0x85678."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_selector_gate_85678.c"

class Plan(ctypes.Structure):
    _fields_ = [("selector", ctypes.c_uint32),
                ("enters_selector1_path", ctypes.c_uint32),
                ("branches_to_85784", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85678.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_selector_gate_85678
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    assert (function(1).enters_selector1_path, function(1).branches_to_85784) == (1, 0)
    for selector in (0, 2, 7, 15, 0xffffffff):
        result = function(selector)
        assert (result.enters_selector1_path, result.branches_to_85784) == (0, 1)

print("recovered 0x85678 selector-gate vectors: ok")
