#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_dispatch_811b8.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "table_base", "bounded_to_table", "selected_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_dispatch_811b8
    build.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    expected = [0x811F0, 0x81260, 0x812AC, 0x81300,
                0x81390, 0x8140C, 0x81480, 0x81528]
    for state, target in enumerate(expected):
        plan = Plan()
        build(state, ctypes.byref(plan))
        assert plan.table_base == 0x811D0
        assert plan.bounded_to_table == 1
        assert plan.selected_target == target

    for state in (8, 31, 0xFFFFFFFF):
        plan = Plan()
        build(state, ctypes.byref(plan))
        assert plan.bounded_to_table == 0
        assert plan.selected_target == 0x815AC


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("811bc", "cmpobl 7,g4,0x815ac"),
    ("811c0", "ld 0x64(g0),g4"),
    ("811c4", "ld 0x811d0[g4*4],g4"),
    ("811cc", "bx (g4)"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"811b8 listing dataflow missing: {address} {text}"

print("recovered 0x811b8 secondary-dispatch vectors: ok")
