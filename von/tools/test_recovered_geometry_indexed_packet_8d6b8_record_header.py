#!/usr/bin/env python3
"""Vectors for the 0x8d6b8 indexed-geometry record header."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_geometry_indexed_packet_8d6b8_record_header.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_pointer", "record_pointer_after", "record_field_6", "record_field_8",
        "record_field_a", "xor_mask", "gated_value", "masked_field_6",
        "masked_field_8", "masked_field_a")]
    _fields_ += [("packet", ctypes.c_uint32 * 4)]
    _fields_ += [(name, ctypes.c_uint32) for name in ("command_47", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8d6b8:.*addo.*g13,12,g13", r"8d6bc:.*st.*r6,0x884000",
        r"8d6c4:.*xor.*g5,g7,g5", r"8d6d0:.*xor.*g6,g7,g6",
        r"8d6dc:.*xor.*g4,g7,g4", r"8d6e0:.*st.*g4,0x884000",
        r"8d6e8:.*ble.*0x8d848", r"8d6ec:.*mov.*5,r5"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "header.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_geometry_indexed_packet_8d6b8_record_header
        function.argtypes = [ctypes.c_uint32] * 6
        function.restype = Result
        result = function(0x1000, 0x12, 0x34, 0x56, 0xff, 1)
        assert (result.record_pointer_after, result.masked_field_6,
                result.masked_field_8, result.masked_field_a) == (0x100c, 0xed, 0xcb, 0xa9)
        assert list(result.packet) == [47, 0xed, 0xcb, 0xa9]
        assert (result.command_47, result.continuation) == (47, 0x8d848)
        assert function(0x1000, 1, 2, 3, 4, 2).continuation == 0x8d6ec
    print("recovered 0x8d6b8 record-header vectors: ok")


if __name__ == "__main__":
    main()
