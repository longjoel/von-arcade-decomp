#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_handler_status_82840.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_int32 if name in ("first_remainder", "second_remainder") else ctypes.c_uint32) for name in (
        "accepted", "status", "random_calls", "first_remainder",
        "second_remainder")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handler-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_handler_status_82840
    build.argtypes = [ctypes.c_uint32, ctypes.c_int32,
                      ctypes.c_int32, ctypes.c_int32]
    build.restype = Plan

    def values(selector, global_value, random1=0, random2=0):
        result = build(selector, global_value, random1, random2)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(0, 0, 3, 7) == (1, 14, 2, 0, 1)
    assert values(0, 0, 1, 2) == (1, 15, 2, 1, 2)
    assert values(0, 0, 2, 3) == (1, 29, 2, 2, 3)
    assert values(0, 0, -1, 2) == (1, 15, 2, -1, 2)
    assert values(1, 0, 12) == (1, 30, 1, 0, 2)
    assert values(1, 0, 15) == (1, 29, 1, 0, 5)
    assert values(1, 0, 14) == (1, 30, 1, 0, 4)
    assert values(2, 0, 13) == (1, 30, 1, 0, 3)
    assert values(2, 0, 15) == (1, 29, 1, 0, 5)
    assert values(5, 0, 10) == (1, 30, 1, 0, 0)
    assert values(5, 0, 11) == (1, 30, 1, 0, 1)
    assert values(5, 0, 14) == (1, 30, 1, 0, 4)
    assert values(5, 0, 15) == (1, 29, 1, 0, 5)
    assert values(6, 1) == (1, 13, 0, 0, 0)
    assert values(6, -1, 2) == (1, 30, 2, 2, 0)
    assert values(6, -1, 3, 2) == (1, 13, 1, 0, 0)
    assert values(6, -1, -1) == (1, 13, 1, -1, 0)
    assert values(7, 0, 14) == (1, 29, 1, 0, 4)
    assert values(7, 0, 16) == (1, 29, 1, 0, 6)
    assert values(8, 0) == (1, 30, 0, 0, 0)
    assert values(9, 0) == (1, 29, 0, 0, 0)
    assert values(10, 0) == (0, 29, 0, 0, 0)

print("recovered 0x82840 handler-status vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("82844:", "remi 3,g0,g0"),
        ("82850:", "remi 3,g0,g0"),
        ("82860:", "remi 10,g0,g0"),
        ("82878:", "remi 10,g0,g0"),
        ("828f0:", "ld 0x504d60,g4"),
        ("82910:", "bal 0xf5058"),
        ("82918:", "cmpibl 1,g0,0x82924"),
        ("82928:", "remi 10,g0,g0"),
        ("82940:", "remi 10,g0,g0")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x82840 handler-status listing evidence: ok")
