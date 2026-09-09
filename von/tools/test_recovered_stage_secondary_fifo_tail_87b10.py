#!/usr/bin/env python3
"""Vectors for the fixed 0x87b10 secondary FIFO tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_fifo_tail_87b10.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("service_target", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32),
                ("word_count", ctypes.c_uint32),
                ("words", ctypes.c_uint32 * 2),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87b10:.*call.*0x294b0",
                        r"87b18:.*st.*0x884000",
                        r"87b20:.*mov.*16,g3",
                        r"87b24:.*st.*0x884000",
                        r"87b2c:.*ld.*0x51c988"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_fifo_tail_87b10
        function.argtypes = []
        function.restype = Result
        result = function()
        assert result.service_target == 0x294B0
        assert (result.fifo_address, result.word_count) == (0x884000, 2)
        assert list(result.words) == [8, 16]
        assert result.continuation == 0x87B2C
    print("recovered 0x87b10 secondary-FIFO-tail vectors: ok")


if __name__ == "__main__":
    main()
