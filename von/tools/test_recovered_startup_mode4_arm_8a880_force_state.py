#!/usr/bin/env python3
"""Vector for the selector-tail success epilogue at 0x8a880."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a880_force_state.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("state_51c9b4", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a880:.*mov.*1,r12", r"8a884:.*st.*r12,0x51c9b4",
                        r"8a88c:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a880_force_state
        function.argtypes = []
        function.restype = Result
        result = function()
        assert (result.state_51c9b4, result.continuation) == (1, 0x8a88c)
    print("recovered 0x8a880 force-state vector: ok")


if __name__ == "__main__":
    main()
