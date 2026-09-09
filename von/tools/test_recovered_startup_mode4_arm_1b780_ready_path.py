#!/usr/bin/env python3
"""Validate slot-12 ready-path record updates and state selection."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b780_ready_path.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "ready_required", "ready_value", "record_index_address", "record_index",
        "record_table_base", "record_table_offset", "record_table_entry_address",
        "record_table_entry_before", "record_table_entry_after", "record_counter_address",
        "record_counter_before", "record_counter_after", "record_value_address", "record_value",
        "status_address", "status_value", "status_zero", "register_19_value", "state_address",
        "state_value", "command_address", "command_value", "record_update_call",
        "message_continuation")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "ready.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b780_ready_path
        fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(1, 3, 9, 10, 0x44, 0, 9, ctypes.byref(result)) == 1
        assert result.record_table_entry_address == 0x1d00000 + (3 << 4) + 0xac
        assert result.record_table_entry_after == 10
        assert result.record_counter_after == 11 and result.record_value == 0x44
        assert result.state_value == 15 and result.command_value == 19
        assert result.record_update_call == 0x2330 and result.message_continuation == 0x1b950

        result = Result()
        fn(1, 7, 0, 0xffffffff, 0x55, 2, 9, ctypes.byref(result))
        assert result.record_counter_after == 0
        assert result.record_table_entry_after == 1
        assert result.state_value == 5 and result.command_value == 40

        result = Result()
        fn(1, 7, 0, 0, 0x55, 2, 0xffff, ctypes.byref(result))
        assert result.state_value == 5 and result.command_value == 0x1e

    print("PASS: 0x1b780 slot-12 ready path")


if __name__ == "__main__":
    main()
