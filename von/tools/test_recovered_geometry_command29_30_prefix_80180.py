#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_command29_30_prefix_80180.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def assert_listing_dataflow():
    listing = LISTING.read_text(encoding="utf-8")
    evidence = (
        ("80188", "ldos 0x8(r4),g4"),
        ("801a8", "and g5,g4,g7"),
        ("801bc", "ld 0x884000,g1"),
        ("801c8", "subr g1,g7,r8"),
        ("801cc", "ldos 0x8(r4),g7"),
        ("8023c", "subr g1,g7,r5"),
    )
    lines = [" ".join(line.split()) for line in listing.splitlines()]
    for address, text in evidence:
        normalized_text = " ".join(text.split())
        assert any(address + ":" in line and normalized_text in line for line in lines), \
            f"80180 listing dataflow missing: {address} {text}"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("object_word_8", ctypes.c_int32),
        ("object_word_10", ctypes.c_int32),
        ("anchor_word", ctypes.c_uint32),
        ("plus_6000_word", ctypes.c_uint32),
        ("minus_6000_word", ctypes.c_uint32),
        ("response_command29", ctypes.c_uint32),
        ("response_command30_plus", ctypes.c_uint32),
        ("response_command30_minus", ctypes.c_uint32),
        ("command29_difference", ctypes.c_uint32),
        ("command30_minus_difference", ctypes.c_uint32),
        ("packet_words", ctypes.c_uint32),
        ("fifo_destination", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command29-30-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_command29_30_prefix_80180
    build.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.POINTER(Plan)]

    plan = Plan()
    build(-0x2000, 0x1234, 0x00ABCDEF,
          0x00000100, 0x00000200, 0x00000300, ctypes.byref(plan))
    assert plan.plus_6000_word == 0x4000
    assert plan.minus_6000_word == 0x8000
    assert plan.anchor_word == 0x00ABCDEF
    assert plan.command29_difference == 0x00001234 - 0x100
    assert plan.command30_minus_difference == 0x00001234 - 0x300
    assert plan.packet_words == 9
    assert plan.fifo_destination == 0x884000

    build(0x9000, -2, 0, 0, 0, 0, ctypes.byref(plan))
    assert plan.plus_6000_word == 0xF000
    assert plan.minus_6000_word == 0x3000
    assert plan.command29_difference == 0xFFFFFFFE

assert_listing_dataflow()

print("recovered 0x80180 command-29/30 prefix vectors: ok")
