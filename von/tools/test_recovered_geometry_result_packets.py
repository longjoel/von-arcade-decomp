#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_result_packets.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "result-packets.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    request38 = lib.recovered_geometry_result_request38
    request38.restype = ctypes.c_uint32
    request38.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    request31 = lib.recovered_geometry_result_request31
    request31.restype = ctypes.c_uint32
    request31.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                          ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    values = (ctypes.c_uint32 * 3)(0xffffffff, 2, 3)
    packet = (ctypes.c_uint32 * 4)()
    assert request38(values, packet) == 4
    assert list(packet) == [0x38, 0xffffffff, 2, 3]
    references = (ctypes.c_uint32 * 3)(4, 5, 6)
    scratch = (ctypes.c_uint32 * 3)(7, 8, 9)
    packet31 = (ctypes.c_uint32 * 7)()
    assert request31(references, scratch, packet31) == 7
    assert list(packet31) == [31, 4, 5, 6, 7, 8, 9]

print("recovered geometry result-packet vectors: ok")
