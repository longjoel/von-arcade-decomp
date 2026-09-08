#!/usr/bin/env python3
"""Check the frame-scan retry loop at i960 0x853a0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_scan_loop_853a0.c"

class Plan(ctypes.Structure):
    _fields_ = [("incoming_index", ctypes.c_uint32),
                ("next_index", ctypes.c_uint32),
                ("next_table_offset", ctypes.c_uint32),
                ("next_row_offset", ctypes.c_uint32),
                ("continues_scan", ctypes.c_uint32),
                ("restores_saved_registers", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib853a0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_scan_loop_853a0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(6, 0x120, 0x340)
    assert (result.next_index, result.next_table_offset,
            result.next_row_offset, result.continues_scan,
            result.restores_saved_registers) == (7, 0x1a8, 0x3c8, 1, 0)
    result = function(7, 0, 0)
    assert (result.next_index, result.continues_scan,
            result.restores_saved_registers) == (8, 0, 1)

print("recovered 0x853a0 scan-loop vectors: ok")
