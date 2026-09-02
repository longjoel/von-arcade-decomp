#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_command_packet_variant.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command-packet-variant.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_command_packet_variant
    function.restype = ctypes.c_uint32
    function.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(ctypes.c_uint32)]
    for values in ((0, 1, 2, 3, 4, 5), (0xffffffff, 0x80000000, 7, 11, 13, 17)):
        g0, g1, g2, g3, g4, g6 = values
        packet = (ctypes.c_uint32 * 18)()
        assert function(*values, packet) == 18
        expected = [0, g4, g0, (g1 + g3) & 0xffffffff, g2, g0,
                    (g1 + g3) & 0xffffffff, g2, 0x01540601,
                    0x7f000000, 0x3f800000, (g0 - g3) & 0xffffffff,
                    (g1 - g3) & 0xffffffff, g2, (g0 + g3) & 0xffffffff,
                    (g1 - g3) & 0xffffffff, g2, 0]
        assert list(packet) == expected

print("recovered geometry command-packet variant vectors: ok")
