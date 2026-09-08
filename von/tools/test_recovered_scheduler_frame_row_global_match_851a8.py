#!/usr/bin/env python3
"""Check the first row predicate at i960 0x851a8."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_row_global_match_851a8.c"


class Plan(ctypes.Structure):
    _fields_ = [("row_field_0", ctypes.c_uint32),
                ("global_504d68", ctypes.c_uint32),
                ("matches", ctypes.c_uint32),
                ("r7_after_compare", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib851a8.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_row_global_match_851a8
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(2, 2)
    assert (result.row_field_0, result.global_504d68,
            result.matches, result.r7_after_compare) == (2, 2, 1, 1)
    result = function(0x10003, 2)
    assert (result.row_field_0, result.matches, result.r7_after_compare) == (3, 0, 0)

print("recovered 0x851a8 row-global-match vectors: ok")
