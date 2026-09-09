#!/usr/bin/env python3
"""Vectors for the fixed 0x87f60 counter gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_counter_gate_87f60.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("phase_value", ctypes.c_uint32),
                ("counter_before", ctypes.c_uint32),
                ("seed_value", ctypes.c_uint32),
                ("counter_address", ctypes.c_uint32),
                ("counter_after", ctypes.c_uint32),
                ("initializer_target", ctypes.c_uint32),
                ("initializer_called", ctypes.c_uint32),
                ("counter_low_bits", ctypes.c_uint32),
                ("modulo_upload_admitted", ctypes.c_uint32),
                ("modulo_base", ctypes.c_uint32),
                ("modulo_remainder", ctypes.c_uint32),
                ("modulo_divisor", ctypes.c_uint32),
                ("upload_body_target", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87f60:.*ld.*0x503a14",
                        r"87f74:.*bne.*0x87f88",
                        r"87f78:.*st.*0x51c9b0",
                        r"87f80:.*call.*0x8d170",
                        r"87f90:.*addo.*g4,1,g4",
                        r"87f94:.*st.*0x51c9b0",
                        r"87fa4:.*and.*3,g0,g4",
                        r"87fa8:.*cmpibne.*0,g4.*0x88030"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "counter.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_counter_gate_87f60
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        first = function(0, 99, 120)
        assert (first.initializer_called, first.counter_after,
                first.modulo_upload_admitted, first.modulo_remainder) == (1, 120, 1, 0)
        later = function(1, 119, 0)
        assert (later.initializer_called, later.counter_after,
                later.counter_low_bits, later.modulo_upload_admitted,
                later.modulo_remainder) == (0, 120, 0, 1, 0)
        skipped = function(1, 4, 0)
        assert (skipped.counter_after, skipped.counter_low_bits,
                skipped.modulo_upload_admitted) == (5, 1, 0)
        assert (later.counter_address, later.initializer_target,
                later.modulo_base, later.modulo_divisor,
                later.upload_body_target) == (0x51C9B0, 0x8D170, 120, 120, 0x87FAC)
    print("recovered 0x87f60 secondary-counter-gate vectors: ok")


if __name__ == "__main__":
    main()
