#!/usr/bin/env python3
"""Check the inverted timing/status sibling at i960 0x78740."""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_timing_status_variant_78740.c"


class Result(ctypes.Structure):
    _fields_ = [("action10", ctypes.c_uint32),
                ("status_write", ctypes.c_uint32),
                ("dispatcher_status_write", ctypes.c_uint32),
                ("valid", ctypes.c_uint32),
                ("threshold_source", ctypes.c_uint32),
                ("current_source", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32),
                ("action10_target", ctypes.c_uint32)]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtiming-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-lm", "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_timing_status_variant_78740
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Result

    result = function(bits(6.0), bits(5.0), 0, 0x2)
    assert (result.action10, result.status_write,
            result.dispatcher_status_write, result.valid,
            result.threshold_source, result.current_source,
            result.status_destination, result.action10_target) == \
        (1, 0, 1, 1, 0x504dd8, 0x504d60, 0x504d84, 0x78408)
    result = function(bits(5.0), bits(5.0), 1, 0x4)
    assert (result.action10, result.status_write,
            result.dispatcher_status_write, result.valid) == (0, 1, 1, 1)
    result = function(bits(4.0), bits(5.0), 8, 0)
    assert (result.action10, result.status_write,
            result.dispatcher_status_write, result.valid) == (0, 1, 0, 1)
    result = function(bits(float("nan")), bits(5.0), 6, 0x2)
    assert (result.action10, result.status_write,
            result.dispatcher_status_write, result.valid) == (0, 0, 1, 0)

print("recovered 0x78740 timing/status vectors: ok")
