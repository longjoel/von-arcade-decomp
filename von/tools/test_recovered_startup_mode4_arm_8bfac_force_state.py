#!/usr/bin/env python3
"""Vectors for the 0x8bfac selector-1 success epilogue."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8bfac_force_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("state_51c9b4", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8bfac:.*mov.*1,g8", r"8bfb0:.*st.*g8,0x51c9b4", r"8bfc0:.*ret"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8bfac_force_state
        function.restype = Result
        result = function()
        assert (result.state_51c9b4, result.continuation) == (1, 0x8bfc0)
    print("recovered 0x8bfac force-state vectors: ok")


if __name__ == "__main__":
    main()
