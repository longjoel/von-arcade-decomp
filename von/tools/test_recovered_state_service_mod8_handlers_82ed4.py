#!/usr/bin/env python3
"""Check modulo-8 service handlers at i960 0x82ed4 and 0x82f10."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_mod8_handlers_82ed4.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-mod8.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_mod8_handler
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan

    assert function(0x82ED4, 2, 3).downstream_value == 3
    assert function(0x82ED4, -1, 3).downstream_value == 3
    assert function(0x82ED4, -1, 2).route == 0
    assert function(0x82ED4, 1, 2).route == 0
    assert function(0x82ED4, 6, 0).downstream_value == 4
    assert function(0x82ED4, 5, 3).route == 0
    assert function(0x82F10, 4, 3).downstream_value == 3
    assert function(0x82F10, 5, 3).downstream_value == 3
    assert function(0x82F10, 7, 3).downstream_value == 6
    assert function(0x82F10, 7, 2).route == 0
    assert function(0x82F10, 0, 3).route == 0

print("recovered 0x82ed4/0x82f10 modulo-8 vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("82ed8:", "cmpi g0,0"),
        ("82ee8:", "notand g5,7,g4"),
        ("82ef0:", "cmpibge 3,g5,0x82f04"),
        ("82f14:", "cmpi g0,0"),
        ("82f28:", "subo g4,g0,g5"),
        ("82f2c:", "cmpibne 4,g5,0x82f38"),
        ("82f4c:", "cmpibne 7,g5,0x82f60"),
        ("82fac:", "cmpobl 7,g5,0x830a0")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x82ed4/0x82f10 listing evidence: ok")
