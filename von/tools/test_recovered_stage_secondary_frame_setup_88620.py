#!/usr/bin/env python3
"""Vectors for the 0x88620 secondary frame-setup prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_frame_setup_88620.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("incoming_counter", ctypes.c_uint32), ("mode_value", ctypes.c_uint32),
                ("g14_value", ctypes.c_uint32), ("setup_call", ctypes.c_uint32),
                ("setup_argument", ctypes.c_uint32), ("setup_seed", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("fifo_word_count", ctypes.c_uint32),
                ("published_byte_address", ctypes.c_uint32),
                ("published_byte_value", ctypes.c_uint32), ("next_counter", ctypes.c_uint32),
                ("counter_limit", ctypes.c_uint32), ("dispatch_table_address", ctypes.c_uint32),
                ("dispatch_boundary", ctypes.c_uint32), ("dispatch_target", ctypes.c_uint32),
                ("dispatch_buffer", ctypes.c_uint32), ("dispatch_helper", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88620:.*call.*0x295d0", r"88624:.*mov.*8,g3",
                        r"88630:.*mov.*16,g3", r"8863c:.*lda.*0xd000",
                        r"88644:.*stob.*g14,0x503c7a", r"88650:.*call.*0x2a990",
                        r"88654:.*ld.*0x51c984", r"88660:.*addo.*g4,1,g4",
                        r"88664:.*cmpible.*g4,g5,0x8866c",
                        r"88680:.*bl.*0x88780", r"88684:.*ld.*0x88690\[g5\*4\]"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "setup.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_frame_setup_88620
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        result = function(0x20, 4, 0x12345678)
        assert (result.next_counter, result.published_byte_value,
                result.setup_call, result.setup_argument, result.fifo_word_count,
                result.dispatch_target, result.dispatch_buffer,
                result.dispatch_helper) == (0x21, 0x78, 0x295d0, 0xd000, 2,
                                             0x886e0, 0x5040d0, 0x88bd0)
        result = function(0xb4, 15, 0x100)
        assert (result.next_counter, result.dispatch_target,
                result.dispatch_buffer, result.dispatch_helper) == (
                    0xb4, 0x88770, 0x503ad0, 0x8ca80)
        result = function(0, 2, 0x100)
        assert (result.dispatch_target, result.dispatch_buffer,
                result.dispatch_helper) == (0x88780, 0x503ad0, 0x8a890)
        assert (result.fifo_address, result.published_byte_address,
                result.dispatch_table_address, result.dispatch_boundary) == (
                    0x884000, 0x503c7a, 0x88690, 15)
    print("recovered 0x88620 secondary-frame-setup vectors: ok")


if __name__ == "__main__":
    main()
