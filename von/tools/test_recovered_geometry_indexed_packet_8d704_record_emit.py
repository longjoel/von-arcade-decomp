#!/usr/bin/env python3
"""Vectors for the 0x8d704 indexed-geometry record emitter."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_geometry_indexed_packet_8d704_record_emit.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_record_0", "source_record_4", "source_record_8", "selected_record_0",
        "selected_record_2", "selected_record_4", "selected_record_6", "selected_record_8",
        "xor_mask", "readback_word", "more_records")]
    _fields_ += [("packet", ctypes.c_uint32 * 13), ("window_word", ctypes.c_uint32 * 4),
                 ("window_address", ctypes.c_uint32 * 4)]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "control_address", "control_value", "completion_word", "fifo_address",
        "packet_emitted", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8d704:.*ld.*\(g3\),g4", r"8d708:.*cmpibe.*0,g4,0x8d834",
        r"8d70c:.*st.*r5,0x884000", r"8d714:.*addo.*31,16,r6",
        r"8d720:.*ldos.*0x4\(g2\),g4", r"8d738:.*st.*g4,0x884000",
        r"8d758:.*ldos.*0x2\(g2\),g4", r"8d768:.*shlo.*16,g4,g4",
        r"8d778:.*ldos.*\(g2\),g4", r"8d798:.*ldos.*\(g13\),g4",
        r"8d7b8:.*addo.*31,27,r6", r"8d7c4:.*ld.*0x802008,g4",
        r"8d7f0:.*st.*r6,0x800010", r"8d82c:.*st.*r6,0x884000",
        r"8d834:.*addo.*g3,12,g3", r"8d844:.*bg.*0x8d704",
        r"8d848:.*mov.*0,g0"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "emit.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_geometry_indexed_packet_8d704_record_emit
        function.argtypes = [ctypes.c_uint32] * 11
        function.restype = Result
        result = function(0x11111111, 0x22222222, 0x33333333, 0x10001, 0x8002,
                          0x12, 0x34, 0x56, 0xffff, 0x44444444, 0)
        assert list(result.packet) == [5, 47, 0x12, 0x34, 0x56, 22, 0xffff8002,
                                       21, 1, 20, 1, 58, 0x44444444]
        assert list(result.window_word) == [0x11111111, 0x22222222, 0x33333333, 0]
        assert list(result.window_address) == [0x804000, 0x804004, 0x804008, 0x80400c]
        assert (result.control_address, result.control_value, result.completion_word,
                result.packet_emitted, result.continuation) == (0x800010, 0x101, 6, 1, 0x8d848)
        assert function(1, 2, 3, 4, 5, 6, 7, 8, 0xff, 9, 1).continuation == 0x8d704
    print("recovered 0x8d704 record-emitter vectors: ok")


if __name__ == "__main__":
    main()
