#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_mod5_status_table_836d0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "handled", "writes_status", "status", "writes_tail",
        "tail_504d8c", "tail_504d90")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-mod5.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_mod5_status_table_836d0
    build.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    build.restype = Plan

    expected = [35, 19, 36, 40, 42]
    for remainder, status in enumerate(expected):
        first = build(0x836D0, remainder, 77)
        assert (first.handled, first.writes_status, first.status,
                first.writes_tail) == (1, 1, status, 0)
        second = build(0x837D0, remainder, 77)
        assert (second.handled, second.status, second.writes_tail,
                second.tail_504d8c, second.tail_504d90) == (1, status, 1, 77, 15)
    assert build(0x836D0, 5, 0).handled == 0
    assert build(0x836D0, -1, 0).handled == 0
    assert build(0x12345, 0, 0).handled == 0

print("recovered 0x836d0/0x837d0 modulo-5 status-table vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("836d4:", "remi 5,g0,g0"),
        ("836d8:", "cmpobl 4,g0,0x8374c"),
        ("836dc:", "ld 0x836e8[g0*4],g4"),
        ("836fc:", "addo 31,4,g2"),
        ("837d0:", "remi 5,g0,g0"),
        ("837d4:", "cmpobl 4,g0,0x83834"),
        ("837d8:", "ld 0x837e4[g0*4],g4"),
        ("83838:", "st g14,0x504d8c"),
        ("83840:", "st g2,0x504d90")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x836d0/0x837d0 listing evidence: ok")
