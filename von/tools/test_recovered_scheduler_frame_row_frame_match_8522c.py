#!/usr/bin/env python3
"""Check the post-handler frame match at i960 0x8522c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_row_frame_match_8522c.c"

class Plan(ctypes.Structure):
    _fields_ = [("row_field_6_low_byte", ctypes.c_uint32),
                ("saved_frame_value", ctypes.c_uint32),
                ("matches", ctypes.c_uint32),
                ("incoming_r7", ctypes.c_uint32),
                ("outgoing_r7", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib8522c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_row_frame_match_8522c
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0x1202, 2, 4)
    assert (result.row_field_6_low_byte, result.saved_frame_value,
            result.matches, result.incoming_r7, result.outgoing_r7) == (2, 2, 1, 4, 5)
    result = function(0x102, 0x102, 0)
    assert (result.row_field_6_low_byte, result.matches, result.outgoing_r7) == (2, 0, 0)

print("recovered 0x8522c frame-match vectors: ok")
