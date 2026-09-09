#!/usr/bin/env python3
"""Vectors for the six-entry 0x88cec dispatch table."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88cec_dispatch_table.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector", "table_address", "entry_address", "target_address",
        "entry_count", "in_range")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88cd4:.*ld.*0x51c99c", r"88ce0:.*ld.*0x88cec\[g4\*4\]",
                        r"88ce8:.*bx.*\(g4\)", r"88cec:.*\.word.*0x00088d04",
                        r"88cf0:.*\.word.*0x00088ea0", r"88cf4:.*\.word.*0x0008903c",
                        r"88cf8:.*\.word.*0x0008931c", r"88cfc:.*\.word.*0x00089930",
                        r"88d00:.*\.word.*0x00089814"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "table.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88cec_dispatch_table
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        expected = [0x88d04, 0x88ea0, 0x8903c, 0x8931c, 0x89930, 0x89814]
        for selector, target in enumerate(expected):
            result = function(selector)
            assert (result.in_range, result.entry_address, result.target_address) == (
                1, 0x88cec + selector * 4, target)
        result = function(6)
        assert result.in_range == 0 and result.target_address == 0
        assert (result.table_address, result.entry_count) == (0x88cec, 6)
    print("recovered 0x88cec dispatch-table vectors: ok")


if __name__ == "__main__":
    main()
