#!/usr/bin/env python3
"""Validate the recovered selector/staging boundary for SHARC opcode 0x17."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_17.c"


with tempfile.TemporaryDirectory() as directory:
    library_path = pathlib.Path(directory) / "opcode17.so"
    subprocess.run(
        ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library_path)],
        check=True,
    )
    library = ctypes.CDLL(str(library_path))

    select = library.recovered_sharc_opcode_17_select_record
    select.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
        ctypes.c_float, ctypes.c_float,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
    ]
    select.restype = ctypes.c_int

    record1 = [
        0x3F800000, 0x40000000, 0x40A00000, 0x40800000,
        0x40E00000, 0x40C00000, 0x41100000, 0x41000000,
        0x40400000, 0x41200000, 0x41300000, 0x41400000,
    ]
    record2 = [
        0x40000000, 0x40000000, 0x40A00000, 0x40800000,
        0x40E00000, 0x40C00000, 0x41100000, 0x41000000,
        0x40400000, 0x41200000, 0x41300000, 0x41400000,
    ]
    bank = (ctypes.c_uint32 * 32)(*(record1 + [0] * 4 + record2 + [0] * 4))
    selectors = (ctypes.c_uint32 * 2)(0, 1)
    staged = (ctypes.c_uint32 * 12)()
    determinant = ctypes.c_float()

    result = select(selectors, 2, 1, bank, 32, 0.0, 0.0, staged, ctypes.byref(determinant))
    assert result == 1
    assert list(staged) == record2
    assert determinant.value != 0.0

    result = select(selectors, 2, 0, bank, 32, 0.0, 0.0, staged, ctypes.byref(determinant))
    assert result == 1 and list(staged) == record1

    result = select(selectors, 2, 0, bank, 11, 0.0, 0.0, staged, ctypes.byref(determinant))
    assert result == -1

print("PASS: recovered SHARC opcode-0x17 selector/staging contract")
