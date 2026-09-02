#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_profile_packet.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "profile-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_profile_packet
    function.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]
    command = (ctypes.c_uint32 * 14)()
    output = (ctypes.c_uint32 * 4)()
    math_words = (ctypes.c_uint32 * 4)(0x10, 0x20, 0x30, 0x40)
    fallback = (ctypes.c_uint32 * 3)(0xaa, 0xbb, 0xcc)
    assert function(3, 0x12345678, 0x55, math_words, fallback, 0xfeed,
                    command, output) == 14
    assert list(command) == [28, 0x3c00, 27, 0x9e00, 28, 0x10, 28, 0x10,
                              28, 0x9e00, 43, 0x20, 0x30, 0x40]
    assert list(output) == [0xfeed, 0xfeed, 0xfeed, 0x55]

    assert function(2, 7, 0x66, math_words, fallback, 0x1234,
                    command, output) == 4
    assert list(command[:4]) == [43, 0xaa, 0xbb, 0xcc]
    assert list(output) == [0x1234, 0x1234, 0x1234, 0x66]

print("recovered geometry profile-packet vectors: ok")
