#!/usr/bin/env python3
"""Validate slot-20 shared upload/state tail."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_878f8_shared_tail.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status_a_address", "status_a_value", "status_a_mode_write", "status_b_address",
        "status_b_value", "status_b_mode_write", "mode_address", "mode_value", "mode_write_count", "timing_address",
        "timing_before", "timing_incremented", "timing_after", "timing_limit", "timing_table_index",
        "timing_table_shifted", "timing_table_scaled", "first_source", "first_destination",
        "first_bytes", "second_source", "second_destination", "second_bytes", "upload_call",
        "upload_count", "post_upload_call", "marker_address", "marker_value", "seed_value",
        "seed_addresses0", "seed_addresses1", "seed_addresses2", "seed_addresses3",
        "seed_addresses4", "seed_addresses5", "terminal_state_address", "terminal_state_value", "return_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "tail.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_878f8_shared_tail
        fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(6, 7, 0x20, 0x49, 0x55, 4, ctypes.byref(result)) == 1
        assert result.status_a_mode_write == 1 and result.status_b_mode_write == 0
        assert result.mode_value == 1 and result.timing_incremented == 0x21
        assert result.timing_after == 0x21
        assert result.timing_table_shifted == 0x12
        assert result.timing_table_scaled == 0x6c00
        assert result.first_source == 0x5241f0 and result.second_source == 0x52f5f0
        assert result.first_destination == 0x503ad0 and result.second_destination == 0x5040d0
        assert result.upload_call == 0xf5d40 and result.upload_count == 2
        assert result.post_upload_call == 0x88380
        assert result.marker_address == 0x503a60 and result.marker_value == 1
        assert result.mode_address == 0x51c97c and result.mode_write_count == 1
        assert (result.seed_addresses0, result.seed_addresses1, result.seed_addresses2,
                result.seed_addresses3, result.seed_addresses4, result.seed_addresses5) == (
                    0x51c988, 0x51c99c, 0x51d5e0, 0x51c9c0, 0x51c9b4, 0x51c9bc)
        assert result.terminal_state_value == 5 and result.return_target == 0x87a00

        result = Result()
        fn(7, 7, 0x76, 0, 0x55, 0xffffffff, ctypes.byref(result))
        assert result.mode_write_count == 0 and result.mode_value == 1 and result.timing_after == 0x77
        result = Result()
        fn(7, 7, 0x77, 0, 0x55, 0xffffffff, ctypes.byref(result))
        assert result.timing_incremented == 0x78 and result.timing_after == 0x55
        assert result.terminal_state_value == 0

        result = Result()
        fn(0, 0, 0x76, 0, 0x55, 9, ctypes.byref(result))
        assert result.mode_write_count == 2 and result.status_a_mode_write == 1
        assert result.status_b_mode_write == 1 and result.terminal_state_value == 10

    print("PASS: 0x878f8 shared slot-20 tail")


if __name__ == "__main__":
    main()
