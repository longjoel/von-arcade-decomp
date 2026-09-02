#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_18.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "sharc-opcode-18.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    window = lib.recovered_sharc_opcode_18_window
    word_pointer = ctypes.POINTER(ctypes.c_uint32)
    window.argtypes = [word_pointer, ctypes.c_uint32, word_pointer, word_pointer]

    table = (ctypes.c_uint32 * 64)(*[0x10000000 + index for index in range(64)])
    scratch = (ctypes.c_uint32 * 16)(*[0xA5A5A5A5] * 16)
    output = (ctypes.c_uint32 * 12)()
    window(table, 2, scratch, output)
    assert list(scratch) == [0x10000020 + index for index in range(16)]
    assert list(output) == [0x10000020 + index for index in range(12)]

    window(table, 0, scratch, output)
    assert list(scratch) == [0x10000000 + index for index in range(16)]
    assert list(output) == [0x10000000 + index for index in range(12)]

print("recovered SHARC opcode-0x18 table-window vectors: ok")
