#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state5_8140c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state_64", "current_state_504d68", "result_table",
        "result_value", "result_destination", "selector_value",
        "selector_destination", "state6_target", "state4_result_target",
        "state4_return_target", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state5.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state5_8140c
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.POINTER(Plan)]

    plan = Plan()
    build(6, 3, 0x1111, ctypes.byref(plan))
    assert (plan.result_table, plan.result_destination,
            plan.target) == (0x72750, 0x504D94, 0x815E0)

    build(4, 3, 0x2222, ctypes.byref(plan))
    assert (plan.selector_value, plan.selector_destination,
            plan.target) == (7, 0x504D94, 0x815D8)

    build(2, 3, 0x3333, ctypes.byref(plan))
    assert (plan.result_destination, plan.selector_destination,
            plan.target) == (0, 0, 0x81440)


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("8140c", "ld 0x64(g6),g4"),
    ("81410", "cmpibne 6,g4,0x81430"),
    ("8141c", "ld 0x72750[g4*4],g4"),
    ("81424", "st g4,0x504d94"),
    ("8142c", "b 0x815e0"),
    ("81434", "cmpibne 4,g4,0x81440"),
    ("81438", "mov 7,g2"),
    ("8143c", "b 0x815d8"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"8140c listing dataflow missing: {address} {text}"

print("recovered 0x8140c secondary-state5 vectors: ok")
