#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_packet_tail.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "packet-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_packet_tail
    function.restype = ctypes.c_uint32
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    for g4, g5 in ((0, 0), (1, 2), (0xffffffff, 0x80000000)):
        packet = (ctypes.c_uint32 * 3)()
        assert function(g4, g5, packet) == 3
        assert list(packet) == [g4, g5, 0]

print("recovered geometry packet-tail vectors: ok")
