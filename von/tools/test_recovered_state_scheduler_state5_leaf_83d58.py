#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_state5_leaf_83d58.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("random_calls", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-state5.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_state5_leaf_83d58
    build.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(-2, -1, 0, 0, 0, 30) == (0, 30, 0)
    assert values(-1, -2, 0, 0, 0, 30) == (1, 18, 0)
    assert values(1, 0, 2, 0, 0, 30) == (5, 33, 1)
    assert values(1, 0, 3, 1, 0x40340000, 30) == (5, 33, 1)
    assert values(1, 0, 4, 1, 0x40340000, 30) == (4, 27, 1)
    assert values(1, 0, 4, 1, 1, 30) == (2, 19, 1)
    assert values(1, 0, 5, 0, 0, 30) == (2, 19, 1)
    assert values(1, 0, 6, 0, 0, 30) == (3, 25, 1)
    assert values(1, 0, -1, 0, 0, 30) == (5, 33, 1)
    assert values(1, 0, -1, 1, 0x40340000, 30) == (5, 33, 1)

print("recovered 0x83d58 state5-leaf vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83d7c:", "bal 0xf5058"),
        ("83d80:", "remi 10,g0,g0"),
        ("83d84:", "cmpibge 5,g0,0x83d98"),
        ("83d98:", "cmpibge 3,g0,0x83dd4"),
        ("83da4:", "cmpibne 1,g4,0x83dc4"),
        ("83da8:", "ldl 0x504e20,g4"),
        ("83db0:", "cmpibne g4,g5,0x83dc4"),
        ("83db4:", "mov 27,g3"),
        ("83dc4:", "mov 19,g2"),
        ("83dd4:", "addo 31,2,g3")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83d58 state5-leaf listing evidence: ok")
