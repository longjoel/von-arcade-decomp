#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

with tempfile.TemporaryDirectory() as directory:
    so = pathlib.Path(directory) / "reclamp.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
        "-o", str(so),
        str(ROOT / "von/i960/recovered_geometry_projection_threshold_reclamp_76808.c"),
    ], check=True)
    function = ctypes.CDLL(str(so)).recovered_geometry_projection_threshold_reclamp_76808
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = ctypes.c_uint32

    assert function(0, 0) == 0x50
    assert function(10, 20) == 0x73
    assert function(200, 20) == 300
    assert function(0xffffffff, 21) == 201
    assert function(0xffffffff, 1000) == 300

print("PASS: original 0x76808 projection threshold re-clamp")
