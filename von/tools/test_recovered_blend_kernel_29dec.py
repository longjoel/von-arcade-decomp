#!/usr/bin/env python3
"""Validate the 0x29d50 per-texel blend kernel against integer oracles.

Provenance: synthetic (vonj-maincpu.lst 0x29dec-0x29e1c canonical
instance); no trace-derived vectors. Proves the code matches the
reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile

MASK = 0x00FF00FF
M32 = 0x100000000


def oracle_mul(pixel, factor):
    return (((factor * (pixel & MASK)) % M32) >> 8) % M32


def oracle_fade(pixel, factor):
    masked = pixel & MASK
    diff = (masked - MASK) % M32
    return (masked + (((factor * diff) % M32) >> 8)) % M32


VECTORS = [
    0x00000000, 0x00FFFFFF, 0x00FF00FF, 0x0000AB00, 0x00123456,
    0x12345678, 0xFF00FF00, 0xFFFFFFFF, 0x00808080, 0x01010101,
]
FACTORS = [0x0, 0x1, 0x2, 0x7F, 0xFF, 0x100, 0x101, 0x200, 0xDEAD]

with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "blend-kernel.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_blend_kernel_29dec.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    mul_fn = lib.recovered_blend_kernel_mul
    fade_fn = lib.recovered_blend_kernel_fade
    mul_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    mul_fn.restype = ctypes.c_uint32
    fade_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    fade_fn.restype = ctypes.c_uint32

    count = 0
    for pixel in VECTORS:
        for factor in FACTORS:
            assert mul_fn(pixel, factor) == oracle_mul(pixel, factor), \
                (hex(pixel), hex(factor))
            assert fade_fn(pixel, factor) == oracle_fade(pixel, factor), \
                (hex(pixel), hex(factor))
            count += 2

    # Spot checks with hand-derived values.
    assert mul_fn(0x00FFFFFF, 0x100) == 0x00FF00FF
    assert fade_fn(0x00FFFFFF, 0x100) == 0x00FF00FF
    assert mul_fn(0x12345678, 0x100) == 0x00340078
    assert fade_fn(0x00000000, 0x100) == 0x0000FF01
    assert mul_fn(0x00FF00FF, 0x200) == 0x00FE01FE
    assert fade_fn(0x00FF00FF, 0x0) == 0x00FF00FF

print(f"PASS: 0x29d50 blend kernel ({count} oracle vectors)")
