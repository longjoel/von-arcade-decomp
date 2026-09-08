#!/usr/bin/env python3
"""Check the host packet plan at i960 0x78890."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_packet_78890.c"


class Plan(ctypes.Structure):
    _fields_ = [("selector", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("transition", ctypes.c_uint32),
                ("action", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 15)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_packet_78890
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None
    sibling = api.recovered_state_geometry_packet_78a30
    sibling.argtypes = function.argtypes
    sibling.restype = None

    result = Plan()
    function(0x1234, 0x3f800000, 0xff00, 100, 200, 40, 80,
             10, 20, 0, 0, ctypes.byref(result))
    assert (result.selector, result.status, result.transition, result.action) == (
        0x1234, 0, 0, 5)
    assert list(result.packet) == [
        29, 0x4f00, 0x3f800000,
        30, 0x4f00, 0x3f800000,
        10, 0xffffff74, 50,
        62, 90, 40, 220, 80, 0x3f800000,
    ]

    function(0x1234, 7, 0, 0, 0, 0, 0, 0, 0, 0x20, 1,
             ctypes.byref(result))
    assert (result.status, result.transition, result.action) == (1, 6, 20)

    sibling(0x4321, 0x3f000000, 0, 100, 200, 40, 80,
            10, 20, 0, 0, ctypes.byref(result))
    assert result.packet[1] == 0xb000
    assert result.packet[4] == 0xb000
    assert result.packet[2] == result.packet[5] == result.packet[14] == 0x3f000000

print("recovered 0x78890 geometry-packet vectors: ok")
