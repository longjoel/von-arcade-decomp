#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_state5_status_prefix_83624.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "value_504e1c", "status", "random_calls",
        "calls_82800", "table_remainder_5")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-state5-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_state5_status_prefix_83624
    build.argtypes = [ctypes.c_uint32, ctypes.c_double, ctypes.c_double,
                      ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_uint32]
    build.restype = Plan

    assert (build(4, 0, 10, 0, 0, 0, 0).route,
            build(4, 0, 10, 0, 0, 0, 0).value_504e1c) == (0, 1)
    result = build(5, 10, 9, 0, 0, 0, 0x12)
    assert (result.route, result.calls_82800) == (1, 1)
    assert build(5, 10, -1, 0, 0, 0, 0).status == 0
    assert (build(5, -2, -1, 0, 0, 0, 0).route,
            build(5, -2, -1, 0, 0, 0, 0).status) == (2, 18)
    assert (build(5, 0, 1, 0, 0, 3, 0).route,
            build(5, 0, 1, 0, 0, 3, 0).table_remainder_5) == (3, 3)
    assert (build(5, 0, 1, 1, 3, 3, 0).route,
            build(5, 0, 1, 1, 3, 3, 0).random_calls) == (3, 2)
    assert build(5, 0, 1, 1, 4, 0, 1).status == 42
    assert build(5, 0, 1, 1, 4, 0, 0).status == 35

print("recovered 0x83624 state-5 status-prefix vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83634:", "st g2,0x504e1c"),
        ("83658:", "ble 0x83670"),
        ("83688:", "mov 18,g3"),
        ("836a8:", "remi 10,g0,g0"),
        ("836ac:", "cmpibge 3,g0,0x836d0"),
        ("836c0:", "addo 31,4,g4")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83624 state-5 status-prefix listing evidence: ok")
