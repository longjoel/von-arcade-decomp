#!/usr/bin/env python3
"""Check the counter/dispatch prefix at i960 0x844f4."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_counter_prefix_844f4.c"

class Plan(ctypes.Structure):
    _fields_ = [("slot", ctypes.c_uint32),
                ("jumped_to_847b0", ctypes.c_uint32),
                ("writes_509a68", ctypes.c_uint32),
                ("value_509a68", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib844f4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_counter_prefix_844f4
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert (function(0, 12).writes_509a68, function(0, 12).value_509a68) == (1, 13)
    assert function(0, 59).value_509a68 == 0
    assert function(0, 0xffffffff).value_509a68 == 0
    assert function(1, 12).jumped_to_847b0 == 1
    assert function(3, 12).writes_509a68 == 0

print("recovered 0x844f4 counter-prefix vectors: ok")
