#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_nonstate_remainder6_83e74.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("route", "status", "random_calls", "write_status")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-nonstate-rem6.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_nonstate_remainder6_83e74
    build.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(2, 0, 0, 0, 1, 0, 30) == (2, 30, 0, 0)
    assert values(2, 0, 0, 0, 0, 0, 30) == (0, 0, 0, 0)
    assert values(3, 0, 0, 0, 0, 0, 30) == (0, 0, 0, 0)
    assert values(3, 2, 1, 0x40340000, 0, 0, 30) == (1, 27, 0, 1)
    assert values(3, 2, 0, 0, 0, 1, 30) == (4, 40, 1, 1)
    assert values(3, 2, 0, 0, 0, 2, 30) == (5, 19, 1, 1)
    assert values(3, 2, 0, 0, 0, 0, 30) == (4, 40, 1, 1)
    assert values(3, 2, 0, 0, 0, -1, 30) == (0, 0, 1, 0)

print("recovered 0x83e74 non-state-rem6 vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83e74:", "remi 6,g0,g4"),
        ("83e78:", "cmpibge 2,g4,0x83ef0"),
        ("83e84:", "bbc 1,g4,0x83ef0"),
        ("83e90:", "cmpibne 1,g4,0x83ea8"),
        ("83e9c:", "cmpibne g4,g5,0x83ea8"),
        ("83ea0:", "mov 27,g2"),
        ("83ea8:", "bal 0xf5058"),
        ("83eac:", "remi 3,g0,g0"),
        ("83ed8:", "addo 31,9,g2"),
        ("83ee0:", "mov 19,g3")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83e74 non-state-rem6 listing evidence: ok")
