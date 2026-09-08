#!/usr/bin/env python3
"""Check frame-scan publication/dispatch at i960 0x852b4."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_scan_publication_852b4.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_504e42", ctypes.c_uint32),
                ("value_504e44", ctypes.c_uint32),
                ("frame_selector", ctypes.c_uint32),
                ("selected_status", ctypes.c_uint32),
                ("value_504d9c", ctypes.c_uint32),
                ("restores_saved_registers", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib852b4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_scan_publication_852b4
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(0x400, 0x10023, 2, 99)
    assert (result.value_504e42, result.value_504e44,
            result.selected_status, result.value_504d9c,
            result.restores_saved_registers) == (0x400, 0x23, 4, 4, 1)
    for selector, status in enumerate((6, 5, 4, 2, 3, 1, 1)):
        assert function(0, 0xffff, selector, 88).value_504d9c == status
    result = function(0, 7, 7, 0x12345678)
    assert (result.selected_status, result.value_504d9c) == (0x12345678, 0x12345678)

print("recovered 0x852b4 publication vectors: ok")
