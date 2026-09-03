#!/usr/bin/env python3
"""Test the recovered C polygon-ROM decoder against the verified arena floor."""
import ctypes
import os
import re
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
        data = (ROOT / "von/build/disasm/geometry-rom.bin").read_bytes()
        floor = decode(fn, data, 0x0091af12)
        if len(floor) != 1 or floor[0].attribute != 0x49000a01 or floor[0].vertex_count != 4: raise SystemExit("floor record mismatch")
        p = floor[0].vertex
        if (p[0].x, p[0].y, p[0].z) != (5000.0, -40.0, 5000.0): raise SystemExit("floor corner mismatch")
        def ny(a,b,c): return (b.z-a.z)*(c.x-a.x)-(b.x-a.x)*(c.z-a.z)
        if ny(p[0],p[1],p[2]) * ny(p[1],p[3],p[2]) <= 0: raise SystemExit("floor winding mismatch")
        trace = ROOT / "von/build/disasm/vonj-post-start-45s-drone0.trace"
        if trace.is_file():
            obas = set()
            opcodes = set()
            for line in trace.read_text(errors="replace").splitlines():
                match = re.search(
                    r"vonj_geometry_object: time=([0-9.]+).*?oba=([0-9a-f]+).*?"
                    r"source=polygon-rom opcode=([0-9a-f]+)", line)
                if match and float(match.group(1)) >= 43.0:
                    obas.add(int(match.group(2), 16))
                    opcodes.add(match.group(3))
            if len(obas) != 109 or opcodes != {"00800101"}:
                raise SystemExit("unexpected post-start OBA/opcode set")
            decoded = [len(decode(fn, data, oba)) for oba in sorted(obas)]
            if min(decoded) < 1 or max(decoded) != 781:
                raise SystemExit("live match OBA decoder range mismatch")
            print(f"PASS: live match OBA decoder oracle ({len(obas)} objects, {sum(decoded)} polygons)")
        else:
            print("SKIP: live match trace is not present")
        select_trace = ROOT / "von/build/disasm/vonj-geometry-select-45s-drone0.trace"
        if select_trace.is_file():
            obas = set()
            opcodes = set()
            for line in select_trace.read_text(errors="replace").splitlines():
                match = re.search(
                    r"vonj_geometry_object: time=([0-9.]+).*?oba=([0-9a-f]+).*?"
                    r"source=polygon-rom opcode=([0-9a-f]+)", line)
                if match:
                    obas.add(int(match.group(2), 16))
                    opcodes.add(match.group(3))
            if len(obas) != 684 or opcodes != {"00800101"}:
                raise SystemExit("unexpected machine-select OBA/opcode set")
            decoded = [len(decode(fn, data, oba)) for oba in sorted(obas)]
            if min(decoded) < 1 or max(decoded) != 781:
                raise SystemExit("machine-select OBA decoder range mismatch")
            print(f"PASS: machine-select OBA decoder oracle ({len(obas)} objects, {sum(decoded)} polygons)")
    print("PASS: C polygon-ROM decoder and arena floor")
if __name__ == "__main__": main()
