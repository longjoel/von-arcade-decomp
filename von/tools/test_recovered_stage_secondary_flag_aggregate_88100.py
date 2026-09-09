#!/usr/bin/env python3
"""Vectors for the fixed 0x88100 flag aggregation block."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_flag_aggregate_88100.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("initial_first_code", ctypes.c_uint32),
                ("initial_second_code", ctypes.c_uint32),
                ("flag_word_5024a4", ctypes.c_uint32),
                ("flag_word_50249c", ctypes.c_uint32),
                ("mask_r6", ctypes.c_uint32),
                ("mask_r5", ctypes.c_uint32),
                ("mask_g2", ctypes.c_uint32),
                ("mask_g1", ctypes.c_uint32),
                ("counter_value", ctypes.c_uint32),
                ("counter_remainder", ctypes.c_uint32),
                ("row_offset", ctypes.c_uint32),
                ("final_first_code", ctypes.c_uint32),
                ("final_second_code", ctypes.c_uint32),
                ("first_store_address", ctypes.c_uint32),
                ("second_store_address", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88100:.*ldq.*0x3dc0",
                        r"8812c:.*and.*g5,r6,g4",
                        r"88134:.*setbit.*4,g7,g7",
                        r"8813c:.*ld.*0x50249c",
                        r"8814c:.*setbit.*5,g7,g7",
                        r"88150:.*and.*g5,g2,g4",
                        r"88158:.*setbit.*4,g6,g6",
                        r"88160:.*ld.*0x50249c",
                        r"88170:.*setbit.*5,g6,g6",
                        r"88174:.*ld.*0x51c9b0",
                        r"88180:.*remo.*g13,g4,g4",
                        r"88194:.*st.*g7.*0x4",
                        r"8819c:.*st.*g6.*0x8"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "aggregate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_flag_aggregate_88100
        function.argtypes = [ctypes.c_uint32] * 9
        function.restype = Result
        result = function(2, 4, 0x05, 0x08, 0x01, 0x01, 0x08, 0x08, 12)
        assert (result.final_first_code, result.final_second_code) == (18, 36)
        assert (result.counter_remainder, result.row_offset,
                result.first_store_address, result.second_store_address) == (12, 144, 0x561984, 0x561988)
        assert result.continuation == 0x881A4
        result = function(0, 0, 0, 0, 0x01, 0x01, 0x08, 0x08, 0)
        assert (result.final_first_code, result.final_second_code) == (0, 0)
    print("recovered 0x88100 secondary-flag-aggregate vectors: ok")


if __name__ == "__main__":
    main()
