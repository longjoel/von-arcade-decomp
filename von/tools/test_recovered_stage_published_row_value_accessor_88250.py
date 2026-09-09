#!/usr/bin/env python3
"""Vectors for the fixed 0x88250 published-row accessor."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_published_row_value_accessor_88250.c"
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
                ("read_address", ctypes.c_uint32),
                ("result_value", ctypes.c_uint32),
                ("sentinel_value", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88250:.*lda.*0x88290",
                        r"88258:.*mov.*g14,g1",
                        r"88260:.*ld.*0x51c988",
                        r"88268:.*cmpibg.*0.*0x88278",
                        r"8826c:.*lda.*0xffff",
                        r"88278:.*ld.*0x51d5e4",
                        r"88280:.*lda.*\(g4\)\[g4\*2\]",
                        r"88284:.*ldos.*0x561e90\[g4\*4\]",
                        r"8828c:.*bx.*\(g1\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "accessor.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_published_row_value_accessor_88250
        function.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        positive = function(1, 7, 0x12345678)
        assert (positive.row_offset, positive.read_address,
                positive.result_value, positive.table_address) == (84, 0x561ee4, 0x5678, 0x561e90)
        negative = function(0, 7, 0x12345678)
        assert (negative.result_value, negative.sentinel_value) == (0xffff, 0xffff)
        assert (positive.return_trampoline_load_address,
                positive.return_trampoline_target, positive.continuation) == (0x88250, 0x88290, 0x88290)
    print("recovered 0x88250 published-row-accessor vectors: ok")


if __name__ == "__main__":
    main()
