#!/usr/bin/env python3
"""Check the scan prefix and common gate at i960 0x7d1f0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_byte_pair_scan_7d1f0.c"


class Plan(ctypes.Structure):
    _fields_ = [("first_match", ctypes.c_uint32),
                ("second_match", ctypes.c_uint32),
                ("third_scan_done", ctypes.c_uint32),
                ("dispatch_allowed", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("handler_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-byte-scan.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_byte_pair_scan_7d1f0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint8,
                         ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t] + [
                             ctypes.c_uint32] * 8
    function.restype = Plan

    third = (ctypes.c_uint8 * 3)(1, 2, 3)
    base_args = [1, 20, 0, 200, 1, 2, 4, 0]
    result = function(10, 7, 8, third, 3, *base_args)
    assert (result.first_match, result.second_match,
            result.third_scan_done, result.dispatch_allowed,
            result.selector) == (1, 1, 1, 0, 0)

    result = function(10, 7, 20, third, 3, *base_args[:-1], 3)
    assert (result.first_match, result.second_match,
            result.dispatch_allowed) == (1, 0, 1)

    result = function(10, 7, 20, third, 3, 1, 20, 0xffffffff,
                      200, 1, 2, 4, 3)
    assert result.dispatch_allowed == 1
    assert result.handler_target == 0x7D4E8

    for bad_index, bad_value in ((0, 0), (1, 13), (2, 1), (3, 100),
                                 (6, 10), (7, 10)):
        args = list(base_args)
        args[bad_index] = bad_value
        result = function(10, 7, 20, third, 3, *args)
        assert result.dispatch_allowed == 0, (bad_index, bad_value)

    result = function(10, 7, 20, third, 3, 1, 20, 1, 200, 1, 2, 4, 10)
    assert result.dispatch_allowed == 0

print("recovered 0x7d1f0 byte-pair scan vectors: ok")
