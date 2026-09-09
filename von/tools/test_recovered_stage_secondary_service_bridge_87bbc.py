#!/usr/bin/env python3
"""Vectors for the fixed 0x87bbc secondary service bridge."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_service_bridge_87bbc.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("first_buffer", ctypes.c_uint32),
                ("second_buffer", ctypes.c_uint32),
                ("callback_503ad4", ctypes.c_uint32),
                ("callback_5040d4", ctypes.c_uint32),
                ("call_targets", ctypes.c_uint32 * 9),
                ("call_buffer_arguments", ctypes.c_uint32 * 9)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87bb8:.*call.*0xde990",
                        r"87bc4:.*call.*0xbe1f0",
                        r"87bd0:.*call.*0xbd730",
                        r"87be4:.*callx.*\(g1\)",
                        r"87bf0:.*call.*0x23980",
                        r"87bfc:.*call.*0xdf070",
                        r"87c08:.*bal.*0x26cb8",
                        r"87c14:.*call.*0xbd810",
                        r"87c28:.*callx.*\(g1\)"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "bridge.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_service_bridge_87bbc
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        result = function(0x11111111, 0x22222222)
        assert (result.first_buffer, result.second_buffer) == (0x503AD0, 0x5040D0)
        assert list(result.call_targets) == [0xDE990, 0xBE1F0, 0xBD730,
                                             0x11111111, 0x23980, 0xDF070,
                                             0x26CB8, 0xBD810, 0x22222222]
        assert list(result.call_buffer_arguments) == [0, 0x503AD0, 0x503AD0,
                                                      0x503AD0, 0x503AD0,
                                                      0x503AD0, 0x5040D0,
                                                      0x5040D0, 0x5040D0]
    print("recovered 0x87bbc secondary-service-bridge vectors: ok")


if __name__ == "__main__":
    main()
