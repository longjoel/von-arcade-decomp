#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_status_path_83148.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "write_504e1c", "value_504e1c", "write_504d80",
        "value_504d80", "write_504d8c", "value_504d8c", "write_504d90",
        "value_504d90", "random_calls")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "scheduler-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_scheduler_status_path_83148
    build.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                      ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32,
                      ctypes.c_uint32]
    build.restype = Plan

    def result(*args):
        return build(*args)

    assert result(5, 1, 2, 0, 0, 0, 0, 0, 30, 99).value_504d80 == 30
    assert result(5, 1, 2, 0, 0, 0, 0, 0, 30, 99).random_calls == 0
    assert result(5, -1, -2, 0, 0, 0, 0, 0, 30, 99).value_504d80 == 18
    assert result(5, 2, 2, 0, 0, 0, 0, 0, 30, 99).value_504d80 == 19
    assert result(5, 2, 2, 3, 0, 0, 1, 2, 30, 99).value_504d80 == 27
    assert result(5, 2, 2, 4, 0, 0, 1, 3, 30, 99).value_504d80 == 33

    tail = result(4, 2, 2, 13, 0, 0, 0, 0, 30, 99)
    assert (tail.value_504d80, tail.value_504d8c, tail.value_504d90,
            tail.write_504d8c, tail.write_504d90) == (33, 99, 15, 1, 1)
    assert result(4, 2, 2, 2, 0, 0, 0, 0, 30, 99).value_504d80 == 33
    assert result(4, 2, 2, 14, 0, 0, 0, 0, 30, 99).value_504d80 == 33
    assert result(4, 2, 2, 15, 0, 0, 0, 0, 30, 99).value_504d80 == 34
    assert result(4, 2, 2, 15, 120, 0, 0, 3, 30, 99).value_504d80 == 34
    assert result(4, 2, 2, 16, 120, 0, 0, 0, 30, 99).value_504d80 == 33
    assert result(4, 2, 2, 14, 121, 0, 0, 0, 30, 99).value_504d80 == 30
    assert result(4, 1, 2, 0, 0, 0, 0, 0, 26, 99).value_504d80 == 26
    assert result(4, 1, 2, 0, 0, 0, 0, 0, 26, 99).value_504d8c == 99

print("recovered 0x83148 scheduler-status vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("8322c:", "remi 17,g0,g0"),
        ("83254:", "cmpibge 13,g0,0x8329c"),
        ("83260:", "shlo 3,15,g2"),
        ("83264:", "cmpible g4,g2,0x8327c"),
        ("8327c:", "shro 31,g0,g4"),
        ("8329c:", "remi 6,g0,g4"),
        ("832a0:", "cmpibge 3,g4,0x832e0"),
        ("832ac:", "bbc 1,g4,0x832e0"),
        ("832ec:", "mov 15,g2")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83148 scheduler-status listing evidence: ok")
