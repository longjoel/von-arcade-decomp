#!/usr/bin/env python3
"""Vectors for the fixed 0x87d14 command/setup bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_command_setup_87d14.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("first_service_target", ctypes.c_uint32),
                ("first_service_argument", ctypes.c_uint32),
                ("formatter_target", ctypes.c_uint32),
                ("formatter_argument_0", ctypes.c_uint32),
                ("formatter_argument_1", ctypes.c_uint32),
                ("controller_value", ctypes.c_uint32),
                ("controller_mask", ctypes.c_uint32),
                ("controller_service_target", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87d18:.*call.*0x23d60",
                        r"87d24:.*bal.*0x1cac8",
                        r"87d28:.*ld.*0x5024e8",
                        r"87d30:.*and.*4,g0,g0",
                        r"87d34:.*call.*0x1fe60"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "setup.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_command_setup_87d14
        function.argtypes = [ctypes.c_uint32]
        function.restype = Result
        result = function(0x2f)
        assert (result.first_service_target, result.first_service_argument) == (0x23D60, 1)
        assert (result.formatter_target, result.formatter_argument_0,
                result.formatter_argument_1) == (0x1CAC8, 21, 14)
        assert (result.controller_value, result.controller_mask,
                result.controller_service_target) == (0x2F, 4, 0x1FE60)
        assert function(0x20).controller_mask == 0
    print("recovered 0x87d14 secondary-command-setup vectors: ok")


if __name__ == "__main__":
    main()
