#!/usr/bin/env python3
"""Vectors for the 0x8878c secondary frame finalizer."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_frame_finalize_8878c.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c950", "state_51c94c", "state_51c954", "state_51c940",
        "state_51c944", "snapshot_504b98", "snapshot_504b9c", "snapshot_504ba0",
        "short_504ba8", "short_504baa", "fifo_word_0", "fifo_word_1",
        "fifo_word_2", "fifo_word_3", "fifo_word_4", "fifo_word_5",
        "fifo_word_6", "fifo_count", "derived_504d28", "derived_5770f4",
        "fifo_address", "snapshot_base", "short_field_address_504ba8",
        "short_field_address_504baa", "derived_504d28_address",
        "derived_5770f4_address", "return_target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8878c:.*mov.*20,g3", r"88798:.*ld.*0x51c950",
                        r"887a0:.*ld.*0x51c94c", r"887a8:.*ld.*0x51c954",
                        r"887b0:.*ldos.*0x51c940", r"887b8:.*ldis.*0x51c944",
                        r"887fc:.*st.*g7,0x504b98", r"88804:.*st.*g0,0x504b9c",
                        r"8880c:.*st.*g1,0x504ba0", r"88814:.*stos.*g5,0x504baa",
                        r"8881c:.*stos.*g2,0x504ba8", r"88868:.*stos.*g4,0x504d28",
                        r"88870:.*st.*g5,0x5770f4", r"88878:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "finalize.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_frame_finalize_8878c
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        result = function(0x12345678, 0x00000003, 0x00000005, 0x00001234, 0x00005678)
        assert (result.snapshot_504b98, result.snapshot_504b9c,
                result.snapshot_504ba0, result.short_504ba8,
                result.short_504baa) == (0x12345678, 3, 5, 0x5678, 0x1234)
        assert (result.fifo_word_0, result.fifo_word_1, result.fifo_word_2,
                result.fifo_word_3, result.fifo_word_4, result.fifo_word_5,
                result.fifo_word_6) == (20, 0x5678, 21, 0xffffedcc, 18,
                                         0x92345678, 0x80000003)
        assert (result.derived_504d28, result.derived_5770f4) == (0x123, 2)
        assert (result.fifo_count, result.fifo_address, result.return_target) == (
            7, 0x884000, 0x88878)
    print("recovered 0x8878c secondary-frame-finalizer vectors: ok")


if __name__ == "__main__":
    main()
