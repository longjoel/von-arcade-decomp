#!/usr/bin/env python3
"""Vector for selector-1 success epilogue at 0x8aecc."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8aecc_force_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "g14_value", "state_51c9b4", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8aecc:.*st.*g14,0x51c9b4", r"8aed4:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8aecc_force_state
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        result = function(0x12345678)
        assert (result.g14_value, result.state_51c9b4, result.continuation) == (
            0x12345678, 0x12345678, 0x8aed8)
    print("recovered 0x8aecc force-state vector: ok")


if __name__ == "__main__":
    main()
