#!/usr/bin/env python3
"""Vectors for the fixed 0x87ce8 timer-publication gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_timer_publication_87ce8.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_value", ctypes.c_int32),
                ("source_51cbb0", ctypes.c_int16),
                ("source_51d1b0", ctypes.c_int16),
                ("controller_value", ctypes.c_uint32),
                ("state_nonnegative", ctypes.c_uint32),
                ("timer_503ca0", ctypes.c_int16),
                ("timer_5042a0", ctypes.c_int16),
                ("timer_a_address", ctypes.c_uint32),
                ("timer_b_address", ctypes.c_uint32),
                ("first_service_target", ctypes.c_uint32),
                ("first_service_argument", ctypes.c_uint32),
                ("formatter_target", ctypes.c_uint32),
                ("formatter_argument_0", ctypes.c_uint32),
                ("formatter_argument_1", ctypes.c_uint32),
                ("controller_service_target", ctypes.c_uint32),
                ("controller_service_argument", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87ce8:.*ld.*0x51c988",
                        r"87cf0:.*cmpibg.*0.*0x87d14",
                        r"87cf4:.*ldos.*0x51cbb0",
                        r"87cfc:.*ldos.*0x51d1b0",
                        r"87d04:.*stos.*0x503ca0",
                        r"87d0c:.*stos.*0x5042a0",
                        r"87d18:.*call.*0x23d60",
                        r"87d24:.*bal.*0x1cac8",
                        r"87d34:.*call.*0x1fe60"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "publication.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_timer_publication_87ce8
        function.argtypes = [ctypes.c_int32, ctypes.c_int16, ctypes.c_int16,
                             ctypes.c_uint32]
        function.restype = Result
        positive = function(3, -12, 34, 7)
        assert (positive.state_nonnegative, positive.timer_503ca0,
                positive.timer_5042a0, positive.controller_service_argument) == (1, -12, 34, 4)
        assert (positive.first_service_target, positive.first_service_argument) == (0x23D60, 1)
        assert (positive.formatter_target, positive.formatter_argument_0,
                positive.formatter_argument_1) == (0x1CAC8, 21, 14)
        negative = function(-1, -12, 34, 0)
        assert (negative.state_nonnegative, negative.timer_503ca0,
                negative.timer_5042a0, negative.controller_service_argument) == (0, 0, 0, 0)
    print("recovered 0x87ce8 secondary-timer-publication vectors: ok")


if __name__ == "__main__":
    main()
