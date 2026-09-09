#!/usr/bin/env python3
"""Vectors for the 0x8c0c8 selector-routing bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_common_dispatch_8c0c8_selector_routes.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector", "entry_gate_equal", "selector_above_one", "selector_zero",
        "selector_two", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8c0c8:.*be.*0x8c2cc", r"8c0cc:.*cmpibl.*1,g4,0x8c0d8",
        r"8c0d0:.*cmpibe.*0,g4,0x8c0e0", r"8c0d4:.*b.*0x8c760",
        r"8c0d8:.*cmpibe.*2,g4,0x8c660", r"8c0dc:.*b.*0x8c760"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "routes.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_common_dispatch_8c0c8_selector_routes
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        assert function(0, 0).continuation == 0x8c0e0
        assert function(1, 0).continuation == 0x8c760
        assert function(2, 0).continuation == 0x8c660
        assert function(3, 0).continuation == 0x8c760
        assert function(0, 1).continuation == 0x8c2cc
    print("recovered 0x8c0c8 selector-route vectors: ok")


if __name__ == "__main__":
    main()
