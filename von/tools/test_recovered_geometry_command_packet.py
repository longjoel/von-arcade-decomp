#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_command_packet.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_command_packet
    function.restype = ctypes.c_uint32
    function.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(ctypes.c_uint32)]
    vectors = [(0, 1, 2, 3, 4, 5),
               (0xffffffff, 0x80000000, 7, 11, 13, 17),
               (9, 8, 7, 6, 5, 4)]
    for g0, g1, g2, g3, g4, g6 in vectors:
        packet = (ctypes.c_uint32 * 18)()
        assert function(g0, g1, g2, g3, g4, g6, packet) == 18
        expected = [0, g6, g4, g0, (g1 - g3) & 0xffffffff, g2,
                    (g0 - g3) & 0xffffffff, g1, g2, 0x01540601,
                    0x7f000000, 0x3f800000, (g0 + g3) & 0xffffffff,
                    (g1 + g3) & 0xffffffff, g2, g0, g3, g2]
        assert list(packet) == expected

print("recovered geometry command-packet vectors: ok")
