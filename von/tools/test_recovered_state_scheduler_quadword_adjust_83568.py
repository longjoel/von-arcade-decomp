#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_quadword_adjust_83568.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("remainder_8", "value_504d80", "value_504d84",
                 "write_quadword", "write_504d90", "value_504d90")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-adjust.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_quadword_adjust_83568
    build.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32]
    build.restype = Plan

    def values(*args):
        result = build(*args)
        return tuple(getattr(result, name) for name, _ in Plan._fields_)

    assert values(0, 100, 0xabcdef01, 0) == (0, 102, 0xabcdef01, 1, 1, 15)
    assert values(0, 100, 7, 4) == (0, 101, 7, 1, 1, 15)
    assert values(3, 100, 7, 4) == (3, 102, 7, 1, 1, 15)
    assert values(7, 100, 7, 4) == (7, 102, 7, 1, 1, 15)
    assert values(1, 100, 7, 2) == (1, 107, 7, 1, 1, 15)
    assert values(1, 100, 7, 0) == (1, 102, 7, 1, 1, 15)
    assert values(2, 100, 7, 2) == (2, 107, 7, 1, 1, 15)
    assert values(2, 100, 7, 0) == (2, 102, 7, 1, 1, 15)
    assert values(-1, 100, 7, 0) == (0xffffffff, 102, 7, 1, 1, 15)
    assert values(-1, 100, 7, 2) == (0xffffffff, 102, 7, 1, 1, 15)
    assert values(-1, 100, 7, 4) == (0xffffffff, 101, 7, 1, 1, 15)
    assert values(8, 0xffffffff, 9, 0) == (0, 1, 9, 1, 1, 15)

print("recovered 0x83568 quadword-adjust vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83578:", "addo g0,7,g5"),
        ("83580:", "subo g4,g0,g5"),
        ("83598:", "bge 0x835b0"),
        ("835a4:", "bbc 2,g4,0x835b0"),
        ("835bc:", "bbc 1,g4,0x835c8"),
        ("835d4:", "stq g0,(g6)"),
        ("835d8:", "st g13,0x504d90")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83568 quadword-adjust listing evidence: ok")
