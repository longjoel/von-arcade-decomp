#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state6_81480.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state_64", "related_172", "related_17e",
        "current_state_504d68", "special_state_match",
        "special_related_match", "special_zero_match", "result_table",
        "result_value", "result_destination", "special_target",
        "fallback_target", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state6.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state6_81480
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(2, 24, 0, 3, 0x1111, ctypes.byref(plan))
    assert (plan.result_table, plan.result_destination,
            plan.target) == (0x72780, 0x504D94, 0x815E0)

    build(2, 23, 0, 3, 0x2222, ctypes.byref(plan))
    assert (plan.special_state_match, plan.special_related_match,
            plan.target) == (1, 0, 0x814B4)

    build(2, 24, 1, 3, 0x3333, ctypes.byref(plan))
    assert (plan.special_zero_match, plan.target) == (0, 0x814B4)

    build(2, 0x10018, 0x20000, 3, 0x4444, ctypes.byref(plan))
    assert (plan.related_172, plan.related_17e,
            plan.special_related_match, plan.special_zero_match,
            plan.target) == (24, 0, 1, 1, 0x815E0)


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("81480", "ld 0x64(g6),g4"),
    ("81484", "cmpibne 2,g4,0x814b4"),
    ("81488", "ldos 0x172(g6),g4"),
    ("8148c", "cmpibne 24,g4,0x814b4"),
    ("81490", "ldos 0x17e(g6),g4"),
    ("81494", "cmpibe 0,g4,0x814b4"),
    ("814a0", "ld 0x72780[g4*4],g4"),
    ("814a8", "st g4,0x504d94"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"81480 listing dataflow missing: {address} {text}"

print("recovered 0x81480 secondary-state6 vectors: ok")
