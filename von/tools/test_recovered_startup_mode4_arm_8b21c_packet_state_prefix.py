#!/usr/bin/env python3
"""Vectors for selector-3 post-dispatch prefix at 0x8b21c."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b21c_packet_state_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_51c984", "prior_response_base", "timing_delta", "computed_float_word",
        "transformed_base", "state_51c940", "state_51c942", "state_51c948",
        "timing_5770f0", "helper_call", "fifo_address", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8b21c:.*ld.*0x51c984", r"8b224:.*lda.*0xb4",
                        r"8b228:.*subo.*g4,r13,g4", r"8b22c:.*cvtir.*g4,fp0",
                        r"8b24c:.*addrl.*g0,g6,g0", r"8b250:.*ld.*0x5770f0",
                        r"8b26c:.*lda.*0x1000\(g2\)", r"8b274:.*stos.*g6,0x51c940",
                        r"8b27c:.*subo.*g4,g6,g6", r"8b280:.*stos.*g4,0x51c942",
                        r"8b288:.*stos.*g6,0x51c940", r"8b290:.*st.*g0,0x51c948",
                        r"8b298:.*bl.*0x8b2e0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b21c_packet_state_prefix
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(0x78, 0x20000, 0x40600000, 7)
        assert (result.timing_delta, result.transformed_base, result.state_51c940,
                result.state_51c942, result.state_51c948, result.continuation) == (
                    0x3c, 0x1d400, 0x1d400, 0x3c00, 0x40600000, 0x8b298)
    print("recovered 0x8b21c packet/state-prefix vectors: ok")


if __name__ == "__main__":
    main()
