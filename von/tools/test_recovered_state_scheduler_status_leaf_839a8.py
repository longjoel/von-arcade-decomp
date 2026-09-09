#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_status_leaf_839a8.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "status", "random_calls", "write_504d8c", "value_504d8c",
        "write_504d90", "value_504d90")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-leaf.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_status_leaf_839a8
    build.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(1, 2, 0, 5, 0, 0, 0, 33, 77) == (0, 33, 0, 1, 77, 1, 15)
    assert values(2, 2, 0, 5, 4, 1, 5, 33, 77) == (2, 21, 1, 1, 77, 1, 15)
    assert values(2, 2, 0, 5, 0, 0, 0, 33, 77) == (2, 21, 1, 1, 77, 1, 15)
    assert values(2, 2, 2, 5, 4, 1, 5, 33, 77) == (3, 27, 1, 1, 77, 1, 15)
    assert values(2, 2, 2, 5, 4, 1, 0, 33, 77) == (1, 19, 1, 1, 77, 1, 15)
    assert values(5, 2, 7, 5, 2, 1, 0, 33, 77) == (4, 28, 1, 1, 77, 1, 15)
    assert values(5, 2, 7, 5, 2, 0, 0, 33, 77) == (5, 37, 1, 1, 77, 1, 15)
    assert values(2, 2, 6, 5, 0, 1, 0, 33, 77) == (2, 21, 1, 1, 77, 1, 15)
    assert values(2, 2, -1, 5, 4, 1, 5, 33, 77) == (2, 21, 1, 1, 77, 1, 15)

print("recovered 0x839a8 status-leaf vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("839d8:", "bal 0xf5058"),
        ("839dc:", "remi 10,g0,g0"),
        ("839e0:", "cmpibl 3,g0,0x83a34"),
        ("839fc:", "ble 0x83a34"),
        ("83a34:", "cmpibge 6,g0,0x83a60"),
        ("83a40:", "bbc 1,g4,0x83a60"),
        ("83a50:", "addo 31,6,g1"),
        ("83a58:", "mov 28,g1"),
        ("83a60:", "cmpibge 1,g0,0x83a98"),
        ("83aa8:", "st g14,0x504d8c")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x839a8 status-leaf listing evidence: ok")
