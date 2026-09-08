#!/usr/bin/env python3
"""Check the control/ABI gate at i960 0x85080."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_control_gate_85080.c"


class Plan(ctypes.Structure):
    _fields_ = [("saved_g8", ctypes.c_uint32),
                ("saved_g12", ctypes.c_uint32),
                ("restored_g8", ctypes.c_uint32),
                ("restored_g12", ctypes.c_uint32),
                ("returns_immediately", ctypes.c_uint32),
                ("continues_to_850ac", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85080.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_control_gate_85080
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0x12345678, 0x89abcdef, 1)
    assert (result.saved_g8, result.saved_g12, result.restored_g8,
            result.restored_g12, result.returns_immediately,
            result.continues_to_850ac) == (0x12345678, 0x89abcdef,
                                            0x12345678, 0x89abcdef, 1, 0)
    result = function(0xdeadbeef, 0x10203040, 0)
    assert (result.saved_g8, result.saved_g12, result.restored_g8,
            result.restored_g12, result.returns_immediately,
            result.continues_to_850ac) == (0xdeadbeef, 0x10203040,
                                            0xdeadbeef, 0x10203040, 0, 1)

print("recovered 0x85080 control-gate vectors: ok")
