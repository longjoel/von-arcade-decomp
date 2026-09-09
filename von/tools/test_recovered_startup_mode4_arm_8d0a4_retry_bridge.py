#!/usr/bin/env python3
"""Vectors for the 0x8d0a4 completion retry bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8d0a4_retry_bridge.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("retry_target", "continuation")]


def main():
    listing = LISTING.read_text()
    assert re.search(r"8d0a4:.*b.*0x8ccf0", listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "retry.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8d0a4_retry_bridge
        function.argtypes = []
        function.restype = Result
        result = function()
        assert (result.retry_target, result.continuation) == (0x8ccf0, 0x8ccf0)
    print("recovered 0x8d0a4 retry-bridge vectors: ok")


if __name__ == "__main__":
    main()
