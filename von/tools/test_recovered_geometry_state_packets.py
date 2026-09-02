#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_state_packets.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "geometry-state-packets.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_state_update_chain
    build.restype = ctypes.c_uint32
    build.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint32),
    ]

    update = (ctypes.c_uint32 * 3)(0xC1BAA9AC, 0x4116147B, 0x416256D4)
    tail = (ctypes.c_uint32 * 3)(0x42995595, 0xBD23D70A, 0xC234EF6A)
    scalar = (ctypes.c_uint32 * 2)(0x416256D4, 0x41BAA9AC)
    packet = (ctypes.c_uint32 * 11)()
    assert build(update, tail, scalar, packet) == 11
    assert list(packet) == [
        0x23, 0xC1BAA9AC, 0x4116147B, 0x416256D4,
        0x12, 0x42995595, 0xBD23D70A, 0xC234EF6A,
        0x0A, 0x416256D4, 0x41BAA9AC,
    ]

print("recovered geometry state-packet chain: ok")
