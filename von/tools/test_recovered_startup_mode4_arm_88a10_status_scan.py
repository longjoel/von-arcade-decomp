#!/usr/bin/env python3
"""Vectors for the 0x88a10 status-scan continuation."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_88a10_status_scan.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_input", "timing_after_upload", "timing_bias", "scan_count",
        "scan_limit", "zero_status_found", "matched_timing", "publish_address",
        "publish_value", "fallback_address", "fallback_value", "return_target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"88a64:.*mov.*0,r6", r"88a68:.*ld.*0x74\(r7\)",
                        r"88a6c:.*subo.*4,r5,r5", r"88a70:.*cmpible.*0,r5,0x88a78",
                        r"88ac0:.*ldob.*0x200\(r7\)\[g4\]",
                        r"88ac8:.*cmpibe.*0,g4,0x88ae0",
                        r"88acc:.*addo.*r6,1,r6", r"88ad0:.*cmpibge.*29,r6,0x88a6c",
                        r"88ad4:.*st.*g14,0x51c9a0", r"88ae0:.*st.*r5,0x51c998",
                        r"88ae8:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "scan.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88a10_status_scan
        function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        function.restype = Result
        statuses = (ctypes.c_uint8 * 29)(*[7, 8, 0] + [1] * 26)
        result = function(1, statuses, 0x44)
        assert (result.zero_status_found, result.scan_count, result.matched_timing,
                result.publish_value, result.fallback_value) == (1, 3, 0x6d, 0x6d, 0)
        statuses = (ctypes.c_uint8 * 29)(*[1] * 29)
        result = function(1, statuses, 0x44)
        assert (result.zero_status_found, result.scan_count, result.fallback_value) == (0, 29, 0x44)
        assert (result.publish_address, result.fallback_address,
                result.scan_limit, result.return_target) == (0x51c998, 0x51c9a0, 29, 0x88ae8)
    print("recovered 0x88a10 status-scan vectors: ok")


if __name__ == "__main__":
    main()
