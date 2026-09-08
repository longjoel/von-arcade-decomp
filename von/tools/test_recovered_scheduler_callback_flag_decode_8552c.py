#!/usr/bin/env python3
"""Check callback flag decoding at i960 0x8552c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_flag_decode_8552c.c"

class Plan(ctypes.Structure):
    _fields_ = [("flag_byte", ctypes.c_uint32),
                ("value_g1", ctypes.c_uint32),
                ("value_g2", ctypes.c_uint32),
                ("value_g3", ctypes.c_uint32),
                ("value_g13", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib8552c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_flag_decode_8552c
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    result = function(0x8200)
    assert (result.flag_byte, result.value_g1, result.value_g2,
            result.value_g3, result.value_g13) == (0x82, 1, 1, 16, 16)
    result = function(0x8000)
    assert (result.flag_byte, result.value_g1, result.value_g2,
            result.value_g3, result.value_g13) == (0x80, 1, 2, 16, 16)
    result = function(0xff00)
    assert (result.flag_byte, result.value_g1, result.value_g2,
            result.value_g3, result.value_g13) == (0xff, 2, 2, 16, 16)

print("recovered 0x8552c callback-flag vectors: ok")
