#!/usr/bin/env python3
"""Vectors for the selector-4 0x89930 packet/state prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_89930_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_184", "record_8", "record_10", "first_fifo_response",
        "second_fifo_response", "stored_record_184_plus_6000",
        "packet_record_184_plus_6000_low16", "derived_first_word", "derived_difference",
        "packet_29_0", "packet_29_1", "packet_29_2", "packet_30_0", "packet_30_1",
        "packet_30_2", "state_51c940", "state_51c948", "state_51c950", "state_51c954",
        "timing_minus_3", "fifo_address", "float_constant", "first_command",
        "second_command", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89930:.*ldos.*0x184\(r10\)", r"89934:.*mov.*29,r13",
                        r"89948:.*lda.*0x6000\(g7\)", r"89950:.*and.*g4,g7,g4",
                        r"89954:.*st.*g4,0x884000", r"8995c:.*lda.*0x42a00000",
                        r"89964:.*st.*g5,0x884000", r"8996c:.*ld.*0x884000",
                        r"89974:.*ld.*0x8\(r10\)", r"89978:.*mov.*30,r12",
                        r"89984:.*st.*g4,0x884000", r"8998c:.*st.*g5,0x884000",
                        r"89994:.*ld.*0x884000", r"8999c:.*ld.*0x10\(r10\)",
                        r"899a0:.*addr.*g1,g0,g0", r"899a4:.*subr.*g6,g4,g1",
                        r"899b0:.*st.*g7,0x51c940", r"899b8:.*st.*g5,0x51c948",
                        r"899c8:.*st.*g0,0x51c950", r"899d0:.*st.*g1,0x51c954",
                        r"899d8:.*bl.*0x89a10"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_89930_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 6
        function.restype = Result
        result = function(0x7123, 0x30, 0x500, 0x40, 0x60, 7)
        assert (result.stored_record_184_plus_6000,
                result.packet_record_184_plus_6000_low16, result.derived_first_word,
                result.derived_difference, result.timing_minus_3) == (
                    0xd123, 0xd123, 0x70, 0x4a0, 4)
        assert (result.packet_29_0, result.packet_29_1, result.packet_29_2,
                result.packet_30_0, result.packet_30_1, result.packet_30_2) == (
                    29, 0xd123, 0x42a00000, 30, 0xd123, 0x42a00000)
        assert (result.state_51c940, result.state_51c948, result.state_51c950,
                result.state_51c954, result.fifo_address, result.continuation) == (
                    0xd123, 0x42a00000, 0x70, 0x4a0, 0x884000, 0x899d8)
    print("recovered 0x89930 packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
