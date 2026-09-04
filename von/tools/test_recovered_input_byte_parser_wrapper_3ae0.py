#!/usr/bin/env python3
"""Test the exact two-record wrapper at original-ROM address 0x3ae0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


class State(ctypes.Structure):
    _fields_ = [
        ("first", ctypes.c_uint8),
        ("second", ctypes.c_uint8),
        ("count", ctypes.c_uint16),
        ("status_mask", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "parser-wrapper.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-o", str(library),
        str(ROOT / "von/i960/recovered_input_byte_parser_3a38.c"),
        str(ROOT / "von/i960/recovered_input_byte_parser_wrapper_3ae0.c"),
    ], check=True)
    function = ctypes.CDLL(str(library)).recovered_input_byte_parser_wrapper_3ae0
    function.argtypes = [ctypes.POINTER(State), ctypes.POINTER(State)]

    first = State(1, 9, 4, 0xffffffff)
    second = State(0, 0, 2, 0)
    function(ctypes.byref(first), ctypes.byref(second))

    # 0x3a38 is called first with bit 0, then with bit 1.
    assert (first.first, first.second, first.count, first.status_mask) == (0, 9, 4, 0xfffffffe)
    assert (second.first, second.second, second.count, second.status_mask) == (7, 7, 1, 2)

    # The wrapper always makes both calls, including when the records are empty.
    first = State(0, 0, 0, 0xaaaaaaaa)
    second = State(0, 0, 0, 0x55555555)
    function(ctypes.byref(first), ctypes.byref(second))
    assert (first.first, first.second, first.count, first.status_mask) == (0, 0, 0, 0xaaaaaaaa)
    assert (second.first, second.second, second.count, second.status_mask) == (0, 0, 0, 0x55555555)

print("PASS: original 0x3ae0 input-byte parser wrapper vectors")
