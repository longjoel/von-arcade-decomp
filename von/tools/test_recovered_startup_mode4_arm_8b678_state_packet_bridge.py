#!/usr/bin/env python3
"""Vectors for the 0x8b678 shared state/packet bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8b678_state_packet_bridge.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "flag_51d5e0", "candidate_51d5e4", "state_51c9b8", "retry_51c9bc",
        "retry_limit", "retry_active", "published_word_51c988", "delta_10",
        "delta_8", "packet_command", "packet_selector", "fifo_response",
        "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8b678:.*ld.*0x51d5e0", r"8b680:.*cmpibne.*0,g4,0x8b6a8",
        r"8b694:.*cmpibne.*g5,g4,0x8b6dc", r"8b69c:.*st.*g9,0x51d5e0",
        r"8b6b4:.*addo.*g4,1,g4", r"8b6b8:.*cmpi.*26,g4",
        r"8b6c8:.*addo.*31,30,g8", r"8b6d4:.*st.*g14,0x51d5e0",
        r"8b6f4:.*mov.*10,g9", r"8b710:.*ld.*0x51c99c",
        r"8b724:.*stos.*r7,0x51c940"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "bridge.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8b678_state_packet_bridge
        function.argtypes = [ctypes.c_uint32] * 12
        function.restype = Result
        matched = function(0, 9, 9, 4, 0x55, 7, 100, 80, 40, 10, 2, 0x1234)
        assert (matched.flag_51d5e0, matched.retry_active, matched.delta_10,
                matched.delta_8, matched.packet_command, matched.fifo_response) == (1, 0, 20, 30, 10, 0x1234)
        retry = function(1, 0, 9, 4, 0x55, 7, 100, 80, 40, 10, 2, 0x5678)
        assert (retry.retry_51c9bc, retry.retry_active, retry.published_word_51c988,
                retry.flag_51d5e0) == (5, 1, 38, 0x55)
        exhausted = function(1, 0, 9, 25, 0x55, 7, 100, 80, 40, 10, 2, 0)
        assert (exhausted.retry_51c9bc, exhausted.retry_active, exhausted.published_word_51c988) == (26, 0, 0)
    print("recovered 0x8b678 state/packet-bridge vectors: ok")


if __name__ == "__main__":
    main()
