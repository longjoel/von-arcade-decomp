#!/usr/bin/env python3
"""Vectors for the fixed 0x87ee0 terminal publication block."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_terminal_publication_87ee0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("status_503aa4", ctypes.c_uint32),
                ("status_marker_address", ctypes.c_uint32),
                ("status_marker_value", ctypes.c_uint32),
                ("progress_address", ctypes.c_uint32),
                ("progress_value", ctypes.c_uint32),
                ("value_503a70", ctypes.c_uint32),
                ("value_503a78", ctypes.c_uint32),
                ("command_address", ctypes.c_uint32),
                ("command_value", ctypes.c_uint32),
                ("state_address", ctypes.c_uint32),
                ("state_value", ctypes.c_uint32),
                ("state_seed", ctypes.c_uint32),
                ("progress_one_value", ctypes.c_uint32),
                ("progress_alternate_value", ctypes.c_uint32),
                ("command_low_value", ctypes.c_uint32),
                ("command_high_value", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87ee0:.*ld.*0x503aa4",
                        r"87ef0:.*st.*0x503a60",
                        r"87f0c:.*lda.*0xb4",
                        r"87f20:.*st.*0x503a04",
                        r"87f28:.*cmpi.*g5,g4",
                        r"87f40:.*st.*0x5032f4",
                        r"87f48:.*st.*0x51d5e0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "terminal.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_terminal_publication_87ee0
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        low = function(1, 10, 10, 0x12345678)
        assert (low.status_marker_value, low.progress_value, low.command_value,
                low.state_value) == (1, 1, 0x61, 0x12345678)
        high = function(2, 11, 10, 0x12345678)
        assert (high.progress_value, high.command_value, high.return_target) == (0xB4, 0x63, 0x87F50)
        zero = function(0, 0, 1, 0)
        assert (zero.progress_value, zero.command_value) == (1, 0x61)
    print("recovered 0x87ee0 secondary-terminal-publication vectors: ok")


if __name__ == "__main__":
    main()
