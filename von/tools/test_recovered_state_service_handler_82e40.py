#!/usr/bin/env python3
"""Check the service handler at i960 0x82e40."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_handler_82e40.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-handler.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_handler_82e40
    function.argtypes = [ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan

    assert function(0, 3).route == 0
    assert function(-1, 3).route == 0
    assert function(3, 3).route == 0
    assert (function(4, 3).route, function(4, 3).downstream_value) == (1, 2)
    assert (function(4, 2).route, function(4, 2).downstream_value) == (2, 5)
    assert function(4, 0xffffffff).downstream_value == 5

print("recovered 0x82e40 service-handler vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("82e44:", "remi 5,g0,g5"),
        ("82e48:", "cmpibne 4,g5,0x82fac"),
        ("82e54:", "mov 5,g5"),
        ("82e5c:", "mov 2,g5"),
        ("82e60:", "b 0x82fac")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x82e40 service-handler listing evidence: ok")
