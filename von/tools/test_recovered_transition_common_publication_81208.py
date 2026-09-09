#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_common_publication_81208.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("global_table_index", ctypes.c_uint32), ("result_table", ctypes.c_uint32),
        ("result_value", ctypes.c_uint32), ("control_504dc8", ctypes.c_uint32),
        ("timing_504d60", ctypes.c_float),
        ("result_destination", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("published_status", ctypes.c_uint32),
        ("status_override", ctypes.c_uint32), ("target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "common-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_common_publication_81208
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_float, ctypes.POINTER(Plan)]

    plan = Plan()
    build(3, 0x12345678, 1, -1, ctypes.byref(plan))
    assert (plan.result_table, plan.result_value, plan.result_destination) == (
        0x728A0, 0x12345678, 0x504D94)
    assert (plan.status_destination, plan.published_status,
            plan.status_override, plan.target) == (0x504D94, 23, 1, 0x81508)

    build(3, 7, 1, 0, ctypes.byref(plan))
    assert plan.target == 0x81518

    build(3, 7, 0, -1, ctypes.byref(plan))
    assert (plan.status_destination, plan.published_status, plan.target) == (
        0, 0, 0x815E0)

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("81218", "ld 0x728a0[g4*4],g4"),
    ("81224", "st g4,0x504d94"),
    ("81238", "movr g4,fp0"),
    ("81248", "cmprl fp0,g2"),
    ("81250", "st g3,0x504d94"),
    ("81258", "bl 0x81508"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"81208 listing dataflow missing: {address} {text}"

print("recovered 0x81208 common-publication vectors: ok")
