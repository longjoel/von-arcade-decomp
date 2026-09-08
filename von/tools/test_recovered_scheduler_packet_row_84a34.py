#!/usr/bin/env python3
"""Check packet-row layout at i960 0x84a34."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_packet_row_84a34.c"

class Plan(ctypes.Structure):
    _fields_ = [("destination_offset", ctypes.c_uint32),
                ("source_0", ctypes.c_uint32),
                ("source_2", ctypes.c_uint32),
                ("source_4", ctypes.c_uint32),
                ("source_6", ctypes.c_uint32),
                ("source_a", ctypes.c_uint32),
                ("field_8c", ctypes.c_int32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84a34.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_packet_row_84a34
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32]
    function.restype = Plan
    result = function(0x5050a0, 2, 1, 2, 3, 4, 5, 5)
    assert (result.destination_offset, result.source_0, result.source_2,
            result.source_4, result.source_6, result.source_a,
            result.field_8c) == (0x5051c0, 1, 2, 3, 4, 5, 220)

print("recovered 0x84a34 packet-row vectors: ok")
