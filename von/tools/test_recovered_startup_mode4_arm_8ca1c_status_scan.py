#!/usr/bin/env python3
"""Vectors for the 0x8ca1c status-table scan."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8ca1c_status_scan.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status_table", "lower_threshold", "upper_threshold", "first_status",
        "first_status_masked", "first_status_next", "matched", "match_index",
        "match_address", "match_count", "no_match_address", "no_match_value",
        "entry_count", "entry_stride", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8ca1c:.*mov.*0,g6", r"8ca20:.*lda.*0x200\(r8\),g5",
        r"8ca24:.*ldob.*\(g5\),g4", r"8ca2c:.*cmpoble.*g4,r10,0x8ca48",
        r"8ca38:.*cmpobg.*g4,r9,0x8ca48", r"8ca44:.*cmpibe.*0,g4,0x8ca6c",
        r"8ca48:.*addo.*g6,1,g6", r"8ca4c:.*cmpi.*31,g6",
        r"8ca50:.*lda.*0x20\(g5\),g5", r"8ca54:.*bge.*0x8ca24",
        r"8ca58:.*addo.*r7,1,r7", r"8ca5c:.*cmpibge.*26,r7,0x8c9cc",
        r"8ca60:.*st.*g14,0x51c9a0", r"8ca6c:.*st.*r5,0x51c998",
        r"8ca74:.*st.*g6,0x51c994"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "scan.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8ca1c_status_scan
        function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        status = (ctypes.c_uint8 * (32 * 0x20))()
        status[0] = 4
        status[1] = 1
        status[2 * 0x20] = 7
        status[2 * 0x20 + 1] = 0
        matched = function(0x600000, status, 3, 7)
        assert (matched.matched, matched.match_index, matched.match_address,
                matched.match_count, matched.first_status, matched.first_status_next) == (1, 2,
                                                                                           0x600040, 3, 4, 1)
        empty = (ctypes.c_uint8 * (32 * 0x20))()
        no_match = function(0x600000, empty, 3, 7)
        assert (no_match.matched, no_match.match_index, no_match.no_match_address,
                no_match.no_match_value, no_match.continuation) == (0, 32, 0x51c9a0, 0, 0x8ca80)
    print("recovered 0x8ca1c status-scan vectors: ok")


if __name__ == "__main__":
    main()
