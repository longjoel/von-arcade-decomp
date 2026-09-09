#!/usr/bin/env python3
"""Check the eight-record search at i960 0x84994."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_record_search_84994.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("selected_index", ctypes.c_uint32),
                ("selected_value", ctypes.c_int32),
                ("selected_valid", ctypes.c_uint32),
                ("compared_records", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84994.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_record_search_84994
    function.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
    function.restype = Plan
    records = (ctypes.c_int32 * 8)(10, 20, 30, 40, 50, 60, 70, 80)
    assert (function(25, records).selected_index,
            function(25, records).selected_value,
            function(25, records).selected_valid) == (0, 10, 1)
    assert (function(5, records).selected_valid,
            function(5, records).compared_records) == (0, 8)
    assert (function(99, records).selected_index,
            function(99, records).selected_value,
            function(99, records).compared_records) == (0, 10, 8)
    assert (function(0xffffffff, records).selected_index,
            function(0xffffffff, records).selected_value) == (0, 10)
    signed_records = (ctypes.c_int32 * 8)(-10, -20, -30, 0, 10, 20, 30, 40)
    signed_result = function(-5, signed_records)
    assert (signed_result.selected_index, signed_result.selected_value,
            signed_result.selected_valid) == (2, -30, 1)

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("84994:", "subo 1,0,r8"),
    ("84998:", "cmpibe g7,r8,0x849b0"),
    ("849a4:", "ldos 0x8e(r7)[g4*16],g4"),
    ("849ac:", "cmpible g7,g4,0x849c8"),
    ("849c8:", "addo g5,1,g5"),
    ("849cc:", "cmpibge 7,g5,0x84994"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x84994 record-search vectors: ok")
