#!/usr/bin/env python3
"""Check recovery packet-row layout at i960 0x84c98."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_row_84c98.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("destination_offset", ctypes.c_uint32),
                ("field_0", ctypes.c_int32), ("field_2", ctypes.c_int32),
                ("field_4", ctypes.c_int32), ("field_6", ctypes.c_int32),
                ("field_8", ctypes.c_int32), ("field_a", ctypes.c_int32),
                ("field_84", ctypes.c_int32),
                ("source_start", ctypes.c_uint32),
                ("recovery_record_field_86", ctypes.c_uint32),
                ("field_c", ctypes.c_uint16 * 60)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84c98.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_recovery_row_84c98
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32,
                         ctypes.POINTER(ctypes.c_uint16)]
    function.restype = Plan
    source = (ctypes.c_uint16 * 60)(*range(60))
    result = function(0x5074a0, 2, 1, 2, 3, 4, 5, 6, 5, 59, source)
    assert (result.destination_offset, result.field_0, result.field_a,
            result.field_84, result.source_start,
            result.recovery_record_field_86) == (0x5075c0, 1, 6, 220, 54, 100)
    assert (result.field_c[0], result.field_c[59]) == (0, 59)
    result = function(0, 0, 0, 0, 0, 0, 0, 0, 0, 10, source)
    assert (result.source_start, result.field_c[0], result.field_c[49]) == (10, 0, 49)
    signed = function(0x5074a0, 0, -1, -2, -3, -4, -5, -6, 0, 0, source)
    assert (signed.field_0, signed.field_a, signed.field_84) == (-1, -6, 240)

print("recovered 0x84c98 recovery-row vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("84c98:", "shlo 4,g4,g4"),
    ("84c9c:", "ldos 0x5096a0(g4),g5"),
    ("84cc4:", "ldos 0xa(g4)[r4],g2"),
    ("84cdc:", "stos g5,(g3)"),
    ("84d00:", "addo 31,28,g7"),
    ("84d08:", "cmpi g6,g7"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x84c98 recovery-row listing evidence: ok")
