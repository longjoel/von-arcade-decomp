#!/usr/bin/env python3
"""Test the instruction-locked table and common exits of i960 0x79d60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_secondary_dispatch_79d60.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))

    target = lib.recovered_secondary_dispatch_target_79d60
    target.argtypes = [ctypes.c_uint32]
    target.restype = ctypes.c_uint32
    expected_targets = [
        0x00079DB4, 0x00079E10, 0x00079E8C, 0x00079EF4,
        0x00079F5C, 0x00079FF4, 0x0007A098, 0x0007A150,
        0x0007A204, 0x0007A214,
    ]
    for state, expected in enumerate(expected_targets):
        assert target(state) == expected
    assert target(10) == 0xFFFFFFFF
    assert target(0xFFFFFFFF) == 0xFFFFFFFF

    transition = lib.recovered_secondary_shared_transition_79d60
    transition.argtypes = [ctypes.c_uint32]
    transition.restype = ctypes.c_uint32
    assert transition(0x0007A1E4) == 15
    assert transition(0x0007A11C) == 14
    assert transition(0x0007A1F4) == 13
    assert transition(0x0007A204) == 13
    for address in (0, 0x00079DB4, 0x0007A214, 0xFFFFFFFF):
        assert transition(address) == 0xFFFFFFFF

    table_address = lib.recovered_secondary_dispatch_table_address_79d60
    table_address.restype = ctypes.c_uint32
    assert table_address() == 0x00079D8C

print("recovered secondary-dispatch routing: ok")
