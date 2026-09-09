#!/usr/bin/env python3
"""Vectors for the shared 0x8bfd0 post-epilogue dispatch."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_common_dispatch_8bfd0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "initial_selector", "scan_word_51c998", "candidate_51d5e4", "mode_byte",
        "state_51c9a0", "g14_value", "retry_51c9a8", "selector_51c99c",
        "state_updated", "retry_limit", "retry_promoted", "current_record_10",
        "linked_record_10", "current_record_8", "linked_record_8", "delta_10",
        "delta_8", "packet_command", "fifo_response", "continuation")]


def main():
    listing = LISTING.read_text()
    for instruction in (
        r"8bfd0:.*addo.*16,sp,sp", r"8bfd4:.*ld.*0x51c99c,g4",
        r"8bff0:.*ld.*0x51c998,g5", r"8bff8:.*ld.*0x51d5e4,g4",
        r"8c004:.*st.*g14,0x51c9a0", r"8c028:.*cmpibne.*1,g4,0x8c038",
        r"8c02c:.*st.*g14,0x51c99c", r"8c03c:.*st.*r9,0x51c99c",
        r"8c044:.*ld.*0x51c99c,g4", r"8c058:.*addo.*g4,1,g4",
        r"8c06c:.*cmpibl.*9,g4,0x8c078", r"8c070:.*st.*g14,0x51c99c",
        r"8c078:.*ld.*0x10\(r4\),g5", r"8c090:.*mov.*10,r8",
        r"8c0ac:.*ld.*0x51c99c,g4", r"8c0c0:.*stos.*g2,0x51c940"):
        assert re.search(instruction, listing)
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "dispatch.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_common_dispatch_8bfd0
        function.argtypes = [ctypes.c_uint32] * 12
        function.restype = Result
        promoted = function(0, 7, 7, 0, 0, 3, 4, 100, 80, 40, 10, 0x1234)
        assert (promoted.state_51c9a0, promoted.selector_51c99c, promoted.state_updated,
                promoted.retry_51c9a8, promoted.retry_promoted) == (3, 3, 1, 4, 0)
        held = function(1, 7, 9, 1, 2, 3, 7, 100, 80, 40, 10, 0)
        assert (held.selector_51c99c, held.retry_51c9a8, held.retry_promoted) == (3, 8, 1)
        packet = function(2, 0, 0, 1, 4, 3, 0, 100, 80, 40, 10, 0x5678)
        assert (packet.delta_10, packet.delta_8, packet.packet_command, packet.fifo_response) == (20, 30, 10, 0x5678)
    print("recovered 0x8bfd0 common-dispatch vectors: ok")


if __name__ == "__main__":
    main()
