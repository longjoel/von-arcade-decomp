#!/usr/bin/env python3
"""Validate the selector-zero MMIO write sequence at i960 0x6fec0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_control_selector_6fec0.c"

WRITE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32)


with tempfile.TemporaryDirectory(prefix="von-geometry-control-6fec0-") as directory:
    library = pathlib.Path(directory) / "control.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_control_selector_6fec0
    function.argtypes = [ctypes.c_uint32, WRITE, ctypes.c_void_p]
    function.restype = ctypes.c_uint32

    writes = []

    @WRITE
    def write(_opaque, address, value):
        writes.append((address, value))

    assert function(1, write, None) == 0
    assert writes == []

    assert function(0, write, None) == 1
    assert writes == [
        (0x00800030, 0x00000303),
        (0x00804000, 0x00000080),
        (0x00804004, 0x01F40204),
        (0x00804008, 0x00F80140),
        (0x0080400C, 0x00F80140),
        (0x00804000, 0x00F80140),
        (0x00804000, 0x00F80140),
    ]

print("PASS: 0x6fec0 selector and exact MMIO write sequence")
