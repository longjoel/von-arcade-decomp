#!/usr/bin/env python3
"""Vector for selector-3 success epilogue at 0x8b604."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b604_force_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("state_51c9b4", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b604:.*mov.*1,r12", r"8b608:.*st.*r12,0x51c9b4",
                        r"8b610:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b604_force_state
        function.argtypes = []
        function.restype = Result
        result = function()
        assert (result.state_51c9b4, result.continuation) == (1, 0x8b610)
    print("recovered 0x8b604 force-state vector: ok")


if __name__ == "__main__":
    main()
