#!/usr/bin/env python3
"""Vectors for the 0x88af0 status/timing tail."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88af0_status_gate.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_input", "timing_after_upload", "timing_bias", "marker_1d0",
        "scan_count", "scan_limit", "match_found", "published_value",
        "publication_address", "no_match_value", "timing_wrap_count", "return_target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88b44:.*mov.*0,r6", r"88b48:.*ld.*0x74\(r7\)",
                        r"88b4c:.*subo.*4,r5,r5", r"88b50:.*cmpible.*0,r5,0x88b58",
                        r"88b94:.*ldos.*0x1d0\(r7\)", r"88b98:.*cmpibe.*0,g4,0x88bb4",
                        r"88b9c:.*subo.*6,r5,r4", r"88ba8:.*st.*r4,0x51c9b8",
                        r"88bb8:.*cmpibge.*29,r6,0x88b4c",
                        r"88bbc:.*subo.*1,0,g3", r"88bc0:.*st.*g3,0x51c9b8",
                        r"88bc8:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88af0_status_gate
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        function.restype = Result
        result = function(1, 1)
        assert (result.match_found, result.scan_count, result.published_value) == (1, 1, 0x6f)
        result = function(1, 0)
        assert (result.match_found, result.scan_count, result.published_value) == (0, 29, 0xffffffff)
        assert (result.publication_address, result.no_match_value,
                result.scan_limit, result.return_target) == (0x51c9b8, 0xffffffff, 29, 0x88bc8)
    print("recovered 0x88af0 status-gate vectors: ok")


if __name__ == "__main__":
    main()
