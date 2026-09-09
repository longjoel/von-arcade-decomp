#!/usr/bin/env python3
"""Check the recovery/table gate at i960 0x84b10."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_recovery_gate_84b10.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("value_509a70", ctypes.c_int32),
                ("writes_509a70", ctypes.c_uint32),
                ("table_base", ctypes.c_uint32),
                ("continues_to_scan", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84b10.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_recovery_gate_84b10
    function.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_int32]
    function.restype = Plan
    result = function(120, 3, 0, 1, 240)
    assert (result.value_509a70, result.writes_509a70,
            result.table_base, result.continues_to_scan) == (0, 1, 0x5074a0 + 3 * 1088, 1)
    assert function(120, 0, 0, 1, 240).value_509a70 == 0
    assert function(-1, 3, 0x4, 1, 240).continues_to_scan == 0
    assert function(-1, 3, 0, 1, 239).continues_to_scan == 0
    assert function(-1, 3, 0, 0, 240).continues_to_scan == 0

print("recovered 0x84b10 recovery-gate vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("84b4c:", "lda (g4)[g4*16],g4"),
    ("84b50:", "shlo 6,g4,g4"),
    ("84b54:", "lda 0x5074a0(g4),r7"),
    ("84b7c:", "ld 0x503a14,g4"),
    ("84b88:", "cmpible g4,r10,0x84d60"),
    ("84b94:", "cmpibne 0,g4,0x84d60"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x84b10 recovery-gate listing evidence: ok")
