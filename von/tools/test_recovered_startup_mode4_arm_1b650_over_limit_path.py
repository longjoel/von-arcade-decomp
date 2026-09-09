#!/usr/bin/env python3
"""Validate slot-12 over-limit record and notification sequencing."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b650_over_limit_path.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_31c0_call", "helper_31c0_target", "selector_address",
        "selector_value", "record_index_address", "record_index",
        "record_table_base", "record_lane_offset", "record_increment",
        "record_value_before", "record_value_after",
        "record_address", "helper_2330_call", "helper_2330_target",
        "status_word_address", "status_word_value", "status_byte_address",
        "status_byte_value", "helper_29c08_call", "helper_29c08_target",
        "state_address", "state_before", "state_after", "command_address",
        "command_value", "row_address", "row_before", "row_counter_address",
        "row_counter_increment", "notify_selector_address",
        "notify_selector_value", "notify_argument", "helper_184e8_call",
        "helper_184e8_target", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "over_limit.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b650_over_limit_path
        fn.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(1, 3, 12, 0, 9, 5, 0, 0, ctypes.byref(result)) == 1
        assert result.record_lane_offset == 0xac and result.command_value == 19
        assert result.record_address == 0x1d00000 + (3 << 4) + 0xac
        assert (result.record_value_before, result.record_value_after) == (12, 13)
        assert result.state_after == 15 and result.helper_29c08_call == 0
        assert result.notify_argument == 0xf0 and result.continuation_target == 0x1b950

        result = Result()
        fn(0, 7, 99, 7, 0, 0, 5, 1, ctypes.byref(result))
        assert result.record_lane_offset == 0xb0 and result.helper_29c08_call == 1
        assert result.record_address == 0x1d00000 + (7 << 4) + 0xb0
        assert (result.record_value_before, result.record_value_after) == (99, 100)
        assert result.command_value == 20 and result.state_after == 1
        assert result.row_counter_increment == 1 and result.notify_argument == 0xf9

        result = Result()
        fn(0, 1, 3, 7, 1, 4, 2, 0, ctypes.byref(result))
        assert result.helper_29c08_call == 0 and result.command_value == 19
        assert result.state_after == 15 and result.row_counter_increment == 0

        result = Result()
        fn(1, 2, 4, 0, 0, 1, 0, 0, ctypes.byref(result))
        assert result.helper_29c08_call == 1
        result = Result()
        fn(1, 2, 4, 0, 7, 1, 0, 0, ctypes.byref(result))
        assert result.helper_29c08_call == 0

    print("PASS: 0x1b650 slot-12 over-limit path")


if __name__ == "__main__":
    main()
