#!/usr/bin/env python3
"""Check the counter/dispatch prefix at i960 0x844f4."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_counter_prefix_844f4.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("slot", ctypes.c_uint32),
                ("jumped_to_847b0", ctypes.c_uint32),
                ("writes_509a68", ctypes.c_uint32),
                ("value_509a68", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib844f4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_counter_prefix_844f4
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert (function(0, 12, 59).writes_509a68,
            function(0, 12, 59).value_509a68) == (1, 13)
    assert function(0, 59, 59).value_509a68 == 0
    assert function(0, 40, 41).value_509a68 == 41
    assert function(0, 40, 39).value_509a68 == 0xffffffed
    assert function(0, 0xffffffff, 59).value_509a68 == 0
    assert function(1, 12, 59).jumped_to_847b0 == 1
    assert function(3, 12, 59).writes_509a68 == 0

print("recovered 0x844f4 counter-prefix vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("844f4:", "cmpibne 0,g5,0x847b0"),
        ("844f8:", "ld 0x509a68,g1"),
        ("84500:", "addo 31,28,r13"),
        ("84504:", "addo g1,1,g1"),
        ("84508:", "cmpible g1,r13,0x84514"),
        ("8450c:", "lda 0xffffffc4(g1),g1"),
        ("8451c:", "st g1,0x509a68")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x844f4 counter-prefix listing evidence: ok")
