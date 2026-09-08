#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Pair(ctypes.Structure):
    _fields_ = [
        ("left_request_0", ctypes.c_uint32),
        ("left_request_1", ctypes.c_uint32),
        ("right_request_0", ctypes.c_uint32),
        ("right_request_1", ctypes.c_uint32),
        ("left_delta_low", ctypes.c_uint16),
        ("right_delta_low", ctypes.c_uint16),
        ("left_band", ctypes.c_uint32),
        ("right_band", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    so = pathlib.Path(directory) / "pair.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
        "-o", str(so),
        str(ROOT / "von/i960/recovered_geometry_object_band_pair_76590.c"),
    ], check=True)
    library = ctypes.CDLL(str(so))
    function = library.recovered_geometry_object_band_pair_76590
    function.argtypes = [
        ctypes.c_uint16, ctypes.c_uint16,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Pair),
    ]
    function.restype = None

    result = Pair()
    function(0x4000, 0x8000, 100, 200, 40, 80, 0x3c00, 0x7000,
             ctypes.byref(result))
    assert (result.left_request_0, result.left_request_1,
            result.right_request_0, result.right_request_1) == (
                0xffffff88, 60, 120, 0xffffffc4)
    assert (result.left_delta_low, result.right_delta_low) == (0x0400, 0x1000)
    assert (result.left_band, result.right_band) == (1, 1)

    # The classifier consumes only the low 16 bits, including at its signed
    # boundaries.  These values exercise the positive/negative transitions.
    function(0x0000, 0x0000, 0, 0, 0, 0, 0xfffffc73, 0x00005000,
             ctypes.byref(result))
    assert result.left_band == 0 and result.right_band == 6

print("PASS: original 0x76590 cross-object request/band pair")
