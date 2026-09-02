#!/usr/bin/env python3
"""Test exact residual distance-packet operand provenance at i960 0xdf2f4."""

import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_residual_operand_flow_df2f4.c"


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


with tempfile.TemporaryDirectory(prefix="von-residual-flow-") as directory:
    library = Path(directory) / "residual-flow.so"
    subprocess.run(["cc", "-std=c99", "-O2", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_residual_distance_requests
    build.argtypes = [
        ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
        ctypes.c_float, ctypes.c_float, ctypes.POINTER(ctypes.c_uint32),
    ]
    build.restype = ctypes.c_uint32

    packets = (ctypes.c_uint32 * 14)()
    assert build(2.0, 3.0, 0.25, -0.5, 7.0, -8.0, packets) == 14
    assert list(packets) == [
        31, bits(0.5), 0, 0, 0, bits(-3.0), 0,
        31, bits(7.0), 0, 0, 0, bits(-8.0), 0,
    ]

print("recovered geometry residual operand flow: ok")
