#!/usr/bin/env python3
"""Validate slot-20 response normalization and dispatch selection."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_86eec_response_selector.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "response_value", "response_source_address", "special_response", "special_store_address", "special_store_value",
        "special_path", "response_mask", "response_byte", "normalized_response",
        "normalization_remainder", "threshold", "threshold_exceeded", "dispatch_table_address",
        "dispatch_index", "dispatch_slot_address", "dispatch_target", "continuation_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selector.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_86eec_response_selector
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int

        result = Result()
        assert fn(10, ctypes.byref(result)) == 1
        assert result.response_source_address == 0x51C98C
        assert result.special_path == 1 and result.special_store_address == 0x51c97c
        assert result.special_store_value == 8 and result.continuation_target == 0x873cc

        result = Result()
        fn(0x17, ctypes.byref(result))
        assert result.response_byte == 0x17
        assert result.normalization_remainder == 4 and result.normalized_response == 0x13
        assert result.dispatch_index == 0x13
        assert result.dispatch_slot_address == 0x86f34 + 0x13 * 4
        assert result.dispatch_target == 0x878e8

        result = Result()
        fn(0xf0, ctypes.byref(result))
        assert result.normalized_response == 0xeb
        assert result.threshold_exceeded == 1 and result.continuation_target == 0x878e8

        result = Result()
        fn(0x20, ctypes.byref(result))
        assert result.normalized_response == 0x1f
        assert result.dispatch_target == 0x87210

        result = Result()
        fn(0xa9, ctypes.byref(result))
        assert result.normalized_response == 0xa9
        assert result.dispatch_target == 0x8737c

        expected_targets = {
            0x01: 0x871f4, 0x1f: 0x87210, 0x25: 0x8722c,
            0x31: 0x87248, 0x37: 0x87264, 0x3d: 0x87280,
            0x49: 0x8729c, 0x4f: 0x872d0, 0x7f: 0x8730c,
            0x85: 0x87328, 0x8b: 0x87344, 0x9d: 0x87360,
            0xa9: 0x8737c,
        }
        for index, target in expected_targets.items():
            result = Result()
            fn(index, ctypes.byref(result))
            assert result.normalized_response == index
            assert result.dispatch_slot_address == 0x86f34 + index * 4
            assert result.dispatch_target == target
        for index in (0, 7, 0x7d, 0x7e):
            result = Result()
            fn(index, ctypes.byref(result))
            assert result.dispatch_target == 0x878e8, (index, hex(result.normalized_response), hex(result.dispatch_target))

    print("PASS: 0x86eec startup slot-20 response selector")


if __name__ == "__main__":
    main()
