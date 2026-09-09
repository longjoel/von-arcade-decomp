#!/usr/bin/env python3
"""Validate the secondary slot-20 response selector."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_mode4_arm_873dc_secondary_selector.c"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status_value", "response_value", "response_mask", "normalized_response",
        "status_source_address", "response_source_address",
        "special_response", "special_mode", "special_store_address", "special_store_value",
        "special_path", "special_target", "response_byte", "normalization_remainder", "threshold",
        "failure_target", "table_address", "dispatch_index", "dispatch_slot_address", "dispatch_target")]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "selector.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE), "-o", str(library)], check=True)
        fn = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_873dc_secondary_selector
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        result = Result()
        assert fn(1, 0x1f, ctypes.byref(result)) == 1
        assert (result.status_source_address, result.response_source_address) == (0x51C9D0, 0x51C990)
        assert result.dispatch_target == 0x878e8
        result = Result()
        assert fn(0, 10, ctypes.byref(result)) == 1
        assert result.special_mode == 9 and result.special_store_address == 0x51c97c
        assert result.special_store_value == 9 and result.special_path == 1
        assert result.dispatch_target == 0x878d8
        expected = {1: 0x876e8, 0x1f: 0x87704, 0x25: 0x87720, 0x31: 0x8775c,
                    0x37: 0x87778, 0x3d: 0x87794, 0x49: 0x8779c, 0x4f: 0x877d0,
                    0x7f: 0x8780c, 0x85: 0x87828, 0x8b: 0x87844, 0x9d: 0x8784c,
                    0xa9: 0x87888}
        for response, target in expected.items():
            result = Result()
            assert fn(0, response, ctypes.byref(result)) == 1
            assert result.normalized_response == response
            assert result.dispatch_index == response
            assert result.dispatch_slot_address == 0x87428 + response * 4
            assert result.dispatch_target == target
        for response in (0, 7, 0x7d, 0x7e, 0xb0, 0xff):
            result = Result()
            assert fn(0, response, ctypes.byref(result)) == 1
            assert result.dispatch_target == 0x878e8
    print("PASS: 0x873dc secondary slot-20 selector")


if __name__ == "__main__":
    main()
