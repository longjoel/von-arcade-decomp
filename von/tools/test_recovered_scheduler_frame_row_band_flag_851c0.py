#!/usr/bin/env python3
"""Check the row-band predicate at i960 0x851c0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_row_band_flag_851c0.c"


class Plan(ctypes.Structure):
    _fields_ = [("row_field_6", ctypes.c_uint32),
                ("frame_upper", ctypes.c_uint32),
                ("lower_bound", ctypes.c_uint32),
                ("upper_bound", ctypes.c_uint32),
                ("low_upper_special_case", ctypes.c_uint32),
                ("sets_r5", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib851c0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_row_band_flag_851c0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(100, 100)
    assert (result.row_field_6, result.lower_bound, result.upper_bound,
            result.low_upper_special_case, result.sets_r5) == (100, 30, 170, 0, 1)
    assert function(29, 100).sets_r5 == 0
    assert function(171, 100).sets_r5 == 0
    # For upper <= 69, the lower-bound comparison is bypassed.
    assert function(0, 69).sets_r5 == 1
    assert function(140, 69).sets_r5 == 0
    # The low-halfword mask is applied before all comparisons.
    assert function(0x10064, 100).sets_r5 == 1

print("recovered 0x851c0 row-band-flag vectors: ok")
