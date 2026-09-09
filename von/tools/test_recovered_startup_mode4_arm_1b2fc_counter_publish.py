#!/usr/bin/env python3
"""Validate slot-11 counter snapshots, publications, and trigger gate."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_1b2fc_counter_publish.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_74_address", "counter_74_before", "counter_74_after",
        "counter_6c_address", "counter_6c_value", "counter_6c_low",
        "counter_70_address", "counter_70_value", "counter_70_low",
        "ready_address", "ready_value", "limit_address", "limit_value",
        "row_address", "row_value", "publication_30a_address",
        "publication_30a_value", "publication_30c_address", "publication_30c_value",
        "publication_30e_address", "publication_30e_value", "trigger_ready_clear",
        "trigger_progress_exceeded", "trigger_row_exceeded", "trigger_command",
        "command_address", "command_value", "trigger_call", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "counter.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_1b2fc_counter_publish
        fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(0xffffffff, 0x10009, 0x20003, 0, 4, 9, ctypes.byref(result)) == 1
        assert result.counter_74_after == 0
        assert result.publication_30a_value == 0
        assert result.publication_30c_value == 9
        assert result.publication_30e_value == 3
        assert result.trigger_command == 1 and result.command_value == 20
        assert result.trigger_call == 0x31c0 and result.continuation_target == 0x1b380

        result = Result()
        fn(7, 5, 6, 1, 4, 9, ctypes.byref(result))
        assert result.trigger_ready_clear == 0
        assert result.trigger_command == 0 and result.command_value == 0

        result = Result()
        fn(7, 0x80000005, 6, 0, 4, 9, ctypes.byref(result))
        assert result.counter_6c_low == 5
        assert result.trigger_progress_exceeded == 0 and result.trigger_command == 0

        result = Result()
        fn(7, 9, 6, 0, 4, 0x80000009, ctypes.byref(result))
        assert result.trigger_progress_exceeded == 1
        assert result.trigger_row_exceeded == 0 and result.trigger_command == 0

    print("PASS: 0x1b2fc slot-11 counter/publication seam")


if __name__ == "__main__":
    main()
