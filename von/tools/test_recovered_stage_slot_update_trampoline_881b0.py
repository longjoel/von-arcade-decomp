#!/usr/bin/env python3
"""Vectors for the fixed 0x881b0 slot-update trampoline."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_slot_update_trampoline_881b0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("counter_value", ctypes.c_uint32),
                ("first_value", ctypes.c_uint32),
                ("second_value", ctypes.c_uint32),
                ("modulo_divisor", ctypes.c_uint32),
                ("counter_remainder", ctypes.c_uint32),
                ("row_offset", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32),
                ("first_store_address", ctypes.c_uint32),
                ("second_store_address", ctypes.c_uint32),
                ("trampoline_load_address", ctypes.c_uint32),
                ("trampoline_target", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"881b0:.*lda.*0x881f4",
                        r"881b8:.*mov.*g14,g2",
                        r"881c0:.*ld.*0x51c9b0",
                        r"881c8:.*shlo.*3,15,g6",
                        r"881cc:.*remo.*g6,g4,g4",
                        r"881d0:.*lda.*0x561e90",
                        r"881e0:.*st.*g0.*0x4",
                        r"881e8:.*st.*g1.*0x8",
                        r"881f0:.*bx.*\(g2\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "slot.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_slot_update_trampoline_881b0
        function.argtypes = [ctypes.c_uint32] * 3
        function.restype = Result
        result = function(121, 0x11111111, 0x22222222)
        assert (result.counter_remainder, result.row_offset,
                result.first_store_address, result.second_store_address) == (1, 12, 0x561ea0, 0x561ea4)
        assert (result.first_value, result.second_value, result.table_address,
                result.trampoline_load_address, result.trampoline_target,
                result.continuation) == (0x11111111, 0x22222222, 0x561E90,
                                          0x881B0, 0x881F4, 0x881F4)
    print("recovered 0x881b0 slot-update-trampoline vectors: ok")


if __name__ == "__main__":
    main()
