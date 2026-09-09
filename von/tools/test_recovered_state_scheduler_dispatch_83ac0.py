#!/usr/bin/env python3
"""Check the state/timing dispatcher at i960 0x83ac0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_dispatch_83ac0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32), ("terminal", ctypes.c_uint32),
                ("write_504d80", ctypes.c_uint32), ("value_504d80", ctypes.c_uint32),
                ("write_504d98", ctypes.c_uint32), ("value_504d98", ctypes.c_uint32),
                ("write_504e1c", ctypes.c_uint32), ("value_504d8c", ctypes.c_uint32),
                ("value_504d90", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib83ac0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_dispatch_83ac0
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert function(149, 19, 5, 0, 100, 0, 0, 77).value_504d98 == 77
    assert function(150, 19, 5, 99, 100, 0, 0, 77).route == 1
    assert function(150, 19, 5, -1, -2, 0, 0, 77).value_504d80 == 18
    assert function(150, 0, 5, 100, 100, 2, 0, 77).route == 4
    assert function(150, 0, 5, 100, 100, 3, 0, 77).value_504d80 == 28
    assert function(150, 0, 5, 100, 100, 4, 0, 77).value_504d80 == 26
    assert function(150, 0, 5, 100, 100, 5, 0, 77).value_504d80 == 21
    assert function(150, 0, 5, 100, 100, -1, 0, 77).route == 9
    assert function(150, 0, 4, 100, 100, 4, 0x2, 77).value_504d80 == 26
    assert function(150, 0, 4, 100, 100, -1, 0x4, 77).route == 3
    assert function(150, 0, 4, 100, 100, 4, 0x4, 77).value_504d80 == 28
    assert function(150, 0, 4, 100, 100, 5, 0x4, 77).value_504d80 == 28
    result = function(150, 0, 4, 100, 100, 4, 0, 77)
    assert (result.value_504d80, result.value_504d8c, result.value_504d90) == (21, 77, 15)

print("recovered 0x83ac0 scheduler-dispatch vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83c48:", "remi 7,g0,g0"),
        ("83c4c:", "cmpibge 4,g0,0x83c5c"),
        ("83c54:", "call 0x79d60"),
        ("83c60:", "ld 0x504e30,g4"),
        ("83c68:", "bbc 1,g4,0x83c74"),
        ("83c74:", "cmpibge 0,g0,0x83c94"),
        ("83c84:", "mov 28,g3"),
        ("83c94:", "mov 21,g2"),
        ("83ca0:", "mov 15,g3")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83ac0 scheduler-dispatch listing evidence: ok")
