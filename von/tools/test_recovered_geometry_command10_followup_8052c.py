#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_command10_followup_8052c.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("selected_word_18", ctypes.c_int32),
        ("selected_word_10", ctypes.c_int32),
        ("selected_word_8", ctypes.c_int32),
        ("object_word_10", ctypes.c_int32),
        ("object_word_8", ctypes.c_int32),
        ("command10_payload_0", ctypes.c_uint32),
        ("command10_payload_1", ctypes.c_uint32),
        ("board_response", ctypes.c_uint32),
        ("response_minus_selected_word_8", ctypes.c_uint32),
        ("bit15_set", ctypes.c_uint32),
        ("packet_words", ctypes.c_uint32),
        ("fifo_destination", ctypes.c_uint32),
        ("clear_bit15_target", ctypes.c_uint32),
        ("set_bit15_target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command10-followup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_command10_followup_8052c
    build.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
        ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x3000, 0x1000, 0x0800, 0x1800, 0x0400, 0x2000,
          ctypes.byref(plan))
    assert plan.command10_payload_0 == 0x1800
    assert plan.command10_payload_1 == 0xFFFFF400
    assert plan.response_minus_selected_word_8 == 0x1800
    assert plan.bit15_set == 0
    assert plan.clear_bit15_target == 0x80580

    build(0, 0, 0x12348000, 0, 0, 0x00000000, ctypes.byref(plan))
    assert plan.response_minus_selected_word_8 == 0x8000
    assert plan.bit15_set == 1
    assert plan.selected_word_8 == -32768
    assert plan.set_bit15_target == 0x805A8


listing = [" ".join(line.split()) for line in (ROOT / "von/build/disasm/vonj-maincpu.lst").read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("80574", "ldos 0x8(g0),g5"),
    ("80578", "subo g5,g4,g4"),
    ("8057c", "bbs 15,g4,0x805a8"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"8052c listing dataflow missing: {address} {text}"

print("recovered 0x8052c command-10 follow-up vectors: ok")
