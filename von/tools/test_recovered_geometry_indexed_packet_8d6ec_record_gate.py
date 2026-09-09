#!/usr/bin/env python3
"""Vectors for the 0x8d6ec indexed-geometry record gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_geometry_indexed_packet_8d6ec_record_gate.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_base", "table_base", "record_index", "record_active_word",
        "source_cursor_after", "table_cursor", "record_address", "record_stride",
        "table_record_bias", "active_path", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8d6ec:.*mov.*5,r5", r"8d6f0:.*addo.*g1,12,g3",
        r"8d6f4:.*addo.*g13,2,g2", r"8d6f8:.*shlo.*1,g0,g4",
        r"8d6fc:.*addo.*g0,g4,g4", r"8d700:.*lda.*\(g1\)\[g4\*4\],g1",
        r"8d704:.*ld.*\(g3\),g4", r"8d708:.*cmpibe.*0,g4,0x8d834"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_geometry_indexed_packet_8d6ec_record_gate
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        active = function(0x1000, 0x2000, 3, 1)
        assert (active.source_cursor_after, active.table_cursor, active.record_address,
                active.record_stride, active.table_record_bias, active.active_path,
                active.continuation) == (0x100c, 0x2002, 0x1024, 0xc, 2, 1, 0x8d704)
        inactive = function(0x1000, 0x2000, 3, 0)
        assert (inactive.active_path, inactive.continuation) == (0, 0x8d834)
    print("recovered 0x8d6ec record-gate vectors: ok")


if __name__ == "__main__":
    main()
