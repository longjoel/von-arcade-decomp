#!/usr/bin/env python3
"""Check the ratio/status prefix at i960 0x83348."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_ratio_prefix_83310.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("value_504e1c", ctypes.c_uint32),
                ("mode_504e30", ctypes.c_uint32),
                ("mode_changed", ctypes.c_uint32),
                ("random_table_dispatch", ctypes.c_uint32),
                ("random_table_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-ratio-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_ratio_prefix_83310
    function.argtypes = [ctypes.c_double, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_int32]
    function.restype = Plan

    result = function(0.9, 0x4, 5, 2)
    assert (result.value_504e1c, result.mode_504e30,
            result.mode_changed, result.random_table_dispatch) == (1, 4, 0, 0)
    result = function(0.95, 0x4, 4, 2)
    assert (result.mode_504e30, result.mode_changed,
            result.random_table_dispatch) == (0, 1, 0)
    result = function(0.95, 0x4, 5, 2)
    assert (result.mode_504e30, result.random_table_target) == (0, 0x833f8)
    assert function(0.95, 0x0, 5, 4).random_table_target == 0x83418
    assert function(0.95, 0x0, 5, -1).random_table_dispatch == 0
    assert function(float("nan"), 0x4, 5, 0).mode_changed == 1

print("recovered 0x83310 ratio-prefix vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("83360:", "divr g5,g4,g4"),
        ("83378:", "cmprl fp0,g2"),
        ("83394:", "bbc 2,g4,0x833a4"),
        ("833b4:", "remi 5,g0,g0"),
        ("833b8:", "cmpobl 4,g0,0x83428"),
        ("833bc:", "ld 0x833c8[g0*4],g4")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x83310 ratio-prefix listing evidence: ok")
