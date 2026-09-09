#!/usr/bin/env python3
"""Vectors for the shared 0x88880 record-state loader."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_secondary_record_state_loader_88880.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "phase_value", "record_word_30", "record_halfword_48",
        "linked_record_halfword_48", "record_halfword_1d6", "phase_required",
        "record_gate_address", "state_51c98c", "state_51c990", "argument_861e8",
        "helper_target", "loaded_any_state", "accepted")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88880:.*ld.*0x503a00", r"88888:.*cmpibne.*10,g4,0x888e8",
                        r"8888c:.*ldos.*0x30\(g0\)",
                        r"88890:.*cmpibne.*0,g4,0x888e8",
                        r"88894:.*ldos.*0x48\(g0\)",
                        r"888a8:.*st.*g4,0x51c98c",
                        r"888b0:.*ld.*0x74\(g0\)",
                        r"888b4:.*ldos.*0x48\(g5\)",
                        r"888c8:.*st.*g4,0x51c990",
                        r"888d0:.*ldos.*0x1d6\(g0\)",
                        r"888e4:.*bal.*0x861e8"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "loader.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_secondary_record_state_loader_88880
        function.argtypes = [ctypes.c_uint32] * 5
        function.restype = Result
        result = function(10, 0, 0x12340001, 0x56780002, 0xabcd0034)
        assert (result.accepted, result.state_51c98c, result.state_51c990,
                result.argument_861e8, result.loaded_any_state) == (1, 1, 2, 0x34, 1)
        result = function(10, 1, 3, 4, 5)
        assert result.accepted == 0 and result.state_51c98c == 0
        result = function(9, 0, 3, 4, 5)
        assert result.accepted == 0 and result.argument_861e8 == 0
        assert (result.phase_required, result.record_gate_address,
                result.helper_target) == (10, 0x30, 0x861e8)
    print("recovered 0x88880 record-state-loader vectors: ok")


if __name__ == "__main__":
    main()
