#!/usr/bin/env python3
"""Check the flag finalizer at i960 0x84470."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_flag_finalize_84470.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_509a60", ctypes.c_uint32),
                ("set_bit6", ctypes.c_uint32),
                ("set_bit7", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84470.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_flag_finalize_84470
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    assert function((1 << 5) | (1 << 1)).value_509a60 & (1 << 7)
    assert function((1 << 4) | (1 << 0)).set_bit6 == 1
    assert function((1 << 4) | (1 << 1)).set_bit6 == 1
    assert function((1 << 5) | (1 << 0)).set_bit6 == 1
    assert function((1 << 5)).value_509a60 == (1 << 5)
    assert function((1 << 4)).value_509a60 == (1 << 4)

print("recovered 0x84470 flag-finalizer vectors: ok")
