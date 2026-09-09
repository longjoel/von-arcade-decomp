#!/usr/bin/env python3
"""Vectors for the 0x88d70 response/state bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88d70_response_state_bridge.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_184", "first_fifo_response", "record_8", "second_fifo_response",
        "record_10", "derived_51c950", "derived_51c954", "state_51c940",
        "state_51c948", "address_51c940", "address_51c948", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88d70:.*ld.*0x10\(g0\)", r"88d74:.*addr.*g2,g1,g0",
                        r"88d78:.*subr.*g6,g4,g1", r"88d84:.*stos.*g7,0x51c940",
                        r"88d8c:.*st.*g5,0x51c948", r"88d9c:.*st.*g0,0x51c950",
                        r"88da4:.*st.*g1,0x51c954", r"88dac:.*bl.*0x88de4"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "bridge.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88d70_response_state_bridge
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        result = function(0x100, 0x200, 0x30, 0x40, 0x500)
        assert (result.derived_51c950, result.derived_51c954,
                result.state_51c940, result.state_51c948) == (0x230, 0x4c0, 0x100, 0x42a00000)
        assert (result.address_51c940, result.address_51c948, result.continuation) == (
            0x51c940, 0x51c948, 0x88da8)
    print("recovered 0x88d70 response-state-bridge vectors: ok")


if __name__ == "__main__":
    main()
