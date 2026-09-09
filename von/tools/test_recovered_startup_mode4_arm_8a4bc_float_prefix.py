#!/usr/bin/env python3
"""Vectors for selector-3 floating prefix at 0x8a4bc."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a4bc_float_prefix.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_5770f0", "counter_51c984", "prior_fifo_response", "timing_delta",
        "timing_float_bits", "transformed_base", "state_51c940", "state_51c942",
        "helper_result", "selected_float", "timing_zero_path", "helper_call",
        "positive_fallback", "fifo_address", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a4bc:.*ld.*0x51c984", r"8a4c4:.*lda.*0xb4",
                        r"8a4c8:.*subo.*g4,r13,g4", r"8a4cc:.*cvtir.*g4,fp0",
                        r"8a4d4:.*lda.*0x40080000", r"8a4dc:.*divrl.*g0,fp0,g0",
                        r"8a4f0:.*ld.*0x5770f0", r"8a50c:.*lda.*0x1000\(g2\)",
                        r"8a514:.*stos.*g6,0x51c940", r"8a51c:.*subo.*g4,g6,g6",
                        r"8a520:.*stos.*g4,0x51c942", r"8a528:.*stos.*g6,0x51c940",
                        r"8a554:.*call.*0x6ece0", r"8a570:.*ble.*0x8a584"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a4bc_float_prefix
        function.argtypes = [ctypes.c_uint32] * 4
        function.restype = Result
        result = function(7, 0x78, 0x20000, 0xbf800000)
        assert (result.timing_delta, result.transformed_base, result.state_51c940,
                result.state_51c942, result.selected_float, result.timing_zero_path) == (
                    0x3c, 0x1d400, 0x1d400, 0x3c, 0xbf800000, 0)
        assert (result.helper_call, result.fifo_address, result.continuation) == (
            0x6ece0, 0x884000, 0x8a584)
    print("recovered 0x8a4bc floating-prefix vectors: ok")


if __name__ == "__main__":
    main()
