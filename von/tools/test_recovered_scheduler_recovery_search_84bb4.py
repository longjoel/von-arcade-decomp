#!/usr/bin/env python3
"""Check the recovery-record search at i960 0x84bb4."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_search_84bb4.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("selected_index", ctypes.c_uint32),
                ("selected_value", ctypes.c_int32),
                ("selected_valid", ctypes.c_uint32),
                ("compared_records", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84bb4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_recovery_search_84bb4
    function.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
    function.restype = Plan
    records = (ctypes.c_int32 * 8)(10, 20, 30, 40, 50, 60, 70, 80)
    assert (function(25, records).selected_index,
            function(25, records).selected_value) == (0, 10)
    assert function(5, records).selected_valid == 0
    assert (function(99, records).selected_index,
            function(99, records).selected_value) == (0, 10)
    signed_records = (ctypes.c_int32 * 8)(-10, -20, -30, 0, 10, 20, 30, 40)
    signed_result = function(-5, signed_records)
    assert (signed_result.selected_index, signed_result.selected_value,
            signed_result.selected_valid) == (2, -30, 1)

print("recovered 0x84bb4 recovery-search vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("84bb4:", "subo 1,0,r10"),
    ("84bb8:", "cmpibe g6,r10,0x84bd0"),
    ("84bc4:", "ldos 0x86(r7)[g4*8],g4"),
    ("84bcc:", "cmpible g6,g4,0x84be8"),
    ("84be8:", "addo g5,1,g5"),
    ("84bec:", "cmpibge 7,g5,0x84bb4"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x84bb4 recovery-search listing evidence: ok")
