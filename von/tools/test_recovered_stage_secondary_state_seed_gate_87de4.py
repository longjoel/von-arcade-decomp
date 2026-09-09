#!/usr/bin/env python3
"""Vectors for the fixed 0x87de4 state-seed gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_state_seed_gate_87de4.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("timing_address", ctypes.c_uint32),
                ("timing_value", ctypes.c_uint32),
                ("timing_compare_address", ctypes.c_uint32),
                ("timing_compare_value", ctypes.c_uint32),
                ("state_address", ctypes.c_uint32),
                ("state_value", ctypes.c_uint32),
                ("seed_value", ctypes.c_uint32),
                ("timing_equal", ctypes.c_uint32),
                ("state_is_minus_one", ctypes.c_uint32),
                ("seed_stored", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87de4:.*ld.*0x51d5e4",
                        r"87dec:.*ld.*0x51d5e8",
                        r"87df4:.*cmpibne.*g5,g4.*0x87e10",
                        r"87df8:.*ld.*0x51c988",
                        r"87e00:.*subo.*1,0,g3",
                        r"87e04:.*cmpibne.*g4,g3.*0x87e10",
                        r"87e08:.*st.*0x51c988"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "seed.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_state_seed_gate_87de4
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32]
        function.restype = Result
        seeded = function(4, 4, 0xFFFFFFFF, 0x12345678)
        assert (seeded.timing_equal, seeded.state_is_minus_one,
                seeded.seed_stored, seeded.continuation) == (1, 1, 1, 0x87E10)
        not_seeded = function(4, 5, 0xFFFFFFFF, 0x12345678)
        assert not_seeded.seed_stored == 0
        not_sentinel = function(4, 4, 0, 0x12345678)
        assert not_sentinel.seed_stored == 0
    print("recovered 0x87de4 secondary-state-seed-gate vectors: ok")


if __name__ == "__main__":
    main()
