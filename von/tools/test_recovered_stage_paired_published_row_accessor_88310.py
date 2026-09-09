#!/usr/bin/env python3
"""Vectors for the fixed 0x88310 published paired-row accessor."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_paired_published_row_accessor_88310.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_value", ctypes.c_int32), ("timing_index", ctypes.c_uint32),
                ("return_trampoline_load_address", ctypes.c_uint32),
                ("return_trampoline_target", ctypes.c_uint32),
                ("state_address", ctypes.c_uint32), ("timing_address", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32), ("table_stride", ctypes.c_uint32),
                ("row_offset", ctypes.c_uint32), ("first_read_address", ctypes.c_uint32),
                ("second_read_address", ctypes.c_uint32), ("first_result", ctypes.c_uint32),
                ("second_result", ctypes.c_uint32), ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88310:.*lda.*0x88374", r"88320:.*ld.*0x51c988",
                        r"88328:.*cmpibg.*0.*0x88338",
                        r"8832c:.*st.*g14,\(g0\)", r"88330:.*st.*g14,\(g1\)",
                        r"88340:.*lda.*0x561e90", r"8834c:.*ld.*0x4\(g5\)\[g4\*4\]",
                        r"88364:.*ld.*0x8\(g5\)\[g4\*4\]", r"88370:.*bx.*\(g2\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "accessor.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_paired_published_row_accessor_88310
        function.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        positive = function(2, 9, 0x10203040, 0x50607080)
        assert (positive.row_offset, positive.first_read_address,
                positive.second_read_address, positive.first_result,
                positive.second_result) == (108, 0x561f00, 0x561f04,
                                             0x10203040, 0x50607080)
        nonpositive = function(-1, 9, 1, 2)
        assert (nonpositive.first_result, nonpositive.second_result) == (0, 0)
        assert (positive.return_trampoline_load_address,
                positive.return_trampoline_target, positive.continuation) == (0x88310, 0x88374, 0x88374)
    print("recovered 0x88310 published-paired-row-accessor vectors: ok")


if __name__ == "__main__":
    main()
