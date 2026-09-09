#!/usr/bin/env python3
"""Check callback object scaling at i960 0x858f0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_object_scale_858f0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("object_48", ctypes.c_int32),
                ("object_4a", ctypes.c_int32),
                ("object_190", ctypes.c_int32),
                ("related_state", ctypes.c_int32),
                ("related_source", ctypes.c_int32),
                ("value_503a78", ctypes.c_uint32),
                ("caller_g14", ctypes.c_uint32),
                ("normalized_48", ctypes.c_int32),
                ("normalized_4a", ctypes.c_int32),
                ("quotient", ctypes.c_int32),
                ("value_509b8c", ctypes.c_int32),
                ("value_509b90", ctypes.c_int32),
                ("scaled", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib858f0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_object_scale_858f0
    function.argtypes = [ctypes.c_int16, ctypes.c_int16, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(-2, 6, 0, 11, 350, 999, 0xffffffff, 0x1234)
    assert (result.related_source, result.normalized_48,
            result.quotient, result.value_509b8c,
            result.value_509b90, result.scaled) == (63, -2, 3, -2, 18, 1)
    result = function(4, 7, 0, 14, 0, 450, 0xffffffff, 0x1234)
    assert (result.related_source, result.quotient, result.value_509b90,
            result.scaled) == (64, 4, 28, 1)
    result = function(4, 7, 1, 11, 350, 450, 0xffffffff, 0x1234)
    assert (result.related_source, result.value_509b90, result.scaled) == (63, 21, 1)
    assert function(4, 7, 0, 3, 350, 450, 0xffffffff, 0x1234).value_509b90 == 7
    gated = function(4, 7, 0, 11, 350, 450, 0, 0xdeadbeef)
    assert (gated.value_509b90, gated.scaled) == (ctypes.c_int32(0xdeadbeef).value, 0)

print("recovered 0x858f0 object-scale vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("858f0:", "ldos 0x48(g0),g4"),
    ("858f8:", "ldos 0x190(g0),g6"),
    ("858fc:", "ld 0x503a78,g7"),
    ("85928:", "addo g7,1,r4"),
    ("8592c:", "be 0x8593c"),
    ("85930:", "st g14,0x509b90"),
    ("85960:", "lda 0x64,g1"),
    ("85968:", "mulo g5,g4,g4"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x858f0 object-scale listing evidence: ok")
