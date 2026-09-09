#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state0_811f0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_state", "related_172", "related_17e", "state_gate_passed",
        "offset_gate_passed", "zero_offset_passed", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state0_811f0
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.POINTER(Plan)]

    plan = Plan()
    build(2, 24, 1, ctypes.byref(plan))
    assert (plan.state_gate_passed, plan.offset_gate_passed,
            plan.zero_offset_passed, plan.target) == (1, 1, 0, 0x81498)

    build(2, 24, 0, ctypes.byref(plan))
    assert (plan.zero_offset_passed, plan.target) == (1, 0x81208)

    for values in ((1, 24, 1), (2, 23, 1), (2, 24, 0x100)):
        build(*values, ctypes.byref(plan))
        assert plan.target in (0x81208, 0x81498)
    build(1, 24, 1, ctypes.byref(plan))
    assert plan.target == 0x81208

    build(2, 0x10018, 0x20000, ctypes.byref(plan))
    assert (plan.related_172, plan.related_17e,
            plan.offset_gate_passed, plan.zero_offset_passed,
            plan.target) == (24, 0, 1, 1, 0x81208)


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("811f4", "cmpibne 2,g4,0x81208"),
    ("811f8", "ldos 0x172(g6),g4"),
    ("811fc", "cmpibne 24,g4,0x81208"),
    ("81200", "ldos 0x17e(g6),g4"),
    ("81204", "cmpibne 0,g4,0x81498"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"811f0 listing dataflow missing: {address} {text}"

print("recovered 0x811f0 secondary-state0 vectors: ok")
