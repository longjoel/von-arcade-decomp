#!/usr/bin/env python3
"""Validate slot-12 clear-ready record and row transitions."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b818_clear_ready_path.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "ready_required", "ready_value", "initial_state_address", "initial_state",
        "record_index_address", "record_index", "record_table_base", "record_table_offset",
        "record_table_entry_address", "record_table_entry_before", "record_table_entry_after",
        "record_counter_address", "record_counter_before", "record_counter_after", "row_address",
        "row_before", "row_after", "incoming_value", "row_overwritten", "row_limit",
        "below_row_limit", "state_address", "state_value", "command_address", "command_value",
        "helper_call", "helper_target", "phase_continuation")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "clear.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b818_clear_ready_path
        fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0, 2, 10, 20, 7, 6, ctypes.byref(result)) == 1
        assert result.initial_state == 7 and result.record_counter_after == 21
        assert result.record_table_entry_address == 0x1d00000 + (2 << 4) + 0xac
        assert result.row_before == 7 and result.row_after == 6
        assert result.row_overwritten == 1 and result.helper_call == 0x31c0
        assert result.command_value == 19 and result.state_value == 17
        assert result.phase_continuation == 0x1b940

        result = Result()
        fn(0, 2, 10, 20, 8, 9, ctypes.byref(result))
        assert result.row_after == 9 and result.row_overwritten == 0
        assert result.helper_call == 0 and result.state_value == 7
        assert result.phase_continuation == 0x1b8a8

        result = Result()
        fn(0, 2, 10, 20, 0x80000000, 9, ctypes.byref(result))
        assert result.row_after == 9 and result.below_row_limit == 1
        assert result.row_overwritten == 1 and result.helper_call == 0x31c0

    print("PASS: 0x1b818 slot-12 clear-ready path")


if __name__ == "__main__":
    main()
