#!/usr/bin/env python3
"""Vectors for the 0x87a10 secondary stage clear/callback gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_clear_gate_87a10.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "control_value", "flag_word_5024a4", "exception_word_5024f4",
        "value_503a70", "value_503a78", "bit4_forced", "exception_path",
        "command_address", "command_value", "callback_g0", "callback_target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87a10:.*lda.*0x87a98",
                        r"87a3c:.*mov.*1,g0",
                        r"87a40:.*bx.*\(g1\)",
                        r"87a44:.*cmpibe.*0,g5",
                        r"87a50:.*lda.*0x61",
                        r"87a58:.*lda.*0x63",
                        r"87a70:.*cmpible.*g5,g4",
                        r"87a78:.*st.*0x5032f4",
                        r"87a90:.*mov.*0,g0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_clear_gate_87a10
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result

        result = function(0, 0, 0, 10, 20)
        assert (result.callback_g0, result.command_value) == (0, 0)
        result = function(0, 1 << 4, 0, 10, 20)
        assert (result.bit4_forced, result.callback_g0) == (1, 1)
        result = function(1, 0, 0x61, 10, 20)
        assert (result.exception_path, result.command_value,
                result.callback_g0) == (1, 0x63, 1)
        result = function(1, 0, 0x63, 20, 10)
        assert result.command_value == 0x61
        result = function(1, 0, 0x62, 10, 20)
        assert (result.exception_path, result.command_value,
                result.callback_g0) == (0, 0, 0)
        assert result.command_address == 0x5032F4
        assert result.callback_target == 0x87A98
    print("recovered 0x87a10 secondary-clear vectors: ok")


if __name__ == "__main__":
    main()
