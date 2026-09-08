#!/usr/bin/env python3
"""Check the published-frame decoder at i960 0x853c0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_decode_853c0.c"

class Plan(ctypes.Structure):
    _fields_ = [("bit8_mode", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("table_index", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32),
                ("table_value", ctypes.c_uint32),
                ("packed_value", ctypes.c_uint32),
                ("destination_address", ctypes.c_uint32),
                ("value_504e42", ctypes.c_uint32),
                ("value_504e44", ctypes.c_uint32),
                ("return_trampoline", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib853c0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_decode_853c0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0x300 | 5, 20, 0x600000, 2, 0xAB, 0xCD)
    assert (result.bit8_mode, result.selector, result.table_index,
            result.table_address, result.table_value, result.packed_value,
            result.destination_address, result.value_504e42,
            result.value_504e44, result.return_trampoline) == (
                1, 5, 5, 0x5050a0 + 2 * 1152 + 5 * 25 + 20 + 10,
                0xAB, 0xA0B, 0x60001c, 0x305, 21, 0x85494)
    result = function(5, 239, 0x700000, 0, 0xAB, 0xCD)
    assert (result.bit8_mode, result.table_address, result.table_value,
            result.value_504e42, result.value_504e44) == (0, 0x5074a0 + 5 * 17 + 12 + (239 >> 2) * 2,
                                                            0xCD, 0, 240)

print("recovered 0x853c0 decoder vectors: ok")
