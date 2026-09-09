#!/usr/bin/env python3
"""Vectors for the selector-1 0x89e44 packet/state prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_89e44_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_51c984", "prior_fifo_response", "computed_packet_word", "record_8",
        "record_10", "timing_delta", "transformed_base", "transformed_base_low16",
        "first_fifo_response", "second_fifo_response", "packet_29_0", "packet_29_1",
        "packet_29_2", "packet_30_0", "packet_30_1", "packet_30_2", "state_51c940",
        "state_51c942", "state_51c948", "state_51c950", "state_51c954", "fifo_address",
        "first_command", "second_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89e44:.*ld.*0x51c984", r"89e4c:.*lda.*0xb4",
                        r"89e54:.*cvtir.*g6,fp0", r"89e64:.*divrl.*g0,fp0,g0",
                        r"89e74:.*lda.*0x1000\(g2\)", r"89e7c:.*mov.*29,r12",
                        r"89e88:.*stos.*g7,0x51c940", r"89e90:.*shlo.*8,g6,g6",
                        r"89e94:.*subo.*g6,g7,g7", r"89e9c:.*lda.*0xffff",
                        r"89eac:.*and.*g7,g4,g4", r"89eb0:.*st.*g4,0x884000",
                        r"89eb8:.*st.*g0,0x884000", r"89ec0:.*ld.*0x884000",
                        r"89ec8:.*ld.*0x8\(r10\)", r"89ecc:.*mov.*30,r12",
                        r"89ed8:.*st.*g4,0x884000", r"89ee0:.*st.*g0,0x884000",
                        r"89ee8:.*ld.*0x884000", r"89ef0:.*ld.*0x10\(r10\)",
                        r"89ef4:.*stos.*g6,0x51c942", r"89efc:.*addr.*g13,g3,g13",
                        r"89f00:.*subr.*g2,g5,g1", r"89f0c:.*stos.*g7,0x51c940",
                        r"89f14:.*st.*g0,0x51c948", r"89f24:.*st.*g13,0x51c950",
                        r"89f2c:.*st.*g1,0x51c954", r"89f34:.*bl.*0x89f70"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_89e44_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result
        result = function(0x78, 0x20000, 0x3f800000, 0x30, 0x500, 0x40, 0x60)
        assert (result.timing_delta, result.transformed_base,
                result.transformed_base_low16) == (0x3c, 0x1d400, 0xd400)
        assert (result.packet_29_0, result.packet_29_1, result.packet_29_2,
                result.packet_30_0, result.packet_30_1, result.packet_30_2) == (
                    29, 0xd400, 0x3f800000, 30, 0xd400, 0x3f800000)
        assert (result.state_51c940, result.state_51c942, result.state_51c948,
                result.state_51c950, result.state_51c954, result.fifo_address,
                result.continuation) == (0x1d400, 0x3c, 0x3f800000, 0x70,
                                          0x4a0, 0x884000, 0x89f34)
    print("recovered 0x89e44 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
