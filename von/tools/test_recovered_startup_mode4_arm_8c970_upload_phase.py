#!/usr/bin/env python3
"""Validate the two-stage upload phase of helper 0x8c970."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_8c970_upload_phase.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "timing_before", "current_offset", "current_first_source", "current_second_source",
        "timing_after_step", "timing_next", "next_offset", "next_first_source",
        "next_second_source", "first_destination", "second_destination", "bytes",
        "upload_helper", "initial_upload_count", "retry_upload_count",
        "status_entry_count", "max_retry_passes", "retry_entry",
        "success_mode_address", "success_index_address", "failure_mode_value")]


class StatusResult(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "matched", "match_index", "mode_address", "mode_value",
        "timing_address", "timing_value")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "phase.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c970_upload_phase
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        for timing in (0, 4, 116, 120):
            result = Result()
            assert fn(timing, ctypes.byref(result)) == 1
            next_timing = timing + 4
            wrapped = next_timing - 0x78 if next_timing > 0x78 else next_timing
            current_offset = ((timing >> 2) * 3) << 9
            next_offset = ((wrapped >> 2) * 3) << 9
            assert result.current_offset == current_offset and result.timing_next == wrapped
            assert result.next_offset == next_offset
            assert result.current_first_source == 0x51d5f0 + current_offset
            assert result.current_second_source == 0x5289f0 + current_offset
            assert result.next_first_source == 0x51d5f0 + next_offset
            assert result.next_second_source == 0x5289f0 + next_offset
            assert result.first_destination == 0x503ad0 and result.second_destination == 0x5040d0
            assert result.bytes == 0x600 and result.upload_helper == 0xf5d40
            assert result.initial_upload_count == 2 and result.retry_upload_count == 2
            assert result.status_entry_count == 32 and result.max_retry_passes == 26
            assert result.retry_entry == 0x8c9cc
            assert result.success_mode_address == 0x51c998
            assert result.success_index_address == 0x51c994
            assert result.failure_mode_value == 0

        scan_fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8c970_scan_status
        scan_fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(StatusResult)]
        scan_fn.restype = ctypes.c_int
        statuses = (ctypes.c_uint8 * (32 * 0x20))()
        statuses[3 * 0x20] = 20
        statuses[3 * 0x20 + 1] = 0
        scan_result = StatusResult()
        assert scan_fn(statuses, 10, 20, 44, ctypes.byref(scan_result)) == 1
        assert (scan_result.matched, scan_result.match_index,
                scan_result.mode_value, scan_result.mode_address,
                scan_result.timing_address) == (1, 3, 44, 0x51c998, 0x51c994)
        statuses[3 * 0x20 + 1] = 1
        assert scan_fn(statuses, 10, 20, 44, ctypes.byref(scan_result)) == 1
        assert (scan_result.matched, scan_result.match_index,
                scan_result.mode_value, scan_result.mode_address,
                scan_result.timing_address, scan_result.timing_value) == (
                    0, 32, 0, 0x51c9a0, 0, 0)
    print("PASS: 0x8c970 two-stage upload phase")


if __name__ == "__main__":
    main()
