#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("literal_source_address", ctypes.c_uint32),
        ("source_words", ctypes.c_uint32 * 3),
        ("seed_table_address", ctypes.c_uint32), ("seed_word", ctypes.c_uint32),
        ("seed_word_count", ctypes.c_uint32), ("destination_table_address", ctypes.c_uint32),
        ("destination_stride_bytes", ctypes.c_uint32), ("source_record_count", ctypes.c_uint32),
        ("column_count", ctypes.c_uint32), ("slot_count", ctypes.c_uint32),
        ("table", (ctypes.c_uint16 * 8) * 32 * 3), ("next_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-lookup-build-") as d:
        so = Path(d) / "event-lookup-build.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_event_lookup_table_build_ec820.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_event_lookup_table_build_ec820
        fn.restype = Result
        address = lib.recovered_geometry_event_lookup_table_address_ec820
        address.argtypes = [ctypes.c_uint32] * 3
        address.restype = ctypes.c_uint32
        out = fn()
        assert (out.literal_source_address, list(out.source_words), out.seed_table_address,
                out.seed_word, out.seed_word_count, out.destination_table_address,
                out.destination_stride_bytes, out.source_record_count, out.column_count,
                out.slot_count, out.next_target) == (
            0xead20, [1, 0x20, 0x400], 0x1080000, 0x88888888, 8,
            0x1800010, 2, 3, 32, 8, 0xec8e4)
        assert (out.table[0][0][0], out.table[0][0][7], out.table[1][3][2],
                out.table[2][31][7]) == (0x8000, 0x8007, 0x80a0, 0x1800)
        assert (address(0, 0, 0), address(0, 7, 0), address(1, 8, 0),
                address(2, 31, 7), address(3, 0, 0)) == (
            0x1800810, 0x1800810, 0x18008b0, 0x180097e, 0)
        print("PASS: 0xec820 geometry event lookup table build")


if __name__ == "__main__":
    main()
