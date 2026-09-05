#!/usr/bin/env python3
"""Validate the recovered 0x1bb90 nibble-expansion decoder.

Provenance: synthetic (vonj-maincpu.lst 0x1bb90-0x1bc1c); no
trace-derived vectors. The word kernel is checked exhaustively over
all 65536 inputs against an independently derived bit mapping.
"""
import ctypes
import pathlib
import subprocess
import tempfile


def oracle(pixel):
    i = [(pixel >> b) & 1 for b in range(16)]
    o = [0] * 16
    o[0] = i[12]
    o[1], o[2], o[3], o[4] = i[0], i[1], i[2], i[3]
    o[5] = i[13]
    o[10] = i[8] | i[14]
    o[11] = i[9] | i[8]
    o[12] = i[10] | i[9]
    o[13] = i[11] | i[10]
    o[14] = i[11]
    return sum(b << n for n, b in enumerate(o))


class Run(ctypes.Structure):
    _fields_ = [("iterations", ctypes.c_uint32),
                ("src_end", ctypes.c_uint32),
                ("dst_end", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "nibble-expand.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_nibble_expand_1bb90.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    word_fn = lib.recovered_nibble_expand_word
    word_fn.argtypes = [ctypes.c_uint16]
    word_fn.restype = ctypes.c_uint16
    run_fn = lib.recovered_nibble_expand_run_plan
    run_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32,
                       ctypes.POINTER(Run)]

    # Exhaustive kernel check: any single-bit mapping error shows up.
    for pixel in range(0x10000):
        assert word_fn(pixel) == oracle(pixel), hex(pixel)

    # Signed run schedule with 2-byte strides.
    for count, want in ((-0x80000000, 0), (-1, 0), (0, 0), (1, 1),
                        (2, 2), (0x100, 0x100), (0x7FFFFFFF, 0x7FFFFFFF)):
        run = Run()
        run_fn(0x1000, 0x2000, count, ctypes.byref(run))
        assert run.iterations == want, count
        assert run.src_end == (0x1000 + 2 * want) & 0xFFFFFFFF, count
        assert run.dst_end == (0x2000 + 2 * want) & 0xFFFFFFFF, count

print("PASS: 0x1bb90 nibble-expansion decoder (65536 exhaustive)")
