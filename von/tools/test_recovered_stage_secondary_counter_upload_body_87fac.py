#!/usr/bin/env python3
"""Vectors for the fixed 0x87fac counter upload body."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_counter_upload_body_87fac.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("counter_value", ctypes.c_uint32),
                ("destination_first", ctypes.c_uint32),
                ("destination_second", ctypes.c_uint32),
                ("modulo_divisor", ctypes.c_uint32),
                ("counter_remainder", ctypes.c_uint32),
                ("row_index", ctypes.c_uint32),
                ("table_offset", ctypes.c_uint32),
                ("indexed_source_first", ctypes.c_uint32),
                ("indexed_source_second", ctypes.c_uint32),
                ("indexed_bytes", ctypes.c_uint32),
                ("fixed_source_first", ctypes.c_uint32),
                ("fixed_source_second", ctypes.c_uint32),
                ("fixed_destination_first", ctypes.c_uint32),
                ("fixed_destination_second", ctypes.c_uint32),
                ("fixed_bytes", ctypes.c_uint32),
                ("upload_call", ctypes.c_uint32),
                ("upload_count", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87fac:.*shlo.*3,15,r4",
                        r"87fb0:.*remo.*r4,g0,g0",
                        r"87fb4:.*mov.*r5,g1",
                        r"87fc8:.*lda.*0x51d5f0",
                        r"87fd0:.*call.*0xf5d40",
                        r"87fe0:.*mov.*r6,g1",
                        r"87ff4:.*lda.*0x5289f0",
                        r"87ffc:.*call.*0xf5d40",
                        r"88000:.*lda.*0x560df0",
                        r"88014:.*call.*0xf5d40",
                        r"88018:.*lda.*0x561370",
                        r"8802c:.*call.*0xf5d40"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "body.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_counter_upload_body_87fac
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        result = function(120, 0x503AD0, 0x5040D0)
        assert (result.counter_remainder, result.row_index, result.table_offset) == (0, 0, 0)
        assert (result.indexed_source_first, result.indexed_source_second) == (0x51D5F0, 0x5289F0)
        result = function(44, 0x11111111, 0x22222222)
        assert (result.counter_remainder, result.row_index,
                result.table_offset, result.destination_first,
                result.destination_second) == (44, 11, 0x4200, 0x11111111, 0x22222222)
        assert (result.fixed_source_first, result.fixed_source_second,
                result.fixed_destination_first, result.fixed_destination_second,
                result.fixed_bytes, result.upload_count,
                result.continuation) == (0x560DF0, 0x561370, 0x565320,
                                          0x5658A0, 0x580, 4, 0x88030)
    print("recovered 0x87fac secondary-counter-upload-body vectors: ok")


if __name__ == "__main__":
    main()
