#!/usr/bin/env python3
"""Vectors for the selector-3 0x8931c packet/state prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8931c_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_184", "record_8", "record_10", "table_word_10", "table_word_18",
        "first_fifo_response", "second_fifo_response", "stored_record_184_minus_6000",
        "packet_record_184_minus_6000_low16", "derived_first_word", "derived_difference",
        "packet_29_0", "packet_29_1", "packet_29_2", "packet_30_0", "packet_30_1",
        "packet_30_2", "packet_31_0", "packet_31_1", "packet_31_2", "packet_31_3",
        "packet_31_4", "packet_31_5", "packet_31_6", "state_51c940", "state_51c948",
        "state_51c950", "state_51c954", "fifo_address", "float_constant", "first_command",
        "second_command", "third_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8931c:.*ldos.*0x184\(g0\)", r"89320:.*mov.*29,r13",
                        r"8932c:.*lda.*0x42a00000", r"89334:.*st.*g6,0x51c948",
                        r"89344:.*ld.*0x8\(r10\)", r"89350:.*ld.*0x10\(r10\)",
                        r"89354:.*lda.*0xffffa000\(g4\)", r"8935c:.*and.*g13,g4,g1",
                        r"89360:.*st.*g1,0x884000", r"89378:.*shlo.*5,g5,g5",
                        r"89380:.*ld.*0x10\(g5\)", r"89384:.*ld.*0x18\(g5\)",
                        r"89388:.*ld.*0x884000", r"89390:.*ld.*0x8\(g0\)",
                        r"89394:.*mov.*30,r12", r"893a0:.*st.*g1,0x884000",
                        r"893a8:.*st.*g6,0x884000", r"893b0:.*ld.*0x884000",
                        r"893b8:.*addr.*g7,g4,g7", r"893bc:.*ld.*0x10\(g0\)",
                        r"893c0:.*mov.*31,r13", r"893cc:.*st.*g7,0x884000",
                        r"893d4:.*st.*g2,0x884000", r"893dc:.*mov.*0,g0",
                        r"893f4:.*st.*g7,0x51c950", r"8940c:.*st.*g1,0x51c954",
                        r"89448:.*st.*g1,0x884000"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8931c_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result
        result = function(0x7123, 0x30, 0x500, 0x111, 0x222, 0x40, 0x60)
        assert (result.stored_record_184_minus_6000,
                result.packet_record_184_minus_6000_low16, result.derived_first_word,
                result.derived_difference) == (0x1123, 0x1123, 0x70, 0x4a0)
        assert (result.packet_29_0, result.packet_29_1, result.packet_29_2,
                result.packet_30_0, result.packet_30_1, result.packet_30_2) == (
                    29, 0x1123, 0x42a00000, 30, 0x1123, 0x42a00000)
        assert (result.packet_31_0, result.packet_31_1, result.packet_31_2,
                result.packet_31_3, result.packet_31_4, result.packet_31_5,
                result.packet_31_6) == (31, 0x70, 0x111, 0, 0, 0x4a0, 0x222)
        assert (result.state_51c940, result.state_51c948, result.state_51c950,
                result.state_51c954, result.fifo_address, result.continuation) == (
                    0x1123, 0x42a00000, 0x70, 0x4a0, 0x884000, 0x89450)
    print("recovered 0x8931c packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
