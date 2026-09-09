#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_nonstate_prefix_83de4.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "status", "random_calls")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-nonstate-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_nonstate_prefix_83de4
    build.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(-2, -1, 17, 30) == (0, 30, 0)
    assert values(-1, -2, 17, 30) == (1, 18, 0)
    assert values(1, 0, 1, 30) == (5, 0, 1)
    assert values(1, 0, 2, 30) == (5, 0, 1)
    assert values(1, 0, 11, 30) == (5, 0, 1)
    assert values(1, 0, 12, 30) == (3, 25, 1)
    assert values(1, 0, 13, 30) == (4, 34, 1)
    assert values(1, 0, 14, 30) == (2, 30, 1)
    assert values(1, 0, -1, 30) == (5, 0, 1)
    assert values(1, 0, -2, 30) == (5, 0, 1)

print("recovered 0x83de4 non-state-prefix vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83de4:", "bal 0xf5058"),
        ("83e14:", "remi 18,g0,g0"),
        ("83e18:", "bg 0x83f18"),
        ("83e40:", "cmpibge 11,g0,0x83e74"),
        ("83e44:", "remi 3,g0,g4"),
        ("83e48:", "cmpibe 2,g4,0x83f18"),
        ("83e5c:", "mov 25,g2"),
        ("83e64:", "addo 31,3,g3")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83de4 non-state-prefix listing evidence: ok")
