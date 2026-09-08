#!/usr/bin/env python3
"""Check recovery packet-row layout at i960 0x84c98."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_row_84c98.c"

class Plan(ctypes.Structure):
    _fields_ = [("destination_offset", ctypes.c_uint32),
                ("field_0", ctypes.c_uint32), ("field_2", ctypes.c_uint32),
                ("field_4", ctypes.c_uint32), ("field_6", ctypes.c_uint32),
                ("field_8", ctypes.c_uint32), ("field_a", ctypes.c_uint32),
                ("field_84", ctypes.c_int32),
                ("source_start", ctypes.c_uint32),
                ("recovery_record_field_86", ctypes.c_uint32),
                ("field_c", ctypes.c_uint16 * 60)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84c98.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_recovery_row_84c98
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_int32, ctypes.c_int32,
                         ctypes.POINTER(ctypes.c_uint16)]
    function.restype = Plan
    source = (ctypes.c_uint16 * 60)(*range(60))
    result = function(0x5074a0, 2, 1, 2, 3, 4, 5, 6, 5, 59, source)
    assert (result.destination_offset, result.field_0, result.field_a,
            result.field_84, result.source_start,
            result.recovery_record_field_86) == (0x5075c0, 1, 6, 220, 0, 100)
    assert (result.field_c[0], result.field_c[59]) == (0, 59)
    result = function(0, 0, 0, 0, 0, 0, 0, 0, 0, 10, source)
    assert (result.source_start, result.field_c[0], result.field_c[49]) == (11, 11, 0)

print("recovered 0x84c98 recovery-row vectors: ok")
