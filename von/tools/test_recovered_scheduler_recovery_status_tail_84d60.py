#!/usr/bin/env python3
"""Check the recovery status tail at i960 0x84d60."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_status_tail_84d60.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_509ac0", ctypes.c_uint32),
                ("value_509b10", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84d60.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_recovery_status_tail_84d60
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert (function(1, 0).value_509ac0, function(1, 0).value_509b10) == (1, 0)
    assert function(0, 1 << 3).value_509b10 == 1
    assert function(0, 0xff).value_509b10 == 1
    assert function(0, 1 << 2).value_509b10 == 0

print("recovered 0x84d60 recovery-status-tail vectors: ok")
