#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_command10_classifier_prefix_803c8.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("selected_word_18", ctypes.c_int32),
        ("selected_word_10", ctypes.c_int32),
        ("object_word_10", ctypes.c_int32),
        ("object_word_8", ctypes.c_int32),
        ("object_word_184", ctypes.c_int32),
        ("command10_payload_0", ctypes.c_uint32),
        ("command10_payload_1", ctypes.c_uint32),
        ("command10_response", ctypes.c_uint32),
        ("classifier_raw_difference", ctypes.c_uint32),
        ("classifier_input", ctypes.c_int32),
        ("packet_words", ctypes.c_uint32),
        ("fifo_destination", ctypes.c_uint32),
        ("classifier_target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command10-classifier-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_command10_classifier_prefix_803c8
    build.argtypes = [
        ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_int32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x3000, 0x1000, 0x1800, 0x0800, 0x4000, 0x00005000,
          ctypes.byref(plan))
    assert plan.command10_payload_0 == 0x1800
    assert plan.command10_payload_1 == 0xFFFFF800
    assert plan.classifier_raw_difference == 0x1000
    assert plan.classifier_input == 0x1000
    assert plan.packet_words == 3
    assert plan.fifo_destination == 0x884000
    assert plan.classifier_target == 0x73508

    build(0, 0, 0, 0, 0x12348000, 0x00000000, ctypes.byref(plan))
    assert plan.classifier_input == -32768
    assert plan.object_word_184 == -32768


listing = [" ".join(line.split()) for line in (ROOT / "von/build/disasm/vonj-maincpu.lst").read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("803ec", "ldos 0x184(g0),g4"),
    ("803f0", "subo g4,g5,g0"),
    ("803f4", "shlo 16,g0,g0"),
    ("803f8", "shri 16,g0,g0"),
    ("803fc", "bal 0x73508"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"803c8 listing dataflow missing: {address} {text}"

print("recovered 0x803c8 command-10 classifier-prefix vectors: ok")
