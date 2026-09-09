#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_state5_status_branch_83884.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "value_504e1c", "status", "random_calls", "calls_82800")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-state5-branch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_state5_status_branch_83884
    build.argtypes = [ctypes.c_uint32, ctypes.c_double, ctypes.c_double,
                      ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_double, ctypes.c_int32]
    build.restype = Plan

    assert build(4, 0, 1, 0, 0, 0, 0, 0).route == 0
    assert (build(5, 10, 9, 0, 0, 0, 0, 0).route,
            build(5, 10, 9, 0, 0, 0, 0, 0).calls_82800) == (1, 1)
    assert (build(5, 0, 1, 1, 2, 9, 4, 0).status,
            build(5, 0, 1, 1, 2, 9, 4, 0).random_calls) == (28, 1)
    assert (build(5, 0, 5, 1, 3, 7, 4, 0).status,
            build(5, 0, 5, 1, 3, 7, 4, 0).random_calls) == (28, 2)
    assert build(5, 0, 1, 0, 9, 2, 4, 0).status == 19
    assert build(5, 0, 1, 1, 9, 2, 4, 4).status == 27
    assert build(5, 0, 1, 1, 9, 2, 4, 3).status == 19
    assert build(5, 0, 5, 0, 9, 7, 4, 0).status == 37
    assert build(5, 0, 5, 1, 9, 7, 4, 0).status == 28
    assert build(5, 0, 1, 1, 9, 7, 8, 3).status == 19
    assert build(5, 0, 1, 1, 9, 1, 8, 3).status == 21

print("recovered 0x83884 state-5 status-branch vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83894:", "st g1,0x504e1c"),
        ("838b8:", "ble 0x838d0"),
        ("838e4:", "cmpibl 3,g0,0x8393c"),
        ("8392c:", "cmpibge 6,g0,0x8395c"),
        ("8394c:", "addo 31,6,g1"),
        ("83998:", "mov 21,g1")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83884 state-5 status-branch listing evidence: ok")
