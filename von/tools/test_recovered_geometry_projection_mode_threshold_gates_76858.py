#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

with tempfile.TemporaryDirectory() as directory:
    so = pathlib.Path(directory) / "gates.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
        "-o", str(so),
        str(ROOT / "von/i960/recovered_geometry_projection_mode_threshold_gates_76858.c"),
    ], check=True)
    function = ctypes.CDLL(str(so)).recovered_geometry_projection_mode_threshold_gates_76858
    function.argtypes = [
        ctypes.c_uint32, ctypes.c_uint16, ctypes.c_uint16,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
    ]
    function.restype = ctypes.c_uint32

    # Mode 1 bypasses the 101 gate; the low-r4 gates still apply.
    assert function(1, 10, 40, 480, 20, 2, 86) == 90
    assert function(1, 10, 40, 480, 20, 4, 91) == 100
    assert function(1, 10, 40, 480, 20, 5, 91) == 91

    # 10 >= 40/4 and 20 - (480/48) == 10, so threshold 99 rises to 101.
    assert function(2, 10, 40, 480, 20, 5, 99) == 101
    assert function(2, 9, 40, 480, 20, 5, 99) == 99
    assert function(2, 10, 40, 480, 20, 5, 100) == 100

print("PASS: original 0x76858 projection mode threshold gates")
