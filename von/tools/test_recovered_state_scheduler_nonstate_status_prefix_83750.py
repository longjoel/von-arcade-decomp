#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_nonstate_status_prefix_83750.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "status", "random_calls", "calls_82800",
        "table_remainder_5")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-nonstate-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_nonstate_status_prefix_83750
    build.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_uint32,
                      ctypes.c_int32, ctypes.c_int32]
    build.restype = Plan

    result = build(10, 9, 0, 0, 0)
    assert (result.route, result.calls_82800) == (0, 1)
    assert build(-2, -1, 0, 0, 0).status == 18
    result = build(0, 1, 0, 8, 4)
    assert (result.route, result.random_calls,
            result.table_remainder_5) == (2, 1, 4)
    result = build(0, 1, 1, 3, 2)
    assert (result.route, result.random_calls,
            result.table_remainder_5) == (2, 2, 2)
    result = build(0, 1, 1, 4, 0)
    assert (result.route, result.status, result.random_calls) == (3, 42, 2)

print("recovered 0x83750 non-state status-prefix vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83768:", "ble 0x83780"),
        ("83798:", "mov 18,g3"),
        ("837a8:", "cmpibne 1,g4,0x837cc"),
        ("837b4:", "cmpibge 3,g0,0x837cc"),
        ("837bc:", "addo 31,11,g2")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83750 non-state status-prefix listing evidence: ok")
