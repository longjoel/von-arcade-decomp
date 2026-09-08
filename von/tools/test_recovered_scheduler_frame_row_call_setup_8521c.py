#!/usr/bin/env python3
"""Check the shared row-handler call setup at i960 0x8521c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_row_call_setup_8521c.c"

class Plan(ctypes.Structure):
    _fields_ = [("object_field_74", ctypes.c_uint32),
                ("frame_pointer", ctypes.c_uint32),
                ("argument_g0", ctypes.c_uint32),
                ("argument_g1", ctypes.c_uint32),
                ("argument_g2", ctypes.c_uint32),
                ("call_target", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib8521c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_row_call_setup_8521c
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0x12345678, 0x1000)
    assert (result.object_field_74, result.frame_pointer, result.argument_g0,
            result.argument_g1, result.argument_g2, result.call_target) == (
                0x12345678, 0x1000, 0x12345678, 0x1040, 0x1044, 0x847c0)

print("recovered 0x8521c row-call-setup vectors: ok")
