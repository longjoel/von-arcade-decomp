#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state4_81390.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("control_504dc8", ctypes.c_uint32), ("flag_504e30", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32), ("result_value", ctypes.c_uint32),
        ("result_destination", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("published_status", ctypes.c_uint32),
        ("flag_bit2_set", ctypes.c_uint32),
        ("flag_bit1_set", ctypes.c_uint32),
        ("timing_504d60", ctypes.c_float),
        ("related_threshold", ctypes.c_float),
        ("related_float_passed", ctypes.c_uint32),
        ("related_float_target", ctypes.c_uint32),
        ("bit1_clear_target", ctypes.c_uint32),
        ("bit1_set_target", ctypes.c_uint32),
        ("control_failure_target", ctypes.c_uint32), ("target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state4_81390
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_float, ctypes.POINTER(Plan)]

    plan = Plan()
    build(1, 4, 0x1111, 3.0, ctypes.byref(plan))
    assert (plan.status_destination, plan.published_status,
            plan.flag_bit2_set, plan.target) == (0x504D94, 23, 1, 0x81570)

    build(1, 0, 0x2222, 4.0, ctypes.byref(plan))
    assert (plan.flag_bit2_set, plan.flag_bit1_set,
            plan.related_float_passed, plan.target) == (0, 0, 0, 0x8159C)

    build(1, 6, 0x3333, 4.0, ctypes.byref(plan))
    assert (plan.flag_bit1_set, plan.target) == (1, 0x8158C)

    build(0, 4, 0x4444, 3.0, ctypes.byref(plan))
    assert (plan.result_destination, plan.status_destination,
            plan.published_status, plan.target) == (0x504D94, 0, 0, 0x815E0)


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("813a0", "ld 0x728a0[g4*4],g4"),
    ("813b4", "st g4,0x504d94"),
    ("813dc", "ld 0xffffffcc(g6),g4"),
    ("813e4", "movr g4,fp0"),
    ("813f4", "cmprl fp0,g2"),
    ("81404", "bbs 1,g4,0x8158c"),
    ("81408", "b 0x8159c"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"81390 listing dataflow missing: {address} {text}"

print("recovered 0x81390 secondary-state4 vectors: ok")
