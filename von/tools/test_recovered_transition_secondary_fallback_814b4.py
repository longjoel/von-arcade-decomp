#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_fallback_814b4.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("control_504dc8", ctypes.c_uint32),
        ("current_state_504d68", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32), ("result_value", ctypes.c_uint32),
        ("result_destination", ctypes.c_uint32), ("control_one", ctypes.c_uint32),
        ("timing_504d60", ctypes.c_float), ("timing_threshold", ctypes.c_float),
        ("timing_float_passed", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("initial_status", ctypes.c_uint32), ("final_status", ctypes.c_uint32),
        ("state_destination", ctypes.c_uint32),
        ("published_state", ctypes.c_uint32),
        ("control_failure_target", ctypes.c_uint32),
        ("timing_pass_target", ctypes.c_uint32),
        ("timing_fail_target", ctypes.c_uint32), ("target", ctypes.c_uint32))]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-fallback.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_fallback_814b4
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_float, ctypes.POINTER(Plan)]

    plan = Plan()
    build(1, 3, 0x1111, 3.0, ctypes.byref(plan))
    assert (plan.result_destination, plan.status_destination,
            plan.initial_status, plan.final_status, plan.state_destination,
            plan.published_state) == (0x504D94, 0x504D94, 23, 23, 0x504D98, 1)

    build(1, 3, 0x2222, 4.0, ctypes.byref(plan))
    assert (plan.timing_float_passed, plan.status_destination,
            plan.initial_status, plan.final_status, plan.state_destination,
            plan.published_state) == (0, 0x504D94, 23, 8, 0, 0)

    build(0, 3, 0x3333, 3.0, ctypes.byref(plan))
    assert (plan.status_destination, plan.initial_status, plan.final_status,
            plan.state_destination, plan.target) == (0, 0, 0, 0, 0x815E0)


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("814c4", "ld 0x728a0[g4*4],g4"),
    ("814cc", "cmpi g5,1"),
    ("814d0", "st g4,0x504d94"),
    ("814d8", "bne 0x815e0"),
    ("814dc", "ld 0x504d60,g4"),
    ("814f4", "cmprl fp0,g2"),
    ("814fc", "st g3,0x504d94"),
    ("8150c", "st g2,0x504d98"),
    ("8151c", "st g3,0x504d94"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"814b4 listing dataflow missing: {address} {text}"

print("recovered 0x814b4 secondary-fallback vectors: ok")
