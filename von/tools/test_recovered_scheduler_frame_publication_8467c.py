#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_publication_8467c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Publication(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "row_offset", "selector_result", "packed_field_08",
        "field_08_flags", "field_0a", "called_847c0")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "frame-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_frame_publication_8467c
    build.argtypes = [ctypes.c_uint32] * 6
    build.restype = Publication

    result = build(3, 1, 1, 0x12, 0x34, 0x5678)
    assert (result.row_offset, result.selector_result,
            result.packed_field_08, result.field_08_flags,
            result.field_0a, result.called_847c0) == (
        48, 0x5678, 0xf412, 0xc000, 0x5678, 1)
    result = build(0, 0, 0, 0xab, 0xcd, 99)
    assert result.packed_field_08 == 0xcdab
    assert result.field_08_flags == 0

print("recovered 0x8467c frame-publication vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("8467c:", "ldib 0x509ac0,g4"),
        ("84684:", "cmpi 1,g4"),
        ("84694:", "ldib 0x509b10,g4"),
        ("8469c:", "cmpi 1,g4"),
        ("846ac:", "mov r12,g0"),
        ("846b8:", "call 0x847c0"),
        ("846bc:", "ld 0x509a68,g7"),
        ("84700:", "shlo 4,g7,g13"),
        ("84704:", "stos r7,0xa(g13)[r8]"),
        ("8470c:", "shlo 8,g6,g6"),
        ("8471c:", "stos g4,0x8(g13)[r8]")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x8467c frame-publication listing evidence: ok")
