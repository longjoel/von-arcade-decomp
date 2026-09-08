#!/usr/bin/env python3
"""Check bulk packet-row copying at i960 0x84a80."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_packet_row_copy_84a80.c"

class Plan(ctypes.Structure):
    _fields_ = [("field_0", ctypes.c_uint32),
                ("field_2", ctypes.c_uint32),
                ("field_4", ctypes.c_uint32),
                ("field_6", ctypes.c_uint32),
                ("field_a", ctypes.c_uint32),
                ("field_8e", ctypes.c_uint32),
                ("copied_count", ctypes.c_uint32),
                ("field_c", ctypes.c_uint16 * 60)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84a80.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_packet_row_copy_84a80
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_uint16)]
    function.restype = Plan
    source = (ctypes.c_uint16 * 60)(*range(60))
    result = function(1, 2, 3, 4, 5, source)
    assert (result.field_0, result.field_2, result.field_4,
            result.field_6, result.field_a, result.field_8e,
            result.copied_count) == (1, 2, 3, 4, 5, 100, 60)
    assert (result.field_c[0], result.field_c[59]) == (0, 59)

print("recovered 0x84a80 packet-row-copy vectors: ok")
