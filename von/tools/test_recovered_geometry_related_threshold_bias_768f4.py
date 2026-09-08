#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

with tempfile.TemporaryDirectory() as directory:
    so = pathlib.Path(directory) / "bias.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
        "-o", str(so),
        str(ROOT / "von/i960/recovered_geometry_related_threshold_bias_768f4.c"),
    ], check=True)
    function = ctypes.CDLL(str(so)).recovered_geometry_related_threshold_bias_768f4
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    for state in (0, 3, 4, 6):
        assert function(state, 7, 100) == 110
    assert function(5, 2, 100) == 110
    assert function(5, 7, 100) == 100
    assert function(5, 2, 0xfffffff8) == 2  # i960 32-bit wrap

print("PASS: original 0x768f4 related-object threshold bias")
