#!/usr/bin/env python3
"""Test the 0xdf0cc response-vector selector."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_object_response_vector_selector.c"
WORD3 = ctypes.POINTER(ctypes.c_uint32)

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "response-vector-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    select = lib.recovered_geometry_object_select_response_vector
    select.argtypes = [ctypes.c_int32, WORD3, WORD3, WORD3, WORD3]
    select.restype = None

    vectors = [
        (0x11111111, 0x22222222, 0x33333333),
        (0x44444444, 0x55555555, 0x66666666),
        (0x77777777, 0x88888888, 0x99999999),
    ]
    sources = [(ctypes.c_uint32 * 3)(*vector) for vector in vectors]
    expected = {0: vectors[0], 1: vectors[1], 2: vectors[2]}

    for selector in range(-8, 9):
        selected = (ctypes.c_uint32 * 3)()
        select(selector, *sources, selected)
        assert tuple(selected) == expected.get(selector, (0, 0, 0))

print("recovered geometry object response-vector selector: ok")
