#!/usr/bin/env python3
"""Check the recovered i960 0x3120 table-checksum contract."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_crc16_table.c"


def crc_table() -> list[int]:
    values = []
    for index in range(256):
        value = index << 8
        for _ in range(8):
            value = ((value << 1) ^ 0x1021) & 0xffff if value & 0x8000 else (value << 1) & 0xffff
        values.append(value)
    return values


def reference(data: bytes, stride: int, count: int, table: list[int]) -> int:
    state = 0xDEBDEB00
    cursor = 0
    for _ in range(count):
        index = (state >> 24) & 0xff
        state = (((state + data[cursor]) << 8) & 0xffffffff) ^ (table[index] << 16)
        cursor += stride
    signed = table[(state >> 24) & 0xff]
    if signed & 0x8000:
        signed |= 0xffff0000
    return (signed ^ (((state << 8) & 0xffffffff) >> 16)) & 0xffffffff


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libcrc16_table.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_crc16_table
        function.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint16)]
        function.restype = ctypes.c_uint32

        table = crc_table()
        table_array = (ctypes.c_uint16 * 256)(*table)
        for data, stride, count in [(b"", 1, 0), (b"abcdef", 1, 6), (b"a0b1c2", 2, 3)]:
            storage = ctypes.create_string_buffer(data or b"\0")
            expected = reference(data or b"\0", stride, count, table)
            actual = function(storage, stride, count, table_array)
            assert actual == expected, (data, stride, count, actual, expected)

    print("recovered CRC-table vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
