#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_packet_header_84524.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Header(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "row_offset", "field_0e", "field_00", "field_02", "field_04",
        "writes_field_06", "field_06", "direct_continuation",
        "continuation_r7")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-header.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_packet_header_84524
    build.argtypes = [ctypes.c_uint32] * 8
    build.restype = Header

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Header._fields_)

    assert values(3, 0x8001, 7, 0xffffffff, 0x2c, 0x12, 0x55, 5) == (
        48, 0x8001, 7, 5, 0x122c, 1, 0x55, 1, 16)
    assert values(3, 0x8001, 7, 99, 0x2c, 0x12, 0x55, 5) == (
        48, 0x8001, 7, 5, 0x122c, 0, 0, 0, 0)

print("recovered 0x84524 packet-header vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("84540:", "shlo 4,g1,g3"),
        ("84544:", "cvtzri g4,g0"),
        ("84558:", "subo 1,0,r13"),
        ("8455c:", "stos g6,0xe(g3)[g13]"),
        ("84564:", "cmpi g2,r13"),
        ("84570:", "shlo 8,g4,g4"),
        ("84578:", "stos g5,0x4(g3)[g13]"),
        ("84580:", "stos g0,0x2(g3)[g13]"),
        ("84588:", "bne 0x8459c"),
        ("8458c:", "stos g14,0x6(g3)[g13]"),
        ("84594:", "mov 16,r7")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x84524 packet-header listing evidence: ok")
