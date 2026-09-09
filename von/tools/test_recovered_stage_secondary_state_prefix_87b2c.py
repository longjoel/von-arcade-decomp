#!/usr/bin/env python3
"""Vectors for the fixed 0x87b2c secondary state/timing prefix."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_state_prefix_87b2c.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_address", ctypes.c_uint32),
                ("state_before", ctypes.c_uint32),
                ("state_after", ctypes.c_uint32),
                ("timing_address", ctypes.c_uint32),
                ("timing_before", ctypes.c_uint32),
                ("timing_candidate", ctypes.c_uint32),
                ("timing_after", ctypes.c_uint32),
                ("timing_limit", ctypes.c_uint32),
                ("route_word", ctypes.c_uint32),
                ("selected_buffer", ctypes.c_uint32),
                ("first_service_target", ctypes.c_uint32),
                ("fixed_call_targets", ctypes.c_uint32 * 6),
                ("buffer_service_target", ctypes.c_uint32),
                ("final_service_target", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87b2c:.*ld.*0x51c988",
                        r"87b40:.*bg.*0x87b4c",
                        r"87b44:.*addo.*g5,1,g5",
                        r"87b4c:.*addo.*g4,1,g4",
                        r"87b50:.*lda.*0x77",
                        r"87b70:.*call.*0x88620",
                        r"87b74:.*call.*0xc8f10",
                        r"87b78:.*mov.*0,g0",
                        r"87b7c:.*call.*0x6fec0",
                        r"87b84:.*mov.*0,g0",
                        r"87b8c:.*call.*0xc8f60",
                        r"87ba4:.*call.*0x9baa0",
                        r"87bb8:.*call.*0xde990"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "prefix.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_state_prefix_87b2c
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        zero = function(0, 0x20, 0)
        assert (zero.state_after, zero.timing_after, zero.selected_buffer) == (1, 0x20, 0x503AD0)
        advance = function(3, 0x77, 1)
        assert (advance.state_after, advance.timing_candidate, advance.timing_after,
                advance.selected_buffer) == (3, 0x78, 0, 0x5040D0)
        assert advance.first_service_target == 0x88620
        assert list(advance.fixed_call_targets[:5]) == [0xC8F10, 0x6FEC0, 0x9B308,
                                                        0x6FEC0, 0xC8F60]
        assert (advance.buffer_service_target, advance.final_service_target) == (0x9BAA0, 0xDE990)
    print("recovered 0x87b2c secondary-state-prefix vectors: ok")


if __name__ == "__main__":
    main()
