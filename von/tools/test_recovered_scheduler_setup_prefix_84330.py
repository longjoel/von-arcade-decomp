#!/usr/bin/env python3
"""Check the setup prefix at i960 0x84330."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_setup_prefix_84330.c"

class Plan(ctypes.Structure):
    _fields_ = [("stack_adjust", ctypes.c_uint32),
                ("clear_509a60", ctypes.c_uint32),
                ("clear_words", ctypes.c_uint32),
                ("low_two_bits", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84330.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_setup_prefix_84330
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    assert (function(0,).stack_adjust, function(0).clear_words) == (16, 3)
    assert function(1).clear_509a60 == 0
    assert function(0x1002).low_two_bits == 2

print("recovered 0x84330 setup-prefix vectors: ok")
