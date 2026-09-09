#!/usr/bin/env python3
"""Vectors for the fixed 0x88030 row-publication body."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_row_publication_88030.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("counter_value", ctypes.c_uint32),
                ("destination_first", ctypes.c_uint32),
                ("destination_second", ctypes.c_uint32),
                ("first_row_word", ctypes.c_uint32),
                ("second_row_word", ctypes.c_uint32),
                ("modulo_divisor", ctypes.c_uint32),
                ("counter_remainder", ctypes.c_uint32),
                ("row_offset", ctypes.c_uint32),
                ("first_row_address", ctypes.c_uint32),
                ("second_row_address", ctypes.c_uint32),
                ("counter_low_bits", ctypes.c_uint32),
                ("asset_upload_admitted", ctypes.c_uint32),
                ("asset_index", ctypes.c_uint32),
                ("asset_offset", ctypes.c_uint32),
                ("asset_source_first", ctypes.c_uint32),
                ("asset_source_second", ctypes.c_uint32),
                ("asset_destination_first", ctypes.c_uint32),
                ("asset_destination_second", ctypes.c_uint32),
                ("asset_bytes", ctypes.c_uint32),
                ("asset_upload_call", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88030:.*ld.*0x51c9b0",
                        r"8803c:.*remo.*g3,g5,r4",
                        r"88040:.*ldos.*0x108\(r5\)",
                        r"88050:.*st.*0x5618f0",
                        r"88058:.*ldos.*0x108\(r6\)",
                        r"88064:.*st.*0x561e90",
                        r"8806c:.*be.*0x880b4",
                        r"88078:.*lda.*0x59",
                        r"88084:.*remi.*g3,g4,g4",
                        r"8808c:.*lda.*0x533df0",
                        r"8809c:.*call.*0xf5d40",
                        r"880a0:.*lda.*0x54a5f0",
                        r"880b0:.*call.*0xf5d40",
                        r"880b4:.*call.*0x880c0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "rows.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_row_publication_88030
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        aligned = function(12, 0x503AD0, 0x5040D0, 0x12345678, 0xABCDEF01)
        assert (aligned.counter_remainder, aligned.row_offset,
                aligned.first_row_address, aligned.second_row_address,
                aligned.asset_upload_admitted) == (12, 144, 0x561980, 0x561f20, 0)
        assert (aligned.first_row_word, aligned.second_row_word) == (0x5678, 0xEF01)
        nonzero = function(1, 0x503AD0, 0x5040D0, 0, 0)
        assert (nonzero.asset_upload_admitted, nonzero.asset_index,
                nonzero.asset_offset, nonzero.asset_destination_first,
                nonzero.asset_destination_second) == (1, 9, 0x2400, 0x503CD0, 0x5042D0)
        assert (nonzero.asset_source_first, nonzero.asset_source_second,
                nonzero.asset_bytes, nonzero.continuation) == (0x5361F0, 0x54C9F0, 0x400, 0x880C0)
    print("recovered 0x88030 secondary-row-publication vectors: ok")


if __name__ == "__main__":
    main()
