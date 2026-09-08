#!/usr/bin/env python3
"""Exhaustively check the 121-entry 0xf5210 formatter dispatch table."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_formatter_dispatch.c"
FALLBACK = 0x000F5BF4

EXPECTED = [FALLBACK] * 121
EXPECTED[0] = 0x000F51BC
for index, target in {
    32: 0x000F53F4, 35: 0x000F5408, 37: 0x000F5608,
    42: 0x000F5410, 43: 0x000F5474, 45: 0x000F546C,
    46: 0x000F547C, 48: 0x000F5544,
    68: 0x000F561C, 76: 0x000F5588, 79: 0x000F5800,
    85: 0x000F5954, 88: 0x000F59B4, 99: 0x000F55A0,
    100: 0x000F5620, 104: 0x000F5590, 108: 0x000F5598,
    110: 0x000F5790, 111: 0x000F5804, 112: 0x000F5860,
    115: 0x000F58BC, 117: 0x000F5958, 120: 0x000F59BC,
}.items():
    EXPECTED[index] = target
for index in (49, 50, 51, 52, 53, 54, 55, 56, 57):
    EXPECTED[index] = 0x000F554C
for index in (69, 71, 101, 102, 103):
    EXPECTED[index] = 0x000F5688
EXPECTED[105] = 0x000F5620

with tempfile.TemporaryDirectory(prefix="von-formatter-dispatch-") as directory:
    library = Path(directory) / "formatter-dispatch.so"
    subprocess.run(
        [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
        check=True,
    )
    recovered = ctypes.CDLL(str(library))
    target = recovered.recovered_text_formatter_dispatch_target
    target.argtypes = [ctypes.c_uint32]
    target.restype = ctypes.c_uint32
    assert [target(index) for index in range(121)] == EXPECTED
    assert target(121) == FALLBACK
    assert target(0xFFFFFFFF) == FALLBACK

print("recovered formatter dispatch table: ok")
