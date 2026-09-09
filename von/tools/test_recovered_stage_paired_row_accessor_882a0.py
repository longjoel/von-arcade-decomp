#!/usr/bin/env python3
"""Vectors for the fixed 0x882a0 paired-row accessor."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_paired_row_accessor_882a0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_value", ctypes.c_int32),
                ("timing_index", ctypes.c_uint32),
                ("return_trampoline_load_address", ctypes.c_uint32),
                ("return_trampoline_target", ctypes.c_uint32),
                ("state_address", ctypes.c_uint32),
                ("timing_address", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32),
                ("table_stride", ctypes.c_uint32),
                ("row_offset", ctypes.c_uint32),
                ("first_read_address", ctypes.c_uint32),
                ("second_read_address", ctypes.c_uint32),
                ("first_result", ctypes.c_uint32),
                ("second_result", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"882a0:.*lda.*0x88304",
                        r"882b0:.*ld.*0x51c988",
                        r"882b8:.*cmpibg.*0.*0x882c8",
                        r"882bc:.*st.*g14,\(g0\)",
                        r"882c0:.*st.*g14,\(g1\)",
                        r"882d8:.*lda.*\(g4\)\[g4\*2\]",
                        r"882dc:.*ld.*0x4\(g5\)\[g4\*4\]",
                        r"882f4:.*ld.*0x8\(g5\)\[g4\*4\]",
                        r"88300:.*bx.*\(g2\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "accessor.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_paired_row_accessor_882a0
        function.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        positive = function(1, 7, 0x11223344, 0x55667788)
        assert (positive.row_offset, positive.first_read_address,
                positive.second_read_address, positive.first_result,
                positive.second_result) == (84, 0x561948, 0x56194c,
                                             0x11223344, 0x55667788)
        nonpositive = function(0, 7, 0x11223344, 0x55667788)
        assert (nonpositive.first_result, nonpositive.second_result) == (0, 0)
        assert (positive.return_trampoline_load_address,
                positive.return_trampoline_target, positive.continuation) == (
                    0x882a0, 0x88304, 0x88304)
    print("recovered 0x882a0 paired-row-accessor vectors: ok")


if __name__ == "__main__":
    main()
