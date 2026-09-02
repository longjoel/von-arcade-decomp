#!/usr/bin/env python3
"""Test the semantic model of SHARC opcode 0x1f's endpoint distance."""

from __future__ import annotations

import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1f.c"


def f32(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-1f-") as directory:
        library = Path(directory) / "libopcode_1f.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-fPIC", "-shared", str(SOURCE), "-lm", "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        length = lib.recovered_sharc_opcode_1f_length
        length.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        length.restype = ctypes.c_uint32
        seed = lib.recovered_sharc_rsqrts_seed
        seed.argtypes = [ctypes.c_uint32]
        seed.restype = ctypes.c_uint32

        seed_vectors = {
            0x00000000: 0x5f350000,
            0x3f800000: 0x3f7f8000,
            0x40000000: 0x3f350000,
            0x7f800000: 0x1f7f8000,
            0xff800000: 0xffffffff,
            0x7fc00001: 0xffffffff,
        }
        for input_bits, expected_bits in seed_vectors.items():
            actual_bits = seed(input_bits)
            if actual_bits != expected_bits:
                raise SystemExit(
                    f"RSQRTS seed mismatch: 0x{input_bits:08x} -> "
                    f"0x{actual_bits:08x}, expected 0x{expected_bits:08x}"
                )

        vectors = (
            ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), 0xffffffff),
            ((0.0, 0.0), (1.0, 0.0), (0.0, 0.0), 0x3f800000),
            ((3.0, 0.0), (4.0, 0.0), (12.0, 0.0), 0x414fffff),
            ((1.25, 0.75), (-2.75, 0.75), (0.5, -0.5), 0x406b26a8),
            # Live interpreter-backed boundary probes.  The asymmetric
            # nextafter case is deliberately retained: it distinguishes
            # the SHARC truncating refinement from a rounded host sqrtf.
            ((1.0, 0.0), (1.0, 0.0), (0.0, 0.0), 0x3fb504f3),
            ((1.0000001192092896, 0.0), (0.0, 0.0), (0.0, 0.0), 0x3f800001),
            ((1.0, 0.0), (1.0000001192092896, 0.0), (0.0, 0.0), 0x3fb504f4),
            ((16777216.0, 0.0), (16777216.0, 0.0), (16777216.0, 0.0), 0x4bddb3d7),
        )
        for x_pair, y_pair, z_pair, expected in vectors:
            values = (x_pair[0], x_pair[1], y_pair[0], y_pair[1], z_pair[0], z_pair[1])
            inputs = (ctypes.c_uint32 * 6)(*(f32(value) for value in values))
            got_bits = length(inputs)
            if got_bits != expected:
                raise SystemExit(
                    f"opcode 0x1f length mismatch: {values!r} -> "
                    f"0x{got_bits:08x}, expected 0x{expected:08x}"
                )

    print("recovered SHARC opcode-0x1f endpoint-distance vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
