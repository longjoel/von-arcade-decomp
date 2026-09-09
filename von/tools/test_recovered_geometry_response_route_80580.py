#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_response_route_80580.c"
RUNTIME_SOURCE = ROOT / "von/i960/recovered_runtime_math.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("bit15_set", ctypes.c_uint32), ("record_word_8", ctypes.c_int32),
        ("object_word_184", ctypes.c_int32),
        ("bias_504de4", ctypes.c_int32),
        ("signed_classifier_input", ctypes.c_int32),
        ("classifier_band", ctypes.c_uint32),
        ("classifier_target", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32),
        ("classifier_result", ctypes.c_uint32),
        ("action_destination", ctypes.c_uint32), ("action_value", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("published_status", ctypes.c_uint32),
        ("callback_target", ctypes.c_uint32),
        ("callback_argument", ctypes.c_uint32),
        ("global_counter", ctypes.c_uint32), ("global_threshold", ctypes.c_uint32),
        ("counter_gate_passed", ctypes.c_uint32), ("next_target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "response-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    str(RUNTIME_SOURCE), "-o", str(library)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_response_route_80580
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0, 0x1000, 0x0200, 0x0300, 4, 0x12345678, 0x5dd,
          ctypes.byref(plan))
    assert plan.signed_classifier_input == 0x0e00
    assert plan.classifier_band == 1
    assert plan.classifier_target == 0x73508
    assert plan.result_table == 0x72660
    assert plan.action_value == 20
    assert plan.published_status == 4
    assert plan.callback_target == 0x7D1F0
    assert plan.callback_argument == 0x12345678
    assert plan.counter_gate_passed == 1
    assert plan.next_target == 0x80600

    build(1, -0x1000, 0x0100, 0x0200, 6, 0, 0x5dc, ctypes.byref(plan))
    assert plan.signed_classifier_input == -0x1300
    assert plan.classifier_band == 8
    assert plan.counter_gate_passed == 0
    assert plan.next_target == 0x806F4


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("80580", "ldos 0x8(g0),g0"),
    ("80584", "ldos 0x184(g10),g4"),
    ("805c0", "subo g5,g0,g0"),
    ("805cc", "subo g4,g0,g0"),
    ("805d0", "bal 0x73508"),
    ("805d4", "ld 0x72660[g0*4],g4"),
    ("805ec", "st g4,0x504d94"),
    ("805f4", "call 0x7d1f0"),
    ("80604", "cmpible g4,g8,0x806f4"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"80580 listing dataflow missing: {address} {text}"

print("recovered 0x80580 response-route vectors: ok")
