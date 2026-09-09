#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_status_tail_80650.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("publication_gate_passed", ctypes.c_uint32),
        ("incoming_status", ctypes.c_uint32), ("status_minus_8", ctypes.c_uint32),
        ("mapped_status", ctypes.c_uint32),
        ("callback_enable", ctypes.c_uint32),
        ("callback_target", ctypes.c_uint32),
        ("callback_argument", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("action_destination", ctypes.c_uint32),
        ("action_value", ctypes.c_uint32), ("return_value", ctypes.c_uint32),
        ("target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_status_tail_80650
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(Plan)]

    for incoming, expected in ((8, 1), (9, 4), (10, 5),
                               (11, 6), (18, 2), (19, 3), (12, 12)):
        plan = Plan()
        build(incoming, 1, 0x12345678, ctypes.byref(plan))
        assert plan.mapped_status == expected
        assert plan.status_destination == 0x504D94
        assert plan.action_value == 30
        assert plan.callback_target == 0x79050
        assert plan.callback_argument == 0x12345678
        assert plan.target == 0x806F4

    plan = Plan()
    build(8, 0, 0x12345678, ctypes.byref(plan))
    assert plan.mapped_status == 1
    assert plan.status_destination == 0x504D94
    assert plan.action_value == 30
    assert plan.callback_enable == 0
    assert plan.callback_target == 0
    assert plan.callback_argument == 0
    assert plan.target == 0x806F4


listing = [" ".join(line.split()) for line in (ROOT / "von/build/disasm/vonj-maincpu.lst").read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("80658", "subo 8,g5,g4"),
    ("8065c", "cmpobl 11,g4,0x806c8"),
    ("80660", "ld 0x8066c[g4*4],g4"),
    ("806d0", "cmpi 1,g4"),
    ("806d4", "st g5,0x504d94"),
    ("806e4", "call 0x79050"),
    ("806ec", "st g9,0x504db8"),
    ("806f4", "mov 1,g0"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"80650 listing dataflow missing: {address} {text}"

print("recovered 0x80650 status-tail vectors: ok")
