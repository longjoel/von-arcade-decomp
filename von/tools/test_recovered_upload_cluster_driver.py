#!/usr/bin/env python3
"""Drive the executable upload-cluster driver against array windows.

Compiles von/i960/recovered_upload_cluster.c with the proven kernel
unit and executes full 768-store runs, checking every destination word
against independent integer oracles laid out with the exact strided
cadence from the listing.
"""
import ctypes
import pathlib
import subprocess
import tempfile

MASK = 0x00FF00FF
M32 = 0x100000000
WORDS = 8192
INNER = 32
PASSES = 8
STRIDE = 0x180 // 4


def oracle_mul(pixel, factor):
    return (((factor * (pixel & MASK)) % M32) >> 8) % M32


def oracle_fade(pixel, factor):
    masked = pixel & MASK
    diff = (masked - MASK) % M32
    return (masked + (((factor * diff) % M32) >> 8)) % M32


def pattern(index):
    return (0xA5000000 | ((index * 0x010203) & 0xFFFFFF)) % M32


I960 = pathlib.Path(__file__).parents[1] / "i960"

with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "upload-cluster.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(I960 / "recovered_upload_cluster.c"),
                    str(I960 / "recovered_blend_kernel_29dec.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    svc = lib.recovered_upload_cluster_service
    svc.argtypes = ([ctypes.POINTER(ctypes.c_uint32)] * 3 +
                    [ctypes.POINTER(ctypes.c_uint32)] * 6)
    svc.restype = ctypes.c_uint32

    def make_windows():
        srcs = [(ctypes.c_uint32 * WORDS)() for _ in range(3)]
        dsts = [(ctypes.c_uint32 * WORDS)() for _ in range(3)]
        for w in srcs:
            for i in range(WORDS):
                w[i] = pattern(i)
        return srcs, dsts

    def slots(fade, counter, mode):
        return ((ctypes.c_uint32 * 1)(fade),
                (ctypes.c_uint32 * 1)(counter),
                (ctypes.c_uint32 * 1)(mode))

    # Guard: sub-3 counters perform no stores and bump nothing.
    srcs, dsts = make_windows()
    f, c, m = slots(0x80, 2, 0)
    assert svc(f, c, m, srcs[0], dsts[0], srcs[1], dsts[1],
               srcs[2], dsts[2]) == 0
    assert c[0] == 2
    assert all(w[i] == 0 for w in dsts for i in range(WORDS))

    # Direct run: fade 0x80, bank 4, every dst word verified.
    srcs, dsts = make_windows()
    f, c, m = slots(0x80, 4, 0)
    assert svc(f, c, m, srcs[0], dsts[0], srcs[1], dsts[1],
               srcs[2], dsts[2]) == 768
    assert c[0] == 5
    seen = [0, 0, 0]
    for p in range(PASSES):
        for i in range(INNER):
            idx = (4 << 10) + p * (INNER + STRIDE) + i
            for plane in range(3):
                assert dsts[plane][idx] == oracle_mul(pattern(idx), 0x180), \
                    (p, i, plane)
                seen[plane] += 1
    assert seen == [256, 256, 256]
    # Untouched regions stay zero.
    assert dsts[0][0] == 0 and dsts[0][WORDS - 1] == 0

    # Direct fade form: fade 0 is an identity run.
    srcs, dsts = make_windows()
    f, c, m = slots(0, 4, 0)
    assert svc(f, c, m, srcs[0], dsts[0], srcs[1], dsts[1],
               srcs[2], dsts[2]) == 768
    for p in range(PASSES):
        for i in range(INNER):
            idx = (4 << 10) + p * (INNER + STRIDE) + i
            assert dsts[1][idx] == pattern(idx) & MASK, (p, i)

    # Blend run: mode 0b101 over bank 5, all planes verified.
    srcs, dsts = make_windows()
    f, c, m = slots(0x80, 5, 0b101)
    assert svc(f, c, m, srcs[0], dsts[0], srcs[1], dsts[1],
               srcs[2], dsts[2]) == 768
    assert c[0] == 6
    bank = 5 << 10
    for p in range(PASSES):
        for i in range(INNER):
            idx01 = bank + p * (INNER + STRIDE) + i
            idx2 = bank + p * (INNER + 2 * STRIDE) + i
            assert dsts[0][idx01] == oracle_fade(pattern(idx01), 0x80)
            assert dsts[1][idx01] == oracle_mul(pattern(idx01), 0x80)
            assert dsts[2][idx2] == oracle_fade(pattern(idx2), 0x80)

print("PASS: upload-cluster driver runs (guard, direct, fade, blend)")
