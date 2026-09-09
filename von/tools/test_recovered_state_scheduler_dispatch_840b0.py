#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_dispatch_840b0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "terminal", "write_504d98", "value_504d98",
                 "write_504e1c", "value_504e1c", "next_address")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-dispatch-840b0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_dispatch_840b0
    build.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                      ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(149, 19, 5, 0x1234) == (0, 1, 1, 0x1234, 0, 0, 0)
    assert values(150, 19, 5, 0x1234) == (1, 0, 0, 0, 1, 1, 0x84104)
    assert values(150, 20, 4, 0xdeadbeef) == (2, 0, 0, 0, 1, 1, 0x841a0)

print("recovered 0x840b0 dispatch vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("840b0:", "ld 0x504dc0,g4"),
        ("840c0:", "cmpi g4,g1"),
        ("840dc:", "st g14,0x504d98"),
        ("840e8:", "ld 0x504d7c,g4"),
        ("840f0:", "mov 1,g1"),
        ("840f4:", "cmpi g4,5"),
        ("840f8:", "st g1,0x504e1c"),
        ("84100:", "bne 0x841a0")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x840b0 dispatch listing evidence: ok")
