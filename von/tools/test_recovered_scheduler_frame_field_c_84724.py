#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_field_c_84724.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Field(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "packed_frame_low16", "object_108_packed", "field_0c",
        "state31_path", "set_frame_bit3")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "frame-field-c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_frame_field_c_84724
    build.argtypes = [ctypes.c_uint32] * 7
    build.restype = Field

    result = build(0x1, 0x10, 0x20, 0x40, 0xabcf, 7, 0)
    assert (result.packed_frame_low16, result.object_108_packed,
            result.field_0c, result.state31_path) == (0x71, 0x0bf, 0x71bf, 0)
    result = build(0x1, 0x10, 0x20, 0x40, 0xabcf, 31, 0x4321)
    assert (result.packed_frame_low16, result.field_0c,
            result.state31_path, result.set_frame_bit3) == (0x79, 0x7b21, 1, 1)

print("recovered 0x84724 frame-field vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("84724:", "or g5,g1,g5"),
        ("8472c:", "or g0,g5,g5"),
        ("84730:", "ldos 0x108(r4),g4"),
        ("84748:", "shro 4,g4,g4"),
        ("8474c:", "cmpi g7,31"),
        ("84788:", "setbit 3,g0,g0"),
        ("84794:", "shlo 8,g0,g4"),
        ("847a0:", "and g4,r13,g4"),
        ("847a4:", "or g3,g4,g4"),
        ("847a8:", "stos g4,0xc(g13)[r8]")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x84724 frame-field listing evidence: ok")
