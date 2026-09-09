#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_packet_fifo_prelude_8459c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Packet(ctypes.Structure):
    _fields_ = [("fifo_word_count", ctypes.c_uint32),
                ("fifo_words", ctypes.c_uint32 * 8),
                ("record_field_06", ctypes.c_uint32),
                ("returned_word", ctypes.c_uint32),
                ("continues_8467c", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-fifo.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_packet_fifo_prelude_8459c
    build.argtypes = [ctypes.c_uint32] * 8
    build.restype = Packet

    result = build(0x11223344, 0x55667788, 0x99aabbcc, 0xddeeff00,
                   1, 2, 0x12345678, 0xfeedface)
    assert result.fifo_word_count == 8
    assert list(result.fifo_words) == [
        0xffffffff, 0x11223344, 0x55667788, 0x99aabbcc,
        0xddeeff00, 10, 1, 2]
    assert result.record_field_06 == 0xfeedface
    assert result.returned_word == 0x5678
    assert result.continues_8467c == 1

print("recovered 0x8459c packet-FIFO vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("8459c:", "shlo 1,g2,g4"),
        ("845a4:", "shlo 1,g4,g4"),
        ("845cc:", "addo 31,31,r13"),
        ("845d0:", "st r13,0x884000"),
        ("84640:", "mov 10,r13"),
        ("84644:", "st r13,0x884000"),
        ("8465c:", "ld 0x884000,g0"),
        ("84664:", "shlo 16,g0,g0"),
        ("84668:", "shri 16,g0,g0"),
        ("8466c:", "stos g7,0x6(g3)[g13]"),
        ("84674:", "bal 0x73508"),
        ("84678:", "mov g0,r7")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x8459c packet-FIFO listing evidence: ok")
