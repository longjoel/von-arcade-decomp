#!/usr/bin/env python3
"""Vectors for the fixed 0x880c0 dual flag decoder."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_flag_pair_880c0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("flag_word_5024a4", ctypes.c_uint32),
                ("flag_word_50249c", ctypes.c_uint32),
                ("first_mask", ctypes.c_uint32),
                ("second_mask", ctypes.c_uint32),
                ("first_table_address", ctypes.c_uint32),
                ("second_table_address", ctypes.c_uint32),
                ("first_code", ctypes.c_uint32),
                ("second_code", ctypes.c_uint32),
                ("zero_code", ctypes.c_uint32),
                ("two_code", ctypes.c_uint32),
                ("four_code", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"880c0:.*ld.*0x5024a4",
                        r"880c8:.*ldq.*0x3d90",
                        r"880d4:.*and.*g5,r5,g4",
                        r"880e4:.*mov.*2,g7",
                        r"880ec:.*ld.*0x50249c",
                        r"880f4:.*and.*r5,g4,g4",
                        r"880fc:.*mov.*4,g7",
                        r"88100:.*ldq.*0x3dc0",
                        r"88108:.*and.*g5,g1,g4",
                        r"88110:.*mov.*2,g6",
                        r"88118:.*ld.*0x50249c",
                        r"88120:.*and.*g1,g4,g4",
                        r"88128:.*mov.*4,g6"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "flags.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_flag_pair_880c0
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(0x05, 0x08, 0x01, 0x08)
        assert (result.first_code, result.second_code) == (2, 4)
        result = function(0x00, 0x00, 0x01, 0x08)
        assert (result.first_code, result.second_code) == (0, 0)
        result = function(0x08, 0x08, 0x01, 0x08)
        assert (result.first_code, result.second_code) == (0, 2)
        assert (result.first_table_address, result.second_table_address,
                result.continuation) == (0x3D90, 0x3DC0, 0x88100)
    print("recovered 0x880c0 secondary-flag-pair vectors: ok")


if __name__ == "__main__":
    main()
