#!/usr/bin/env python3
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
    library = pathlib.Path(directory) / "parser.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-o", str(library),
        str(ROOT / "von/i960/recovered_input_byte_parser_3a38.c"),
    ], check=True)
    function = ctypes.CDLL(str(library)).recovered_input_byte_parser_3a38
    function.argtypes = [ctypes.POINTER(State), ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    state = State(0, 0, 0, 0xaaaaaaaa)
    assert function(ctypes.byref(state), 3) == 0
    assert (state.first, state.second, state.count, state.status_mask) == (0, 0, 0, 0xaaaaaaaa)

    state = State(0, 0, 2, 0)
    assert function(ctypes.byref(state), 3) == 4
    assert (state.first, state.second, state.count, state.status_mask) == (7, 7, 1, 8)

    state = State(0, 9, 4, 0)
    assert function(ctypes.byref(state), 2) == 1
    assert (state.first, state.second, state.count, state.status_mask) == (255, 9, 4, 0)

    state = State(1, 9, 4, 0xffffffff)
    assert function(ctypes.byref(state), 7) == 2
    assert (state.first, state.second, state.count, state.status_mask) == (0, 9, 4, 0xffffff7f)

    state = State(4, 0, 4, 0)
    assert function(ctypes.byref(state), 31) == 3
    assert (state.first, state.second, state.count, state.status_mask) == (3, 255, 4, 0)

print("PASS: original 0x3a38 input-byte parser vectors")
