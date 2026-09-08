#!/usr/bin/env python3
"""Check the random remainder producer at i960 0x82f84."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_random_mod7_82f84.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-random-mod7.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_random_mod7_82f84
    function.argtypes = [ctypes.c_int32]
    function.restype = ctypes.c_int32
    bits_function = api.recovered_state_service_random_mod7_82f84_bits
    bits_function.argtypes = [ctypes.c_uint32]
    bits_function.restype = ctypes.c_uint32

    for value in range(-21, 22):
        expected = value % 7 if value >= 0 else -((-value) % 7)
        assert function(value) == expected
    assert bits_function(0xffffffff) == 0xffffffff
    assert bits_function(14) == 0

print("recovered 0x82f84 random-mod7 vectors: ok")
