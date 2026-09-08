#!/usr/bin/env python3
"""Check the secondary row predicate at i960 0x85204."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_row_secondary_match_85204.c"


class Plan(ctypes.Structure):
    _fields_ = [("row_field_4", ctypes.c_uint32),
                ("frame_g9_low", ctypes.c_uint32),
                ("matches", ctypes.c_uint32),
                ("incoming_r5", ctypes.c_uint32),
                ("outgoing_r5", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85204.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_row_secondary_match_85204
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0x10002, 0x20002, 3)
    assert (result.row_field_4, result.frame_g9_low, result.matches,
            result.incoming_r5, result.outgoing_r5) == (2, 2, 1, 3, 4)
    result = function(2, 3, 0)
    assert (result.matches, result.outgoing_r5) == (0, 0)

print("recovered 0x85204 secondary-match vectors: ok")
