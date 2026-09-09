#!/usr/bin/env python3
"""Validate the exact indexed-upload phase of helper 0x88a10."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_88a10_indexed_upload_phase.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_input", "timing_bias", "effective_timing", "timing_shifted", "table_offset",
        "first_source", "first_destination", "second_source", "second_destination", "bytes",
        "upload_helper", "upload_count", "status_scan_count")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "phase.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_88a10_indexed_upload_phase
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for timing in (0, 1, 0x20, 0x77, 0xffffffff):
            result = Result()
            assert fn(timing, ctypes.byref(result)) == 1
            effective = ((timing + 0x78) & 0xffffffff) if timing else 0
            offset = (((effective >> 2) * 3) << 9) & 0xffffffff
            assert result.effective_timing == effective and result.table_offset == offset
            assert result.first_source == (0x51d5f0 + offset) & 0xffffffff
            assert result.second_source == (0x5289f0 + offset) & 0xffffffff
            assert result.first_destination == 0x503ad0 and result.second_destination == 0x5040d0
            assert result.bytes == 0x600 and result.upload_helper == 0xf5d40
            assert result.upload_count == 2 and result.status_scan_count == 29
    print("PASS: 0x88a10 indexed upload phase")


if __name__ == "__main__":
    main()
