#!/usr/bin/env python3
"""Check the recovery-record search at i960 0x84bb4."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_search_84bb4.c"

class Plan(ctypes.Structure):
    _fields_ = [("selected_index", ctypes.c_uint32),
                ("selected_value", ctypes.c_uint32),
                ("selected_valid", ctypes.c_uint32),
                ("compared_records", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84bb4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_recovery_search_84bb4
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    function.restype = Plan
    records = (ctypes.c_uint32 * 8)(10, 20, 30, 40, 50, 60, 70, 80)
    assert (function(25, records).selected_index,
            function(25, records).selected_value) == (0, 10)
    assert function(5, records).selected_valid == 0
    assert (function(99, records).selected_index,
            function(99, records).selected_value) == (0, 10)

print("recovered 0x84bb4 recovery-search vectors: ok")
