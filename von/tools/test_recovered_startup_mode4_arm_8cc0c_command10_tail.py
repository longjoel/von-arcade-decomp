#!/usr/bin/env python3
"""Vectors for the 0x8cc0c selector-0 command-10 tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8cc0c_command10_tail.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_51c950", "state_51c954", "state_51c948", "computed_state_51c94c",
        "command_10_word_0", "command_10_word_1", "command_10_word_2",
        "first_response", "second_response", "record_30")]
    _fields_ += [(name, ctypes.c_uint32 * 3) for name in ("command_10_packet_0", "command_10_packet_1")]
    _fields_ += [(name, ctypes.c_uint32) for name in (
        "state_51c940", "state_51c944", "state_51c94c", "fifo_address",
        "command_10", "record_zero_path", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8cc0c:.*ld.*0xc\(r10\),g4", r"8cc10:.*movr.*r8,fp0",
        r"8cc18:.*lda.*0x40200000,g1", r"8cc20:.*ld.*0x10\(r10\),g6",
        r"8cc24:.*ld.*0x51c954,g7", r"8cc2c:.*ld.*0x51c950,g5",
        r"8cc3c:.*ld.*0x8\(r10\),g4", r"8cc44:.*subr.*g7,g6,g6",
        r"8cc48:.*subr.*g4,g5,g5", r"8cc4c:.*mov.*10,r13",
        r"8cc60:.*st.*g6,0x884000", r"8cc68:.*st.*g5,0x884000",
        r"8cc70:.*ld.*0x884000,g7", r"8cc7c:.*ld.*0xc\(r10\),g6",
        r"8cc98:.*mov.*10,r12", r"8cc9c:.*ld.*0x51c948,g6",
        r"8ccb4:.*st.*g6,0x884000", r"8ccbc:.*st.*g4,0x884000",
        r"8ccc4:.*ld.*0x884000,g5", r"8cccc:.*ldos.*0x30\(r10\),g4",
        r"8ccd0:.*stos.*g7,0x51c940", r"8ccd8:.*st.*g0,0x51c94c",
        r"8cce0:.*cmpi.*g4,0", r"8cce4:.*stos.*g5,0x51c944",
        r"8ccec:.*bne.*0x8d094"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8cc0c_command10_tail
        function.argtypes = [ctypes.c_uint32] * 10
        function.restype = Result
        zero = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 0)
        assert list(zero.command_10_packet_0) == [10, 5, 6]
        assert list(zero.command_10_packet_1) == [10, 3, 7]
        assert (zero.state_51c940, zero.state_51c944, zero.state_51c94c,
                zero.record_zero_path, zero.continuation) == (8, 9, 4, 1, 0x8ccf0)
        nonzero = function(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        assert (nonzero.record_zero_path, nonzero.continuation) == (0, 0x8d094)
    print("recovered 0x8cc0c command-10-tail vectors: ok")


if __name__ == "__main__":
    main()
