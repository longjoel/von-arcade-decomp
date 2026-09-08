#!/usr/bin/env python3
"""Check the low-byte gate at i960 0x850ac."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_ratio_gate_850ac.c"


class Plan(ctypes.Structure):
    _fields_ = [("low_byte", ctypes.c_uint32),
                ("exits_to_85128", ctypes.c_uint32),
                ("continues_to_ratio_setup", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib850ac.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_ratio_gate_850ac
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    for value, low_byte, exits in ((0x00000000, 0, 0),
                                   (0x1234010a, 10, 0),
                                   (0xabcdef0b, 11, 1),
                                   (0xfffffffe, 254, 1)):
        result = function(value)
        assert (result.low_byte, result.exits_to_85128,
                result.continues_to_ratio_setup) == (low_byte, exits, 1 - exits)

print("recovered 0x850ac ratio-gate vectors: ok")
