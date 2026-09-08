#!/usr/bin/env python3
"""Check the terminal count gate at i960 0x852ac."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_scan_terminal_gate_852ac.c"

class Plan(ctypes.Structure):
    _fields_ = [("r5", ctypes.c_uint32),
                ("r7", ctypes.c_uint32),
                ("exits_to_853a0", ctypes.c_uint32),
                ("continues_to_852b4", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib852ac.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_scan_terminal_gate_852ac
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    for r5, r7 in ((2, 2), (3, 1), (3, 2)):
        result = function(r5, r7)
        expected_exit = 0 if (r5, r7) == (3, 2) else 1
        assert (result.r5, result.r7, result.exits_to_853a0,
                result.continues_to_852b4) == (r5, r7, expected_exit, 1 - expected_exit)

print("recovered 0x852ac terminal-gate vectors: ok")
