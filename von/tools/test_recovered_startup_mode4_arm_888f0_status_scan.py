#!/usr/bin/env python3
"""Vectors for the 0x888f0 status-scan continuation."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_888f0_status_scan.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_input", "timing_after_upload", "timing_bias", "scan_count",
        "scan_limit", "first_nonzero_seen", "zero_after_nonzero_found",
        "matched_timing", "publish_address", "publish_value", "fallback_address",
        "fallback_value", "timing_wrap_count", "return_target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88948:.*mov.*0,r7", r"88950:.*ld.*0x74\(r8\)",
                        r"88954:.*subo.*4,r5,r5", r"88958:.*cmpible.*0,r5,0x88960",
                        r"889b4:.*ldob.*\(g4\)\[g5\]", r"889c0:.*mov.*1,r6",
                        r"889e4:.*addo.*r7,1,r7", r"889e8:.*cmpibge.*29,r7,0x88954",
                        r"889fc:.*st.*r5,0x51c998", r"88a04:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "scan.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_888f0_status_scan
        function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        function.restype = Result
        statuses = (ctypes.c_uint8 * 29)(*[0, 0, 7, 9, 0] + [0] * 24)
        result = function(1, statuses, 0x55)
        assert (result.first_nonzero_seen, result.zero_after_nonzero_found,
                result.scan_count, result.matched_timing,
                result.publish_value, result.fallback_value) == (1, 1, 5, 0x65, 0x65, 0)
        statuses = (ctypes.c_uint8 * 29)(*[0] * 29)
        result = function(1, statuses, 0x55)
        assert (result.first_nonzero_seen, result.zero_after_nonzero_found,
                result.scan_count, result.fallback_value) == (0, 0, 29, 0x55)
        assert (result.publish_address, result.fallback_address,
                result.scan_limit, result.return_target) == (0x51c998, 0x51c9a0, 29, 0x88a04)
    print("recovered 0x888f0 status-scan vectors: ok")


if __name__ == "__main__":
    main()
