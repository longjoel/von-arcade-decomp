#!/usr/bin/env python3
"""Vectors for the selector-0 0x89cf4 floating/packet tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_89cf4_float_packet_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_result", "record_0c", "record_8", "record_10", "state_51c948",
        "state_51c950", "state_51c954", "record_30", "first_fifo_response",
        "second_fifo_response", "selected_float", "derived_float_word",
        "packet_first_10_0", "packet_first_10_1", "packet_first_10_2",
        "packet_second_10_0", "packet_second_10_1", "packet_second_10_2",
        "state_51c940", "state_51c944", "state_51c94c", "helper_call", "fifo_address",
        "first_command", "second_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89cf4:.*bl.*0x89d30", r"89cf8:.*mov.*g13,g0",
                        r"89d04:.*call.*0x6ece0", r"89d18:.*cmprl.*fp0,r12",
                        r"89d24:.*lda.*0x41f00000", r"89d34:.*ld.*0x5770f0",
                        r"89d5c:.*ld.*0xc\(r10\)", r"89d70:.*ld.*0x10\(r10\)",
                        r"89d74:.*ld.*0x51c954", r"89d7c:.*ld.*0x51c950",
                        r"89d84:.*addrl.*fp0,g0,g0", r"89d90:.*addrl.*g0,fp0,g0",
                        r"89d94:.*subr.*g7,g6,g6", r"89d98:.*subr.*g4,g5,g5",
                        r"89d9c:.*mov.*10,r13", r"89db0:.*st.*g6,0x884000",
                        r"89db8:.*st.*g5,0x884000", r"89dc0:.*ld.*0x884000",
                        r"89dc8:.*movr.*g0,fp0", r"89de4:.*subrl.*fp0,g4,g4",
                        r"89de8:.*mov.*10,r12", r"89df4:.*st.*r12,0x884000",
                        r"89e04:.*st.*g6,0x884000", r"89e0c:.*st.*g4,0x884000",
                        r"89e14:.*ld.*0x884000", r"89e20:.*st.*g7,0x51c940",
                        r"89e28:.*st.*g0,0x51c94c", r"89e34:.*stos.*g5,0x51c944",
                        r"89e3c:.*be.*0x8a880", r"89e40:.*b.*0x8a16c"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_89cf4_float_packet_tail
        function.argtypes = [ctypes.c_uint32] * 10
        function.restype = Result
        result = function(0xbf800000, 0x3f000000, 0x40000000, 0x500, 0x42a00000,
                          0x70, 0x80, 0, 0x55, 0x66)
        assert (result.selected_float, result.derived_float_word) == (0xbf800000, 0x3f000000)
        assert (result.packet_first_10_0, result.packet_first_10_1,
                result.packet_first_10_2) == (10, 0x480, 0x3fffff90)
        assert (result.packet_second_10_0, result.packet_second_10_1,
                result.packet_second_10_2) == (10, 0x42a00000, 0x3f000000)
        assert (result.state_51c940, result.state_51c944, result.state_51c94c,
                result.helper_call, result.fifo_address, result.continuation) == (
                    0x55, 0x66, 0x3f800000, 0x6ece0, 0x884000, 0x8a880)
    print("recovered 0x89cf4 floating/packet-tail vectors: ok")


if __name__ == "__main__":
    main()
