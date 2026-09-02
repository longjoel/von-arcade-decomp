#!/usr/bin/env python3
"""Validate the host-side 0x41 -> 0x35 producer at i960 0x6f600."""

from __future__ import annotations

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_35_producer_6f600.c"


class Record(ctypes.Structure):
    _fields_ = [("unused_word0", ctypes.c_uint32),
                ("packet_word1", ctypes.c_uint32),
                ("packet_word2", ctypes.c_uint32),
                ("packet_word3", ctypes.c_uint32),
                ("packet_word4", ctypes.c_uint32)]


class FIFO:
    def __init__(self, read_value: int):
        self.read_value = read_value
        self.writes: list[int] = []
        self.reads = 0


READ = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
WRITE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32)


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


with tempfile.TemporaryDirectory(prefix="von-geometry-35-6f600-") as directory:
    library = pathlib.Path(directory) / "producer.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    producer = ctypes.CDLL(str(library)).recovered_geometry_35_producer_6f600
    producer.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Record), READ, WRITE, ctypes.c_void_p]
    producer.restype = ctypes.c_uint32

    fifo = FIFO(3)

    @READ
    def read(_opaque):
        fifo.reads += 1
        return fifo.read_value

    @WRITE
    def write(_opaque, value):
        fifo.writes.append(value)

    table = (Record * 4)()
    table[3] = Record(0x11111111, 0x22222222, 0x33333333, 0x44444444, 0x55555555)
    x = float_bits(80.75)
    y = float_bits(120.25)
    result = producer(x, y, table, read, write, None)
    assert result == 3
    assert fifo.reads == 2
    assert fifo.writes == [0x41, (60 << 9) + 40,
                           0x22222222, x, 0x44444444, y,
                           0x55555555, 0xCCCCCCCC]

    rejected = producer(float_bits(-1.0), y, table, read, write, None)
    assert rejected == 0x47C34F80
    assert fifo.reads == 2
    assert len(fifo.writes) == 8

print("PASS: 0x6f600 0x41 -> 0x35 producer contract")
