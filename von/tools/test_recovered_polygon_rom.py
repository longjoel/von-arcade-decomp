#!/usr/bin/env python3
"""Test the recovered C polygon-ROM decoder against the verified arena floor."""
import ctypes
import os
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Vec3(ctypes.Structure): _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float)]
class Record(ctypes.Structure): _fields_ = [("attribute", ctypes.c_uint32), ("vertex_count", ctypes.c_uint32), ("vertex", Vec3 * 4)]
CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(Record))
def decode(fn, data, oba):
    array = (ctypes.c_uint8 * len(data)).from_buffer_copy(data); output = []
    @CALLBACK
    def emit(_, record): output.append(Record.from_buffer_copy(record.contents)); return 0
    result = fn(array, len(data), oba, 0, emit, None)
    if result != len(output): raise SystemExit(f"decode result {result}, callback count {len(output)}")
    return output
def main():
    with tempfile.TemporaryDirectory() as temp:
        library = Path(temp) / "polygon.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", ROOT / "von/i960/recovered_polygon_rom.c", "-o", library], check=True)
        fn = ctypes.CDLL(str(library)).recovered_polygon_rom_decode
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32, CALLBACK, ctypes.c_void_p]; fn.restype = ctypes.c_int
        floor = decode(fn, (ROOT / "von/build/disasm/geometry-rom.bin").read_bytes(), 0x0091af12)
        if len(floor) != 1 or floor[0].attribute != 0x49000a01 or floor[0].vertex_count != 4: raise SystemExit("floor record mismatch")
        p = floor[0].vertex
        if (p[0].x, p[0].y, p[0].z) != (5000.0, -40.0, 5000.0): raise SystemExit("floor corner mismatch")
        def ny(a,b,c): return (b.z-a.z)*(c.x-a.x)-(b.x-a.x)*(c.z-a.z)
        if ny(p[0],p[1],p[2]) * ny(p[1],p[3],p[2]) <= 0: raise SystemExit("floor winding mismatch")
    print("PASS: C polygon-ROM decoder and arena floor")
if __name__ == "__main__": main()
