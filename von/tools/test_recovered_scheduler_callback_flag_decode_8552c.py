#!/usr/bin/env python3
"""Check callback flag decoding at i960 0x8552c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_flag_decode_8552c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [("flag_byte", ctypes.c_uint32),
                ("value_g1", ctypes.c_uint32),
                ("value_g2", ctypes.c_uint32),
                ("value_g3", ctypes.c_uint32),
                ("value_g13", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib8552c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_flag_decode_8552c
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan
    result = function(0x8200)
    assert (result.flag_byte, result.value_g1, result.value_g2,
            result.value_g3, result.value_g13) == (0x82, 2, 1, 16, 16)
    result = function(0x8000)
    assert (result.flag_byte, result.value_g1, result.value_g2,
            result.value_g3, result.value_g13) == (0x80, 1, 2, 16, 16)
    result = function(0xff00)
    assert (result.flag_byte, result.value_g1, result.value_g2,
            result.value_g3, result.value_g13) == (0xff, 2, 2, 16, 16)
    assert (function(0xb200).value_g1, function(0xb200).value_g2) == (2, 1)
    assert (function(0x9a00).value_g1, function(0x9a00).value_g2) == (1, 1)

print("recovered 0x8552c callback-flag vectors: ok")

listing = [" ".join(line.split()).lower()
           for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
    ("8552c:", "lda 0xff00,r4"),
    ("85534:", "and g6,r4,g4"),
    ("8553c:", "chkbit 4,g4"),
    ("85548:", "bbc 5,g4,0x85554"),
    ("85554:", "bbs 0,g6,0x8555c"),
    ("85558:", "bbc 1,g6,0x85564"),
    ("85564:", "bbs 2,g6,0x8556c"),
    ("8557c:", "bbs 6,g6,0x85584"),
):
    assert any(address in line and instruction in line for line in listing), (address, instruction)

print("recovered 0x8552c callback-flag listing evidence: ok")
