#!/usr/bin/env python3
"""Check the post-status scheduler table at i960 0x82b4c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_dispatch_82b4c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_dispatch_82b4c
    function.argtypes = [ctypes.c_uint32] * 3
    function.restype = Plan

    expected = [
        0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82C54,
        0x82C08, 0x82C54, 0x82C18, 0x82C28, 0x82C38, 0x82C60,
        0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82D68, 0x82D68,
        0x82D68, 0x82C6C, 0x82CC0, 0x82CC8, 0x82CD0, 0x82CD8,
        0x82CE0, 0x82CC8, 0x82CB0, 0x82CE8, 0x82D04, 0x82D68,
        0x82D68, 0x82D68, 0x82D18, 0x82CC8, 0x82CC8, 0x82CC0,
        0x82CC0, 0x82CB0, 0x82D34, 0x82D48, 0x82D68, 0x82D68,
        0x82D68, 0x82D5C,
    ]
    for status, target in enumerate(expected):
        result = function(status, 43, 1)
        assert (result.dispatched, result.target) == (1, target)
    assert function(0, 43, 0).dispatched == 0
    assert function(43, 42, 1).dispatched == 0
    assert function(44, 43, 1).dispatched == 0

print("recovered 0x82b4c scheduler-dispatch vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("82b38:", "ldl 0x504d80,g4"),
        ("82b40:", "cmpibne 1,g5,0x82da4"),
        ("82b48:", "cmpobg g4,g13,0x82d68"),
        ("82b4c:", "ld 0x82b58[g4*4],g4"),
        ("82b54:", "bx (g4)")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x82b4c scheduler-dispatch listing evidence: ok")
