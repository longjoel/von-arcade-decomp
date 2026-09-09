#!/usr/bin/env python3
"""Vectors for the 0x8b620 post-selector dispatch gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b620_dispatch_gate.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_51c984", "g14_value", "threshold_61", "threshold_77",
        "selector_51c99c", "source_object", "linked_record", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b620:.*mov.*g8,r15", r"8b62c:.*ld.*0x51c984",
                        r"8b634:.*addo.*31,28,g9", r"8b638:.*ld.*0x74\(g0\)",
                        r"8b63c:.*cmpi.*g4,g9", r"8b648:.*st.*g14,0x51c99c",
                        r"8b654:.*lda.*0x77", r"8b658:.*cmpibg.*g4,g8,0x8b66c",
                        r"8b65c:.*mov.*1,g9", r"8b66c:.*mov.*2,g8",
                        r"8b678:.*ld.*0x51d5e0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b620_dispatch_gate
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        low = function(61, 5, 0x100, 0x200)
        assert (low.selector_51c99c, low.threshold_61, low.continuation) == (5, 61, 0x8b678)
        middle = function(0x77, 5, 0x100, 0x200)
        assert middle.selector_51c99c == 1
        high = function(0x78, 5, 0x100, 0x200)
        assert high.selector_51c99c == 2
    print("recovered 0x8b620 dispatch-gate vectors: ok")


if __name__ == "__main__":
    main()
